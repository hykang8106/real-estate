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
from study_land_price import *

# 유성구, 공주시, 금산군 일때, 시군구 있음:
#
# 거래금액, 거래면적, 거래유형, 년, 법정동, 시군구, 용도지역, 월, 일, 중개사소재지, 지목, 지역코드, 해제사유발생일, 해제여부, 구분
# 51,912, 381, '', 2020, 용계동, 유성구, 자연녹지지역, 8, 6, '', 전, 30200, 21.01.21, O, 지분
# 
# 세종시 일때, 시군구 없음:
#
# 법정동, 용도지역
# 조치원읍 정리, 준주거지역
# 연기면 연기리, 계획관리지역
# 고운동, 제1종전용주거지역
#
# 용도지역 예: 개발제한구역, 자연녹지지역, 준주거지역, 제2종일반주거지역, 제1종일반주거지역, \
# 일반상업지역, 준공업지역, 용도미지정, 보전녹지지역, 제1종전용주거지역, 계획관리지역, \
# 농림지역, 생산관리지역
#
# 지목 예(28 개): 도로, 답, 대, 전, 임야, 주차장, 창고용지, 괴수원, 하천, 유지, 잡종지, 학교용지, 공장용지, \
# 묘지, 제방, 구거

def process_land_price_df(price_df, gu, dong, district, category):

    # remove row where '해제여부' column have 'O'
    price_df = price_df[price_df['해제여부'] != 'O'].reset_index(drop=True)

    # remove row where '구분' column have '지분'
    price_df = price_df[price_df['구분'] != '지분'].reset_index(drop=True)

    # drop not useful column
    if '시군구' in price_df.columns:
        price_df = price_df.drop(columns=['거래유형', '시군구', '중개사소재지', '지역코드', \
            '해제사유발생일', '해제여부', '구분'])
    else:
        price_df = price_df.drop(columns=['거래유형', '중개사소재지', '지역코드', '해제사유발생일', \
            '해제여부', '구분'])

    price_df = price_df.rename(columns={'거래면적':'area_m2', '법정동':'dong', \
        '년':'contract_yyyy', '월':'contract_mm', '일':'contract_dd', \
        '거래금액':'sale_price_1e4', '용도지역':'district', '지목':'category'})

    price_df.sale_price_1e4 = price_df.sale_price_1e4.str.replace(',','').astype(int)
    price_df.area_m2 = price_df.area_m2.str.replace(',','').astype(float)
    price_df.contract_yyyy = price_df.contract_yyyy.astype(int)
    price_df.contract_mm = price_df.contract_mm.astype(int)
    price_df.contract_dd = price_df.contract_dd.astype(int)

    # remove row where 'district' column have '용도미지정'
    price_df = price_df[price_df.district != '용도미지정']

    if dong != 'all':
        price_df = price_df[price_df.dong == dong]

    if district != 'all':
        price_df = price_df[price_df.district == district]

    if category != 'all':
        price_df = price_df[price_df.category == category]

    price_df = price_df.loc[:, ['district', 'category', 'area_m2', 'sale_price_1e4', 'dong', \
        'contract_yyyy', 'contract_mm', 'contract_dd']]

    price_df = price_df.sort_values(by=['contract_yyyy', 'contract_mm', 'contract_dd']).reset_index(drop=True)

    return price_df

if __name__ == "__main__":

    if len(sys.argv) != 7:
        print("#### [error] need input: 'gu' 'dong' 'from_yyyymm' 'to_yyyyymm' 'district' 'category'")
        print('[example 1] query_land_price 유성구 문지동 201701 202112 제1종일반주거지역 대')
        print('[example 2] query_land_price 세종특별자치시 조치원읍 201901 202112 all all')
        print('[example 3] query_land_price 세종특별자치시 연기면 201901 202112 all all')
        print('[example 4] query_land_price 세종특별자치시 all 201901 202112 all all')
        print('[example 5] query_land_price 서귀포시 all 202001 202112 all all')
        print('[example 6] query_land_price 제주시 all 202001 202112 all all')
        print('[example 7] query_land_price 고흥군 all 202001 202112 all all')
        sys.exit()
    
    query_type = 'land_sale'
    gu = sys.argv[1]
    dong = sys.argv[2]
    from_yyyymm = sys.argv[3]
    to_yyyymm = sys.argv[4]
    # district: '용도지역'
    district = sys.argv[5]
    # category: '지목'
    category = sys.argv[6]
    if int(to_yyyymm) - int(from_yyyymm) < 0:
        print("#### [error] 'from_yyyymm' must not be greater than 'to_yyyymm'")
        sys.exit()

    code = load_code()

    gu_code = get_gu_code(code, gu)
    if not gu_code:
        print("#### check 'gu' input")
        sys.exit()

    if dong != 'all':
        dong_code = get_dong_code(code, gu + ' ' + dong)
        if not dong_code:
            print("#### check 'dong' input")
            sys.exit()

    yyyymm_list = get_yyyymm_list(from_yyyymm, to_yyyymm)
    # base_date_list = get_base_date_list(from_year, to_year)

    items_list = []
    for base_date in yyyymm_list:
        res = get_data(land_sale_url, service_key, gu_code, base_date)
        if res.status_code == 200:
            print('.', end='')
        else:
            print('status code =', res.status_code)
        items_list += get_items(res)

    # res.close()

    price_df = pd.DataFrame(items_list)

    price_df = process_land_price_df(price_df, gu, dong, district, category)

    if price_df.empty:
        print('\n#### query result filtering output empty, check program input')
        sys.exit()

    filename = \
        '{}_{}_{}_{}_{}_{}_{}.xls'.format(query_type, gu, dong, from_yyyymm, to_yyyymm, district, category)

    price_df.to_excel(filename, index=False)
    print("\n### query result saved into file =", filename)

    sys.exit()

    study_land_price(price_df, query_type, gu, dong, from_yyyymm, to_yyyymm, district, category)
