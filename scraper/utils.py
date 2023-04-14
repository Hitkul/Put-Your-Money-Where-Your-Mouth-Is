import json
import os
import requests
import logging
from logging.handlers import TimedRotatingFileHandler
from bs4 import BeautifulSoup


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


def create_counter_file():
    counter = {"last id completed":0,
    "Number of public profiles":0,
    "Number of private profiles":0,
    "Number of active commitments":0,
    "Number of completed commitments":0}

    with open("../data/counter.json",'w') as fp:
        json.dump(counter, fp, indent=4)

    return counter

def create_private_user_file():
    private_users = []
    with open("../data/private_users.txt",'w') as fp:
        fp.write("\n".join(private_users))

    return private_users

def create_user_directory_str(user_id):
    if os.path.exists(f"../data/users/{user_id}"):
        logger.info("Directory already exists")
        return
    
    os.mkdir(f"../data/users/{user_id}")
    os.mkdir(f"../data/users/{user_id}/completed_commitments")
    os.mkdir(f"../data/users/{user_id}/active_commitments")
    os.mkdir(f"../data/users/{user_id}/HTML_dumps")


def load_web_page(url):
    logger.info(f"loading page {url}")
    page = requests.get(url)
    logger.info(f"done loading page, Status code {page.status_code}")
    assert page.status_code==200
    return page

def make_soup_object(page):
    soup = BeautifulSoup(page.content, "html.parser")
    logger.info("Converted page to soup object")
    return soup

def dump_HTML_file(page,path):
    logger.info(f"Dumping as HTML at {path}")
    with open(path, 'wb+') as f:
        f.write(page.content)


if __name__=="__main__":
    create_user_directory_str(2)