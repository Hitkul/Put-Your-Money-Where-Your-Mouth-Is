import json
import logging
import os
import time
from logging.handlers import TimedRotatingFileHandler

from tqdm import tqdm
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
        active_commitments_listview = active_commitments_div.find(id='yw0')
        if 'empty' not in active_commitments_listview['class']:
            active_commitments_present= True
        

        completed_commitments_div = commitments_div.find(id='commitmentListContainer_tab_1')
        completed_commitments_listview = completed_commitments_div.find(id='yw2')
        if 'empty' not in completed_commitments_listview['class']:
            completed_commitments_present= True

    return active_commitments_present, completed_commitments_present

############################----- ACTIVE COMMITMENT CODE -----############################

def scrape_active_commitments_listview(active_commitments_listview):
    active_commitments_page = {}
    items_div = active_commitments_listview.find('div',class_='items')
    commitment_items = items_div.find_all('div',class_=['commitmentRow','othersCommitmentRow'])
    for c_item in commitment_items:
        title_div = c_item.find('div',class_=['container','commitmentInfo','commitmentTitle'])
        title_a_tag = title_div.find('a')
        active_commitments_page['https://www.stickk.com'+title_a_tag['href']] = title_a_tag.text.strip()
    
    return active_commitments_page

def load_active_commitment_page(user_id,page_number):
    url = f'https://www.stickk.com/commitment/{user_id}?ajax=yw0&id_page={page_number}'
    page = load_web_page(url)
    page_soup = make_soup_object(page)
    dump_HTML_file(page,f"../data/users/{user_id}/HTML_dumps/active_page_{page_number}.html")
    return page_soup


def scrape_active_commitments_links(user_id,main_page_soup):
    active_commitments = {}

    commitments_div_soup = main_page_soup.find(id='commitmentListContainer')
    active_commitments_div = commitments_div_soup.find(id='commitmentListContainer_tab_0')
    active_commitments_listview = active_commitments_div.find(id='yw0')
    
    total_page_numbers = number_of_pages(active_commitments_listview)

    logger.info(f"scraping active commitments on page 1, total pages {total_page_numbers}")
    
    active_commitments.update(scrape_active_commitments_listview(active_commitments_listview))

    if total_page_numbers>1:
        for page_number in range(2, total_page_numbers+1):
            logger.info(f"scraping active commitments on page {page_number}, total pages {total_page_numbers}") 
            main_page_soup = load_active_commitment_page(user_id,page_number)

            commitments_div_soup = main_page_soup.find(id='commitmentListContainer')
            active_commitments_div = commitments_div_soup.find(id='commitmentListContainer_tab_0')
            active_commitments_listview = active_commitments_div.find(id='yw0')
            active_commitments.update(scrape_active_commitments_listview(active_commitments_listview))

    return active_commitments


############################----- COMPLETED COMMITMENT CODE -----############################
def scrape_completed_commitments_listview(completed_commitments_listview):
    completed_commitments_page = {}
    items_div = completed_commitments_listview.find('div',class_='items')
    commitment_items = items_div.find_all('div',class_=['commitmentRow','othersCommitmentRow'])
    for c_item in commitment_items:
        title_div = c_item.find('div',class_=['container','commitmentInfo','commitmentTitle'])
        title_a_tag = title_div.find('a')
        completed_commitments_page['https://www.stickk.com'+title_a_tag['href']] = title_a_tag.text.strip()
    
    return completed_commitments_page


def load_completed_commitment_page(user_id,page_number):
    url = f'https://www.stickk.com/commitment/{user_id}?ajax=yw2&id_page={page_number}'
    page = load_web_page(url)
    page_soup = make_soup_object(page)
    dump_HTML_file(page,f"../data/users/{user_id}/HTML_dumps/completed_page_{page_number}.html")
    return page_soup


def scrape_completed_commitments_links(user_id,main_page_soup):
    completed_commitments = {}

    commitments_div_soup = main_page_soup.find(id='commitmentListContainer')
    completed_commitments_div = commitments_div_soup.find(id='commitmentListContainer_tab_1')
    completed_commitments_listview = completed_commitments_div.find(id='yw2')

    total_page_numbers = number_of_pages(completed_commitments_listview)

    logger.info(f"scraping completed commitments on page 1, total pages {total_page_numbers}")

    completed_commitments.update(scrape_completed_commitments_listview(completed_commitments_listview))

    if total_page_numbers>1:
        for page_number in range(2, total_page_numbers+1):
            logger.info(f"scraping completed commitments on page {page_number}, total pages {total_page_numbers}") 
            main_page_soup = load_completed_commitment_page(user_id,page_number)

            commitments_div_soup = main_page_soup.find(id='commitmentListContainer')
            completed_commitments_div = commitments_div_soup.find(id='commitmentListContainer_tab_1')
            completed_commitments_listview = completed_commitments_div.find(id='yw2')
            completed_commitments.update(scrape_completed_commitments_listview(completed_commitments_listview))

    return completed_commitments


def scrape_commitment_details(link_to_commitment,user_id):
    details = {}
    commitment_page = load_web_page(link_to_commitment)
    commitment_page_soup = make_soup_object(commitment_page)

    logger.info("Basic details extraction")
    details['title'] = commitment_page_soup.find('span',id = 'commitmentTitle').text.strip()
    description_tag = commitment_page_soup.find('div',id = 'commitmentSummaryICommitToText')
    if not description_tag:
        description_tag = commitment_page_soup.find('div',id = 'iCommitToTitleText')
    details['description'] = description_tag.text.strip()

    logger.info("Scraping Details dialog")
    details_dialog_div = commitment_page_soup.find('div',id='commitmentDetailsDialogContent')
    details_dialog_content_div = details_dialog_div.find('div',class_=['stickkContainer02','content'])
    
    for c_item in details_dialog_content_div.find_all('div'):
        label_text = c_item.find('span',class_='label')
        label_value = c_item.find('span',class_='cell2')
        if label_text and label_value:
            details[label_text.text[:-1].strip()] = label_value.text.strip()

    logger.info("Scraping commitment results")
    commitment_results_div = commitment_page_soup.find('div',class_ = 'commitmentDetailsDetailsSuccessContainer')
    if commitment_results_div:
        details['Successful Periods'] = commitment_results_div.find('div',class_='successfulPeriods').text.split(":")[-1].strip()
        details['Unsuccessful Periods'] = commitment_results_div.find('div',class_='failedPeriods').text.split(":")[-1].strip()

    right_containers = commitment_page_soup.find('div',id='membersCommitmentsRightContainer')

    logger.info("Scraping Stakes info")
    details['stakes_details']={}
    stakes_div = right_containers.find('div',class_='financialColumn stickkContainer05 p-2')
    
    if stakes_div:
        details['stakes_details']['recipient'] = stakes_div.find('div',class_='stakeRecipient mt-2').text.strip()

        stakes_details_div = stakes_div.find('div',class_='financialDetails mt-2') 
        for item_div in stakes_details_div.find_all('div'):
            label_text = item_div.find('span',class_='label')
            label_value = item_div.find('span',class_='value')
            if label_text and label_value:
                details['stakes_details'][label_text.text[:-1].strip()] = label_value.text.strip()
    else:
        details['stakes_details']=None

    logger.info("Scraping referee information")
    details['referee']=[]
    referee_div = right_containers.find('div',class_='stickkContainer01 supporterColumn stickkContainer05 mt-5 p-2') 
    referee_list = referee_div.find('ul',id='refereeList')
    for li_items in referee_list.find_all('li'):
        a_tag = li_items.find('a',class_='username')
        details['referee'].append({"username":a_tag['title'],"profile_url":a_tag['href']})
    
    logger.info("Scraping supported information")
    details['supporters']=[]
    supporters_div = right_containers.find('div',class_='supporterColumn stickkContainer05 mt-2 p-2')
    supporters_list = supporters_div.find('ul',id='supporterList')
    if supporters_list:    
        for li_items in supporters_list.find_all('li'):
            a_tag = li_items.find('a',class_='username')
            details['supporters'].append({"username":a_tag['title'],"profile_url":a_tag['href']})
    else:
        details['supporters']=None


    dump_HTML_file(commitment_page,f"../data/users/{user_id}/HTML_dumps/commitment_id_{details['Contract ID']}_main.html")
    return details,commitment_page_soup

def scrape_posts(commitment_page_soup):
    posts = []
    wall_post_list_view = commitment_page_soup.find('div',id='wallPostsListView')
    items_div = wall_post_list_view.find('div',class_='items')

    if items_div.find('span',class_='empty'):
        logger.info("No post available in this commitment")
        return posts
    
    for wall_post in items_div.find_all('div',class_='wallItem'):
        post_dict = {}
        post_dict['author'] = wall_post.find('div',class_='username').text.strip()
        post_dict['author_link'] = wall_post.find('a',class_='avatarContainer avatarContainerTiny')['href']
        post_dict['time'] = wall_post.find('div',class_='postTime').text.strip()
        post_dict['text'] = wall_post.find('td',class_='text').text.strip()
        
        img_li = wall_post.find('li',class_='albumUploadContainer')
        if img_li:
            post_dict['img src'] = img_li.find('img')['src']

        posts.append(post_dict)

    return posts

def scrape_photos(commitment_page_soup):
    photos = []
    wall_photos_list_view = commitment_page_soup.find('div',id='albumContainer')
    items_ul = wall_photos_list_view.find('ul',class_='items')

    if items_ul.find('span',class_='empty'):
        logger.info("No photos available in this commitment")
        return photos

    for ph_tags in items_ul.find_all('li',class_='albumUploadContainer'):
        photo_dict = {}
        photo_dict['date'] = ph_tags.find('div',class_='date').text.strip()
        photo_dict['title'] = ph_tags.find('a')['title'].strip()
        photo_dict['src'] = ph_tags.find('img')['src']

        photos.append(photo_dict)

    return photos


def scrape_reports_list_view(report_list_view):
    reports_page = []
    items_div = report_list_view.find('div',class_='items')
    period_items = items_div.find_all('div',class_='period')

    for p_item in period_items:
        p_report={}
        data_div = p_item.find_all('div',recursive=False)[0]
        value_divs = data_div.find_all('div',recursive=False)
        for vd in value_divs:
            p_report[vd.find('label').text.strip()] = vd.find('div',class_='floatRight').text.strip()
        
        reports_page.append(p_report)

    return reports_page
        

# def load_active_commitment_page(user_id,page_number):
#     url = f'https://www.stickk.com/commitment/{user_id}?ajax=yw0&id_page={page_number}'
#     page = load_web_page(url)
#     page_soup = make_soup_object(page)
#     dump_HTML_file(page,f"../data/users/{user_id}/HTML_dumps/active_page_{page_number}.html")
#     return page_soup


# def scrape_active_commitments_links(user_id,main_page_soup):


#             main_page_soup = load_active_commitment_page(user_id,page_number)

#             commitments_div_soup = main_page_soup.find(id='commitmentListContainer')
#             active_commitments_div = commitments_div_soup.find(id='commitmentListContainer_tab_0')
#             active_commitments_listview = active_commitments_div.find(id='yw0')
#             active_commitments.update(scrape_active_commitments_listview(active_commitments_listview))

def load_report_page(link_to_commitment,page_number):
    commitment_id = int(link_to_commitment.split("/")[-1].strip())

    url = f'https://www.stickk.com/commitment/periods/{commitment_id}?ID_page={page_number}&ajax=reportingPeriodsListView'
    page = load_web_page(url)

    return page


def scrape_reports(commitment_page_soup,link_to_commitment):
    reports = []
    report_list_view = commitment_page_soup.find('div',id='reportingPeriodsListView')
    total_page_numbers = number_of_pages(report_list_view)
    logger.info(f"scraping reports on page 1, total pages {total_page_numbers}")
    reports.extend(scrape_reports_list_view(report_list_view))

    if total_page_numbers>1:
        for page_number in range(2, total_page_numbers+1):
            logger.info(f"scraping reports on page {page_number}, total pages {total_page_numbers}") 
            page = load_report_page(link_to_commitment,page_number)
            print(page.content)
            break
    
    
    return reports
    

def scrape_commitment_page(link_to_commitment, is_active,user_id):
    details,commitment_page_soup = scrape_commitment_details(link_to_commitment,user_id)

    reports = scrape_reports(commitment_page_soup,link_to_commitment)

    return reports

    if is_active:
        return details

    posts = scrape_posts(commitment_page_soup)
    photos = scrape_photos(commitment_page_soup)
    
    return details,posts,photos



if __name__ == "__main__":
    from pprint import pprint
    reports = scrape_commitment_page('https://www.stickk.com/commitment/details/765439', False,429276)
    # reports = scrape_commitment_page('https://www.stickk.com/commitment/details/646352', False,233320)
    # reports = scrape_commitment_page('https://www.stickk.com/commitment/details/964364', False,233320)
    
    # pprint(reports)