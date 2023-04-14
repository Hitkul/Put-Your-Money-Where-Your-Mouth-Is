import json
from tqdm import tqdm
import time 
import os
import logging
from logging.handlers import TimedRotatingFileHandler

from utils import *
from user_profile import *


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


logger.info("Reading ../data/counter.json")
try:
    with open("../data/counter.json","r") as fp:
        counter = json.load(fp)
except:
    logger.info("counter file not present, creating new")
    counter = create_counter_file()

logger.info("Reading ../data/private_users.txt")
try:
    with open("../data/private_users.txt",'r') as fp:
        private_users = fp.readlines()

    private_users = [int(i.strip()) for i in private_users]
except:
    logger.info("private_user file not present, creating new")
    private_users = create_private_user_file()

logger.info("Starting main loop")
while True:
    user_id_to_scrape = counter['last id completed']+1
    logger.info(f"Staring scraping for user id {user_id_to_scrape}")

    logger.info(f"Creating directory str for {user_id_to_scrape}")
    create_user_directory_str(user_id_to_scrape)

    logger.info(f"Feathing main user page for id {user_id_to_scrape}")
    fetch_user_profile_page(user_id_to_scrape)




