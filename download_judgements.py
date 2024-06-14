from bs4 import BeautifulSoup
from datetime import datetime as dt
import requests
import os
import shutil
import re
from urllib.parse import urlparse, parse_qs

global_case_map={}

def extract_case_details(html_content):
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract all <li> tags
    li_tags = soup.find_all('li')

    # Initialize a list to store the results
    results = []

    # Process and filter the <li> tags according to your format
    for li in li_tags:
        a_tag = li.find('a', href=True)
        if a_tag and a_tag['href'].startswith("https://www.sci.gov.in/wp-admin/admin-ajax.php"):
            link = a_tag['href']
            case_details = a_tag.get_text(strip=True)
            date_span = a_tag.find('span', style="color:red;")
            if date_span:
                case_date = date_span.get_text(strip=True)
                # Append the tuple (case_details, link, date) to the results list
                results.append((case_details, link, case_date))

    return results


def download_judgements_page():
    response = requests.get('https://www.sci.gov.in/latest-orders/')
    if response.status_code == 200:
        cases = extract_case_details(response.text)
        return cases

def parse_diary_num(link):
    parsed_url = urlparse(link)
    query_params = parse_qs(parsed_url.query)
    return query_params['diary_no'][0]

def show_cases():
    cases = download_judgements_page()
    case_objs = []
    for case_details, link, date in cases:
        split_details = case_details.split('-')
        title = split_details[0].strip()
        hearing_date = split_details[-1].strip(')')

        no_whitespace_string = re.sub(
            r'\s+', '_', title)
        short_case_name = re.sub(r'[^A-Za-z0-9_]+', '', no_whitespace_string)
        diary_num = parse_diary_num(link)
        key = f"{diary_num}-{short_case_name}"
        
        case_obj = { 'diary_no': diary_num, 'title': key,  'link' : link }
        case_objs.append(case_obj)
        global_case_map[key] = case_obj
    return case_objs
