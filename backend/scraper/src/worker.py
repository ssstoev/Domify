import sqlite3
import requests
from bs4 import BeautifulSoup
import time
import os

_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'ads_storage.db')

from scraper.src.database import add_missing_col_information, fetch_missing_rows, fetch_pending_ads, update_records

def normalize_fields(scraped_data):
    """Map Bulgarian HTML field names to database column names"""
    mapping = {
        'Цена на м2/EUR/:': 'price_m2_eur',
        'Цена на м2/BGN/:': 'price_m2_bgn',
        'Квадратура /м2/:': 'size_m2',
        'Етаж :': 'floor',
        'Акт 16:': 'akt16',
        'Енергиен клас:': 'energy_class',
        'Потребление:': 'potreblenie',
        'Дължи се комисион на брокера': 'broker_commision',
        'Бележки': 'additional_notes',
    }
    
    normalized = {}
    for bg_key, value in scraped_data.items():
        if bg_key in mapping:
            normalized[mapping[bg_key]] = value
        else:
            normalized[bg_key] = value  # Keep unmapped fields
    
    return normalized

def run_worker(batch_size=20):
    while True:
        # 1. Connect to DB for reading
        conn = sqlite3.connect(_DB_PATH)
        conn.execute("PRAGMA busy_timeout = 10000")  # 10 second timeout

        cursor = conn.cursor()
        pending_ads = fetch_pending_ads(conn, batch_size=batch_size)
        cursor.close()
        conn.close()  # Close connection completely after reading

        if not pending_ads:
            break

        updates = []
        # fetch all additional info
        for ad_item in pending_ads:
            print(10*"=" + f"Fetching the html for item {ad_item["hash_id"]}..." + 10*"=")
            item_response = requests.get(ad_item['link'])
            item_soup = BeautifulSoup(item_response.text, "html.parser")
            
            # grab the sidebar with descrtiptions (single element)
            try:
                aside_info = item_soup.find("aside", class_="info-sidebar")
                # print(aside_info)

                # find simple-table divs and filter by whether they contain td or p
                simple_tables = aside_info.find_all("div", class_="simple-table") if aside_info else []
                tables_with_td = [tbl for tbl in simple_tables if tbl.find("td")]
                tables_with_p = [tbl for tbl in simple_tables if tbl.find("p")]

                # if you want the first matching table only
                table_with_td_info = tables_with_td[0] if tables_with_td else None
                table_with_p_info = tables_with_p[0] if tables_with_p else None

                # description lives on the specific page
                description = item_soup.find("div", class_="text")
                description_text = description.get_text(" ", strip=True) if description else ""
                ad_item["description"] = description_text
                # print(description_text)
                
                for row in table_with_td_info.find_all("tr") if table_with_td_info else []:
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        key = cols[0].get_text(strip=True)
                        value = cols[1].get_text(strip=True)
                        ad_item[key] = value

                # extract text from <p> tags inside the simple-table
                p_texts = [p.get_text(" ", strip=True) for p in table_with_p_info.find_all("p")] if table_with_p_info else []
                p_texts

                # optional: split "key: value" style lines into a dict
                for text in p_texts:
                    if ":" in text:
                        key, value = text.split(":", 1)
                        ad_item[key.strip()] = value.strip()

                # print(10*"=" + f"Finished with item {id}" + 10*"=")
                ad_item = normalize_fields(ad_item)  # Convert field names
                # WIP: Scrape the total price (add DB col before that)
                update = {
                    "hash_id": ad_item["hash_id"],
                    "description": ad_item.get("description", ""),
                    "price_m2_eur": ad_item.get("price_m2_eur", ""),
                    "price_m2_bgn": ad_item.get("price_m2_bgn", ""),
                    "size_m2": ad_item.get("size_m2", ""),
                    "floor": ad_item.get("floor", ""),
                    "akt16": ad_item.get("akt16", ""),
                    "energy_class": ad_item.get("energy_class", ""),
                    "potreblenie": ad_item.get("potreblenie", ""),
                    "broker_commision": ad_item.get("broker_commision", ""),
                    "additional_notes": ad_item.get("additional_notes", ""),
                }
                updates.append(update)
            except Exception as e:
                print(f"error when processing html of page {ad_item.get('hash_id')}: {e}")
        
        # print("Updated list: \n", updates)

        # Batch update all records once - open NEW connection for writing
        if updates:
            time.sleep(0.5)  # Increase delay to ensure lock is released
            write_conn = sqlite3.connect(_DB_PATH, timeout=30)
            write_conn.execute("PRAGMA busy_timeout = 30000")
            update_records(write_conn, updates)
            write_conn.close()
        
        print(f"updated new batch of {batch_size} records")
    return None

def backfill_new_column(batch_size=20):
    total_updated_count = 0
    while True:
        # 1. Connect to DB for reading
        conn = sqlite3.connect(_DB_PATH)
        conn.execute("PRAGMA busy_timeout = 10000")  # 10 second timeout
        
        # get the urls of the empty values
        print("fetching the batch... ")
        extras_list = fetch_missing_rows(conn, "extras")
        print(f"fetched the hash_ids of the missing cols: {len(extras_list)}")
        conn.close()

        # if there're no left missing extras
        if len(extras_list) == 0:
            break

        # for each item in the extras_list scrape the data and add it to the db
        try:
            updates = []
            for item in extras_list:
                print(f"Scraping info for item {item["hash_id"]}..")
                response = requests.get(item["link"])
                print(f"Scraped the info for item {item["hash_id"]}")

                soup = BeautifulSoup(response.content, "html.parser")
                result = soup.find("ul", class_="extras")
                li_items = result.find_all('li') if result else []

                update_dict = {
                    "hash_id": item["hash_id"],
                    "extras": "; ".join([li.get_text(strip=True) for li in li_items]) if li_items else "EMPTY"
                    }
                
                updates.append(update_dict)
            print("scraping of batch finished")
        except Exception as e:
            print(e)

        if updates:
            # time.sleep(0.5)  # Increase delay to ensure lock is released
            write_conn = sqlite3.connect(_DB_PATH, timeout=30)
            write_conn.execute("PRAGMA busy_timeout = 30000")
            print("updating the DB with new info...")
            add_missing_col_information(write_conn, "extras", updates, "extras")
            write_conn.close()
        
        total_updated_count += batch_size
        print(f"updated a total of {total_updated_count} records")

    return None

def backfill_imgurl_column(batch_size=20):
    total_updated_count = 0
    while True:
        # 1. Connect to DB for reading
        conn = sqlite3.connect(_DB_PATH)
        conn.execute("PRAGMA busy_timeout = 10000")  # 10 second timeout
        
        # get the urls of the empty values
        # print("fetching the batch... ")
        result_list = fetch_missing_rows(conn, "imgUrl")
        # print(f"fetched the hash_ids of the missing cols: {len(result_list)}")
        print(result_list)
        conn.close()

        # if there're no left missing extras
        if len(result_list) == 0:
            break

        # for each item in the result_list scrape the data and add it to the db
        updates = []
        for item in result_list:
            try:
                print(f"Scraping info for item {item['link']}..")
                response = requests.get(item["link"])
                print(f"Scraped the info for item {item['link']}")

                soup = BeautifulSoup(response.content, "html.parser")
                result = soup.find("img", {"itemprop": "image"})
                src = result.get("src") if result else None
                print("src:", src)
                update_dict = {
                    "hash_id": item["hash_id"],
                    "imgUrl": "https://www.imoti.net" + src if src else "EMPTY"
                    }
                updates.append(update_dict)
            except Exception as e:
                print(f"error scraping {item.get('hash_id')}: {e}")
                # still mark as EMPTY so it won't be re-fetched endlessly
                updates.append({"hash_id": item["hash_id"], "imgUrl": "EMPTY"})
        print("scraping of batch finished")

        if updates:
            # time.sleep(0.5)  # Increase delay to ensure lock is released
            write_conn = sqlite3.connect(_DB_PATH, timeout=30)
            write_conn.execute("PRAGMA busy_timeout = 30000")
            print("updating the DB with new info...")
            add_missing_col_information(write_conn, "imgUrl", updates, "imgUrl")
            write_conn.close()
        
        total_updated_count += len(updates)
        print(f"updated a total of {total_updated_count} records")

    return None


