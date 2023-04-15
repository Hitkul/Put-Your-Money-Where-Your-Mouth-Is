import json
import logging
import os
import time
from logging.handlers import TimedRotatingFileHandler

from tqdm import tqdm
from utils import *

################ Logging Setup ##################
logger = logging.getLogger(f"Stickk data collector - {__name__}")
logger.setLevel(logging.DEBUG)

LOG_FILE  = "../logs/Stickk_data_Collector.log"
c_handler = logging.StreamHandler()
f_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')

c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

logger.addHandler(c_handler)
logger.addHandler(f_handler)
###############################################

def check_commitment_status(soup):
    active_commitments_present = False
    completed_commitments_present = False

    commitments_div = soup.find(id='commitmentListContainer')

    if commitments_div:
        active_commitments_div = commitments_div.find(id='commitmentListContainer_tab_0')
        active_commitments_listview = active_commitments_div.find(id='yw0')
        if 'empty' not in active_commitments_listview['class']:
            active_commitments_present= True
        

        completed_commitments_div = commitments_div.find(id='commitmentListContainer_tab_1')
        completed_commitments_listview = completed_commitments_div.find(id='yw2')
        if 'empty' not in completed_commitments_listview['class']:
            completed_commitments_present= True

    return active_commitments_present, completed_commitments_present

############################----- ACTIVE COMMITMENT CODE -----############################

def scrape_active_commitments_listview(active_commitments_listview):
    active_commitments_page = {}
    items_div = active_commitments_listview.find('div',class_='items')
    commitment_items = items_div.find_all('div',class_=['commitmentRow','othersCommitmentRow'])
    for c_item in commitment_items:
        title_div = c_item.find('div',class_=['container','commitmentInfo','commitmentTitle'])
        title_a_tag = title_div.find('a')
        active_commitments_page['https://www.stickk.com'+title_a_tag['href']] = title_a_tag.text.strip()
    
    return active_commitments_page

def load_active_commitment_page(user_id,page_number):
    url = f'https://www.stickk.com/commitment/{user_id}?ajax=yw0&id_page={page_number}'
    page = load_web_page(url)
    page_soup = make_soup_object(page)
    dump_HTML_file(page,f"../data/users/{user_id}/HTML_dumps/active_page_{page_number}.html")
    return page_soup


def scrape_active_commitments_links(user_id,main_page_soup):
    active_commitments = {}

    commitments_div_soup = main_page_soup.find(id='commitmentListContainer')
    active_commitments_div = commitments_div_soup.find(id='commitmentListContainer_tab_0')
    active_commitments_listview = active_commitments_div.find(id='yw0')
    
    total_page_numbers = number_of_pages(active_commitments_listview)

    logger.info(f"scraping active commitments on page 1, total pages {total_page_numbers}")
    
    active_commitments.update(scrape_active_commitments_listview(active_commitments_listview))

    if total_page_numbers>1:
        for page_number in range(2, total_page_numbers+1):
            logger.info(f"scraping active commitments on page {page_number}, total pages {total_page_numbers}") 
            main_page_soup = load_active_commitment_page(user_id,page_number)

            commitments_div_soup = main_page_soup.find(id='commitmentListContainer')
            active_commitments_div = commitments_div_soup.find(id='commitmentListContainer_tab_0')
            active_commitments_listview = active_commitments_div.find(id='yw0')
            active_commitments.update(scrape_active_commitments_listview(active_commitments_listview))

    return active_commitments


############################----- COMPLETED COMMITMENT CODE -----############################
def scrape_completed_commitments_listview(completed_commitments_listview):
    completed_commitments_page = {}
    items_div = completed_commitments_listview.find('div',class_='items')
    commitment_items = items_div.find_all('div',class_=['commitmentRow','othersCommitmentRow'])
    for c_item in commitment_items:
        title_div = c_item.find('div',class_=['container','commitmentInfo','commitmentTitle'])
        title_a_tag = title_div.find('a')
        completed_commitments_page['https://www.stickk.com'+title_a_tag['href']] = title_a_tag.text.strip()
    
    return completed_commitments_page


def load_completed_commitment_page(user_id,page_number):
    url = f'https://www.stickk.com/commitment/{user_id}?ajax=yw2&id_page={page_number}'
    page = load_web_page(url)
    page_soup = make_soup_object(page)
    dump_HTML_file(page,f"../data/users/{user_id}/HTML_dumps/completed_page_{page_number}.html")
    return page_soup


def scrape_completed_commitments_links(user_id,main_page_soup):
    completed_commitments = {}

    commitments_div_soup = main_page_soup.find(id='commitmentListContainer')
    completed_commitments_div = commitments_div_soup.find(id='commitmentListContainer_tab_1')
    completed_commitments_listview = completed_commitments_div.find(id='yw2')

    total_page_numbers = number_of_pages(completed_commitments_listview)

    logger.info(f"scraping completed commitments on page 1, total pages {total_page_numbers}")

    completed_commitments.update(scrape_completed_commitments_listview(completed_commitments_listview))

    if total_page_numbers>1:
        for page_number in range(2, total_page_numbers+1):
            logger.info(f"scraping completed commitments on page {page_number}, total pages {total_page_numbers}") 
            main_page_soup = load_completed_commitment_page(user_id,page_number)

            commitments_div_soup = main_page_soup.find(id='commitmentListContainer')
            completed_commitments_div = commitments_div_soup.find(id='commitmentListContainer_tab_1')
            completed_commitments_listview = completed_commitments_div.find(id='yw2')
            completed_commitments.update(scrape_completed_commitments_listview(completed_commitments_listview))

    return completed_commitments



if __name__ == "__main__":
    load_active_commitment_page(721182,2)
    # from user_profile import *
    # for i in [234678,1,724678,233320]:
    #     foo = fetch_user_profile_page(i)
    #     print(i,check_commitment_status(foo))