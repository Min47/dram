from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from Config.config import Config
from Database.models import Base, DateDim, RegionDim
from datetime import date, timedelta
import pandas as pd

class DatabaseManager:
    def __init__(self, echo: bool = False):
        # Create engine from config
        self.engine = create_engine(
            Config.postgres.connection_url(),
            echo=echo,
            future=True
        )
        # Session factory
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            future=True
        )

    def init_db(self, force_reset: bool = False):
        """Create tables if they don't exist, or reset everything if force_reset=True"""
        print("------------")
        print("| Database |")
        print("------------")
        if force_reset:
            print("> Tables: Dropping all and recreating.")
            Base.metadata.drop_all(self.engine)
        
        Base.metadata.create_all(self.engine)
        print("> Tables: Created.")

        # Ensure dimension tables are populated
        self.ensure_dimensions(date_dim=True, region_dim=force_reset)

    def get_session(self) -> Session:
        """Get a new DB session"""
        return self.SessionLocal()
    
    # ----------------------------
    # DIMENSION LOADERS
    # ----------------------------
    def ensure_date_dim(self, start_date = date(2020, 1, 1), years_ahead: int = 1):
        """
        Ensure date_dim has continuous daily entries from 2020-01-01 → today+years_ahead.
        If rows exist but range is incomplete, fill the missing dates.
        """
        with self.get_session() as session:
            end_date = date.today() + timedelta(days=365 * years_ahead)

            # Find max date already in table
            max_date = session.query(DateDim.date).order_by(DateDim.date.desc()).first()

            if max_date:
                # Continue from the day after the last date
                next_date = max_date[0] + timedelta(days=1)
                if next_date > end_date:
                    print(f"> [DataDim] Table already covers until {max_date[0]}. Nothing to add.")
                    return
                start_date = next_date  # Extend from last existing date
            else:
                print(f"> [DataDim] Table empty, starting fresh from {start_date}.")

            # Insert missing dates in bulk
            rows = []
            d = start_date
            while d <= end_date:
                rows.append(
                    DateDim(
                        date=d,
                        year=d.year,
                        quarter=(d.month - 1) // 3 + 1,
                        month=d.month,
                        week=d.isocalendar()[1],  # ISO week
                        day_of_week_num=d.isoweekday(),  # 1=Mon, 7=Sun
                        day_of_week_name=d.strftime("%A"),
                    )
                )
                d += timedelta(days=1)

            if rows:
                session.bulk_save_objects(rows)
                session.commit()
                print(f"> [DataDim] Inserted {len(rows)} new dates up to {end_date}.")
            else:
                print("> [DataDim] No new dates inserted.")

    def ensure_region_dim(self):
        """
        Populate region_dim with detailed country metadata from GitHub.
        Self-healing: inserts missing countries, skips existing.
        """
        countries_url = "https://raw.githubusercontent.com/annexare/Countries/main/dist/countries.csv"
        countries_df = pd.read_csv(countries_url)

        # Continent code -> name
        continent_map = {
            "AF": "Africa",
            "AN": "Antarctica",
            "AS": "Asia",
            "EU": "Europe",
            "NA": "North America",
            "OC": "Oceania",
            "SA": "South America",
        }
        # Reverse map: name -> code
        continent_name_to_code = {v: k for k, v in continent_map.items()}

        with self.get_session() as session:
            existing = {r.country_code for r in session.query(RegionDim.country_code).all()}
            inserted, skipped, failed = 0, 0, 0

            for idx, row in countries_df.iterrows():
                code = str(row["Code"]).strip()
                if code in existing:
                    skipped += 1
                    continue

                continent_name_raw = str(row.get("Continent", "")).strip()
                continent_code = continent_name_to_code.get(continent_name_raw, None)
                continent_name = continent_name_raw if continent_name_raw else "Unknown"

                # Clean values (replace NaN/None with None, not "nan")
                def clean(val):
                    return None if pd.isna(val) or str(val).strip().lower() == "nan" else str(val).strip()

                try:
                    session.add(
                        RegionDim(
                            country_code=code,
                            country_name=clean(row.get("Name")),
                            native_name=clean(row.get("Native")),
                            phone_code=clean(row.get("Phone")),
                            continent_code=continent_code,
                            continent_name=continent_name,
                            capital=clean(row.get("Capital")),
                            currency=clean(row.get("Currency")),
                            languages=",".join(
                                clean(row.get("Languages")).replace(";", ",").split(",")
                            ) if clean(row.get("Languages")) else None
                        )
                    )
                    session.flush()
                    inserted += 1

                except Exception as e:
                    failed += 1
                    print("[RegionDim] Insert failed at row", idx, ":", row.to_dict())
                    print("Error:", e)
                    session.rollback()

            session.commit()
            print(f"> [RegionDim] Inserted: {inserted}, skipped: {skipped}, failed: {failed}.")

    def ensure_dimensions(self, date_dim: bool = True, region_dim: bool = False):
        """Convenience method: load both date_dim & region_dim"""
        if date_dim:
            self.ensure_date_dim()
        if region_dim:
            self.ensure_region_dim()

    # ----------------------------
    # CRUD Methods
    # ----------------------------
    def add(self, obj):
        """Add a new record (ORM object)"""
        with self.get_session() as session:
            session.add(obj)
            session.commit()
            session.refresh(obj)  # Refresh to get updated fields (e.g., auto ID)
            return obj

    def update(self, model, record_id, updates: dict):
        """Update a record by primary key"""
        with self.get_session() as session:
            instance = session.get(model, record_id)
            if not instance:
                return None
            for key, value in updates.items():
                setattr(instance, key, value)
            session.commit()
            session.refresh(instance)
            return instance

    def delete(self, model, record_id):
        """Delete a record by primary key"""
        with self.get_session() as session:
            instance = session.get(model, record_id)
            if not instance:
                return False
            session.delete(instance)
            session.commit()
            return True

    def fetch_all(self, model):
        """Fetch all rows from a given model/table"""
        with self.get_session() as session:
            return session.query(model).all()
        
    def fetch_by_filter(self, model, **filters):
        """
        Fetch rows by keyword filters.
        Example: db.fetch_by_filter(DramPrices, dram_type="DDR5", price_usd=3.5)
        """
        with self.get_session() as session:
            query = session.query(model).filter_by(**filters)
            return query.all()

    # ----------------------------
    # Utility Methods
    # ----------------------------
    def truncate_all(self):
        """
        Truncate (delete all rows) from all tables.
        Resets sequences for SERIAL/IDENTITY columns too.
        """
        with self.get_session() as session:
            for table in reversed(Base.metadata.sorted_tables):
                session.execute(text(f"TRUNCATE {table.name} RESTART IDENTITY CASCADE"))
            session.commit()
        print("> All tables truncated & sequences reset.")