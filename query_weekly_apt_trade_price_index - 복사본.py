
# public data portal:
# https://www.data.go.kr/data/15058352/openapi.do
# login info: id = khy716, pw = hykang8106!
#
# 데이터명 = '한국부동산원_주간아파트동향 조회 서비스'

import pandas as pd
import sys

from util_real_estate import *
from define_file_url_key import *

# this program only use 'getAptTradingPriceIndex' service: service_type_list[0]
service_type_list = ['getAptTradingPriceIndex', 'getAptTradingPriceindexSize', \
		'getAptTradingPriceindexAge', 'getAptTradingmarketTrend', 'getAptRentalMarketTrend']

'''
<response>
<header>
<resultCode>00</resultCode>
<resultMsg>NORMAL SERVICE.</resultMsg>
</header>
<body>
<item>
<regionCd>11000</regionCd>
<regionNm>서울</regionNm>
<contractType>매매</contractType>
<rsRow>20180805,105.7|20180812,105.7|20180819,105.7|20180826,105.7</rsRow>
</item>
</body>
</response>
'''

def get_week_apt_items(response):

    root = ET.fromstring(response.content)
    item_list = []
    for child in root.find('body').find('item'):
        elements = child.findall('*')
        data = {}
        for element in elements:
            tag = element.tag.strip()
            text = element.text.strip()
            # print tag, text
            data[tag] = text
        item_list.append(data)  
    return item_list

if __name__ == "__main__":

	if len(sys.argv) != 5:
		print("#### [error] need input: 'gu' 'from_yyyymmdd' 'to_yyyyymmdd' 'contract_type'")
		print('[example 1] query_weekly_apt_trade_price_index 유성구 20200101 20211201 S')
		sys.exit()

	gu = sys.argv[1]
	from_yyyymmdd = sys.argv[2]
	to_yyyymmdd = sys.argv[3]
	contract_type = sys.argv[4]
	if not contract_type in ['S', 'D']:
		print("#### 'contract type' must be one of 'S', 'D'")
		print("#### 'S' = '매매', 'D' = '전세'")
		sys.exit()
		
	code = load_code()

	gu_code = get_gu_code(code, gu)
	if not gu_code:
		print("#### check 'gu' input")
		sys.exit()

	msg = weekly_apt_trend_url + '/' + service_type_list[0] + '?' + 'startdate=' + from_yyyymmdd + \
		'&' + 'enddate=' + to_yyyymmdd + '&' + 'region=' + gu_code + '&' + \
		'contractType=' + contract_type + '&' + 'serviceKey=' + service_key

	response = requests.get(msg)
	# print(response.content)

	items = get_week_apt_items(response)
	print(items)
