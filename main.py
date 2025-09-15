from Database.database import DatabaseManager
from Database.models import DateDim, DramPrices

def main():
    db = DatabaseManager(echo=False)
    db.init_db()

    # Insert sample data
    db.add(DateDim(date="2025-01-01", year=2025, quarter=1, month=1, week=1, day_of_week="Monday"))
    db.add(DramPrices(date="2025-01-01", dram_type="DDR5", price_usd=3.5, source="manual"))
    db.add(DramPrices(date="2025-01-01", dram_type="DDR4", price_usd=2.1, source="manual"))

    # Fetch by filter
    ddr5_prices = db.fetch_by_filter(DramPrices, dram_type="DDR5")
    print("DDR5 Prices:", ddr5_prices)

    # Fetch multiple filters
    exact_price = db.fetch_by_filter(DramPrices, dram_type="DDR4", price_usd=2.1)
    print("DDR4 @ $2.1:", exact_price)

if __name__ == "__main__":
    main()
