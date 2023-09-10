""" 
[branch: change_cmd_arg]

commit [1] message

(1) change command argument:
"""

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

# 용도지역
use_area_list = ['개발제한구역', '자연녹지지역', '준주거지역', '제2종일반주거지역', '제1종일반주거지역', \
    '일반상업지역', '준공업지역', '용도미지정', '보전녹지지역', '제1종전용주거지역', '계획관리지역', \
    '농림지역', '생산관리지역']

# 지목
land_purpose_list = ['도로', '답', '대', '전', '임야', '주차장', '창고용지', '괴수원', '하천', \
    '유지', '잡종지', '학교용지', '공장용지', '묘지', '제방', '구거']

help_message = \
    """ 
    #### [input] 'metro' 'gu' 'from_yyyymm' 'to_yyyyymm' 'dong' 'use_area' 'land_purpose'
    #### 'metro' : 서울, 부산, 광역시, 도, 제주, 세종
    #### 'gu' : 구, 시, 군, 세종
    #### 'from_yyyymm' : 시작월, yyyymm
    #### 'to_yyyyymm' : 종료월, yyyymm
    #### 'dong' : 법정동, 읍, 면 (예: 행당동, 반곡동, 조치원읍, 금남면)
    #### 'use_area' : 용도지역 (예: 개발제한구역, 자연녹지지역, 준주거지역, 제2종일반주거지역, 제1종일반주거지역,
    #### 일반상업지역, 준공업지역, 용도미지정, 보전녹지지역, 제1종전용주거지역, 계획관리지역, 농림지역, 생산관리지역)
    #### 'land_purpose' : 지목 (예: 도로, 답, 대, 전, 임야, 주차장, 창고용지, 괴수원, 하천, 유지, 잡종지, 
    #### 학교용지, 공장용지, 묘지, 제방, 구거)

    [example] query_land_price 대전 유성구 201701 202112 문지동 제1종일반주거지역 대
    [example] query_land_price 세종 세종 201901 202112 조치원읍
    [example] query_land_price 세종 세종 201901 202112 연기면
    [example] query_land_price 강원도 춘천시 201901 202112
    [example] query_land_price 세종 세종 201901 202112
    [example] query_land_price 제주 서귀포시 202001 202112
    [example] query_land_price 제주 제주시 202001 202112
    [example] query_land_price 전라남도 고흥군 202001 202112
    """

if __name__ == "__main__":

    if len(sys.argv) < 5:
        print(help_message)
        sys.exit()
    
    metro = sys.argv[1]
    gu = sys.argv[2]
    from_yyyymm = sys.argv[3]
    to_yyyymm = sys.argv[4]

    if int(to_yyyymm) - int(from_yyyymm) < 0:
        print("#### [error] 'from_yyyymm' must not be greater than 'to_yyyymm'")
        sys.exit()

    dong = ''
    use_area ='' 
    land_purpose = ''
    if len(sys.argv) == 6:
        dong = sys.argv[5]

    if len(sys.argv) == 7:
        dong = sys.argv[5]
        use_area = sys.argv[6] # 용도지역

    if len(sys.argv) == 8:
        dong = sys.argv[5]
        use_area = sys.argv[6]
        land_purpose = sys.argv[7] # 지목

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

    if use_area and (not use_area in use_area_list):
        print("#### check 'use_area' input")
        sys.exit()

    if land_purpose and (not land_purpose in land_purpose_list):
        print("#### check 'land_purpose' input")
        sys.exit()

    yyyymm_list = get_yyyymm_list(from_yyyymm, to_yyyymm)

    items_list = []
    for base_date in yyyymm_list:
        res = get_data(land_sale_url, service_key, gu_code, base_date)
        if res.status_code == 200:
            print('.', end='')
        else:
            print('status code =', res.status_code)
        items_list += get_items(res)

    price_df = pd.DataFrame(items_list)

    price_df = process_land_sale(price_df, dong, use_area, land_purpose)

    if price_df.empty:
        print('\n#### query result filtering output empty, check program input')
        sys.exit()

    if not os.path.isdir(query_result_folder):
        os.mkdir(query_result_folder)

    if len(sys.argv) == 5:
        filename = '토지매매_{}_{}_{}_{}.xls'.\
            format(metro, gu, from_yyyymm, to_yyyymm)
    if len(sys.argv) == 6:
        filename = '토지매매_{}_{}_{}_{}_{}.xls'.\
            format(metro, gu, from_yyyymm, to_yyyymm, dong)
    if len(sys.argv) == 7:
        filename = '토지매매_{}_{}_{}_{}_{}_{}.xls'.\
            format(metro, gu, from_yyyymm, to_yyyymm, dong, use_area)
    if len(sys.argv) == 8:
        filename = '토지매매_{}_{}_{}_{}_{}_{}_{}.xls'.\
            format(metro, gu, from_yyyymm, to_yyyymm, dong, use_area, land_purpose)

    filename = os.path.join(query_result_folder, filename)
    price_df.to_excel(filename, index=False)
    print("\n### query result saved into file =", filename)

    # sys.exit()

    # study_land_price(price_df, query_type, gu, dong, from_yyyymm, to_yyyymm, district, category)
