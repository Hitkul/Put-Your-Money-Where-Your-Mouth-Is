import json
import logging
import os
import time
from logging.handlers import TimedRotatingFileHandler

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from cred import *

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

last_request_time = 0

def create_counter_file():
    counter = {"last id completed":0,
    "Number of user not found profiles":0,
    "Number of public profiles":0,
    "Number of private profiles":0,
    "Number of active commitments":0,
    "Number of completed commitments":0}

    with open("../data/counter.json",'w') as fp:
        json.dump(counter, fp, indent=4)

    return counter

def dump_counter_file(counter):
    with open("../data/counter.json",'w') as fp:
        json.dump(counter, fp, indent=4)

def create_private_user_file():
    private_users = []
    with open("../data/private_users.txt",'w') as fp:
        fp.write("\n".join(private_users))

    return private_users

def dump_private_user_file(private_users):
    with open("../data/private_users.txt",'w') as fp:
        fp.write("\n".join(private_users))

def create_user_not_found_file():
    users_not_found = []
    with open("../data/users_not_found.txt",'w') as fp:
        fp.write("\n".join(users_not_found))

    return users_not_found

def dump_user_not_found_file(users_not_found):
    with open("../data/users_not_found.txt",'w') as fp:
        fp.write("\n".join(users_not_found))

def create_user_directory_str(user_id):
    if os.path.exists(f"../data/users/{user_id}"):
        logger.info("Directory already exists")
        return
    
    os.mkdir(f"../data/users/{user_id}")
    os.mkdir(f"../data/users/{user_id}/completed_commitments")
    os.mkdir(f"../data/users/{user_id}/active_commitments")
    os.mkdir(f"../data/users/{user_id}/HTML_dumps")


def load_web_page(url,s=None):
    global last_request_time

    logger.info("checking if last request was more then a second ago or not")
    if (time.time() - last_request_time) < 1.0:
        logger.info("sleeping for a second to reduce request load")
        time.sleep(1.0-(time.time() - last_request_time))

    ua = UserAgent()
    header = {'User-Agent':str(ua.chrome)}

    logger.info(f"loading page {url}")
    last_request_time = time.time()
    if s:
        page = s.get(url,headers=header)
    else:
        page = requests.get(url, headers=header)
    
    logger.debug(f"done loading page, Status code {page.status_code}")
    assert page.status_code==200
    return page

def login():
    logger.info("Logging into stickk")
    ua = UserAgent()
    header = {'User-Agent':str(ua.chrome)}
    s = requests.Session()
    login_payload = {
        "LoginForm[username]":username,
        "LoginForm[password]":password,
        "LoginForm[rememberMe]":0
    }

    login_url = "https://www.stickk.com/login"

    post_request = s.post(login_url, data=login_payload, headers=header)
    logger.debug(f"Login request status code {post_request.status_code}")
    return s


def make_soup_object(page):
    soup = BeautifulSoup(page.content, "html.parser")
    logger.info("Converted page to soup object")
    return soup

def dump_HTML_file(page,path):
    logger.info(f"Dumping as HTML at {path}")
    with open(path, 'wb+') as f:
        f.write(page.content)

def dump_json(content, path):
    logger.info(f"Dumping as Json at {path}")
    with open(path,'w') as fp:
        json.dump(content,fp,indent=4)

def number_of_pages(list_view):
    pager_div = list_view.find('div',class_='pager')

    if pager_div:
        last_element = pager_div.find('li',class_='last')
        href_text = last_element.find('a')['href']
        return int(href_text.split("page=")[-1].strip())

    return 1



if __name__=="__main__":
    # create_user_directory_str(732608)
    s = login()
    try_url = f'https://www.stickk.com/commitment/periods/765439?ID_page=2&ajax=reportingPeriodsListView'
    page = load_web_page(try_url,s)
    print(page.content)