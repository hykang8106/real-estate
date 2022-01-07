
# [ref] https://kosis.kr/openapi/mypage/myPage_01List.jsp
# id = khy716, pw = uresj38106!
#
# 기관명 = '한국부동산원'
# 기관코드 = '408'
# 통계표명 = '유형별 주택매매가격지수(2011.6=100)'
# 통계표ID = 'DT_304N_04_00001'
# 통계조사명 = '전국주택가격동향조사'

#######################################################
# not coded: as of 211227
#######################################################

import requests
import pandas as pd
import sys

# seoul first gu
url = 'https://kosis.kr/openapi/statisticsData.do?method=getList&apiKey=NDZiMWYyNjU3YzE4Zjk1MmU5MzhhNDQ2NTg3NTFkZjQ=&format=json&jsonVD=Y&userStatsId=khy716/408/DT_304N_04_00001/2/1/20211227095323_1&prdSe=M&startPrdDe=201106&endPrdDe=201212'
# seoul last gu
url = 'https://kosis.kr/openapi/statisticsData.do?method=getList&apiKey=NDZiMWYyNjU3YzE4Zjk1MmU5MzhhNDQ2NTg3NTFkZjQ=&format=json&jsonVD=Y&userStatsId=khy716/408/DT_304N_04_00001/2/1/20211227095323_25&prdSe=M&startPrdDe=201106&endPrdDe=201212'

# daejeon yuseong gu
url = 'https://kosis.kr/openapi/statisticsData.do?method=getList&apiKey=NDZiMWYyNjU3YzE4Zjk1MmU5MzhhNDQ2NTg3NTFkZjQ=&format=json&jsonVD=Y&userStatsId=khy716/408/DT_304N_04_00001/2/1/20211227095323_27&prdSe=M&startPrdDe=201106&endPrdDe=201212'





# service_key = 'NDZiMWYyNjU3YzE4Zjk1MmU5MzhhNDQ2NTg3NTFkZjQ='

'''
 {'TBL_NM': '지역별 전월세전환율',
  'PRD_DE': '202109',
  'TBL_ID': 'DT_30404_N0010',
  'ITM_NM': '지역별 전월세전환율',
  'ITM_ID': 'T1',
  'UNIT_NM': '%',
  'ORG_ID': '408',
  'UNIT_NM_ENG': '%',
  'C1_OBJ_NM': '주택유형별',
  'C1_OBJ_NM_ENG': 'Type',
  'C2_OBJ_NM': '지역별',
  'C2_OBJ_NM_ENG': 'Region',
  'DT': '4.603118476',
  'PRD_SE': 'M',
  'C2': 'a1204',
  'C1': '01',
  'C1_NM': '아파트',
  'C2_NM': '유성',
  'C1_NM_ENG': 'Apartments'}
'''

def extract_conv_rate(conv):

   yyyymm = conv.PRD_DE.astype(int)
   conv_rate = conv.DT.astype(float)

   return yyyymm, conv_rate

if len(sys.argv) != 3:
   print("#### [error] need 'start_date', 'end_date' input")
   print("[example] query_rent_conv_rate 201611 202109")
   sys.exit()

start_date = sys.argv[1]
end_date = sys.argv[2]
duration_date = 'startPrdDe=' + start_date + '&' + 'endPrdDe=' + end_date

sejong_apt_rent_conv_rate_url = \
   'https://kosis.kr/openapi/statisticsData.do?method=getList&apiKey=NDZiMWYyNjU3YzE4Zjk1MmU5MzhhNDQ2NTg3NTFkZjQ=&format=json&jsonVD=Y&userStatsId=khy716/408/DT_30404_N0010/2/1/20211226142357_2&prdSe=M&' + duration_date

yuseong_apt_rent_conv_rate_url = \
   'https://kosis.kr/openapi/statisticsData.do?method=getList&apiKey=NDZiMWYyNjU3YzE4Zjk1MmU5MzhhNDQ2NTg3NTFkZjQ=&format=json&jsonVD=Y&userStatsId=khy716/408/DT_30404_N0010/2/1/20211226175544_1&prdSe=M&' + duration_date

sejong_single_rent_conv_rate_url = \
   'https://kosis.kr/openapi/statisticsData.do?method=getList&apiKey=NDZiMWYyNjU3YzE4Zjk1MmU5MzhhNDQ2NTg3NTFkZjQ=&format=json&jsonVD=Y&userStatsId=khy716/408/DT_30404_N0010/2/1/20211226183637_2&prdSe=M&' + duration_date

daejeon_single_rent_conv_rate_url = \
   'https://kosis.kr/openapi/statisticsData.do?method=getList&apiKey=NDZiMWYyNjU3YzE4Zjk1MmU5MzhhNDQ2NTg3NTFkZjQ=&format=json&jsonVD=Y&userStatsId=khy716/408/DT_30404_N0010/2/1/20211226183637_1&prdSe=M&' + duration_date

'''
sejong_apt_rent_conv_rate_url = \
   'https://kosis.kr/openapi/statisticsData.do?method=getList&apiKey=NDZiMWYyNjU3YzE4Zjk1MmU5MzhhNDQ2NTg3NTFkZjQ=&format=json&jsonVD=Y&userStatsId=khy716/408/DT_30404_N0010/2/1/20211226142357_2&prdSe=M&startPrdDe=201611&endPrdDe=202109'

yuseong_apt_rent_conv_rate_url = \
   'https://kosis.kr/openapi/statisticsData.do?method=getList&apiKey=NDZiMWYyNjU3YzE4Zjk1MmU5MzhhNDQ2NTg3NTFkZjQ=&format=json&jsonVD=Y&userStatsId=khy716/408/DT_30404_N0010/2/1/20211226175544_1&prdSe=M&startPrdDe=201611&endPrdDe=202109'

sejong_single_rent_conv_rate_url = \
   'https://kosis.kr/openapi/statisticsData.do?method=getList&apiKey=NDZiMWYyNjU3YzE4Zjk1MmU5MzhhNDQ2NTg3NTFkZjQ=&format=json&jsonVD=Y&userStatsId=khy716/408/DT_30404_N0010/2/1/20211226183637_2&prdSe=M&startPrdDe=201611&endPrdDe=202109'

daejeon_single_rent_conv_rate_url = \
   'https://kosis.kr/openapi/statisticsData.do?method=getList&apiKey=NDZiMWYyNjU3YzE4Zjk1MmU5MzhhNDQ2NTg3NTFkZjQ=&format=json&jsonVD=Y&userStatsId=khy716/408/DT_30404_N0010/2/1/20211226183637_1&prdSe=M&startPrdDe=201611&endPrdDe=202109'
'''

url_list = [sejong_apt_rent_conv_rate_url, yuseong_apt_rent_conv_rate_url, \
   sejong_single_rent_conv_rate_url, daejeon_single_rent_conv_rate_url]

conv_rate_table = pd.DataFrame()

for count, url in enumerate(url_list):
   res = requests.get(url)
   data = res.json()
   conv = pd.DataFrame(data)
   yyyymm, conv_rate = extract_conv_rate(conv)
   conv_rate_table[0] = yyyymm
   conv_rate_table[count + 1] = conv_rate

conv_rate_table.columns=['yyyymm', 'apt_sejong', 'apt_yuseong', 'single_sejong', 'single_daejeon']

filename = 'rent_conv_rate_{}_{}.xls'.format(start_date, end_date)
conv_rate_table.to_excel(filename, index=False)
