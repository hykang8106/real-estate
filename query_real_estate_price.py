# [ref] https://ai-creator.tistory.com/24

# public data portal:
# https://www.data.go.kr/data/15058352/openapi.do
# login info: id = khy716, pw = hykang8106!

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

if __name__ == "__main__":

    '''
    gu = '유성구'
    dong = '문지동'
    from_year = '2021'
    # from_year = '2017'
    to_year = '2021'
    '''

    if len(sys.argv) < 6:
        print("#### [error] need input: 'query_type' 'gu' 'dong' 'from_yyyymm' 'to_yyyyymm' 'apt_name'")
        print(command_example_1)
        print(command_example_2)
        print(command_example_3)
        print(command_example_4)
        print(command_example_5)
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
            print("#### [error] 'apt_rent', 'apt_sale' need 'apt_name'")
            print(command_example_3)
            print(command_example_4)
            print("#### if you not know apt name, set 'apt_name' to 'all'")
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

    '''
    for base_date in base_date_list:
        res = get_data(url, service_key, gu_code, base_date)
        print(res.status_code)
        items_list += get_items(res)
    '''

    # res.close()

    items = pd.DataFrame(items_list)

    items = proc_result[query_type](items, dong, apt)

    if 'apt' in query_type:
        filename = '{}_{}_{}_{}_{}_{}.xls'.format(query_type, gu, dong, apt, from_yyyymm, to_yyyymm)
    else:
        filename = '{}_{}_{}_{}_{}.xls'.format(query_type, gu, dong, from_yyyymm, to_yyyymm)

    # filename = 'temp.xls'
    items.to_excel(filename, index=False)
    print("\n### query result saved into file =", filename)

    if (query_type == 'single_rent') & (gu == '유성구'):
        conv_rate_col = 'single_daejeon'
    elif (query_type == 'single_rent') & (gu == '세종특별자치시'):
        conv_rate_col = 'single_sejong'
    elif (query_type == 'apt_rent') & (gu == '유성구'):
        conv_rate_col = 'apt_yuseong'
    elif (query_type == 'apt_rent') & (gu == '세종특별자치시'):
        conv_rate_col = 'apt_sejong'
    else:
        conv_rate_col = ''

    sys.exit()

    if query_type == 'single_rent':
        if not conv_rate_col:
            price_per_m2 = compute_single_rent_price_per_m2(items, conv_rate_table, conv_rate_col)
            # plot_rent_price_per_m2()

    elif query_type == 'single_sale':
        price_per_m2 = items['sale_price_1e4'] / items['build_area_m2']

        # price_per_m2 = compute_single_sale_price_per_m2(items)

    elif query_type == 'apt_rent':
        if not conv_rate_col:
            price_per_m2 = compute_apt_rent_price_per_m2(items, conv_rate_table, conv_rate_col)
   
    elif query_type == 'apt_sale':
        price_per_m2 = items['sale_price_1e4'] / items['area_m2']
        # price_per_m2 = compute_apt_sale_price_per_m2(items)
          
        
    # items['conv_deposit_rent_1e4'] = items['deposit_rent_1e4'] + items['month_rent_1e4']

    '''
    if sys.argv[1] == 'single_rent':
        items = process_single_rent(items, dong)
    elif sys.argv[1] == 'single_sale':
        items = process_single_sale(items, dong)
    elif sys.argv[1] == 'apt_rent':
        items = process_apt_rent(items, dong, apt)
    elif sys.argv[1] == 'apt_sale':
        items = process_apt_sale(items, dong, apt)
    '''

'''
soup = BeautifulSoup(res.content, 'lxml-xml')
items = soup.findall('item')
'''