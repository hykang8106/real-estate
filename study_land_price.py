
# 용도지역:
# (1) 도시지역
# (1.1) 주거지역
# (1.1.1) 제1종일반주거지역 
# (1.1.6) ...
# (1.2) 상업지역
# (1.2.1) 일반상업지역
# (1.2.4) ...
# (1.3) 공업지역
# (1.3.1) 준공업지역
# (1.3.3) ...
# (1.4) 녹지지역
# (1.4.1) 보전녹지지역
# (1.4.2) 생산녹지지역
# (1.4.3) 자연녹지지역
# (2) 관리지역
# (2.1) 보전관리지역
# (2.2) 생산관리지역
# (2.3) 계획관리지역
# (3) 농림지역
# (4) 자연환경보전지역
#
# 용도구역: (1) 개발제한구역, (2) 도시자원공원구역, (3) ...
#
# 용도지구: (1) 경관지구, (2) 고도지구, (3) ...
#
# 지목: (1) 대, (2) 전, (3) 답, (4) 임야, (5) 과수원, (28) ...
#

import re, os, sys
import pandas as pd
import numpy as np

import datetime as dt
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import drange
from matplotlib.ticker import NullFormatter
from matplotlib.dates import MonthLocator, DateFormatter

from study_real_estate_price import *

district_input_dict = {'0':'농림지역', '1':'계획관리지역', '2':'개발제한구역', '3':'자연녹지지역'}

category_input_dict = {'0':'전', '1':'답', '2':'임야', '3':'대'}

'''

def compute_rent_price_per_m2(price_df, conv_rate_table, conv_rate_col):

	row_len = price_df.shape[0]
	# print(row_len)
	price_per_m2 = np.zeros(row_len)
	for n in range(row_len):
		if price_df.iloc[n].month_rent_1e4 == 0:
			price_per_m2[n] = price_df.deposit_rent_1e4[n] / price_df.area_m2[n]
			# print('do', n, price_per_m2[n])
		else:
			yyyymm = int(price_df.contract_yyyy[n] * 100 + price_df.contract_mm[n])
			rent_conv_rate = get_rent_conv_rate(yyyymm, conv_rate_table, conv_rate_col)
			# print(rent_conv_rate)
			conv_deposit_rent_1e4 = price_df.deposit_rent_1e4[n] + \
			price_df.month_rent_1e4[n] * 12 / (rent_conv_rate / 100)
			price_per_m2[n] = conv_deposit_rent_1e4 / price_df.area_m2[n]
			# print(n, price_per_m2[n])

	return price_per_m2
'''

def get_param_from_land_filename(file_name):

	filename, file_extension = os.path.splitext(file_name)

	# get parameter from filename
	# file name example = 'land_sale_유성구_문지동_201701_202112_제1종일반주거지역_대'
	param_list = re.split('_', filename)

	param_len = len(param_list)
	if param_len == 8:
		query_type = param_list[0] + '_' + param_list[1]
		gu = param_list[2]
		dong = param_list[3]
		from_yyyymm = param_list[4]
		to_yyyymm = param_list[5]
		district = param_list[6]
		category = param_list[7]
	else:
		print('filename error')
		sys.exit()

	return query_type, gu, dong, from_yyyymm, to_yyyymm, district, category

'''
def make_x_axis_date(price_df):

	row_len = price_df.shape[0]
	x_date = []
	for n in range(row_len):
		dates = dt.date(price_df.contract_yyyy.values[n], price_df.contract_mm.values[n], price_df.contract_dd.values[n])
		x_date.append(dates)

	return x_date
'''

def plot_land_price_per_m2(x_date, price_per_m2, moving_average, gu, dong, district, category):

	plt.figure()
	if len(moving_average) == 0:
		plt.plot_date(x_date, price_per_m2, '-')
	else:
		plt.plot_date(x_date, np.stack((price_per_m2, moving_average), axis=-1), '-')
	title_str = '[{} {} {} {}] '.format(gu, dong, district, category)

	plt.title(title_str + '토지 매매 가격 (제곱미터 당)')
	# plt.title('deposit rent price per m2')
	plt.xlabel('거래일')
	# plt.xlabel('transaction date')
	# plt.ylabel('1e4 KRW')
	plt.ylabel('단위: 만원')
	plt.grid(True)
	if len(moving_average) != 0:
		plt.legend(['not MA', 'MA(30 days)'])
	plt.show(block=False)

	return

'''
def compute_moving_average(price_per_m2, x_date):

	# estimate moving averaging window size(=N) which is equivalent to 30 days(1 month)
	delta_day = [d.days for d in np.diff(x_date)]
	average_delta_day = sum(delta_day) / len(delta_day)
	N = round(30 / average_delta_day)
	print('moving average window =', N)

	# compute moving average
	moving_average = pd.Series(price_per_m2).rolling(N).mean().values

	return moving_average

def get_transact_count(yyyymm_df, price_df):

	yyyymm_df = yyyymm_df.set_index(['contract_yyyy', 'contract_mm'])
	# print(yyyymm_df)

	price_df = price_df.groupby(by=['contract_yyyy', 'contract_mm']).size().reset_index(name='counts')
	price_df = price_df.set_index(['contract_yyyy', 'contract_mm'])
	# print(di)

	for n in price_df.index:
		yyyymm_df.at[n, 'counts'] = price_df.at[n, 'counts']

	return yyyymm_df.counts.values

def plot_rent_transaction_count_per_month(price_df, query_type, gu, dong, apt):

	date_list, yyyymm_df = make_x_axis_yyyymm_bar(price_df)

	deposit_df = price_df[price_df.month_rent_1e4 == 0]
	# deposit_df = price_df.loc[price_df.month_rent_1e4 == 0]
	deposit_count = get_transact_count(yyyymm_df, deposit_df)

	month_df = price_df[price_df.month_rent_1e4 != 0]
	# month_df = price_df.loc[price_df.month_rent_1e4 != 0]
	month_count = get_transact_count(yyyymm_df, month_df)

	width = 15
	plt.figure()
	plt.bar(date_list, deposit_count, width, label='전세')
	plt.bar(date_list, month_count, width, bottom=deposit_count, label='전월세')

	ax = plt.gca()
	ax.xaxis.set_major_locator(MonthLocator(bymonth=(1,7)))
	# ax.xaxis.set_major_locator(MonthLocator(bymonth=(1, 7)))
	ax.xaxis.set_minor_locator(MonthLocator())
	ax.xaxis.set_major_formatter(DateFormatter('\'%y-%m'))
	# ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
	ax.xaxis.set_minor_formatter(NullFormatter())
	# ax.xaxis.set_minor_formatter(DateFormatter('%b'))

	plt.xlabel('거래년월')
	plt.ylabel('건수')

	if apt:
		title_str = '[{} {} {}] '.format(gu, dong, apt)
	else:
		title_str = '[{} {}] '.format(gu, dong)

	if query_type == 'single_rent':
		plt.title(title_str + '다가구 주택 월별 전세 거래 건수')
	elif query_type == 'apt_rent':
		plt.title(title_str + '아파트 월별 전세 거래 건수')
	# plt.title('월별 전세 거래 건수')
	plt.grid(True)
	plt.legend()
	plt.show(block=False)

	return

def plot_sale_transaction_count_per_month(price_df, query_type, gu, dong, apt):

	date_list, yyyymm_df = make_x_axis_yyyymm_bar(price_df)

	sale_count = get_transact_count(yyyymm_df, price_df)

	width = 15
	plt.figure()
	plt.bar(date_list, sale_count, width)
	# plt.bar(date_list, sale_count, width, label='전세')
	ax = plt.gca()
	ax.xaxis.set_major_locator(MonthLocator(bymonth=(1,7)))
	ax.xaxis.set_minor_locator(MonthLocator())
	ax.xaxis.set_major_formatter(DateFormatter('\'%y-%m'))
	# ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
	ax.xaxis.set_minor_formatter(NullFormatter())

	plt.xlabel('거래년월')
	plt.ylabel('건수')

	if apt:
		title_str = '[{} {} {}] '.format(gu, dong, apt)
	else:
		title_str = '[{} {}] '.format(gu, dong)

	if query_type == 'single_sale':
		plt.title(title_str + '다가구 주택 월별 매매 거래 건수')
	elif query_type == 'apt_sale':
		plt.title(title_str + '아파트 월별 매매 거래 건수')

	plt.grid(True)
	# plt.legend()
	plt.show(block=False)

	return

def make_x_axis_yyyymm_bar(price_df):

	from_yyyy = price_df.iloc[0]['contract_yyyy']
	from_mm = price_df.iloc[0]['contract_mm']
	to_yyyy = price_df.iloc[-1]['contract_yyyy']
	to_mm = price_df.iloc[-1]['contract_mm']

	from_date = str(int(from_yyyy * 10000 + from_mm * 100 + 1))
	to_date = str(int(to_yyyy * 10000 + to_mm * 100 + 1))
	date_list = pd.date_range(start=from_date, end=to_date, freq='MS')

	yyyymm_df = pd.DataFrame(columns=['contract_yyyy', 'contract_mm', 'counts'])
	yyyymm_df.contract_yyyy = [d.year for d in date_list]
	yyyymm_df.contract_mm = [d.month for d in date_list]
	yyyymm_df.counts = 0

	return date_list, yyyymm_df

def plot_area_histogram(price_df, query_type, gu, dong, apt):

	if query_type == 'single_sale':
		dist = price_df.build_area_m2.values
	else:
		dist = price_df.area_m2.values

	if apt:
		title_str = '[{} {} {}] '.format(gu, dong, apt)
	else:
		title_str = '[{} {}] '.format(gu, dong)

	n_bins = 20

	plt.figure()
	plt.hist(dist)
	# plt.hist(dist1, bins=n_bins)
	plt.xlabel('면적 (m2)')
	plt.ylabel('건수')

	if query_type == 'single_sale':
		plt.title(title_str + '다가구 주택 매매 면적 분포')
	elif query_type == 'apt_sale':
		plt.title(title_str + '아파트 매매 면적 분포')
	elif query_type == 'apt_rent':
		plt.title(title_str + '아파트 전세 면적 분포')
	elif query_type == 'single_rent':
		plt.title(title_str + '다가구 주택 전세 면적 분포')

	plt.grid(True)
	# plt.legend()
	plt.show(block=False)

	return
'''

def user_promt_select_item(item_dict):

	user_input = input(str(item_dict) + '\n==> ')
	if not user_input:
		selection = 'all'
	else:
		selection = item_dict[user_input]

	return selection

def user_promt_select_district():

	user_input = input(str(district_input_dict) + '\n==> ')
	if not user_input:
		district = 'all'
	else:
		district = district_input_dict[user_input]

	return district

def user_promt_select_category():

	user_input = input(str(category_input_dict) + '\n==> ')
	if not user_input:
		category = 'all'
	else:
		category = category_input_dict[user_input]

	return district

def study_land_price(price_df, query_type, gu, dong, from_yyyymm, to_yyyymm, district, category):

	if (dong != 'all') & (district != 'all') & (category != 'all'):

		price_per_m2 = price_df.sale_price_1e4.values / price_df.area_m2.values
		print(len(price_per_m2))

		x_date = make_x_axis_date(price_df)

		moving_average = compute_moving_average(price_per_m2, x_date)

		plot_land_price_per_m2(x_date, price_per_m2, moving_average, gu, dong, district, category)

		return
	
	if district == 'all':

		district = user_promt_select_item(district_input_dict)

	if district == 'all':

		gb = price_df.groupby('district')
		gb_df = [gb.get_group(x).reset_index(drop=True) for x in gb.groups]
		print(gb_df[0])

		average_price_m2 = \
			pd.DataFrame(columns=['district', 'average_price_per_m2', 'std_price_per_m2', \
				'transaction_count'])

		for i, df in enumerate(gb_df):
			average_price_m2.at[i, 'district'] = df.at[0, 'district']
			average_price_m2.at[i, 'average_price_per_m2'] = \
				np.average(df.sale_price_1e4.values / df.area_m2.values)
			average_price_m2.at[i, 'std_price_per_m2'] = \
				np.std(df.sale_price_1e4.values / df.area_m2.values)
			average_price_m2.at[i, 'transaction_count'] = len(df.index)
		
		average_price_m2['transaction_percent'] = \
			average_price_m2['transaction_count'] / sum(average_price_m2['transaction_count'].values) * 100

		filename = 'land_sale_per_district_{}_{}_{}_{}_{}_{}.xls'.\
			format(gu, dong, from_yyyymm, to_yyyymm, district, category)
		average_price_m2.to_excel(filename, index=False, float_format='%.3f')

	if district != 'all':

		price_df = price_df[price_df.district == district].reset_index(drop=True)
		print(price_df)

	if category == 'all':

		category = user_promt_select_item(category_input_dict)

	if category == 'all':

		gb = price_df.groupby('category')
		gb_df = [gb.get_group(x).reset_index(drop=True) for x in gb.groups]
		print(gb_df[0])

		average_price_m2 = \
			pd.DataFrame(columns=['category', 'average_price_per_m2', 'std_price_per_m2', \
				'transaction_count'])

		for i, df in enumerate(gb_df):
			average_price_m2.at[i, 'category'] = df.at[0, 'category']
			average_price_m2.at[i, 'average_price_per_m2'] = \
				np.average(df.sale_price_1e4.values / df.area_m2.values)
			average_price_m2.at[i, 'std_price_per_m2'] = \
				np.std(df.sale_price_1e4.values / df.area_m2.values)
			average_price_m2.at[i, 'transaction_count'] = len(df.index)
		
		average_price_m2['transaction_percent'] = \
			average_price_m2['transaction_count'] / sum(average_price_m2['transaction_count'].values) * 100

		filename = 'land_sale_per_category_{}_{}_{}_{}_{}_{}.xls'.\
			format(gu, dong, from_yyyymm, to_yyyymm, district, category)
		average_price_m2.to_excel(filename, index=False, float_format='%.3f')

	if category != 'all':

		price_df = price_df[price_df.category == category].reset_index(drop=True)
		print(price_df)

		price_per_m2 = price_df.sale_price_1e4.values / price_df.area_m2.values
		print(len(price_per_m2))

		x_date = make_x_axis_date(price_df)

		moving_average = compute_moving_average(price_per_m2, x_date)

		plot_land_price_per_m2(x_date, price_per_m2, moving_average, gu, dong, district, category)

		filename = 'land_sale_{}_{}_{}_{}_{}_{}.xls'.\
			format(gu, dong, from_yyyymm, to_yyyymm, district, category)
		price_df.to_excel(filename, index=False)

	if dong == 'all':

		gb = price_df.groupby('dong')
		gb_df = [gb.get_group(x).reset_index(drop=True) for x in gb.groups]
		print(gb_df[0])

		average_price_m2 = \
			pd.DataFrame(columns=['dong', 'average_price_per_m2', 'std_price_per_m2', \
				'transaction_count'])

		for i, df in enumerate(gb_df):
			average_price_m2.at[i, 'dong'] = df.at[0, 'dong']
			average_price_m2.at[i, 'average_price_per_m2'] = \
				np.average(df.sale_price_1e4.values / df.area_m2.values)
			average_price_m2.at[i, 'std_price_per_m2'] = \
				np.std(df.sale_price_1e4.values / df.area_m2.values)
			average_price_m2.at[i, 'transaction_count'] = len(df.index)
		
		average_price_m2['transaction_percent'] = \
			average_price_m2['transaction_count'] / sum(average_price_m2['transaction_count'].values) * 100

		filename = 'land_sale_per_dong_{}_{}_{}_{}_{}_{}.xls'.\
			format(gu, dong, from_yyyymm, to_yyyymm, district, category)
		average_price_m2.to_excel(filename, index=False, float_format='%.3f')

	return price_df

if __name__ == "__main__":

	file_name_list = ['land_sale_유성구_문지동_201701_202112_제1종일반주거지역_대.xls', \
	'land_sale_세종특별자치시_all_201901_202112_all_all.xls', \
	'land_sale_세종특별자치시_all_202001_202112_all_all.xls', \
	'land_sale_금산군_all_202001_202112_all_all.xls', \
	'land_sale_고흥군_all_202001_202112_all_all.xls', \
	'land_sale_공주시_all_202001_202112_all_all.xls', \
	'land_sale_제주시_all_202001_202112_all_all.xls', \
	'land_sale_서귀포시_all_202001_202112_all_all.xls']

	if len(sys.argv) != 2:
		print('### [error] need integer input to select file')
		print('[example] study_land_price 0')
		sys.exit()

	idx = int(sys.argv[1])
	file_name = file_name_list[idx]

	price_df = pd.read_excel(file_name)

	query_type, gu, dong, from_yyyymm, to_yyyymm, district, category = \
		get_param_from_land_filename(file_name)
	print(query_type, gu, dong, from_yyyymm, to_yyyymm, district, category)

	price_df = \
		study_land_price(price_df, query_type, gu, dong, from_yyyymm, to_yyyymm, district, category)

'''
	 price_per_m2, price_df, x_date = \
		  study_real_estate_price(file_name_list[idx], rent_conv_rate_filename)
'''

'''
	if query_type == 'single_rent':
	if conv_rate_col:
		price_per_m2 = compute_rent_price_per_m2(price_df, conv_rate_table, conv_rate_col)

		x_date = make_x_axis_date(price_df)
	else:
		# rent conversion rate not available,
		# so extract row where month rent is 0(deposit only rent)
		deposit_only_df = price_df.loc[price_df.month_rent_1e4 == 0]
		price_per_m2 = deposit_only_df.deposit_rent_1e4.values / deposit_only_df.area_m2.values

		x_date = make_x_axis_date(deposit_only_df)

	moving_average = compute_moving_average(price_per_m2, x_date)
	plot_price_per_m2(x_date, price_per_m2, moving_average, query_type, gu, dong, apt)

	plot_rent_transaction_count_per_month(price_df, query_type, gu, dong, apt)

	plot_area_histogram(price_df, query_type, gu, dong, apt)

	elif query_type == 'single_sale':
	price_per_m2 = price_df.sale_price_1e4.values / price_df.build_area_m2.values

	x_date = make_x_axis_date(price_df)

	moving_average = compute_moving_average(price_per_m2, x_date)
	plot_price_per_m2(x_date, price_per_m2, moving_average, query_type, gu, dong, apt)

	plot_sale_transaction_count_per_month(price_df, query_type, gu, dong, apt)

	plot_area_histogram(price_df, query_type, gu, dong, apt)

	elif query_type == 'apt_rent':
	if conv_rate_col:
		price_per_m2 = compute_rent_price_per_m2(price_df, conv_rate_table, conv_rate_col)

		x_date = make_x_axis_date(price_df)
	else:
		# rent conversion rate not available,
		# so extract row where month rent is 0(deposit only rent)
		deposit_only_df = price_df.loc[price_df.month_rent_1e4 == 0]
		price_per_m2 = deposit_only_df.deposit_rent_1e4.values / deposit_only_df.area_m2.values

		x_date = make_x_axis_date(deposit_only_df)

	moving_average = compute_moving_average(price_per_m2, x_date)
	plot_price_per_m2(x_date, price_per_m2, moving_average, query_type, gu, dong, apt)

	plot_rent_transaction_count_per_month(price_df, query_type, gu, dong, apt)

	plot_area_histogram(price_df, query_type, gu, dong, apt)

	elif query_type == 'apt_sale':
	price_per_m2 = price_df.sale_price_1e4.values / price_df.area_m2.values

	x_date = make_x_axis_date(price_df)

	moving_average = compute_moving_average(price_per_m2, x_date)
	plot_price_per_m2(x_date, price_per_m2, moving_average, query_type, gu, dong, apt)

	plot_sale_transaction_count_per_month(price_df, query_type, gu, dong, apt)

	plot_area_histogram(price_df, query_type, gu, dong, apt)

	return price_per_m2, price_df, x_date
'''
