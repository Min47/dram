from Database.database import DatabaseManager
from Database.models import DateDim, DramPrices

def main():
    # Set up database and tables
    print("")
    db = DatabaseManager(echo=False)
    db.init_db(force_reset=False)  # Force reset for demo purposes
    print("")

if __name__ == "__main__":
    main()
