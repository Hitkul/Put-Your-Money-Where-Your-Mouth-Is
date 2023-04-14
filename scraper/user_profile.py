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
    print(main_page.content)
    dump_HTML_file(main_page,f"../data/users/{user_id}/HTML_dumps/main_page.html")
    return main_page_soup



if __name__ == "__main__":
    fetch_user_profile_page(1)