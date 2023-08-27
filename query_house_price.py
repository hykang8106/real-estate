# [ref] https://ai-creator.tistory.com/24

# public data portal:
# https://www.data.go.kr/data/15058352/openapi.do
# login info: id = khy716, pw = hykang8106#

import pandas as pd
import requests
import sys
import datetime
import xml.etree.ElementTree as ET

from define_file_url_key import *
from util_real_estate import *
from proc_query_result import *
from query_rent_conv_rate import *
from study_real_estate_price import *

help_message = \
    """ 
    #### [error] need input: 'query_type' 'gu' 'dong' 'from_yyyymm' 'to_yyyyymm' 'apt_name'

    [example] query_house_price single_rent 유성구 문지동 201701 202112
    [example] query_house_price single_sale 유성구 문지동 201701 202112
    [example] query_house_price apt_rent 유성구 문지동 201701 202112 문지효성해링턴플레이스
    [example] query_house_price apt_sale 세종특별자치시 반곡동 201701 202112 수루배마을1단지
    [example] query_house_price apt_sale 세종특별자치시 반곡동 202201 202307 all
    [example] query_house_price apt_sale 성동구 행당동 201701 202112 대림e-편한세상
    [example] query_house_price apt_sale 유성구 전민동 201701 202112 엑스포
    """

if __name__ == "__main__":

    if len(sys.argv) < 6:
        print(help_message)
        sys.exit()

    query_type = sys.argv[1]

    if query_type not in query_type_list:
        print("#### [error] 'query_type': one of 'single_rent', 'single_sale', 'apt_rent', 'apt_sale'")
        sys.exit()

    # to use "proc_result" dict to select function for processing query result
    # function to process single(house) query result need not 'apt' input
    # function to process apt query result need 'apt' input
    apt = ''
    if 'apt' in query_type:
        if len(sys.argv) == 7:
            apt = sys.argv[6]
        else:
            print("#### when query type is 'apt_rent' or 'apt_sale', 'apt_name' must be given")
            print("#### if you include all apt, set 'apt_name' to 'all'")
            print("[example] query_house_price apt_rent 유성구 문지동 201701 202112 문지효성해링턴플레이스")
            print("[example] query_house_price apt_sale 세종특별자치시 반곡동 201701 202112 수루배마을1단지")
            print("[example] query_house_price apt_sale 세종특별자치시 반곡동 201701 202112 all")
            sys.exit()

    url = query_url[query_type]
    gu = sys.argv[2]
    dong = sys.argv[3]
    from_yyyymm = sys.argv[4]
    to_yyyymm = sys.argv[5]
    if int(to_yyyymm) - int(from_yyyymm) < 0:
        print("#### [error] 'from_yyyymm' must not be greater than 'to_yyyymm'")
        sys.exit()

    if 'rent' in query_type:
        # get rent conversion rate to convert mixed rent(deposit + monthly) to deposit only rent 
        conv_rate_table = query_rent_conv_rate(from_yyyymm, to_yyyymm)
        # most recent query result have 3 months delay
        conv_rate_table = extend_rent_conv_rate(conv_rate_table, to_yyyymm)

    code = load_code()

    gu_code = get_gu_code(code, gu)
    if not gu_code:
        print("#### check 'gu' input")
        sys.exit()

    dong_code = get_dong_code(code, gu + ' ' + dong)
    if not dong_code:
        print("#### check 'dong' input")
        sys.exit()

    yyyymm_list = get_yyyymm_list(from_yyyymm, to_yyyymm)
    # base_date_list = get_base_date_list(from_year, to_year)

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

    price_df = proc_result[query_type](price_df, dong, apt)
    if price_df.empty:
        print('\n#### query result filtering output empty, check program input')
        sys.exit()

    if 'apt' in query_type:
        filename = '{}_{}_{}_{}_{}_{}.xls'.format(query_type, gu, dong, apt, from_yyyymm, to_yyyymm)
    else:
        filename = '{}_{}_{}_{}_{}.xls'.format(query_type, gu, dong, from_yyyymm, to_yyyymm)

    price_df.to_excel(filename, index=False)
    print("\n### query result saved into file =", filename)

    sys.exit()

    study_real_estate_price(price_df, conv_rate_table, query_type, gu, dong, apt, from_yyyymm, to_yyyymm)
