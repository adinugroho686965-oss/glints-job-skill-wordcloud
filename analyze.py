from curl_cffi import requests
from payload import get_payload
from collections import Counter

def get_skill(payload,raw_cookies,max_data):
    url = "https://glints.com/api/v2-alc/graphql?op=searchJobsV3"

    headers = {
        "Host": "glints.com",
        "Content-Type": "application/json",
        "x-glints-country-code": "ID",

        "Origin": "https://glints.com",
        "Alt-Used": "glints.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Priority": "u=4",
        "Cookie":raw_cookies
        }

    jobs = []
    max_data = int(max_data/30)
    if max_data < 1:max_data = 1
    for x in range(max_data):
        payload["variables"]['page'] = x+1      
        response = requests.post(url, headers=headers, json=payload  ,impersonate="firefox",).json()
        
        jobs.extend(response['data']['searchJobsV3']['jobsInPage'])

    all_skills = []

    for job in jobs:
        if job.get('skills'):
            for s in job['skills']:
                skill_name = s.get('skill', {}).get('name')
                if skill_name:
                    all_skills.append(skill_name.lower()) 
    return all_skills

def count_frequency_word(word_list):

    word_list_counted = Counter(word_list)

    return word_list_counted




