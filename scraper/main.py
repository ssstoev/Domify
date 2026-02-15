from src.database import init_db
from src.harvester import run_harvester

def main():
    init_db()
    run_harvester()
    return None

if __name__ == "__main__":
    main()