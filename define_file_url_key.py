
from os.path import exists

from proc_query_result import *

# download code file from "https://www.code.go.kr/index.do"
# resave ".txt" file as "utf-8" format

code_file = 'C:\\Users\\hykang\\Desktop\\moonji_project_code\\법정동코드 전체자료.txt'
# when run in joonho computer
if not exists(code_file):
   code_file = 'C:\\Users\\Joon Ho\\Desktop\\hykang\\real_estate\\법정동코드 전체자료.txt'

# public data portal:
# https://www.data.go.kr/data/15058352/openapi.do
# login info: id = khy716, pw = hykang8106!
# valid until 2023/12/11

apt_trade_count_url = 'http://openapi.reb.or.kr/OpenAPI_ToolInstallPackage/service/rest/AptTradingStateSvc/getAptTrdStateCaseOfNbr?'

weekly_apt_trend_url = 'http://openapi.reb.or.kr/OpenAPI_ToolInstallPackage/service/rest/WeeklyAptTrendSvc'

# house_rent_service_key = 'yrvdMVzLvNSv1dGkAUgSoLMOXKSkLq4F11RLR2cHwxSi4MWiMxLyh3CB4XV4g5NB3vw4fVVMhwftbXzyZUwnog%3D%3D'
# service_key = 'yrvdMVzLvNSv1dGkAUgSoLMOXKSkLq4F11RLR2cHwxSi4MWiMxLyh3CB4XV4g5NB3vw4fVVMhwftbXzyZUwnog=='

single_rent_url = 'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcSHRent?'

# house_sale_service_key = 'yrvdMVzLvNSv1dGkAUgSoLMOXKSkLq4F11RLR2cHwxSi4MWiMxLyh3CB4XV4g5NB3vw4fVVMhwftbXzyZUwnog=='
# house_sale_service_key = 'yrvdMVzLvNSv1dGkAUgSoLMOXKSkLq4F11RLR2cHwxSi4MWiMxLyh3CB4XV4g5NB3vw4fVVMhwftbXzyZUwnog%3D%3D'

single_sale_url = 'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcSHTrade?'

apt_sale_url = 'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTrade?'

apt_rent_url = 'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptRent?'

service_key = 'yrvdMVzLvNSv1dGkAUgSoLMOXKSkLq4F11RLR2cHwxSi4MWiMxLyh3CB4XV4g5NB3vw4fVVMhwftbXzyZUwnog%3D%3D'

query_url = {'single_rent' : single_rent_url, 'single_sale' : single_sale_url, \
   'apt_rent' : apt_rent_url, 'apt_sale' : apt_sale_url}

query_type_list = ['single_rent', 'single_sale', 'apt_rent', 'apt_sale']

proc_result = {'single_rent' : process_single_rent, 'single_sale' : process_single_sale, \
   'apt_rent' : process_apt_rent, 'apt_sale' : process_apt_sale}

command_example_1 = "[example] query_real_estate_price single_rent 유성구 문지동 201701 202112"
command_example_2 = "[example] query_real_estate_price single_sale 유성구 문지동 201701 202112"
command_example_3 = "[example] query_real_estate_price apt_rent 유성구 전민동 201701 202112 문지효성해링턴플레이스"
command_example_4 = "[example] query_real_estate_price apt_sale 세종특별자치시 반곡동 201701 202112 수루배마을1단지"
command_example_5 = "[example] query_real_estate_price apt_sale 성동구 행당동 201701 202112 대림e-편한세상"
command_example_6 = "[example] query_real_estate_price apt_sale 유성구 전민동 201701 202112 문지효성해링턴플레이스"

# blow is not needed: use "query_rent_conv_rate.py",
# which query rent conversion rate to kosis web site and save it into excel file
''''
# [ref] https://kosis.kr/statHtml/statHtml.do?orgId=408&tblId=DT_30404_N0010
# as of 211226, [ref] site show 202109 data, so 202110 ~ 202112 data is guessed
# daejoen single house rent conversion rate(in percent)
single_daejeon_conv_rate = {201611:9.0, 201612:8.9, \
   201701:9.0, 201702:9.1, 201703:9.1,	201704:9.1,	201705:9.1,	201706:9.0,	\
   201707:8.9,	201708:8.8,	201709:8.7,	201710:8.7,	201711:8.6,	201712:8.6, \
   201801:8.4,	201802:8.5,	201803:8.6,	201804:8.6,	201805:8.4,	201806:8.5, \
   201807:8.5,	201808:8.4,	201809:8.4,	201810:8.3,	201811:8.2,	201812:8.1, \
	201901:8.3,	201902:8.4,	201903:8.4,	201904:8.4,	201905:8.3,	201906:8.3,	\
   201907:8.2,	201908:8.0,	201909:8.0,	201910:8.0,	201911:7.9,	201912:7.7, \
	202001:7.7,	202002:7.9,	202003:7.9,	202004:7.8,	202005:7.8,	202006:7.8, \
	202007:7.8,	202008:7.5,	202009:7.3,	202010:7.2,	202011:7.1,	202012:7.0, \
	202101:7.0,	202102:7.1,	202103:7.2,	202104:7.1,	202105:7.0,	202106:7.0, \
	202107:7.0,	202108:6.8,	202109:6.7, 202110:6.7, 202111:6.7, 202112:6.7}

# [ref] https://kosis.kr/statHtml/statHtml.do?orgId=408&tblId=DT_30404_N0010
# as of 211226, [ref] site show 202109 data, so 202110 ~ 202112 data is guessed
# sejong apt rent conversion rate(in percent)
apt_sejong_conv_rate = {201611:4.1, 201612:4.1, \
   201701:4.1, 201702:4.2, 201703:4.2,	201704:4.2,	201705:4.3,	201706:4.4,	\
   201707:4.7,	201708:4.8,	201709:4.8,	201710:4.7,	201711:4.6,	201712:4.6, \
   201801:4.6,	201802:4.7,	201803:4.7,	201804:4.8,	201805:4.8,	201806:4.8, \
   201807:4.9,	201808:5.0,	201809:5.1,	201810:5.1,	201811:5.0,	201812:5.0, \
	201901:4.9,	201902:4.8,	201903:4.7,	201904:4.7,	201905:4.7,	201906:4.8,	\
   201907:4.8,	201908:4.9,	201909:4.8,	201910:4.8,	201911:4.8,	201912:4.6, \
	202001:4.6,	202002:4.5,	202003:4.5,	202004:4.5,	202005:4.4,	202006:4.5, \
	202007:4.6,	202008:4.6,	202009:4.5,	202010:4.6,	202011:4.5,	202012:4.5, \
	202101:4.4,	202102:4.3,	202103:4.2,	202104:4.1,	202105:4.0,	202106:4.0, \
	202107:4.1,	202108:4.1,	202109:4.1, 202110:4.1, 202111:4.1, 202112:4.1}

# [ref] https://kosis.kr/statHtml/statHtml.do?orgId=408&tblId=DT_30404_N0010
# as of 211226, [ref] site show 202109 data, so 202110 ~ 202112 data is guessed
# yuseong apt rent conversion rate(in percent)
apt_yuseong_conv_rate = {201611:4.6, 201612:4.6, \
   201701:4.7, 201702:5.0, 201703:5.2,	201704:5.2,	201705:5.1,	201706:5.2,	\
   201707:5.0,	201708:4.9,	201709:4.8,	201710:4.8,	201711:4.8,	201712:4.8, \
   201801:4.7,	201802:4.7,	201803:4.9,	201804:4.9,	201805:5.1,	201806:5.3, \
   201807:5.2,	201808:5.5,	201809:5.0,	201810:4.8,	201811:4.8,	201812:4.8, \
	201901:4.7,	201902:4.6,	201903:4.6,	201904:4.6,	201905:4.7,	201906:4.8,	\
   201907:4.8,	201908:5.0,	201909:4.9,	201910:4.9,	201911:4.8,	201912:4.6, \
	202001:4.7,	202002:4.6,	202003:4.5,	202004:4.3,	202005:4.2,	202006:4.3, \
	202007:4.2,	202008:4.2,	202009:4.2,	202010:4.2,	202011:4.2,	202012:4.3, \
	202101:4.4,	202102:4.5,	202103:4.5,	202104:4.4,	202105:4.6,	202106:4.7, \
	202107:4.8,	202108:4.8,	202109:4.6, 202110:4.6, 202111:4.6, 202112:4.6}
'''

