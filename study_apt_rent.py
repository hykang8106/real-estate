# (1) loop to read apt rent price excel file downloaded from "https://rt.molit.go.kr/"
# (2) merge apt rent price and save into one excel file
# so need post processing program to analyze apt rent price
# use matlab program, "study_apt_rent.m"
# 

import pandas as pd
import os, sys

# after download excel file, must convert excel file(.xlsx) to old format file(.xls)
# because pandas not support xlsx format

if len(sys.argv) != 2:
   print("#### apt name not found: one of 'hyosung', 'narae', 'samsung', 'sejong', 'expo'\n")
   sys.exit()

if sys.argv[1] == 'hyosung':
   file_dir = 'C:\\Users\\hykang\\Desktop\\문지동사업\\아파트실거래가\\문지동\\전월세\\'

   apt_name = 'moonji_hyosung'
   apt_name_korean = '문지효성해링턴플레이스'

elif sys.argv[1] == 'narae':
   file_dir = 'C:\\Users\\hykang\\Desktop\\문지동사업\\아파트실거래가\\전민동\\전월세\\'

   apt_name = 'jeonmin_narae'
   apt_name_korean = '나래'

elif sys.argv[1] == 'samsung':
   file_dir = 'C:\\Users\\hykang\\Desktop\\문지동사업\\아파트실거래가\\전민동\\전월세\\'

   apt_name = 'jeonmin_samsung'
   apt_name_korean = '삼성푸른'

elif sys.argv[1] == 'sejong':
   file_dir = 'C:\\Users\\hykang\\Desktop\\문지동사업\\아파트실거래가\\전민동\\전월세\\'

   apt_name = 'jeonmin_sejong'
   apt_name_korean = '세종'

elif sys.argv[1] == 'expo':
   file_dir = 'C:\\Users\\hykang\\Desktop\\문지동사업\\아파트실거래가\\전민동\\전월세\\'

   apt_name = 'jeonmin_expo'
   apt_name_korean = '엑스포'

else:
   print("### apt name must be one of 'hyosung', 'narae', 'samsung', 'sejong', 'expo'\n")
   sys.exit()


rent = pd.DataFrame()

for file in os.listdir(file_dir):
   if file.endswith('xls'):
      # print(file)
      data = pd.read_excel(file_dir + file, header=16)
      rent = rent.append(data, ignore_index=True)

rent = rent.loc[rent['단지명'] == apt_name_korean]

# for sejong bangok-dong including our apt, '단지명' must not be dropped
rent = rent.drop(['시군구', '번지', '본번', '부번', '단지명', '건축년도', '도로명', '계약기간', '계약구분', \
   '갱신요구권 사용', '종전계약 보증금 (만원)', '종전계약 월세 (만원)'], axis=1)

rent = rent.rename(columns={'전월세구분':'rent_type', '전용면적(㎡)':'area_m2', \
   '계약년월':'contract_yyyymm', '계약일':'contract_dd', \
      '보증금(만원)':'deposit_rent_1e4', '월세(만원)':'month_rent_1e4', '층':'floor'})

# sys.exit()

# remove thousand comma in string, and convert to integer
rent.deposit_rent_1e4 = rent.deposit_rent_1e4.str.replace(',','').astype(int)

# if deposit rent only, set to 0
mask = rent.month_rent_1e4 == 0
rent.loc[mask, 'rent_type'] = 0

# if mixed rent(deposit + month), set to 1
mask = (rent.deposit_rent_1e4 != 0) & (rent.month_rent_1e4 != 0)
rent.loc[mask, 'rent_type'] = 1

'''
# if month rent only, set to 2 (this is rare)
mask = rent.deposit_rent_1e4 == 0
rent.loc[mask, 'rent_type'] = 2
'''

rent = rent.sort_values(by=['contract_yyyymm', 'contract_dd']).reset_index(drop=True)

last_row = rent.iloc[-1].tolist()
# last_row example: [1, 59.973, 202111, 29, 15000, 70, 10]
rent_filename = '{}_apt_rent_{}{}.xlsx'.format(apt_name, last_row[2], last_row[3])
rent.to_excel(rent_filename, index=False)

# sys.exit()

# deposit, month, road, build_year, area, contract_date
