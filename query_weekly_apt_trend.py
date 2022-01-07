
# public data portal:
# https://www.data.go.kr/data/15058352/openapi.do
# login info: id = khy716, pw = hykang8106!
#
# 데이터명 = '한국부동산원_주간아파트동향 조회 서비스'

import pandas as pd
import sys

from util_real_estate import *
from define_file_url_key import *

# weekly_apt_trend_url = 'http://openapi.reb.or.kr/OpenAPI_ToolInstallPackage/service/rest/WeeklyAptTrendSvc'

if __name__ == "__main__":

   gu = '유성구'
   # dong = '문지동'
   # from_year = '2021'
   # from_year = '2017'
   # to_year = '2021'
   start_date = '20200801'
   end_date = '20200901'

   code = load_code()

   gu_code = get_gu_code(code, gu)
   if not gu_code:
      print("#### check 'gu' input")
      sys.exit()

   service_type_list = ['getAptTradingPriceIndex', 'getAptTradingPriceindexSize', \
      'getAptTradingPriceindexAge', 'getAptTradingmarketTrend', 'getAptRentalMarketTrend']

   msg = weekly_apt_trend_url + '/' + service_type_list[0] + '?' + 'startdate=' + start_date + \
      '&' + 'enddate=' + end_date + '&' + 'region=' + gu_code + '&' + 'contractType=' + 'S' + \
      '&' + 'serviceKey=' + service_key

   res = requests.get(msg)

   '''
   dong_code = get_dong_code(code, gu + ' ' + dong)
   if not dong_code:
      print("#### check 'dong' input")
      sys.exit()

   base_date_list = get_base_date_list(from_year, to_year)
   

   items_list = []
   for base_date in base_date_list:
      res = get_data(url, service_key, gu_code, base_date)
      print(res.status_code)
      items_list += get_items(res)

   # res.close()

   items = pd.DataFrame(items_list)
'''