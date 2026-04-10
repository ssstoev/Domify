import requests
from bs4 import BeautifulSoup
import chardet
import sqlite3
import time
import os

_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'ads_storage.db')
import random

from src.database import insert_ad

# def get_last_page_nr(url: str) -> int:
#     '''Returns the total number of pages

#     Args:
#         url (str): the url of the page where you want to extract from.

#     Returns:
#         int: the number of the last page'''

#     response = requests.get(url)
#     soup = BeautifulSoup(response.content, features="html.parser")
#     last_page_number = soup.find("a", class_="last-page").get_text(strip=False)
#     return int(last_page_number)

import hashlib

def generate_ad_id(title, url):
    '''Generate unique customized ID of the ad based on stable fields.
    
    Parameters:
        title (str): ad title
        url (str): link to the ad
    
    Returns:
        str'''
    
    key = f"{title}|{url}"     # choose stable fields
    return hashlib.sha256(key.encode()).hexdigest()

def scrape_single_page(url: str):
    '''Scrape all ads from a single page
    Args:
        url (str): the url of the first page
    
    Returns:
        ads_dict (dict): Dicitonary with all the ads info from the page
    '''
    response = requests.get(url)
    # Detect the encoding of the content
    detected_encoding = chardet.detect(response.content)['encoding']
    # Decode the content using the detected encoding
    if detected_encoding:
        content = response.content.decode(detected_encoding)
    else:
        # Fallback to UTF-8 if encoding detection fails
        content = response.content.decode('utf-8', errors='ignore')

    soup = BeautifulSoup(content, "html.parser")
    box_items = soup.find_all('li', class_ = 'clearfix')

    ads_dict = {}
    prefix = "https://www.imoti.net"
    for real_estate in box_items:
        try:
            link_to_ad = real_estate.find('a').get('href')
            ad_title = real_estate.find('img').get('alt') if real_estate.find('img').get('alt') else None

            # generate unique ID of the ad based on the title & url
            ad_id = generate_ad_id(
                title=ad_title,
                url=link_to_ad
                )
            
            # add a new element to the dict
            ads_dict[ad_id] = {'ad_title': ad_title, 'link_to_ad': prefix + link_to_ad}
        
        except Exception as e:
            print(f"Error at page: {e}")
    
    return ads_dict

def run_harvester():
    '''Extract main ad info from all pages & insert into db'''
    # 1. Connect to DB
    conn = sqlite3.connect(_DB_PATH)
    cursor = conn.cursor() # MUST define this
    
    page_number = 1
    has_next_page = True

    while has_next_page:
        # Construct URL
        current_page_url = f'https://www.imoti.net/bg/obiavi/r/prodava/sofia/?page={page_number}'
        print(50*"=" + f"Currently at page {page_number}" + 50*"=")
        try:
            single_page_ads = scrape_single_page(current_page_url)
            
            # If the function returns None or an empty list, stop
            if not single_page_ads:
                print(f"Finished: No more ads found at page {page_number}.")
                has_next_page = False
                break
            
            insert_ad(cursor, single_page_ads)
            
            # 3. Commit at the end of each page (The Batch)
            conn.commit()
            print(f"Page {page_number} synced to DB.")
            
            page_number += 1
            
            # Add a small delay so you don't get banned!
            time.sleep(random.uniform(1, 3))

        except Exception as e:
            print(f"Error on page {page_number}: {e}")
            # If one page fails, we might want to try the next one instead of stopping
            page_number += 1 
            continue
    
    conn.close()

# def scrape_all_ads_test(url: str) -> dict:
#     last_page_number = get_last_page_nr(url)
#     real_estate_dict = {}

#     for page_number in range(1):
#         print(f"Beginning scrape of page {page_number}...")
#         url_page = f'https://www.imoti.net/bg/obiavi/r/prodava/sofia/?page={page_number}&sid=gSoWpd'
#         response = requests.get(url_page)
#         # Detect the encoding of the content
#         detected_encoding = chardet.detect(response.content)['encoding']

#         # Decode the content using the detected encoding
#         if detected_encoding:
#             content = response.content.decode(detected_encoding)
#         else:
#             # Fallback to UTF-8 if encoding detection fails
#             content = response.content.decode('utf-8', errors='ignore')

#         soup = BeautifulSoup(content, "html.parser")
#         box_items = soup.find_all('li', class_ = 'clearfix')

#         prefix = "https://www.imoti.net"

#         for real_estate in box_items:
#             try:
#                 link_to_ad = real_estate.find('a').get('href')
#                 ad_title = real_estate.find('img').get('alt') if real_estate.find('img').get('alt') else None

#                 # generate unique ID of the ad based on the title & url
#                 ad_id = generate_ad_id(
#                     title=ad_title,
#                     url=link_to_ad
#                     )
                
#                 # add a new element to the dict
#                 real_estate_dict[ad_id] = {'ad_title': ad_title, 'link_to_ad': prefix + link_to_ad}
#             except Exception as e:
#                 print(f"Error at page {page_number}: {e}")

#     print(50*"=")        
#     print("Finished with scraping of pages. \n Continuing with fetching data from specific ad pages...")
#     print(50*"=")   

#     for id, ad_item in real_estate_dict.items():
#         print(10*"=" + f"Fetching the html for item {id}..." + 10*"=")
#         item_response = requests.get(ad_item['link_to_ad'])
#         item_soup = BeautifulSoup(item_response.text, "html.parser")
        
#         # print(10*"=" + "Parsing the HTML..." + 10*"=")
#         # grab the sidebar with descrtiptions (single element)
#         try:
#             aside_info = item_soup.find("aside", class_="info-sidebar")
#             # print(aside_info)

#             # find simple-table divs and filter by whether they contain td or p
#             simple_tables = aside_info.find_all("div", class_="simple-table") if aside_info else []
#             tables_with_td = [tbl for tbl in simple_tables if tbl.find("td")]
#             tables_with_p = [tbl for tbl in simple_tables if tbl.find("p")]

#             # if you want the first matching table only
#             table_with_td_info = tables_with_td[0] if tables_with_td else None
#             table_with_p_info = tables_with_p[0] if tables_with_p else None

#             # description lives on the specific page
#             description = item_soup.find("div", class_="text")
#             description_text = description.get_text(" ", strip=True) if description else ""
#             ad_item["description"] = description_text
#             # print(description_text)
            
#             for row in table_with_td_info.find_all("tr") if table_with_td_info else []:
#                 cols = row.find_all("td")
#                 if len(cols) >= 2:
#                     key = cols[0].get_text(strip=True)
#                     value = cols[1].get_text(strip=True)
#                     ad_item[key] = value

#             # extract text from <p> tags inside the simple-table
#             p_texts = [p.get_text(" ", strip=True) for p in table_with_p_info.find_all("p")] if table_with_p_info else []
#             p_texts

#             # optional: split "key: value" style lines into a dict
#             # p_data = {}
#             for text in p_texts:
#                 if ":" in text:
#                     key, value = text.split(":", 1)
#                     ad_item[key.strip()] = value.strip()

#                 # print(10*"=" + f"Finished with item {id}" + 10*"=")
#         except Exception as e:
#             print(f"error when processing html of page {id}: {e}")

#     print(real_estate_dict)
#     return real_estate_dict

# url = 'https://www.imoti.net/bg/obiavi/r/prodava/sofia/?page=1&sid=gSoWpd'
# scrape_all_ads_test(url)
