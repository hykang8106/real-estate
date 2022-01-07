import pandas as pd
import numpy as np
import requests
import sys
import datetime
import xml.etree.ElementTree as ET

from define_file_url_key import *

def load_code():

    code = pd.read_csv(code_file, sep='\t')
    code.columns = ['code', 'name', 'is_exist']
    code = code[code['is_exist'] == '존재']

    code = code.drop(['is_exist'], axis=1).reset_index(drop=True)

    code['code'] = code['code'].apply(str)

    return code

def get_gu_code(code, gu):

    gu_code = code[(code['name'].str.contains(gu))]
    if gu_code.empty:
        gu_code = ''
        return gu_code
    # print(gu_code)
    gu_code = gu_code['code'].reset_index(drop=True)
    gu_code = str(gu_code[0])[0:5]
    print('gu code =', gu_code)

    return gu_code

def get_dong_code(code, dong):

    dong_code = code[(code['name'].str.contains(dong))]
    if dong_code.empty:
        dong_code = ''
        return dong_code
    dong_code = dong_code['code'].reset_index(drop=True)
    dong_code = str(dong_code[0])
    print('dong code =', dong_code)

    return dong_code

def get_base_date_list(from_year, to_year):

    year = [str("%02d" %(y)) for y in range(int(from_year), int(to_year) + 1)]
    month = [str("%02d" %(m)) for m in range(1, 13)]
    date_list = ["%s%s" %(y, m) for y in year for m in month]
    # date_list = ['202001']

    return date_list

def get_yyyymm_list(from_yyyymm, to_yyyymm):

    a = np.arange(int(from_yyyymm), int(to_yyyymm) + 1)

    a = a[(a % 100 != 0) & (a % 100 <= 12)]

    yyyymm_list = a.astype(str)

    return yyyymm_list

def get_data(url, service_key, gu_code, base_date):

    payload = "LAWD_CD=" + gu_code + "&" + \
              "DEAL_YMD=" + base_date + "&" + \
              "serviceKey=" + service_key + "&"

    res = requests.get(url + payload)
    # print(res.status_code)
    
    return res

def get_items(response):
    
    root = ET.fromstring(response.content)
    item_list = []
    for child in root.find('body').find('items'):
        elements = child.findall('*')
        data = {}
        for element in elements:
            tag = element.tag.strip()
            text = element.text.strip()
            # print tag, text
            data[tag] = text
        item_list.append(data)  
    return item_list
