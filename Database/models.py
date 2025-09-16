# Database/database.py
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# ================================
# DIMENSION TABLES
# ================================

class DateDim(Base):
    __tablename__ = "date_dim"

    date = Column(Date, primary_key=True)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    week = Column(Integer, nullable=False)
    day_of_week_num = Column(Integer, nullable=False)  # 1=Mon, 7=Sun
    day_of_week_name = Column(String(10), nullable=False)

    # Relationships
    dram_prices = relationship("DramPrices", back_populates="date_dim")
    dram_production = relationship("DramProduction", back_populates="date_dim")
    smartphone_shipments = relationship("SmartphoneShipments", back_populates="date_dim")
    pc_shipments = relationship("PcShipments", back_populates="date_dim")
    datacenter_demand = relationship("DatacenterDemand", back_populates="date_dim")
    macro_indicators = relationship("MacroIndicators", back_populates="date_dim")
    competitor_pricing = relationship("CompetitorPricing", back_populates="date_dim")

    __table_args__ = (
        UniqueConstraint("date", name="uq_date_dim_date"),
    )

    def __repr__(self):
        return f"<DateDim(date={self.date}, year={self.year}, month={self.month})>"

class RegionDim(Base):
    __tablename__ = "region_dim"

    region_id = Column(Integer, primary_key=True, autoincrement=True)
    country_code = Column(String(5), nullable=False)
    country_name = Column(String(100), nullable=False)
    native_name = Column(String(100))
    phone_code = Column(String(20))
    continent_code = Column(String(5))
    continent_name = Column(String(50))
    capital = Column(String(100))
    currency = Column(String(50))
    languages = Column(Text)  # store as CSV

    # Relationships
    smartphone_shipments = relationship("SmartphoneShipments", back_populates="region_dim")
    macro_indicators = relationship("MacroIndicators", back_populates="region_dim")

    __table_args__ = (
        UniqueConstraint("country_code", name="uq_region_country_code"),
    )
    
    def __repr__(self):
        return f"<RegionDim(code={self.country_code}, name={self.country_name}, continent={self.continent_name})>"


# ================================
# FACT TABLES
# ================================

class DramPrices(Base):
    __tablename__ = "dram_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, ForeignKey("date_dim.date"), nullable=False)
    dram_type = Column(String(50), nullable=False)
    price_usd = Column(Float, nullable=False)
    source = Column(String(100), default="manual")

    # Relationship
    date_dim = relationship("DateDim", back_populates="dram_prices")

    def __repr__(self):
        return f"<DramPrices(date={self.date}, dram_type='{self.dram_type}', price_usd={self.price_usd})>"


class DramProduction(Base):
    __tablename__ = "dram_production"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, ForeignKey("date_dim.date"), nullable=False)
    fab_location = Column(String(100))
    dram_type = Column(String(50))
    capacity_million_gb = Column(Float)
    utilization_rate = Column(Float)

    # Relationship
    date_dim = relationship("DateDim", back_populates="dram_production")

    def __repr__(self):
        return f"<DramProduction(date={self.date}, fab_location='{self.fab_location}', dram_type='{self.dram_type}')>"


class SmartphoneShipments(Base):
    __tablename__ = "smartphone_shipments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, ForeignKey("date_dim.date"), nullable=False)
    brand = Column(String(100))
    region_id = Column(Integer, ForeignKey("region_dim.region_id"))
    shipments_million_units = Column(Float)

    # Relationships
    date_dim = relationship("DateDim", back_populates="smartphone_shipments")
    region_dim = relationship("RegionDim", back_populates="smartphone_shipments")

    def __repr__(self):
        return f"<SmartphoneShipments(date={self.date}, brand='{self.brand}', region_id={self.region_id})>"


class PcShipments(Base):
    __tablename__ = "pc_shipments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, ForeignKey("date_dim.date"), nullable=False)
    brand = Column(String(100))
    shipments_million_units = Column(Float)

    # Relationship
    date_dim = relationship("DateDim", back_populates="pc_shipments")

    def __repr__(self):
        return f"<PcShipments(date={self.date}, brand='{self.brand}', shipments={self.shipments_million_units})>"


class DatacenterDemand(Base):
    __tablename__ = "datacenter_demand"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, ForeignKey("date_dim.date"), nullable=False)
    application = Column(String(100))
    demand_million_gb = Column(Float)

    # Relationship
    date_dim = relationship("DateDim", back_populates="datacenter_demand")

    def __repr__(self):
        return f"<DatacenterDemand(date={self.date}, application='{self.application}', demand={self.demand_million_gb})>"


class MacroIndicators(Base):
    __tablename__ = "macro_indicators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, ForeignKey("date_dim.date"), nullable=False)
    indicator = Column(String(100))
    value = Column(Float)
    region_id = Column(Integer, ForeignKey("region_dim.region_id"), nullable=True)

    # Relationships
    date_dim = relationship("DateDim", back_populates="macro_indicators")
    region_dim = relationship("RegionDim", back_populates="macro_indicators")

    def __repr__(self):
        return f"<MacroIndicators(date={self.date}, indicator='{self.indicator}', value={self.value}, region_id={self.region_id})>"


class CompetitorPricing(Base):
    __tablename__ = "competitor_pricing"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, ForeignKey("date_dim.date"), nullable=False)
    competitor = Column(String(100))
    dram_type = Column(String(50))
    price_usd = Column(Float)

    # Relationship
    date_dim = relationship("DateDim", back_populates="competitor_pricing")

    def __repr__(self):
        return f"<CompetitorPricing(date={self.date}, competitor='{self.competitor}', dram_type='{self.dram_type}', price_usd={self.price_usd})>"
