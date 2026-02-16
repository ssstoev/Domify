from src.worker import run_worker
from src.database import init_db
from src.harvester import run_harvester

def main():
    init_db()
    # run_harvester()
    run_worker()    
    return None

if __name__ == "__main__":
    main()