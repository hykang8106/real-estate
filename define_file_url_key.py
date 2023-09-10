
from os.path import exists

from proc_query_result import *

query_result_folder = 'query_result_xls'

# download code file from "https://www.code.go.kr/index.do"
# resave ".txt" file as "utf-8" format

code_file = 'C:\\Users\\hykang\\Documents\\workspace\\real-estate\\법정동코드 전체자료.txt'

# public data portal:
# https://www.data.go.kr/data/15058352/openapi.do
# login info: id = khy716, pw = hykang8106#
# valid until 2023/12/11

# my service key
service_key = 'yrvdMVzLvNSv1dGkAUgSoLMOXKSkLq4F11RLR2cHwxSi4MWiMxLyh3CB4XV4g5NB3vw4fVVMhwftbXzyZUwnog%3D%3D'

# 다가구/단독 전세
single_rent_url = 'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcSHRent?'

# 다가구/단독 매매
single_sale_url = 'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcSHTrade?'

# 아파트 매매
apt_sale_url = 'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTrade?'

# 아파트 전세
apt_rent_url = 'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptRent?'

# 토지 매매
land_sale_url = 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcLandTrade?'

#### below url invalid (as of 202309)
# apt_trade_count_url = 'http://openapi.reb.or.kr/OpenAPI_ToolInstallPackage/service/rest/AptTradingStateSvc/getAptTrdStateCaseOfNbr?'
# weekly_apt_trend_url = 'http://openapi.reb.or.kr/OpenAPI_ToolInstallPackage/service/rest/WeeklyAptTrendSvc'

query_url = {'single_rent' : single_rent_url, 'single_sale' : single_sale_url, \
   'apt_rent' : apt_rent_url, 'apt_sale' : apt_sale_url}

query_type_list = ['single_rent', 'single_sale', 'apt_rent', 'apt_sale']

proc_result = {'single_rent' : process_single_rent, 'single_sale' : process_single_sale, \
   'apt_rent' : process_apt_rent, 'apt_sale' : process_apt_sale}

