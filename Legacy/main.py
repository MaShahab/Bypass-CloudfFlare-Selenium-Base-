import warnings

warnings.filterwarnings("ignore")

import csv
import sys
import requests
from bs4 import BeautifulSoup
from time import sleep
import datetime
import re
import json
from urllib.parse import urlparse
import urllib.request

warnings.filterwarnings("ignore", category=DeprecationWarning)

import itertools

from selenium import webdriver
# from selenium.webdriver.edge.options import Options
from selenium.webdriver.chrome.service import Service

from msedge.selenium_tools import EdgeOptions
from msedge.selenium_tools import Edge
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium_stealth import stealth

from selenium.webdriver import ActionChains

from seleniumbase import SB
from seleniumbase import Driver

import undetected_chromedriver as uc

import pandas as pd
import pprint

from datetime import datetime

import time
import asyncio
import random
import ctypes


# Colors
Purple = '\033[95m'
Blue = '\033[94m'
Cyan = '\033[96m'
Green = '\033[92m'
Yellow = '\033[93m'
Red = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
CRED = '\033[91m'


class Person:
    def __init__(self, first_name, middle_name, last_name, nick_name, birth_date, death_date, birth_year, death_year, age, funeral_home, obituary_text, image):
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.nick_name = nick_name
        self.birth_date = birth_date
        self.death_date = death_date
        self.birth_year = birth_year
        self.death_year = death_year
        self.age = age
        self.funeral_home = funeral_home
        self.obituary_text = obituary_text
        self.image = image


def storePerson(person, dst):
    CRED = '\033[91m'

    try:
        person_specification = [person.first_name, person.middle_name, person.last_name, person.nick_name,
                                 person.birth_date, person.death_date, person.birth_year, person.death_year, person.age , person.funeral_home , person.obituary_text, person.image]

        with open(dst, 'a', newline='', encoding="utf-8-sig") as products_file:
            writer = csv.writer(products_file)
            writer.writerow(person_specification)
        print(Blue + "The person with last_name " + '(' + str(person.last_name) +')' + " successfully scraped and stored")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno), person.last_name)

def storeExceptions(exception_log, failure_log):
    try:
        with open(r'Exceptions.csv', 'a', newline='', encoding="utf-8-sig") as e_file:
            writer = csv.writer(e_file)
            writer.writerow([exception_log, failure_log, str(datetime.now())])
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(Red + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))


def removeDatesFromText(text,removeAllNums=False):

    # Removes times in the format "00:00"
    pattern = r'\d{2}:\d{2}'
    text = re.sub(pattern, '', text)

    #Try to remove dates from name
    day_names_pattern = r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b'
    text = re.sub(day_names_pattern, "", text)

    #Date strings
    date_str1 = r'\d{1,2}(?:st|nd|rd|th)?(?: day of)?\s*(?:Jan(?:uary)?\.?|Feb(?:ruary)?\.?|Mar(?:ch)?\.?|Apr(?:il)?\.?|May|Jun(?:e)?\.?|Jul(?:y)?\.?|Aug(?:ust)?\.?|Sep(?:t(?:\.|ember)?)?|Oct(?:ober)?\.?|Nov(?:ember)?\.?|Dec(?:ember)?\.?),?(?:\s*\d{4})'
    date_str2 = r'(?:Jan(?:uary)?\.?|Feb(?:ruary)?\.?|Mar(?:ch)?\.?|Apr(?:il)?\.?|May|Jun(?:e)?\.?|Jul(?:y)?\.?|Aug(?:ust)?\.?|Sep(?:t(?:\.|ember)?)?|Oct(?:ober)?\.?|Nov(?:ember)?\.?|Dec(?:ember)?\.?)\s+\d{1,2}(?:st|nd|rd|th)?,?(?:\s*\d{4})'
    date_str3 = r'\d{1,2}\/\d{1,2}\/\d{2}(?:\d{2})?'
    date_str4 = r'(?:0?[1-9]|1[0-2])-(?:0?[1-9]|[1-2][0-9]|3[0-1])-(?:\d{2}(?:\d{2})?)'
    date_str5 = r'(\d{4}\s*[-–-]\s*\d{4})'
    date_str6 = r'(\b\d{2,4}\b)'
    if removeAllNums:
        date_pattern = f'({date_str1}|{date_str2}|{date_str3}|{date_str4}|{date_str5}|{date_str6})'
    else:
        date_pattern = f'({date_str1}|{date_str2}|{date_str3}|{date_str4}|{date_str5})'
        
    text = re.sub(date_pattern, "", text)
    return text


def preprocessText(text):
    '''Remove HTML tags, Reduce whitespace characters'''
    if text is None:
        return None
    text = text.replace('<br>', ' ')
    text = text.splitlines()
    text = " ".join(text).strip()
    text = re.sub(r'\s+', ' ', text)
    return text


def split_name(name, format='default'):
    # List of common name prefixes and suffixes for reference
    if name is None:
        return None, None, None, None, None, None
    
    #Remove html tags + clean up text
    name = preprocessText(name.strip())
    
 
    #Remove common FH strings:
    obit_strs = ['Obituary','Funeral','Services','Memorial','Service']
    for fh_str in obit_strs:
        name = name.replace(fh_str,'').replace(fh_str.lower(),'').strip()
    
    name = removeDatesFromText(name,removeAllNums=True)

    prefixes = set([
                    "dr.", "dr", "mr.", "mr", "mrs.", "mrs", "ms.", "ms", "sir", "prof.", "prof", "rev.", "rev",
                    "1sg", "a1c", "amn", "cmsaf", "cmssf", "cmsgt", "cpl", "cpo", "csm", "cpl", "fccm", "gysgt", "lcpl", "mcpo",
                    "mcpocg", "mcpo", "mgysgt", "msg", "msgt", "pfc", "po1", "po2", "po3", "pv2", "sa", "scpo", "sfc", "sgm", "sgt",
                    "sma", "smsgt", "sn", "spc", "ssg", "ssgt", "sgt", "sgtmaj", "sgtmajmc", "spc1", "spc2", "spc3", "spc4",
                    "sra", "tsgt", "sister", "brother", "father", "mother", "fr.", "fr"
                ])
    suffixes = set(["jr.", "sr.", "i", "ii", "iii", "iv", "v", "ph.d.", "md", "esq.", "jr", "sr", "esq", "ba", "ph.d", "phd", "phd.","m.d","m.d.","md."])
    
    if format == 'comma':
            pass
            #if ',' in name:
            #   parts = name.split(',')
            #   name = parts[1].strip() + ' ' + parts[0].strip()
    else:
        name = name.replace(',', '')  # Remove commas from the name

    #Further preprocess
        
    # Extract nickname and remove it from the name
    nickname = None
    match = re.search(r'[\("\'](.*?)[\)"\']', name)
    if match:
        nickname = match.group(1)
        name = re.sub(r'[\("\'].*?[\)"\']', '', name).strip()
    
        if len(nickname) >= 50:
            nickname = None
    #Remove trailing and leading punctuation
    pattern = re.compile(r'^[\W_\d]+|[\W_]+$')
    name = pattern.sub('', name).strip()

    parts = re.split(r'(?<! -) (?![\-])', name)
    parts = [p.lower() for p in parts]
    prefix = None
    first_name = None
    middle_name = None
    last_name = None
    suffix = None

    # Check for prefix (using lower for case insensitivity)
    if parts and parts[0] in prefixes:
        prefix = name.split()[0]  # Take original cased prefix from the name
        parts.pop(0)

    # Check for suffix (using lower for case insensitivity)
    if parts and parts[-1] in suffixes:
        suffix = name.split()[-1]  # Take original cased suffix from the name
        suffix = suffix[0].upper() + suffix[1:].lower()
        parts.pop()

    for i, part in enumerate(parts):
        if '-' in part:
            # Split by dash and capitalize each word
            dashed_names = [name.strip().capitalize() for name in part.split('-')]
            parts[i] = '-'.join(dashed_names)

    # Assign names based on the remaining parts
    if parts:
        first_name = parts[0]
        if first_name == first_name.lower():
            first_name = first_name.capitalize().strip()

    if len(parts) > 1:
        last_name = parts[-1]
        pattern = re.compile(r'^[\W_\d]+|[\W_]+$')
        last_name = pattern.sub('', last_name).strip()
        if last_name == last_name.lower():
            last_name = last_name.capitalize().strip()

    if len(parts) > 2:
        middle_name = " ".join([word.capitalize() if word == word.lower() else word for word in parts[1:-1]])
        middle_name = middle_name.strip()

    return prefix, first_name, middle_name, nickname, last_name, suffix


def imageNameConverter(url):
    CRED = '\033[91m'
    try:
        # postfix = url[url.rindex('.') + 1:]
        postfix = 'jpg'
        postfix = postfix.strip()
        currentTime = datetime.datetime.now().strftime("%m-%d %H:%M:%S:%f")
        currentTime_str = re.sub(r':', '', currentTime)
        currentTime_str = re.sub(r'-', '', currentTime_str)
        currentTime_str = re.sub(r' ', '', currentTime_str)
        image_name = 'Obituary-' + currentTime_str + '.' + postfix
        return image_name
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno), url)


def verify_success(sb):
    sb.assert_element('img[alt="Logo Assembly"]', timeout=8)
    sb.sleep(4)


def fetchAllObituaries(page_no):
    try:
        dynamic_page_no = page_no
        while True:
            url = f'https://www.legacy.com/api/_frontend/search?endDate=2024-08-03&firstName=&keyword=&lastName=&limit=100&noticeType=all&offset={dynamic_page_no}&session_id=&startDate=1998-01-01'
            # url = f'https://www.legacy.com/api/_frontend/search?endDate=2024-08-03&firstName=&keyword=&lastName=&limit=1000&noticeType=all&offset=1000&session_id=&startDate=1998-01-01'
            fetchPageObituaries(url)
            print(dynamic_page_no)
            dynamic_page_no = dynamic_page_no + 50

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno), url)


def fetchPageObituaries(soup):
    CRED = '\033[91m'
    CBLUE = '\33[94m'

    global final_first_name, final_middle_name, final_last_name, final_nick_name, final_birth_date, final_death_date, final_birth_year, final_death_year, final_age, final_funeral_home, final_obituary_text, final_image

    try:
        print(type(soup))
        dict_from_json = json.loads(soup.find("body").text)

        obituaries = dict_from_json['obituaries']
        
        for obituary in obituaries:
            
            name = obituary['name']

            final_first_name = name['firstName']
            final_last_name = name['lastName']
            final_middle_name = name['middleName']

            if name['nickName'] == "null" or  name['nickName'] == None:
                final_nick_name = None
            else:
                final_nick_name = name['nickName']

            final_birth_date = None
            final_death_date = None

            dates = obituary['fromToYears']
            if dates == "null" or dates == None or dates == "":
                final_birth_year = None
                final_death_year = None
            else:
                dashed_dates = dates.split('-')
                final_birth_year = str(dashed_dates[0].strip())
                final_death_year = str(dashed_dates[1].strip())

            if obituary['age'] == "null" or  obituary['age'] == None:
                final_age = None
            else:
                final_age = obituary['age']


            funeral_home = obituary['funeralHome']
            if funeral_home is None:
                final_funeral_home = None
            else:
                final_funeral_home = funeral_home['name']
            # print(funeral_home)
            # if funeral_home['name'] == "null" or  funeral_home['name'] == None or funeral_home['name'] == '':
            #     final_funeral_home = None
            # else:
            #     final_funeral_home = funeral_home['name']

            

            if obituary['obitSnippet'] == "null" or  obituary['obitSnippet'] == None:
                final_obituary_text = None
            else:
                final_obituary_text = obituary['obitSnippet']

            if obituary['mainPhoto'] == "null" or  obituary['mainPhoto'] == None:
                final_image = None
            else:
                final_image = obituary['mainPhoto']['url']

            # print(final_image)
            personObject = Person(final_first_name, final_middle_name, final_last_name, final_nick_name, final_birth_date, final_death_date, final_birth_year, final_death_year, final_age, final_funeral_home,
                            final_obituary_text, final_image)
            
            storePerson(personObject, 'output.csv')

        # driver.close()

        sleep(5)


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno),final_first_name)

def bypassCloudflare(link):
    try:

        with SB(uc=True, test=True, locale_code="en") as sb:
            url = link
            options = webdriver.ChromeOptions() 
            user_agents = [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            ]
            options.add_argument(f'user-agent={user_agents}')
            options.add_argument("--headless")
            options.add_argument("--use_subprocess")
            options.add_argument('--no-sandbox')
            options.add_argument('start-maximized')
            options.add_argument('enable-automation')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-browser-side-navigation')
            options.add_argument("--remote-debugging-port=9222")
            options.add_argument('--disable-gpu')
            options.add_argument("--log-level=3")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--auto-open-devtools-for-tabs")
            driver = Driver(uc=True)
            driver.uc_open_with_reconnect(url, 10)
            # sb.type('input[placeholder="Enter domain"]', "https://www.peopleperhour.com")
            # driver.uc_click('span:contains("Check Authority")', reconnect_time=4)
            # breakpoint()

            time.sleep(1)

            html = driver.page_source
            soup = BeautifulSoup(html)

            print(soup)
            
            driver.quit()


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno), link)


def test():
    try:

        driver = Driver(uc=True)
        
        with open('obituaries_urls.csv', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for e,row in enumerate(reader):
                final_url = row[0]
                if e == 0:
                    options = webdriver.ChromeOptions() 
                    user_agents = [
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                    ]
                    options.add_argument(f'user-agent={user_agents}')
                    options.add_argument("--headless")
                    options.add_argument("--use_subprocess")
                    options.add_argument('--no-sandbox')
                    options.add_argument('start-maximized')
                    options.add_argument('enable-automation')
                    options.add_argument('--disable-infobars')
                    options.add_argument('--disable-dev-shm-usage')
                    options.add_argument('--disable-browser-side-navigation')
                    options.add_argument("--remote-debugging-port=9222")
                    options.add_argument('--disable-gpu')
                    options.add_argument("--log-level=3")
                    options.add_argument("--disable-blink-features=AutomationControlled")
                    options.add_argument("--auto-open-devtools-for-tabs")
                    # driver = Driver(uc=True)
                    driver.execute_script("window.open('" + str(final_url) + "');")
                    # sb.type('input[placeholder="Enter domain"]', "https://www.peopleperhour.com")
                    # driver.uc_click('span:contains("Check Authority")', reconnect_time=4)
                    # breakpoint()

                    time.sleep(10)

                    html = driver.page_source
                    soup = BeautifulSoup(html)
                    title = soup.find('title')

                    if title is None:
                        fetchPageObituaries(soup)

                    # print(soup)

                else:
                    driver.execute_script("window.open('" + str(final_url) + "');")
                    time.sleep(5)
                    # close the current, old tab
                    driver.close()
                    # get the handle of the new, recently opened tab
                    window_name = driver.window_handles[0]
                    # switch to the recently opened tab
                    driver.switch_to.window(window_name=window_name)

                    html = driver.page_source
                    soup = BeautifulSoup(html)
                    title = soup.find('title')

                    if title is None:
                        fetchPageObituaries(soup)
                    
                
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))

def make_json(csvFilePath, jsonFilePath):
    data = {}
    with open(csvFilePath, encoding='utf-8-sig') as csvf:
        csvReader = csv.DictReader(csvf)

        for num, rows in enumerate(csvReader):
            data[int(num)] = rows
 
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))


def generateAllObituariesUrls():
    try:
        dynamic_page_no = 50
        while True:
            url = f'https://www.legacy.com/api/_frontend/search?endDate=2024-08-03&firstName=&keyword=&lastName=&limit=100&noticeType=all&offset={dynamic_page_no}&session_id=&startDate=1998-01-01'
            print(url)
            dynamic_page_no = dynamic_page_no + 50
            link = [url]

            with open('obituaries_urls.csv', 'a', newline='', encoding="utf-8-sig") as products_file:
                writer = csv.writer(products_file)
                writer.writerow(link)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))


def mainLinksGenerator(start_date, end_date):   
    try:
        global all_records
        with SB(uc=True, locale_code="en") as sb:
            url = f'https://www.legacy.com/api/_frontend/search?endDate={end_date}&firstName=&keyword=&lastName=&limit=100&noticeType=all&offset=100&session_id=&startDate={start_date}'
            options = webdriver.ChromeOptions() 
            user_agents = [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            ]
            options.add_argument(f'user-agent={user_agents}')
            options.add_argument("--headless")
            options.add_argument("--use_subprocess")
            options.add_argument('--no-sandbox')
            options.add_argument('start-maximized')
            options.add_argument('enable-automation')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-browser-side-navigation')
            options.add_argument("--remote-debugging-port=9222")
            options.add_argument('--disable-gpu')
            options.add_argument("--log-level=3")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--auto-open-devtools-for-tabs")
            driver = Driver(uc=True)
            driver.uc_open_with_reconnect(url, 10)
            # sb.type('input[placeholder="Enter domain"]', "https://www.peopleperhour.com")
            # driver.uc_click('span:contains("Check Authority")', reconnect_time=4)
            # breakpoint()

            time.sleep(1)

            html = driver.page_source
            soup = BeautifulSoup(html)

            dict_from_json = json.loads(soup.find("body").text)

            records_count = int(dict_from_json['totalRecordCount'])

            all_records = records_count + 100

            # print(records_count)

            print(records_count)
            
            driver.quit()


        current_0ffset = 100
        while current_0ffset <= all_records:
            url = f'https://www.legacy.com/api/_frontend/search?endDate={end_date}&firstName=&keyword=&lastName=&limit=100&noticeType=all&offset={str(current_0ffset)}&session_id=&startDate={start_date}'
            print(url)
            print(current_0ffset)
            current_0ffset = current_0ffset + 100
            link = [url]

            with open('obituaries_urls.csv', 'a', newline='', encoding="utf-8-sig") as products_file:
                writer = csv.writer(products_file)
                writer.writerow(link)

        # print(all_records)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))


def previousDate(current_date):
    try:
        import datetime
        s = current_date
        theday = datetime.date(*map(int, s.split('-')))
        prevday = theday - datetime.timedelta(days=1)
        previous_day = prevday.strftime('%Y-%m-%d')
        return str(previous_day)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))



def aaaa(start_index):
    try:

        # with open('date_links.csv', newline='', encoding='utf-8') as f:
        #     reader = csv.reader(f)
        #     rows = list(reader)
        #     rows_count = len(rows)
        #     for i in range(start_index,rows_count):
        #         print(rows[i])

        with open('date_links.csv', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            rows_count = len(rows)
            for i in range(start_index,rows_count):
                print(i)
                final_url = rows[i][0]
                if i == start_index:
                    driver = Driver(uc=True,headless=True,no_sandbox=True)
                    options = webdriver.ChromeOptions() 
                    user_agents = [
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                    ]
                    options.add_argument(f'user-agent={user_agents}')
                    options.add_argument("--headless")
                    options.add_argument("--use_subprocess")
                    options.add_argument('--no-sandbox')
                    options.add_argument('start-maximized')
                    options.add_argument('enable-automation')
                    options.add_argument('--disable-infobars')
                    options.add_argument('--disable-dev-shm-usage')
                    options.add_argument('--disable-browser-side-navigation')
                    options.add_argument("--remote-debugging-port=9222")
                    options.add_argument('--disable-gpu')
                    options.add_argument("--log-level=3")
                    options.add_argument("--disable-blink-features=AutomationControlled")
                    options.add_argument("--auto-open-devtools-for-tabs")
                    # driver = Driver(uc=True)
                    # driver.execute_script("window.open('" + str(final_url) + "');")
                    driver.execute_script("window.open('" + "https://www.legacy.com/api/_frontend/search?endDate=2024-08-06&firstName=&keyword=&lastName=&limit=100&noticeType=all&offset=100&session_id=&startDate=2024-08-06" + "');")
                    time.sleep(5)
                    driver.close()
                    window_name = driver.window_handles[0]
                    driver.switch_to.window(window_name=window_name)
                    # sb.type('input[placeholder="Enter domain"]', "https://www.peopleperhour.com")
                    # driver.uc_click('span:contains("Check Authority")', reconnect_time=4)
                    # breakpoint()

                    time.sleep(15)

                else:
                    
                    driver.execute_script("window.open('" + str(final_url) + "');")
                    time.sleep(5)
                    # close the current, old tab
                    driver.close()
                    # get the handle of the new, recently opened tab
                    window_name = driver.window_handles[0]
                    # switch to the recently opened tab
                    driver.switch_to.window(window_name=window_name)

                    html = driver.page_source
                    soup = BeautifulSoup(html)

                    title = soup.find('title')
                    if title is None:
                        dict_from_json = json.loads(soup.find("body").text)
                        records_count = int(dict_from_json['totalRecordCount'])
                        all_records = records_count + 100

                        print(final_url)
                        print(all_records)

                        current_0ffset = 0
                        while current_0ffset <= all_records:
                            url = re.sub(r'offset=100',f'offset={current_0ffset}',final_url)
                            current_0ffset = current_0ffset + 100
                            link = [url]

                            with open('obituaries_urls.csv', 'a', newline='', encoding="utf-8-sig") as products_file:
                                writer = csv.writer(products_file)
                                writer.writerow(link)

                    time.sleep(0.5)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))

def storeDateLinks():
    try:
        current_date = '2024-08-05'
        while True:

            current_date_link = f'https://www.legacy.com/api/_frontend/search?endDate={current_date}&firstName=&keyword=&lastName=&limit=100&noticeType=all&offset=100&session_id=&startDate={current_date}'
            date_link = [current_date_link]

            with open('date_links.csv', 'a', newline='', encoding="utf-8-sig") as products_file:
                writer = csv.writer(products_file)
                writer.writerow(date_link)
            
            previous_current_date = str(previousDate(current_date))
            current_date = previous_current_date


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))

def verify_success(sb):
    sb.assert_element('div[id*="challenge-error-title"]', timeout=4)
    sb.sleep(3)

def mainFetchObituaries(start_index):
    CRED = '\033[91m'
    Green = '\033[92m'

    try:
        with SB(uc=True) as sb:
            with open('obituaries_urls.csv', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                rows_count = len(rows)
                for i in range(start_index,rows_count):
                    final_url = rows[i][0]
                    print(final_url)
                    if i == start_index:

                        url = "https://www.legacy.com/api/_frontend/search?endDate=2024-08-06&firstName=&keyword=&lastName=&limit=100&noticeType=all&offset=0&session_id=&startDate=2024-08-06"
                        # url = "https://www.google.com"
                        

                        # cursor_script = '''
                        # var cursor = document.createElement('div');
                        # cursor.style.position = 'absolute';
                        # cursor.style.zIndex = '9999';
                        # cursor.style.width = '10px';
                        # cursor.style.height = '10px';
                        # cursor.style.borderRadius = '50%';
                        # cursor.style.backgroundColor = 'red';
                        # cursor.style.pointerEvents = 'none';
                        # document.body.appendChild(cursor);

                        # document.addEventListener('mousemove', function(e) {
                        # cursor.style.left = e.pageX - 5 + 'px';
                        # cursor.style.top = e.pageY - 5 + 'px';
                        # });
                        # '''

                        # from selenium.webdriver.common.actions.action_builder import ActionBuilder

                        # sb.uc_open_with_reconnect(url)
                        # sb.driver.execute_script(cursor_script)
                        # action = ActionBuilder(sb.driver)


                        # time.sleep(15)
                        # sb.uc_gui_click_captcha()
                        # action.pointer_action.move_to_location(215, 295)
                        # time.sleep(5)
                        # action.pointer_action.click()
                        # action.perform()
                        # time.sleep(35)
                        

                        # time.sleep(10)


                        # action = webdriver.ActionChains(sb.driver)
                        # action.move_by_offset(100, 200)    # 10px to the right, 20px to bottom
                        # action.perform()
                        # time.sleep(10)


                        # sb.uc_gui_click_captcha()
                        # sb.assert_element("img#captcha-success", timeout=3)
                        # sb.set_messenger_theme(location="top_left")
                        # sb.post_message("SeleniumBase wasn't detected", duration=3)

                        # sb.uc_open_with_reconnect("https://www.legacy.com/api/_frontend/search?endDate=2024-08-06&firstName=&keyword=&lastName=&limit=100&noticeType=all&offset=0&session_id=&startDate=2024-08-06", 3)
                        # try:
                        #     verify_success(sb)
                        # except Exception:
                        #     if sb.is_element_visible('div[id*="challenge-error-title"]'):
                        #         print("salam")
                        #         # sb.uc_click('span[class*="cb-i"]')
                        #     else:
                        #         # sb.uc_click('span[class*="cb-i"]')
                        #         # time.sleep(20)
                        #         print("hi")
                        #         sb.uc_gui_click_captcha()
                        #     # try:
                        #     #     verify_success(sb)
                        #     # except Exception:
                        #     #     raise Exception("Detected!")

                        # sb.driver.get("https://www.legacy.com/api/_frontend/search?endDate=2024-08-06&firstName=&keyword=&lastName=&limit=100&noticeType=all&offset=0&session_id=&startDate=2024-08-06")
                        # time.sleep(10)

                        # action = webdriver.ActionChains(sb.driver)
                        # action.move_by_offset(10, 20)    # 10px to the right, 20px to bottom
                        # action.perform()
                        # action.click()

                        # WebDriverWait(sb.driver, 10).until(EC.frame_to_be_available_and_switch_to_it("cf-chl-widget-psqcs"))
                        # WebDriverWait(sb.driver, 10).until(EC.presence_of_element_located((By.ID, "cf-chl-widget-psqcs")))
                        # WebDriverWait(sb.driver, 20).until(EC.none_of(WebDriverWait(sb, 20).until(EC.visibility_of_all_elements_located((By.XPATH, "//iframe[@id='cf-chl-widget-psqcs']")))))
                        # # WebDriverWait(sb.driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[@title='Widget containing a Cloudflare security challenge']")))
                        # WebDriverWait(sb.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id=cf-chl-widget-psqcs_response]"))).click()
                        # time.sleep(10)
                        # print("succeeded")

                        sb.driver.maximize_window()
                        sb.driver.execute_script("window.open('" + "https://www.legacy.com/api/_frontend/search?endDate=2024-08-06&firstName=&keyword=&lastName=&limit=100&noticeType=all&offset=0&session_id=&startDate=2024-08-06" + "');")
                        time.sleep(15)
                        sb.uc_gui_click_x_y(430, 466,timeframe=3.64)
                        sb.driver.close()
                        window_name = sb.driver.window_handles[0]
                        sb.driver.switch_to.window(window_name=window_name)
                        time.sleep(15)

                        # html = sb.driver.page_source
                        # soup = BeautifulSoup(html)
                        # spacer_element = soup.find("div",{"class":"spacer"})
                        # print(spacer_element)
                        # print(soup)

                    else:
                        sb.driver.execute_script("window.open('" + str(final_url) + "');")
                        time.sleep(1)
                        # close the current, old tab
                        sb.driver.close()
                        # get the handle of the new, recently opened tab
                        window_name = sb.driver.window_handles[0]
                        # switch to the recently opened tab
                        sb.driver.switch_to.window(window_name=window_name)

                        html = sb.driver.page_source
                        soup = BeautifulSoup(html)
                        title = soup.find('title')

                        if title is None:
                            fetchPageObituaries(soup)
                            print(Green + '\033[1m' + "Iteration " + str(i) + " successfully completed")
                            storeUrlIndex(i)
                        
                        else:
                            print("second approach")
                            sb.driver.quit()
                            raise Exception()
                            # pass


                            # sb.driver.execute_script("window.open('" + "https://www.legacy.com/api/_frontend/search?endDate=2024-08-06&firstName=&keyword=&lastName=&limit=100&noticeType=all&offset=0&session_id=&startDate=2024-08-06" + "');")
                            # time.sleep(15)
                            # sb.uc_gui_click_x_y(430, 466,timeframe=3.64)
                            # sb.driver.close()
                            # window_name = sb.driver.window_handles[0]
                            # sb.driver.switch_to.window(window_name=window_name)
                            

                            # while True:
                            #     time.sleep(15)
                            #     sb.uc_gui_click_x_y(430, 466,timeframe=1.5)
                            #     # sb.driver.close()
                            #     window_name = sb.driver.window_handles[0]
                            #     sb.driver.switch_to.window(window_name=window_name)

                            #     html = sb.driver.page_source
                            #     soup = BeautifulSoup(html)
                            #     title = soup.find('title')

                            #     print(title.text.strip())

                            #     if title.text.strip() != "Just a moment...":
                            #         print("passed")
                            #         # break
                            #     else:
                            #         time.sleep(2.3)
                            #         x,y = moveMouseToRandomOffsets()
                            #         sb.uc_gui_click_x_y(x, y,timeframe=1.5)

                            #         sb.wait_for_element_present("div.main-wrapper", timeout=20)
                            #         time.sleep(20)
                            #         continue

    except:
        global last_line_index
        with open('url_index.txt', 'r') as f:
            last_line = f.readlines()[-1].strip()
            last_line_int = int(last_line)
            last_line_index = last_line_int
            f.close()
        print(last_line_index)
        mainFetchObituaries(last_line_int)


def storeUrlIndex(index):
    try:
        with open('url_index.txt', 'a', encoding='utf-8') as f:
            f.write(str(index)+'\n')

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))


def testClickToBypass():

    # with SB(uc=True,test=True) as sb:
    #     sb.driver.execute_script("window.open('" + "https://www.legacy.com/api/_frontend/search?endDate=2024-08-06&firstName=&keyword=&lastName=&limit=100&noticeType=all&offset=0&session_id=&startDate=2024-08-06" + "');")
    #     time.sleep(15)
    #     sb.driver.close()
    #     window_name = sb.driver.window_handles[0]
    #     sb.driver.switch_to.window(window_name=window_name)
    #     time.sleep(15)


    # with SB(uc=True,disable_csp=True) as sb:
    with SB(uc=True,test=True) as sb:
        # url = "https://www.legacy.com/api/_frontend/search?endDate=2024-08-04&firstName=&keyword=&lastName=&limit=100&noticeType=all&offset=100&session_id=&startDate=2024-08-04"
        # sb.uc_open_with_reconnect(url, 4)
        # time.sleep(15)
        # sb.uc_gui_click_x_y(275, 475,timeframe=1.25)
        # # sb.uc_gui_click_captcha(frame="iframe")
        # time.sleep(40)

        sb.driver.execute_script("window.open('" + "https://www.legacy.com/api/_frontend/search?endDate=2024-08-06&firstName=&keyword=&lastName=&limit=100&noticeType=all&offset=0&session_id=&startDate=2024-08-06" + "');")
        time.sleep(15)
        sb.uc_gui_click_x_y(275, 475,timeframe=0.25)
        sb.driver.close()
        window_name = sb.driver.window_handles[0]
        sb.driver.switch_to.window(window_name=window_name)
        sb.uc_gui_click_x_y(275, 475,timeframe=1.25)
        time.sleep(15)


def moveMouseToRandomOffsets():
    try:
        user32 = ctypes.windll.user32
        screensize = user32.GetSystemMetrics(78), user32.GetSystemMetrics(79)
        x = screensize[0]
        y = screensize[1]
        random_x_offset = random.randint(0, 1910)
        random_y_offset = random.randint(200, 1070-200)

        return random_x_offset, random_y_offset


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))



def testMultipleTryToBypassCloudFlare():
    try:

        with SB(uc=True,disable_csp=True) as sb:
        # with SB(uc=True,test=True) as sb:

            cursor_script = '''
            var cursor = document.createElement('div');
            cursor.style.position = 'absolute';
            cursor.style.zIndex = '9999';
            cursor.style.width = '10px';
            cursor.style.height = '10px';
            cursor.style.borderRadius = '50%';
            cursor.style.backgroundColor = 'red';
            cursor.style.pointerEvents = 'none';
            document.body.appendChild(cursor);

            document.addEventListener('mousemove', function(e) {
            cursor.style.left = e.pageX - 5 + 'px';
            cursor.style.top = e.pageY - 5 + 'px';
            });
            '''

            sb.driver.maximize_window()
            url = "https://www.legacy.com/api/_frontend/search?endDate=2024-08-04&firstName=&keyword=&lastName=&limit=100&noticeType=all&offset=100&session_id=&startDate=2024-08-04"
            sb.uc_open_with_reconnect(url, 4)
            time.sleep(15)

            while True:
                sb.driver.execute_script(cursor_script)
                sb.uc_gui_click_x_y(430, 466,timeframe=1.5)

                html = sb.driver.page_source
                soup = BeautifulSoup(html)
                title = soup.find('title')

                print(title.text.strip())

                if title.text.strip() != "Just a moment...":
                    break
                else:
                    sb.driver.execute_script(cursor_script)
                    x,y = moveMouseToRandomOffsets()
                    sb.uc_gui_click_x_y(x, y,timeframe=1.5)

                    sb.wait_for_element_present("div.main-wrapper", timeout=20)
                    time.sleep(20)
                    continue
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
    



def multipleTryToBypassCloudFlare():
    try:

        # with SB(uc=True,disable_csp=True) as sb:
        with SB(uc=True,test=True) as sb:
            sb.driver.maximize_window()
            sb.driver.execute_script("window.open('" + "https://www.legacy.com/api/_frontend/search?endDate=2024-08-06&firstName=&keyword=&lastName=&limit=100&noticeType=all&offset=0&session_id=&startDate=2024-08-06" + "');")
            time.sleep(10)
            sb.driver.close()
            window_name = sb.driver.window_handles[0]
            sb.driver.switch_to.window(window_name=window_name)
            time.sleep(10)

            while True:
                sb.uc_gui_click_x_y(430, 466,timeframe=1.5)

                html = sb.driver.page_source
                soup = BeautifulSoup(html)
                title = soup.find('title')

                print(title.text.strip())

                if title.text.strip() != "Just a moment...":
                    break
                else:
                    x,y = moveMouseToRandomOffsets()
                    sb.uc_gui_click_x_y(x, y,timeframe=1.5)

                    sb.wait_for_element_present("div.main-wrapper", timeout=20)
                    time.sleep(20)
                    continue
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))

import sys
def testRecursionFunction():
    try:
        for i in range(1,20):
            print(i)
            sys.exit()
            # raise Exception()
    except:
        testRecursionFunction()
        print("salam")




def mainFunction():
    CRED = '\033[91m'

    try:
        testRecursionFunction()

        # multipleTryToBypassCloudFlare()

        # testMultipleTryToBypassCloudFlare()

        # testClickToBypass()

        # global last_line_index
        # with open('url_index.txt', 'r') as f:
        #     last_line = f.readlines()[-1].strip()
        #     last_line_int = int(last_line)
        #     last_line_index = last_line_int
        #     f.close()

        # mainFetchObituaries(last_line_index)

        # aaaa(5269)
        
        # generateAllObituariesUrls()

        # test()

        # storeDateLinks()

        # mainLinksGenerator(start_date='2024-08-04', end_date='2024-08-04')

        # print(previousDate('2024-08-03'))
        # a = previousDate('2024-08-03')
        # print(a)

        # bypassCloudflare('legacy.com/obituaries/search')

        # fetchAllObituaries(50)
        # fetchPageObituaries('https://www.legacy.com/api/_frontend/search?endDate=2024-08-03&firstName=&keyword=&lastName=&limit=50&noticeType=all&offset=100&session_id=&startDate=1998-01-01')
    #    bypassCloudflare('https://www.legacy.com/obituaries/search')

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))

mainFunction()

async def aa():
    await asyncio.sleep(3)
    print("aa finished")

async def bb():
    await asyncio.sleep(2)
    print("bb finished")

    # obituaries = fetchObituariesPage(f'https://www.echovita.com/us/obituaries?page={str(page_no)}')
    # for obituary in obituaries:
    #     obituary_task = asyncio.create_task(fetchObituary(obituary))
    #     await obituary_task
    
  

# asyncio.run(fetchHandler(1))

# make_json('Echovita/Echovita-part8.csv', 'Echovita-part8.json')
