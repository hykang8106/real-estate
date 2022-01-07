import re, os, sys
import pandas as pd
import numpy as np

import datetime as dt
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import drange
from matplotlib.ticker import NullFormatter
from matplotlib.dates import MonthLocator, DateFormatter

# to display korean letter in plot
# [ref] https://mirae-kim.tistory.com/14
matplotlib.rcParams['font.family']='Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus']=False

file_name_list = ['single_rent_유성구_문지동_201701_202112.xls', \
   'single_sale_유성구_문지동_201701_202112.xls', \
   'apt_rent_세종특별자치시_반곡동_수루배마을1단지_201701_202112.xls', \
   'apt_sale_세종특별자치시_반곡동_수루배마을1단지_201701_202112.xls', \
   'apt_sale_성동구_행당동_대림e-편한세상_201701_202112.xls', \
   'apt_rent_성동구_행당동_대림e-편한세상_201701_202112.xls']

rent_conv_rate_filename = 'rent_conv_rate_201611_202112.xls'


def get_rent_conv_rate(yyyymm, conv_rate_table, conv_rate_col):

   mask = conv_rate_table.yyyymm == yyyymm

   conv_rate = conv_rate_table.loc[mask, conv_rate_col].values

   return conv_rate

def compute_rent_price_per_m2(items, conv_rate_table, conv_rate_col):

   row_len = items.shape[0]
   # print(row_len)
   price_per_m2 = np.zeros(row_len)
   for n in range(row_len):
      if items.iloc[n].month_rent_1e4 == 0:
         price_per_m2[n] = items.deposit_rent_1e4[n] / items.area_m2[n]
         # print('do', n, price_per_m2[n])
      else:
         yyyymm = int(items.contract_yyyy[n] * 100 + items.contract_mm[n])
         rent_conv_rate = get_rent_conv_rate(yyyymm, conv_rate_table, conv_rate_col)
         # print(rent_conv_rate)
         conv_deposit_rent_1e4 = items.deposit_rent_1e4[n] + \
         items.month_rent_1e4[n] * 12 / (rent_conv_rate / 100)
         price_per_m2[n] = conv_deposit_rent_1e4 / items.area_m2[n]
         # print(n, price_per_m2[n])

   return price_per_m2

def get_param_from_filename(file_name):

   filename, file_extension = os.path.splitext(file_name)

   # get parameter from filename
   param_list = re.split('_', filename)

   param_len = len(param_list)
   if param_len == 6:
      query_type = param_list[0] + '_' + param_list[1]
      gu = param_list[2]
      dong = param_list[3]
      from_yyyymm = param_list[4]
      to_yyyymm = param_list[5]
      apt = ''
   elif param_len == 7:
      query_type = param_list[0] + '_' + param_list[1]
      gu = param_list[2]
      dong = param_list[3]
      apt = param_list[4]
      from_yyyymm = param_list[5]
      to_yyyymm = param_list[6]
   else:
      print('filename error')
      sys.exit()

   return query_type, gu, dong, apt, from_yyyymm, to_yyyymm

def make_x_axis_date(items):

   row_len = items.shape[0]
   x_date = []
   for n in range(row_len):
      dates = dt.date(items.contract_yyyy.values[n], items.contract_mm.values[n], items.contract_dd.values[n])
      x_date.append(dates)

   return x_date

def plot_price_per_m2(x_date, price_per_m2, moving_average, query_type, gu, dong, apt):

   plt.figure()
   plt.plot_date(x_date, np.stack((price_per_m2, moving_average), axis=-1), '-')
   if apt:
      title_str = '[{} {} {}] '.format(gu, dong, apt)
   else:
      title_str = '[{} {}] '.format(gu, dong)

   if query_type == 'single_rent':
      plt.title(title_str + '다가구 주택 전세 가격 (제곱미터 당)')
   elif query_type == 'apt_rent':
      plt.title(title_str + '아파트 전세 가격 (제곱미터 당)')
   elif query_type == 'single_sale':
      plt.title(title_str + '다가구 주택 매매 가격 (제곱미터 당)')
   elif query_type == 'apt_sale':
      plt.title(title_str + '아파트 매매 가격 (제곱미터 당)')
   # plt.title('deposit rent price per m2')
   plt.xlabel('거래일')
   # plt.xlabel('transaction date')
   # plt.ylabel('1e4 KRW')
   plt.ylabel('단위: 만원')
   plt.grid(True)
   plt.legend(['none', 'moving average (30 days)'])
   plt.show(block=False)

   return

def compute_moving_average(price_per_m2, x_date):

   # estimate moving averaging window size(=N) which is equivalent to 30 days(1 month)
   delta_day = [d.days for d in np.diff(x_date)]
   average_delta_day = sum(delta_day) / len(delta_day)
   N = round(30 / average_delta_day)
   print('moving average window =', N)

   # compute moving average
   moving_average = pd.Series(price_per_m2).rolling(N).mean().values

   return moving_average

def get_transact_count(transact_items, items):

   transact_items = transact_items.set_index(['contract_yyyy', 'contract_mm'])
   # print(transact_items)

   items = items.groupby(by=['contract_yyyy', 'contract_mm']).size().reset_index(name='counts')
   items = items.set_index(['contract_yyyy', 'contract_mm'])
   # print(di)

   for n in items.index:
      transact_items.at[n, 'counts'] = items.at[n, 'counts']


   return transact_items.counts.values

def plot_rent_transaction_count_per_month(items):

   from_yyyy = items.iloc[0]['contract_yyyy']
   from_mm = items.iloc[0]['contract_mm']
   to_yyyy = items.iloc[-1]['contract_yyyy']
   to_mm = items.iloc[-1]['contract_mm']
   date_list, transact_items = make_x_axis_yyyymm_bar(from_yyyy, from_mm, to_yyyy, to_mm)

   # transact_items = transact_items.set_index(['contract_yyyy', 'contract_mm'])
   # print(transact_items)

   deposit_items = items[items.month_rent_1e4 == 0]
   # deposit_items = items.loc[items.month_rent_1e4 == 0]
   yd = get_transact_count(transact_items, deposit_items)

   # di = deposit_items.groupby(by=['contract_yyyy', 'contract_mm']).size().reset_index(name='counts')
   # di = di.set_index(['contract_yyyy', 'contract_mm'])
   # print(di)
   # di_counts = di.counts

   # print('###############')
   # print(transact_items.combine_first(di))

   month_items = items[items.month_rent_1e4 != 0]
   # month_items = items.loc[items.month_rent_1e4 != 0]
   ym = get_transact_count(transact_items, month_items)

   # mi = month_items.groupby(by=['contract_yyyy', 'contract_mm']).size().reset_index(name='counts')
   # mi = mi.set_index(['contract_yyyy', 'contract_mm'])
   # print(mi)
   # mi_counts = mi.counts

   # yd = get_transact_count(transact_items, deposit_items)
   # ym = get_transact_count(transact_items, month_items)
   # yd = np.random.uniform(10,50,len(date_list))
   # ym = np.random.uniform(10,50,len(date_list))
   width = 15
   plt.figure()
   plt.bar(date_list, yd, width, label='전세')
   plt.bar(date_list, ym, width, bottom=yd, label='전월세')
   
   ax = plt.gca()
   ax.xaxis.set_major_locator(MonthLocator(bymonth=(1,7)))
   # ax.xaxis.set_major_locator(MonthLocator(bymonth=(1, 7)))
   ax.xaxis.set_minor_locator(MonthLocator())
   ax.xaxis.set_major_formatter(DateFormatter('\'%y-%m'))
   # ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
   ax.xaxis.set_minor_formatter(NullFormatter())
   # ax.xaxis.set_minor_formatter(DateFormatter('%b'))
   
   plt.xlabel('거래월')
   plt.ylabel('건수')
   plt.title('월별 전세 거래 건수')
   plt.grid(True)
   plt.legend()
   plt.show(block=False)

   return

def plot_sale_transaction_count_per_month(items):



   return

def make_x_axis_yyyymm_bar(from_yyyy, from_mm, to_yyyy, to_mm):

   ##### try to use "pandas.date_range" function, see "learn_pandas.py"
   a = np.arange(int(from_yyyy) * 100 + int(from_mm), int(to_yyyy) * 100 + int(to_mm) + 1)

   yyyymm_list = a[(a % 100 != 0) & (a % 100 <= 12)]

   date_list = []
   for d in yyyymm_list:
      dates = dt.date(d // 100, d % 100, 1)
      date_list.append(dates)

   transact_items = pd.DataFrame(columns=['contract_yyyy', 'contract_mm', 'counts'])
   transact_items.contract_yyyy = [d // 100 for d in yyyymm_list]
   transact_items.contract_mm = [d % 100 for d in yyyymm_list]
   transact_items.counts = 0

   return date_list, transact_items

def study_real_estate_price(file_name, rent_conv_rate_filename):

   query_type, gu, dong, apt, from_yyyymm, to_yyyymm = get_param_from_filename(file_name)
   print(query_type, gu, dong, apt, from_yyyymm, to_yyyymm)

   items = pd.read_excel(file_name)

   conv_rate_table = pd.read_excel(rent_conv_rate_filename)

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
   
   if conv_rate_col:
      print('rent conversion rate column =', conv_rate_col)
   else:
      if 'rent' in query_type:
         print('rent conversion rate not available')

   if query_type == 'single_rent':
      if conv_rate_col:
         price_per_m2 = compute_rent_price_per_m2(items, conv_rate_table, conv_rate_col)

         x_date = make_x_axis_date(items)
      else:
         # extract row where month rent is 0(deposit only rent)
         deposit_only_items = items.loc[items.month_rent_1e4 == 0]
         price_per_m2 = deposit_only_items.deposit_rent_1e4.values / deposit_only_items.area_m2.values

         x_date = make_x_axis_date(deposit_only_items)

      moving_average = compute_moving_average(price_per_m2, x_date)
      plot_price_per_m2(x_date, price_per_m2, moving_average, query_type, gu, dong, apt)

      plot_rent_transaction_count_per_month(items)
         
   elif query_type == 'single_sale':
      price_per_m2 = items.sale_price_1e4.values / items.build_area_m2.values

      x_date = make_x_axis_date(items)

      moving_average = compute_moving_average(price_per_m2, x_date)
      plot_price_per_m2(x_date, price_per_m2, moving_average, query_type, gu, dong, apt)

   elif query_type == 'apt_rent':
      if conv_rate_col:
         price_per_m2 = compute_rent_price_per_m2(items, conv_rate_table, conv_rate_col)

         x_date = make_x_axis_date(items)
      else:
         # extract row where month rent is 0(deposit only rent)
         deposit_only_items = items.loc[items.month_rent_1e4 == 0]
         price_per_m2 = deposit_only_items.deposit_rent_1e4.values / deposit_only_items.area_m2.values

         x_date = make_x_axis_date(deposit_only_items)

      moving_average = compute_moving_average(price_per_m2, x_date)
      plot_price_per_m2(x_date, price_per_m2, moving_average, query_type, gu, dong, apt)
   
   elif query_type == 'apt_sale':
      price_per_m2 = items.sale_price_1e4.values / items.area_m2.values

      x_date = make_x_axis_date(items)
      
      moving_average = compute_moving_average(price_per_m2, x_date)
      plot_price_per_m2(x_date, price_per_m2, moving_average, query_type, gu, dong, apt)

   return price_per_m2, items, x_date


if __name__ == "__main__":

   if len(sys.argv) != 2:
      print('### [error] need index input to select file')
      print('[example] study_real_estate_price 0')
      sys.exit()

   idx = int(sys.argv[1])

   from_yyyy = 2017
   from_mm = 5
   to_yyyy = 2022
   to_mm = 2
   date_list, transact_items = make_x_axis_yyyymm_bar(from_yyyy, from_mm, to_yyyy, to_mm)
   # print(date_list)
   # print(transact_items)

   '''
   y = np.random.uniform(10,50,len(date_list))
   y1 = np.random.uniform(10,50,len(date_list))
   width = 10
   plt.figure()
   plt.bar(date_list, y, width, label='Men')
   plt.bar(date_list, y1, width, bottom=y, label='Women')
   
   ax = plt.gca()
   ax.xaxis.set_major_locator(MonthLocator(bymonth=(1,7)))
   # ax.xaxis.set_major_locator(MonthLocator(bymonth=(1, 7)))
   ax.xaxis.set_minor_locator(MonthLocator())
   ax.xaxis.set_major_formatter(DateFormatter('\'%y-%m'))
   # ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
   ax.xaxis.set_minor_formatter(NullFormatter())
   # ax.xaxis.set_minor_formatter(DateFormatter('%b'))
   
   plt.ylabel('Scores')
   plt.title('Scores by group and gender')
   plt.legend()
   plt.show(block=False)
   '''

   '''
   plt.bar(labels, men_means, width, label='Men')
   plt.bar(labels, women_means, width, bottom=men_means, label='Women')
   plt.ylabel('Scores')
   plt.title('Scores by group and gender')
   plt.legend()
   '''
   

   # sys.exit()

   price_per_m2, items, x_date = study_real_estate_price(file_name_list[idx], rent_conv_rate_filename)

