# (1) loop to read single house rent price excel file downloaded from "https://rt.molit.go.kr/"
# (2) merge single house rent price and save into one excel file
# so need post processing program to analyze single house rent price
# use matlab program, "study_rent.m"
# 

import pandas as pd
import os

# after download excel file, must convert excel file(.xlsx) to old format file(.xls)
# because pandas not support xlsx format

file_dir = 'C:\\Users\\hykang\\Desktop\\문지동사업\\실거래가\\전월세\\'

rent = pd.DataFrame()

for file in os.listdir(file_dir):
   if file.endswith('xls'):
      # print(file)
      data = pd.read_excel(file_dir + file, header=16)
      rent = rent.append(data, ignore_index=True)

rent = rent.drop(['시군구', '번지', '도로명', '계약기간', '계약구분', \
   '갱신요구권 사용', '종전계약 보증금 (만원)', '종전계약 월세 (만원)'], axis=1)

rent = rent.rename(columns={'도로조건':'road_under_m', '계약면적(㎡)':'area_m2', \
   '전월세구분':'rent_type', '계약년월':'contract_yyyymm', '계약일':'contract_dd', \
      '보증금(만원)':'deposit_rent_1e4', '월세(만원)':'month_rent_1e4', '건축년도':'build_yyyy'})

# if road is empty, set to 0
mask = rent.road_under_m == '-'
rent.loc[mask, 'road_under_m'] = 0

mask = rent.road_under_m == '12m미만'
rent.loc[mask, 'road_under_m'] = 12

mask = rent.road_under_m == '25m미만'
rent.loc[mask, 'road_under_m'] = 25

# if build year is empty, set to 0
mask = rent.build_yyyy.isna()
rent.loc[mask, 'build_yyyy'] = 0

rent.build_yyyy = rent.build_yyyy.astype(int)

# remove thousand comma in string, and convert to integer
rent.deposit_rent_1e4 = rent.deposit_rent_1e4.str.replace(',','').astype(int)

# if deposit rent only, set to 0
mask = rent.month_rent_1e4 == 0
rent.loc[mask, 'rent_type'] = 0

# if mixed rent(deposit + month), set to 1
mask = (rent.deposit_rent_1e4 != 0) & (rent.month_rent_1e4 != 0)
rent.loc[mask, 'rent_type'] = 1

# if month rent only, set to 2 (this is rare)
mask = rent.deposit_rent_1e4 == 0
rent.loc[mask, 'rent_type'] = 2

rent = rent.sort_values(by=['contract_yyyymm', 'contract_dd']).reset_index(drop=True)

last_row = rent.iloc[-1].tolist()
# last_row example: [25, 33.0, 0, 202111, 27, 15000, 0, 2017]
rent_filename = 'mooji_house_rent_{}{}.xlsx'.format(last_row[3], last_row[4])
rent.to_excel(rent_filename, index=False)

# sys.exit()

# deposit, month, road, build_year, area, contract_date
