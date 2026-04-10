from scraper.src.worker import backfill_imgurl_column, backfill_new_column, run_worker
from scraper.src.database import create_missing_col, init_db
from scraper.src.harvester import run_harvester

def main():
    # init_db()
    # run_harvester()
    # run_worker()
    # backfill_new_column()
    # create_missing_col("ads_raw", "imgUrl")
    # print("Created new col")
    backfill_imgurl_column()   
    return None

if __name__ == "__main__":
    main()