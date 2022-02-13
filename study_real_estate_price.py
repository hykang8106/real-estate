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

rent_conv_rate_filename = 'rent_conv_rate_201611_202112.xls'


def get_rent_conv_rate(yyyymm, conv_rate_table, conv_rate_col):

    mask = conv_rate_table.yyyymm == yyyymm

    conv_rate = conv_rate_table.loc[mask, conv_rate_col].values

    return conv_rate

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

def make_x_axis_date(price_df):

    row_len = price_df.shape[0]
    x_date = []
    for n in range(row_len):
        dates = dt.date(price_df.contract_yyyy.values[n], price_df.contract_mm.values[n], price_df.contract_dd.values[n])
        x_date.append(dates)

    return x_date

def plot_price_per_m2(x_date, price_per_m2, moving_average, query_type, gu, dong, apt):

    plt.figure()
    # print(moving_average)
    if len(moving_average) == 0:
        plt.plot_date(x_date, price_per_m2, '-')
    else:
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
    if N == 1:
        moving_average = ''
    else:
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

'''
def make_x_axis_yyyymm_bar(price_df):

   from_yyyy = price_df.iloc[0]['contract_yyyy']
   from_mm = price_df.iloc[0]['contract_mm']
   to_yyyy = price_df.iloc[-1]['contract_yyyy']
   to_mm = price_df.iloc[-1]['contract_mm']

   ##### try to use "pandas.date_range" function, see "learn_pandas.py"
   a = np.arange(int(from_yyyy) * 100 + int(from_mm), int(to_yyyy) * 100 + int(to_mm) + 1)

   yyyymm_list = a[(a % 100 != 0) & (a % 100 <= 12)]

   date_list = []
   for d in yyyymm_list:
      dates = dt.date(d // 100, d % 100, 1)
      date_list.append(dates)

   yyyymm_df = pd.DataFrame(columns=['contract_yyyy', 'contract_mm', 'counts'])
   yyyymm_df.contract_yyyy = [d // 100 for d in yyyymm_list]
   yyyymm_df.contract_mm = [d % 100 for d in yyyymm_list]
   yyyymm_df.counts = 0

   return date_list, yyyymm_df
'''

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

def study_real_estate_price(price_df, conv_rate_table, query_type, gu, dong, apt, from_yyyymm, to_yyyymm):

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
            print('#### rent conversion rate not available')

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


if __name__ == "__main__":

    file_name_list = ['single_rent_유성구_문지동_201701_202112.xls', \
    'single_sale_유성구_문지동_201701_202112.xls', \
    'apt_rent_세종특별자치시_반곡동_수루배마을1단지_201701_202112.xls', \
    'apt_sale_세종특별자치시_반곡동_수루배마을1단지_201701_202112.xls', \
    'apt_sale_성동구_행당동_대림e-편한세상_201701_202112.xls', \
    'apt_rent_성동구_행당동_대림e-편한세상_201701_202112.xls']

    if len(sys.argv) != 2:
        print('### [error] need index input to select file')
        print('[example] study_real_estate_price 0')
        sys.exit()

    idx = int(sys.argv[1])
    file_name = file_name_list[idx]

    price_df = pd.read_excel(file_name)

    conv_rate_table = pd.read_excel(rent_conv_rate_filename)

    query_type, gu, dong, apt, from_yyyymm, to_yyyymm = get_param_from_filename(file_name)
    print(query_type, gu, dong, apt, from_yyyymm, to_yyyymm)

    price_per_m2, price_df, x_date = \
        study_real_estate_price(price_df, conv_rate_table, query_type, gu, dong, apt, from_yyyymm, to_yyyymm)

    '''
    price_per_m2, price_df, x_date = \
        study_real_estate_price(file_name_list[idx], rent_conv_rate_filename)
    '''

