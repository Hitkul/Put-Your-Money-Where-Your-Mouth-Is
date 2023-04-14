import json
from tqdm import tqdm
import time 
import os
import logging
from logging.handlers import TimedRotatingFileHandler

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
    counter = {"last id completed":0,
    "Number of public profiles":0,
    "Number of private profiles":0,
    "Number of active commitments":0,
    "Number of completed commitments":0}

    with open("../data/counter.json",'w') as fp:
        json.dump(counter, fp, indent=4)

logger.info("Reading ../data/private_users.txt")
try:
    with open("../data/private_users.txt",'r') as fp:
        private_users = fp.readlines()

    private_users = [int(i.strip()) for i in private_users]
except:
    logger.info("private_user file not present, creating new")
    private_users = []
    with open("../data/private_users.txt",'w') as fp:
        fp.write("\n".join(private_users))

logger.info("Starting main loop")
while True:
    user_id_to_scrape = counter['last id completed']+1
    logger.info(f"Staring scraping for user id {user_id_to_scrape}")
    


