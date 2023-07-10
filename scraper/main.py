import json
import logging
import os
import shutil
import time
from logging.handlers import TimedRotatingFileHandler

from commitment import *
from tqdm import tqdm
from user_profile import *
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

logger.info("Reading ../data/users_not_found.txt")
try:
    with open("../data/users_not_found.txt",'r') as fp:
        users_not_found = fp.readlines()

    users_not_found = [int(i.strip()) for i in users_not_found]
except:
    logger.info("users_not_found file not present, creating new")
    users_not_found = create_user_not_found_file()

consecutive_not_found_counter = 0
# for user_id_to_scrape in [429427,1,233320,725101,721182,429276,743320]:
logger.info("Starting main loop")
while True:
    counter['last id completed'] += 1
    user_id_to_scrape = counter['last id completed']
    logger.info(f"Staring scraping for user id {user_id_to_scrape}")

    logger.info(f"Creating directory str for {user_id_to_scrape}")
    create_user_directory_str(user_id_to_scrape)

    HTTP_500_error_users = [431605,432721]
    if user_id_to_scrape in HTTP_500_error_users:
        logger.info(f"{user_id_to_scrape} HTTP 500 error")

        logger.info(f"deleting directory ../data/users1/{user_id_to_scrape}")
        shutil.rmtree(f"../data/users1/{user_id_to_scrape}")

        counter["Number of user not found profiles"]+=1
        users_not_found.append(str(user_id_to_scrape))
        dump_counter_file(counter)
        dump_user_not_found_file(users_not_found)

        continue

    logger.info(f"Feathing main user page for id {user_id_to_scrape}")
    main_page_soup = fetch_user_profile_page(user_id_to_scrape)

    logger.info(f"Checking if user {user_id_to_scrape} is present")
    is_present = is_user_present(main_page_soup)

    if not is_present:
        logger.info(f"{user_id_to_scrape} not found")

        logger.info(f"deleting directory ../data/users1/{user_id_to_scrape}")
        shutil.rmtree(f"../data/users1/{user_id_to_scrape}")
        
        counter["Number of user not found profiles"]+=1
        users_not_found.append(str(user_id_to_scrape))
        
        dump_counter_file(counter)
        dump_user_not_found_file(users_not_found)
        consecutive_not_found_counter+=1

        if consecutive_not_found_counter>2000:
            logger.info("more then 2000 consecutive users missing.... probably end of the road...exiting for now")
            break
        else:
            continue

    logger.info(f"{user_id_to_scrape} is present")
    consecutive_not_found_counter=0

    logger.info(f"Checking if user {user_id_to_scrape} is private")
    is_private = is_user_private(main_page_soup)

    if is_private:
        logger.info(f"{user_id_to_scrape} is private, adding it to the list, and dumping file to disk")
        
        private_users.append(str(user_id_to_scrape))
        dump_private_user_file(private_users)

        counter["Number of private profiles"]+=1
        dump_counter_file(counter)

        continue

    logger.info(f"{user_id_to_scrape} is public")
    counter["Number of public profiles"]+=1

    
    logger.info(f"Scraping profile info for {user_id_to_scrape}")
    user_info = scrape_user_info(main_page_soup)

    logger.info(f"user info extracted,dumping to file now")
    dump_json(user_info,f'../data/users1/{user_id_to_scrape}/userinfo.json')

    logger.info(f"Checking commitment status for {user_id_to_scrape}")

    active_commitments_present, completed_commitments_present = check_commitment_status(main_page_soup)
    logger.debug(f"Commitment status for {user_id_to_scrape} ACTIVE {active_commitments_present}, COMPLETED {completed_commitments_present}")

    
    if active_commitments_present:
        logger.info(f"Collecting links of active commitments")
        active_commitments = scrape_active_commitments_links(user_id_to_scrape,main_page_soup)
        
        logger.info(f"{len(active_commitments)} found, updating the counter and dumping to file")
        counter['Number of active commitments']+=len(active_commitments)
        dump_json(active_commitments, f"../data/users1/{user_id_to_scrape}/active.json")
    else:
        logger.info(f"No active commitmtents for {user_id_to_scrape}")

    
    if completed_commitments_present:
        logger.info(f"Collecting links of completed commitments")
        completed_commitments = scrape_completed_commitments_links(user_id_to_scrape,main_page_soup)

        logger.info(f"{len(completed_commitments)} found, updating the counter and dumping to file")
        counter['Number of completed commitments']+=len(completed_commitments)
        dump_json(completed_commitments, f"../data/users1/{user_id_to_scrape}/completed.json")
    else:
        logger.info(f"No completed commitments for {user_id_to_scrape}")

    
    if active_commitments_present:
        logger.info(f"Scraping details of active commitments for {user_id_to_scrape}")

        for k,v in active_commitments.items():
            logger.info(f"Scraping details of {k} | {v}")
            commitment_details = scrape_commitment_page(k,True,user_id_to_scrape)

            dump_json(commitment_details, f"../data/users1/{user_id_to_scrape}/active_commitments/{commitment_details['Contract ID']}.json")

    
    if completed_commitments_present:
        logger.info(f"Scraping details of completed commitments for {user_id_to_scrape}")

        s = login()
        for k,v in completed_commitments.items():
            logger.info(f"Scraping details of {k} | {v}")
            commitment_details, commitment_posts, commitment_photos, commitment_reports = scrape_commitment_page(k,False,user_id_to_scrape,s)

            logger.info(f"creating directory for commitment {commitment_details['Contract ID']}")
            if not os.path.exists(f"../data/users1/{user_id_to_scrape}/completed_commitments/{commitment_details['Contract ID']}"):
                os.mkdir(f"../data/users1/{user_id_to_scrape}/completed_commitments/{commitment_details['Contract ID']}")

            dump_json(commitment_details, f"../data/users1/{user_id_to_scrape}/completed_commitments/{commitment_details['Contract ID']}/details.json")
            dump_json(commitment_posts, f"../data/users1/{user_id_to_scrape}/completed_commitments/{commitment_details['Contract ID']}/posts.json")
            dump_json(commitment_photos, f"../data/users1/{user_id_to_scrape}/completed_commitments/{commitment_details['Contract ID']}/photos.json")
            dump_json(commitment_reports, f"../data/users1/{user_id_to_scrape}/completed_commitments/{commitment_details['Contract ID']}/reports.json")
        s.close()
    
    dump_counter_file(counter)
    
    
    




