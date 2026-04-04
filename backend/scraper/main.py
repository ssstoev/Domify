from src.worker import backfill_new_column, run_worker
from src.database import init_db
from src.harvester import run_harvester

def main():
    init_db()
    # run_harvester()
    # run_worker()
    backfill_new_column()    
    return None

if __name__ == "__main__":
    main()