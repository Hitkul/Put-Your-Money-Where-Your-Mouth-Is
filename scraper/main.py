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
    main_page_soup = fetch_user_profile_page(user_id_to_scrape)

    logger.info(f"Checking if user {user_id_to_scrape} is present")
    is_present = is_user_present(main_page_soup)

    if not is_present:
        logger.info(f"{user_id_to_scrape} not found, seems like this is the end, dumping files and exiting")

        logger.info(f"deleting directory ../data/users/{user_id_to_scrape}")
        os.rmdir(f"../data/users/{user_id_to_scrape}")
        dump_counter_file(counter)
        dump_private_user_file(private_users)
        
        break

    logger.info(f"{user_id_to_scrape} is present")

    logger.info(f"Checking if user {user_id_to_scrape} is private")
    is_private = is_user_private(main_page_soup)

    if is_private:
        logger.info(f"{user_id_to_scrape} is private, adding it to the list, and dumping file to disk")
        
        private_users.append(user_id_to_scrape)
        dump_private_user_file(private_users)

        counter["Number of private profiles"]+=1
        counter["last id completed"]+=1
        dump_counter_file(counter)

        continue

    logger.info(f"{user_id_to_scrape} is public")
    counter["Number of public profiles"]+=1

    
    logger.info(f"Scraping profile info for {user_id_to_scrape}")
    user_info = scrape_user_info(main_page_soup)

    logger.info(f"user info extracted,dumping to file now")
    dump_json(user_info,f'../data/users/{user_id_to_scrape}/userinfo.json')



    #TODO: Scraper Active commitment links
    #TODO: Scraper Completed commitments links
    #TODO: Scrape Active commitments details
    #TODO: Scrape Completed commitments details + Reports + Posts + photos
    




