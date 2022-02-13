
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

	root = ET.fromstring(response.text)
	# root = ET.fromstring(response.content)

	'''
	header_list = []
	for child in root.find('header'):
		data = {}
		tag = child.tag.strip()
		text = child.text.strip()
		data[tag] = text
		# print(data)
			
		header_list.append(data)

	# header_list: list of dict, 
	# example = [{'resultCode': '00'}, {'resultMsg': 'NORMAL SERVICE.'}]
	result_code = header_list[0]['resultCode']
	if result_code != '00':
		print('service result code =', result_code)
		print(response.text)
		sys.exit()
	
	'''

	# below not working
	# print(root.header.resultCode.text)

	item_list = []
	for child in root.find('body').find('item'):
		data = {}
		tag = child.tag.strip()
		text = child.text.strip()
		data[tag] = text

		item_list.append(data)

	return item_list

def get_result_code(response):

	root = ET.fromstring(response.text)

	header_list = []
	for child in root.find('header'):
		data = {}
		tag = child.tag.strip()
		text = child.text.strip()
		data[tag] = text
		# print(data)
			
		header_list.append(data)

	# header_list: list of dict, 
	# example = [{'resultCode': '00'}, {'resultMsg': 'NORMAL SERVICE.'}]
	result_code = header_list[0]['resultCode']

	return result_code

# result: list of dict
# example: [{'contractType': '매매'}, {'regionCd': '30200'}, {'regionNm': '유성구'}, \
# {'rsRow': '20200106,74.58|20200113,74.98|20200120,75.53|20200127,76.01|20200203,76.18|20200210,76.47|20200217,76.91'}]

def get_apt_price_index(result):

	contract_type = result[0]['contractType']
	region_code = result[1]['regionCd']
	region_name = result[2]['regionNm']
	apt_price_index = result[3]['rsRow']

	data = [api.split(',') for api in apt_price_index.split('|')]
	api_df = pd.DataFrame(data, columns=['dates', 'price_index'])
	api_df.price_index = api_df.price_index.astype(float)
	api_df.dates = pd.to_datetime(api_df.dates, format='%Y%m%d')
	# api_df.set_index('dates')

	return contract_type, region_code, region_name, apt_price_index, api_df

def query_weekly_apt_trade_price_index(gu, from_yyyymmdd, to_yyyymmdd, contract):

	if contract == '매매':
		contract_type = 'S'
	else:
		contract_type = 'D'
	print('contract =', contract_type)
		
	code = load_code()

	gu_code = get_gu_code(code, gu)
	if not gu_code:
		print("#### check 'gu' input")
		sys.exit()

	msg = weekly_apt_trend_url + '/' + service_type_list[0] + '?' + 'startdate=' + from_yyyymmdd + \
		'&' + 'enddate=' + to_yyyymmdd + '&' + 'region=' + gu_code + '&' + \
		'contractType=' + contract_type + '&' + 'serviceKey=' + service_key
	# print(msg)

	response = requests.get(msg)
	if response.status_code != 200:
		print('response status code =', response.status_code)
		sys.exit()
	# print(response.content)

	result_code = get_result_code(response)
	if result_code != '00':
		print(msg)
		print('service result code =', result_code)
		print(response.text)
		sys.exit()

	result = get_week_apt_items(response)

	# print(result)
	contract_type, region_code, region_name, apt_price_index, api_df = get_apt_price_index(result)
	print(contract_type, region_code, region_name)
	# print(apt_price_index)

	return api_df

if __name__ == "__main__":

	if len(sys.argv) != 5:
		print("#### [error] need input: 'gu' 'from_yyyymmdd' 'to_yyyyymmdd' 'contract'")
		print('[example 1] query_weekly_apt_trade_price_index 유성구 20200101 20211201 매매')
		print('[example 2] query_weekly_apt_trade_price_index 유성구 20200101 20211201 전세')
		print('[example 3] query_weekly_apt_trade_price_index all 20200101 20211201 매매')
		sys.exit()

	gu = sys.argv[1]
	from_yyyymmdd = sys.argv[2]
	to_yyyymmdd = sys.argv[3]
	contract = sys.argv[4]
	if not contract in ['매매', '전세']:
		print("#### 'contract' must be one of '매매', '전세'")
		sys.exit()

	if gu == 'all':
		all_gu_filename = 'all_gu_apt_price_index.xls'
		# read gu from 'all' define file
		pd.read_excel(all_gu_filename)

	else:
		api_df = query_weekly_apt_trade_price_index(gu, from_yyyymmdd, to_yyyymmdd, contract)
	
	'''
	if contract == '매매':
		contract_type = 'S'
	else:
		contract_type = 'D'
	print('contract =', contract_type)
		
	code = load_code()

	gu_code = get_gu_code(code, gu)
	if not gu_code:
		print("#### check 'gu' input")
		sys.exit()

	msg = weekly_apt_trend_url + '/' + service_type_list[0] + '?' + 'startdate=' + from_yyyymmdd + \
		'&' + 'enddate=' + to_yyyymmdd + '&' + 'region=' + gu_code + '&' + \
		'contractType=' + contract_type + '&' + 'serviceKey=' + service_key
	# print(msg)

	response = requests.get(msg)
	if response.status_code != 200:
		print('response status code =', response.status_code)
		sys.exit()
	# print(response.content)

	result_code = get_result_code(response)
	if result_code != '00':
		print(msg)
		print('service result code =', result_code)
		print(response.text)
		sys.exit()

	result = get_week_apt_items(response)

	# print(result)
	contract_type, region_code, region_name, apt_price_index, api_df = get_apt_price_index(result)
	print(contract_type, region_code, region_name)
	# print(apt_price_index)
	'''
