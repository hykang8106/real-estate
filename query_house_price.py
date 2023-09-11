""" 
[branch: change_cmd_arg]

commit [1] message

(1) change command argument:
#### input: 'query_type' 'metro' 'gu' 'from_yyyymm' 'to_yyyyymm' 'dong' 'apt_name'
#### 'dong', 'apt_name' inputs are optional.
#### if 'dong' is not given, all dong is included.
#### if 'apt_name' is not given, all apt is included.
(2) modify 'help_message'
(3) remove 'apt_name' mandatory input when 'query_type' is related to apt
(4) delete 'query_rent_conv_rate' function call when 'query_type' is related to single
(5) delete 'get_dong_code' function call
(6) modify query result excel filename, save excel file into 'query_result_xls' folder
(7) 결과 파일명을 한글로 변경('다가구전세', '다가구매매', '아파트전세', '아파트매매')
"""

# [ref] https://ai-creator.tistory.com/24

# public data portal:
# https://www.data.go.kr/data/15058352/openapi.do
# login info: id = khy716, pw = hykang8106#

import pandas as pd
import requests
import sys, os
import datetime
import xml.etree.ElementTree as ET

from define_file_url_key import *
from util_real_estate import *
from proc_query_result import *
from query_rent_conv_rate import *
from study_real_estate_price import *

help_message = \
    """ 
    #### [input] 'query_type' 'metro' 'gu' 'from_yyyymm' 'to_yyyyymm' 'dong' 'apt_name'
    #### 'query_type' : one of 'single_rent', 'single_sale', 'apt_sale', 'apt_rent'
    #### 'single_rent' = 다가구 전세, 'single_sale' = 다가구 매매, 
    #### 'apt_sale' = 아파트 매매, 'apt_rent' = 아파트 전세
    #### 'metro' : 서울, 부산, 광역시, 도, 제주, 세종
    #### 'gu' : 구, 시, 군, 세종
    #### 'from_yyyymm' : 시작월, yyyymm
    #### 'to_yyyyymm' : 종료월, yyyymm
    #### 'dong' : 법정동, 읍, 면 (예: 행당동, 반곡동, 조치원읍, 금남면)
    #### 'apt' : 아파트명 (예: 대림e-편한세상, 수루배마을1단지)
    #### 'dong', 'apt_name' inputs are optional.
    #### if 'dong' is not given, all 'dong' in 'gu' is included.
    #### if 'apt_name' is not given, all 'apt' in 'dong' is included.

    [example] query_house_price single_rent 대전 유성구 201701 202112 문지동
    [example] query_house_price single_sale 대전 유성구 201701 202112 문지동
    [example] query_house_price single_sale 대전 유성구 201701 202112
    [example] query_house_price apt_rent 대전 유성구 201701 202112 문지동 문지효성해링턴플레이스
    [example] query_house_price apt_rent 대전 유성구 201701 202112
    [example] query_house_price apt_sale 세종 세종 201701 202112 반곡동 수루배마을1단지
    [example] query_house_price apt_sale 세종 세종 202201 202307 반곡동
    [example] query_house_price apt_sale 세종 세종 202201 202307
    [example] query_house_price apt_sale 서울 성동구 201701 202112 행당동 대림e-편한세상
    [example] query_house_price apt_sale 대전 유성구 201701 202112 전민동 엑스포
    """

filename_base = {
    'single_rent' : '다가구전세', 
    'single_sale' : '다가구매매', 
    'apt_rent' : '아파트전세', 
    'apt_sale' : '아파트매매', 
}

if __name__ == "__main__":

    if len(sys.argv) < 6:
        print(help_message)
        sys.exit()

    query_type = sys.argv[1]

    if query_type not in query_type_list:
        print("#### [error] 'query_type': one of 'single_rent', 'single_sale', 'apt_rent', 'apt_sale'")
        sys.exit()

    url = query_url[query_type]
    metro = sys.argv[2]
    gu = sys.argv[3]
    from_yyyymm = sys.argv[4]
    to_yyyymm = sys.argv[5]

    if int(to_yyyymm) - int(from_yyyymm) < 0:
        print("#### [error] 'from_yyyymm' must not be greater than 'to_yyyymm'")
        sys.exit()

    dong = ''
    apt = ''
    if len(sys.argv) == 7:
        dong = sys.argv[6]

    if (len(sys.argv) == 8) and ('apt' in query_type):
        dong = sys.argv[6]
        apt = sys.argv[7]

    code = load_code()

    gu_code = get_gu_code(code, metro, gu)
    if not gu_code:
        print("#### check 'gu' input")
        sys.exit()

    if dong:
        dong_code = get_dong_code(code, gu + ' ' + dong)
        if not dong_code:
            print("#### check 'dong' input")
            sys.exit()

    yyyymm_list = get_yyyymm_list(from_yyyymm, to_yyyymm)

    items_list = []
    for base_date in yyyymm_list:
        res = get_data(url, service_key, gu_code, base_date)
        if res.status_code == 200:
            print('.', end='')
        else:
            print('status code =', res.status_code)
        items_list += get_items(res)

    # res.close()

    price_df = pd.DataFrame(items_list)
    if price_df.empty:
        print('\n#### query result empty, server may be in problem')
        sys.exit()

    price_df = proc_result[query_type](price_df, dong, apt)
    if price_df.empty:
        print('\n#### query result filtering output empty, check input(metro, gu, dong)')
        sys.exit()

    if not os.path.isdir(query_result_folder):
        os.mkdir(query_result_folder)

    if len(sys.argv) == 6:
        filename = '{}_{}_{}_{}_{}.xls'.\
            format(filename_base[query_type], metro, gu, from_yyyymm, to_yyyymm)
    if len(sys.argv) == 7:
        filename = '{}_{}_{}_{}_{}_{}.xls'.\
            format(filename_base[query_type], metro, gu, from_yyyymm, to_yyyymm, dong)
    if len(sys.argv) == 8:
        filename = '{}_{}_{}_{}_{}_{}_{}.xls'.\
            format(filename_base[query_type], metro, gu, from_yyyymm, to_yyyymm, dong, apt)

    filename = os.path.join(query_result_folder, filename)
    price_df.to_excel(filename, index=False)
    print("\n### query result saved into file =", filename)

    # sys.exit()

    # study_real_estate_price(price_df, conv_rate_table, query_type, gu, dong, apt, from_yyyymm, to_yyyymm)
