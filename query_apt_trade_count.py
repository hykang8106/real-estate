
# public data portal:
# https://www.data.go.kr
# login info: id = khy716, pw = hykang8106!
#
# 데이터명 = '한국부동산원_아파트거래현황 조회 서비스'

import pandas as pd

import sys
import matplotlib
import matplotlib.pyplot as plt

from util_real_estate import *
from define_file_url_key import *

# to display korean letter in plot
# [ref] https://mirae-kim.tistory.com/14
matplotlib.rcParams['font.family']='Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus']=False

# modify as your need
# for more info, see "기술문서 아파트 거래현황 조회 서비스.docx"
region_code_dict = {'서울':'11000', '경기':'41000', '부산':'26000', \
	'대구':'27000', '인천':'28000', '광주':'29000', '대전':'30000', '울산':'31000'}

'''
<response>
<header>
<resultCode>00</resultCode>
<resultMsg>NORMALSERVICE</resultMsg>
</header>
<body>
<item>
<regionCd>11000</regionCd>
<regionNm>서울</regionNm>
<rsRow>201808,105|201808,106|201808,107|201808,108</rsRow>
</item>
</body>
</response>
'''

def get_apt_trade_count_items(response):

	root = ET.fromstring(response.text)

	item_list = []
	for child in root.find('body').find('items').find('item'):
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

def get_apt_trade_count(result, region):

	region_code = result[0]['regionCd']
	region_name = result[1]['regionNm']
	apt_trade_count = result[2]['rsRow']

	data = [atc.split(',') for atc in apt_trade_count.split('|')]
	atc_df = pd.DataFrame(data, columns=['dates', 'atc'])
	atc_df.atc = atc_df.atc.astype(int)
	atc_df.dates = pd.to_datetime(atc_df.dates, format='%Y%m')
	# api_df.set_index('dates')

	atc_df.rename(columns={'atc':region}, inplace=True)

	return region_code, region_name, apt_trade_count, atc_df

def query_apt_trade_count(region, from_yyyymm, to_yyyymm):

	region_code = region_code_dict[region]

	msg = apt_trade_count_url + 'startmonth=' + from_yyyymm + \
		'&' + 'endmonth=' + to_yyyymm + '&' + 'region=' + region_code + '&' + \
		'serviceKey=' + service_key
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

	result = get_apt_trade_count_items(response)

	# print(result)
	region_code, region_name, apt_trade_count, atc_df = get_apt_trade_count(result, region)
	print(region_code, region_name)
	# print(apt_price_index)

	return atc_df

if __name__ == "__main__":

	if len(sys.argv) != 3:
		print("#### [error] need input: 'from_yyyymm' 'to_yyyyymm'")
		print('[example] query_apt_trade_count 202001 202112')
		sys.exit()

	from_yyyymm = sys.argv[1]
	to_yyyymm = sys.argv[2]

	# atc_df = pd.DataFrame()
	for i, region in enumerate(list(region_code_dict)):
		# print(i)
		tmp_atc_df = query_apt_trade_count(region, from_yyyymm, to_yyyymm)

		if not i:
			atc_df = tmp_atc_df
		else:
			atc_df = pd.concat([atc_df, tmp_atc_df[region]], axis=1)


	filename = 'apt_trade_count_{}_{}.xls'.format(from_yyyymm, to_yyyymm)

	atc_df.to_excel(filename, index=False)
	# warning: 'dates' column in excel file have datetime format, 'yyyy-mm-dd 00:00:00' 
	# so manually change 'dates' column format to 'yyyy-mm-dd'
	print("\n### query result saved into file =", filename)

	# plt.figure()
	atc_df.plot.line(x='dates')
	plt.grid(True)
	plt.title('아파트거래건수')
	plt.show(block=False)

