import json
from tqdm import tqdm
import time 
import os
import logging
from logging.handlers import TimedRotatingFileHandler
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


def fetch_user_profile_page(user_id):
    url = f"https://www.stickk.com/commitment/{user_id}"
    main_page = load_web_page(url)
    main_page_soup = make_soup_object(main_page)
    dump_HTML_file(main_page,f"../data/users/{user_id}/HTML_dumps/main_page.html")
    return main_page_soup

def is_user_present(soup):
    check_phrase = "User not found"

    elements = soup.find("div", class_="notice error")

    if elements and (check_phrase in elements.text):
        return False
    
    return True


def is_user_private(soup):
    private_phrase_1 = "You need to be logged in to view this profile"
    private_phrase_2 = "In order to view this profile, you must request to add the user as a friend and they must approve"
    
    elements = soup.find("div", class_="notice error")
    
    if elements and (private_phrase_1 in elements.text or private_phrase_2 in elements.text):
        return True
    
    return False

def scrape_user_info(soup):
    user_info = {}
    profile_side_container = soup.find(id='othersProfileSideContainer')
    
    profile_image_div = profile_side_container.find(id='othersProfileWidgetImage')
    user_info["img_link"] = profile_image_div.find('img')['src'].strip()

    profile_username_div = profile_side_container.find(id='othersProfileUsername')
    user_info["username"] = profile_username_div.text.strip()

    profile_other_info_div = profile_side_container.find(id='othersProfileInfoContainer')

    user_info["location"] = profile_other_info_div.find(id='othersProfileLocation').text.strip()
    user_info["joined_date"] = profile_other_info_div.find(id='othersProfileJoinedDate').text.strip()
    user_info["intrest"] = profile_other_info_div.find(id='topProfileInterests').text.strip()
    user_info["message"] = profile_other_info_div.find(id='topProfileMessage').text.strip()

    for k,v in user_info.items():
        if v == "":
            user_info[k]=None

    return user_info


def check_commitment_status(soup):
    active_commitments_present = False
    completed_commitments_present = False

    commitments_div = soup.find(id='commitmentListContainer')

    if commitments_div:
        active_commitments_div = commitments_div.find(id='commitmentListContainer_tab_0')
        completed_commitments_div = commitments_div.find(id='commitmentListContainer_tab_1')

        active_commitments_listview = active_commitments_div.find(id='yw0')
        if 'empty' not in active_commitments_listview['class']:
            active_commitments_present= True

        completed_commitments_listview = completed_commitments_div.find(id='yw2')
        if 'empty' not in completed_commitments_listview['class']:
            completed_commitments_present= True

    return active_commitments_present, completed_commitments_present


if __name__ == "__main__":
    for i in [234678,1,724678,233320]:
        foo = fetch_user_profile_page(i)
        print(i,check_commitment_status(foo))