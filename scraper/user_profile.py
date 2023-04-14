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



if __name__ == "__main__":
    foo = fetch_user_profile_page(1)
    print(is_user_present(foo))