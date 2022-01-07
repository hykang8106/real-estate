
def process_single_rent(items, dong, apt=''):

    items = items.drop(['계약기간', '계약구분', '갱신요구권사용', '종전계약보증금', \
        '종전계약월세', '지역코드'], axis=1)

    items = items.rename(columns={'계약면적':'area_m2', '법정동':'dong', \
        '년':'contract_yyyy', '월':'contract_mm', '일':'contract_dd', \
            '보증금액':'deposit_rent_1e4', '월세금액':'month_rent_1e4', '건축년도':'build_yyyy'})

    items = items[items['dong'] == dong].reset_index(drop=True)
    items = items.drop(['dong'], axis=1)

    # if build year is empty, set to 0
    mask = items.build_yyyy.isna()
    items.loc[mask, 'build_yyyy'] = 0

    items.build_yyyy = items.build_yyyy.astype(int)

    items.area_m2 = items.area_m2.astype(float)

    items.contract_yyyy = items.contract_yyyy.astype(int)
    items.contract_mm = items.contract_mm.astype(int)
    items.contract_dd = items.contract_dd.astype(int)

    items.month_rent_1e4 = items.month_rent_1e4.astype(int)

    # remove thousand comma in string, and convert to integer
    items.deposit_rent_1e4 = items.deposit_rent_1e4.str.replace(',','').astype(int)

    items = items.loc[:, ['area_m2', 'contract_yyyy', 'contract_mm', 'contract_dd', \
        'deposit_rent_1e4', 'month_rent_1e4', 'build_yyyy']]

    items = items.sort_values(by=['contract_yyyy', 'contract_mm', 'contract_dd']).reset_index(drop=True)

    return items

def process_single_sale(items, dong, apt=''):

    items = items[items['해제여부'] != 'O'].reset_index(drop=True)

    items = items[items['법정동'] == dong].reset_index(drop=True)

    items = items[items['주택유형'] == '다가구'].reset_index(drop=True)

    items = items.drop(['거래유형', '법정동', '주택유형', '중개사소재지', \
        '해제사유발생일', '지역코드', '해제여부'], axis=1)

    items = items.rename(columns={'대지면적':'land_area_m2', '연면적':'build_area_m2', \
        '년':'contract_yyyy', '월':'contract_mm', '일':'contract_dd', \
            '거래금액':'sale_price_1e4', '건축년도':'build_yyyy'})

    mask = items.build_yyyy.isna()
    items.loc[mask, 'build_yyyy'] = 0

    items.build_yyyy = items.build_yyyy.astype(int)

    items.land_area_m2 = items.land_area_m2.astype(float)
    items.build_area_m2 = items.build_area_m2.astype(float)

    items.contract_yyyy = items.contract_yyyy.astype(int)
    items.contract_mm = items.contract_mm.astype(int)
    items.contract_dd = items.contract_dd.astype(int)

    # remove thousand comma in string, and convert to integer
    items.sale_price_1e4 = items.sale_price_1e4.str.replace(',','').astype(int)

    items = items.loc[:, ['land_area_m2', 'build_area_m2', 'contract_yyyy', 'contract_mm', 'contract_dd', \
        'sale_price_1e4', 'build_yyyy']]

    items = items.sort_values(by=['contract_yyyy', 'contract_mm', 'contract_dd']).reset_index(drop=True)

    return items

def process_apt_sale(items, dong, apt):

    items = items[items['해제여부'] != 'O'].reset_index(drop=True)

    items = items[items['법정동'] == dong].reset_index(drop=True)

    if apt != 'all':
        items = items[items['아파트'] == apt].reset_index(drop=True)

    items = items.drop(['거래유형', '법정동', '중개사소재지', \
        '해제사유발생일', '지역코드', '해제여부', '지번'], axis=1)

    items = items.rename(columns={'전용면적':'area_m2', \
        '년':'contract_yyyy', '월':'contract_mm', '일':'contract_dd', \
            '거래금액':'sale_price_1e4', '건축년도':'build_yyyy', '층':'floor', '아파트':'apt'})

    items.build_yyyy = items.build_yyyy.astype(int)
    items.floor = items.floor.astype(int)

    items.area_m2 = items.area_m2.astype(float)

    items.contract_yyyy = items.contract_yyyy.astype(int)
    items.contract_mm = items.contract_mm.astype(int)
    items.contract_dd = items.contract_dd.astype(int)

    # remove thousand comma in string, and convert to integer
    items.sale_price_1e4 = items.sale_price_1e4.str.replace(',','').astype(int)

    items = items.loc[:, ['apt', 'area_m2', 'contract_yyyy', 'contract_mm', 'contract_dd', \
        'sale_price_1e4', 'build_yyyy', 'floor']]

    items = items.sort_values(by=['contract_yyyy', 'contract_mm', 'contract_dd']).reset_index(drop=True)

    return items

def process_apt_rent(items, dong, apt):

    items = items[items['법정동'] == dong].reset_index(drop=True)

    if apt != 'all':
        items = items[items['아파트'] == apt].reset_index(drop=True)

    items = items.drop(['갱신요구권사용', '법정동', '계약구분', '계약기간', \
        '종전계약보증금', '지역코드', '종전계약월세', '지번'], axis=1)

    items = items.rename(columns={'전용면적':'area_m2', \
        '년':'contract_yyyy', '월':'contract_mm', '일':'contract_dd', \
            '보증금액':'deposit_rent_1e4', '월세금액':'month_rent_1e4', \
                '건축년도':'build_yyyy', '층':'floor', '아파트':'apt'})

    items.build_yyyy = items.build_yyyy.astype(int)
    items.floor = items.floor.astype(int)

    items.area_m2 = items.area_m2.astype(float)

    items.contract_yyyy = items.contract_yyyy.astype(int)
    items.contract_mm = items.contract_mm.astype(int)
    items.contract_dd = items.contract_dd.astype(int)

    items.month_rent_1e4 = items.month_rent_1e4.astype(int)

    # remove thousand comma in string, and convert to integer
    items.deposit_rent_1e4 = items.deposit_rent_1e4.str.replace(',','').astype(int)

    items = items.loc[:, ['apt', 'area_m2', 'contract_yyyy', 'contract_mm', 'contract_dd', \
        'deposit_rent_1e4', 'month_rent_1e4', 'build_yyyy', 'floor']]

    items = items.sort_values(by=['contract_yyyy', 'contract_mm', 'contract_dd']).reset_index(drop=True)

    return items
    