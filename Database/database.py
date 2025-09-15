from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from Config.config import Config
from Database.models import Base  # Import the same Base and all models


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

    def init_db(self):
        """Create tables if they don't exist"""
        Base.metadata.create_all(self.engine)
        print("> Database initialized with tables.")

    def get_session(self) -> Session:
        """Get a new DB session"""
        return self.SessionLocal()

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
        """Truncate (delete all rows) from all tables"""
        with self.get_session() as session:
            for table in reversed(Base.metadata.sorted_tables):
                session.execute(table.delete())
            session.commit()
        print("> All tables truncated.")