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
    from user_profile import *
    for i in [234678,1,724678,233320]:
        foo = fetch_user_profile_page(i)
        print(i,check_commitment_status(foo))