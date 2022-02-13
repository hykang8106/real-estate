
def process_single_rent(price_df, dong, apt=''):

    price_df = price_df.drop(['계약기간', '계약구분', '갱신요구권사용', '종전계약보증금', \
        '종전계약월세', '지역코드'], axis=1)

    price_df = price_df.rename(columns={'계약면적':'area_m2', '법정동':'dong', \
        '년':'contract_yyyy', '월':'contract_mm', '일':'contract_dd', \
            '보증금액':'deposit_rent_1e4', '월세금액':'month_rent_1e4', '건축년도':'build_yyyy'})

    price_df = price_df[price_df['dong'] == dong].reset_index(drop=True)
    price_df = price_df.drop(['dong'], axis=1)

    # if build year is empty, set to 0
    mask = price_df.build_yyyy.isna()
    price_df.loc[mask, 'build_yyyy'] = 0

    price_df.build_yyyy = price_df.build_yyyy.astype(int)

    price_df.area_m2 = price_df.area_m2.astype(float)

    price_df.contract_yyyy = price_df.contract_yyyy.astype(int)
    price_df.contract_mm = price_df.contract_mm.astype(int)
    price_df.contract_dd = price_df.contract_dd.astype(int)

    price_df.month_rent_1e4 = price_df.month_rent_1e4.astype(int)

    # remove thousand comma in string, and convert to integer
    price_df.deposit_rent_1e4 = price_df.deposit_rent_1e4.str.replace(',','').astype(int)

    price_df = price_df.loc[:, ['area_m2', 'contract_yyyy', 'contract_mm', 'contract_dd', \
        'deposit_rent_1e4', 'month_rent_1e4', 'build_yyyy']]

    price_df = price_df.sort_values(by=['contract_yyyy', 'contract_mm', 'contract_dd']).reset_index(drop=True)

    return price_df

def process_single_sale(price_df, dong, apt=''):

    price_df = price_df[price_df['해제여부'] != 'O'].reset_index(drop=True)

    price_df = price_df[price_df['법정동'] == dong].reset_index(drop=True)

    price_df = price_df[price_df['주택유형'] == '다가구'].reset_index(drop=True)

    price_df = price_df.drop(['거래유형', '법정동', '주택유형', '중개사소재지', \
        '해제사유발생일', '지역코드', '해제여부'], axis=1)

    price_df = price_df.rename(columns={'대지면적':'land_area_m2', '연면적':'build_area_m2', \
        '년':'contract_yyyy', '월':'contract_mm', '일':'contract_dd', \
            '거래금액':'sale_price_1e4', '건축년도':'build_yyyy'})

    mask = price_df.build_yyyy.isna()
    price_df.loc[mask, 'build_yyyy'] = 0

    price_df.build_yyyy = price_df.build_yyyy.astype(int)

    price_df.land_area_m2 = price_df.land_area_m2.astype(float)
    price_df.build_area_m2 = price_df.build_area_m2.astype(float)

    price_df.contract_yyyy = price_df.contract_yyyy.astype(int)
    price_df.contract_mm = price_df.contract_mm.astype(int)
    price_df.contract_dd = price_df.contract_dd.astype(int)

    # remove thousand comma in string, and convert to integer
    price_df.sale_price_1e4 = price_df.sale_price_1e4.str.replace(',','').astype(int)

    price_df = price_df.loc[:, ['land_area_m2', 'build_area_m2', 'contract_yyyy', 'contract_mm', 'contract_dd', \
        'sale_price_1e4', 'build_yyyy']]

    price_df = price_df.sort_values(by=['contract_yyyy', 'contract_mm', 'contract_dd']).reset_index(drop=True)

    return price_df

def process_apt_sale(price_df, dong, apt):

    price_df = price_df[price_df['해제여부'] != 'O'].reset_index(drop=True)

    price_df = price_df[price_df['법정동'] == dong].reset_index(drop=True)

    if apt != 'all':
        price_df = price_df[price_df['아파트'] == apt].reset_index(drop=True)

    price_df = price_df.drop(['거래유형', '법정동', '중개사소재지', \
        '해제사유발생일', '지역코드', '해제여부', '지번'], axis=1)

    price_df = price_df.rename(columns={'전용면적':'area_m2', \
        '년':'contract_yyyy', '월':'contract_mm', '일':'contract_dd', \
            '거래금액':'sale_price_1e4', '건축년도':'build_yyyy', '층':'floor', '아파트':'apt'})

    price_df.build_yyyy = price_df.build_yyyy.astype(int)
    price_df.floor = price_df.floor.astype(int)

    price_df.area_m2 = price_df.area_m2.astype(float)

    price_df.contract_yyyy = price_df.contract_yyyy.astype(int)
    price_df.contract_mm = price_df.contract_mm.astype(int)
    price_df.contract_dd = price_df.contract_dd.astype(int)

    # remove thousand comma in string, and convert to integer
    price_df.sale_price_1e4 = price_df.sale_price_1e4.str.replace(',','').astype(int)

    price_df = price_df.loc[:, ['apt', 'area_m2', 'contract_yyyy', 'contract_mm', 'contract_dd', \
        'sale_price_1e4', 'build_yyyy', 'floor']]

    price_df = price_df.sort_values(by=['contract_yyyy', 'contract_mm', 'contract_dd']).reset_index(drop=True)

    return price_df

def process_apt_rent(price_df, dong, apt):

    price_df = price_df[price_df['법정동'] == dong].reset_index(drop=True)

    if apt != 'all':
        price_df = price_df[price_df['아파트'] == apt].reset_index(drop=True)

    price_df = price_df.drop(['갱신요구권사용', '법정동', '계약구분', '계약기간', \
        '종전계약보증금', '지역코드', '종전계약월세', '지번'], axis=1)

    price_df = price_df.rename(columns={'전용면적':'area_m2', \
        '년':'contract_yyyy', '월':'contract_mm', '일':'contract_dd', \
            '보증금액':'deposit_rent_1e4', '월세금액':'month_rent_1e4', \
                '건축년도':'build_yyyy', '층':'floor', '아파트':'apt'})

    price_df.build_yyyy = price_df.build_yyyy.astype(int)
    price_df.floor = price_df.floor.astype(int)

    price_df.area_m2 = price_df.area_m2.astype(float)

    price_df.contract_yyyy = price_df.contract_yyyy.astype(int)
    price_df.contract_mm = price_df.contract_mm.astype(int)
    price_df.contract_dd = price_df.contract_dd.astype(int)

    price_df.month_rent_1e4 = price_df.month_rent_1e4.astype(int)

    # remove thousand comma in string, and convert to integer
    price_df.deposit_rent_1e4 = price_df.deposit_rent_1e4.str.replace(',','').astype(int)

    price_df = price_df.loc[:, ['apt', 'area_m2', 'contract_yyyy', 'contract_mm', 'contract_dd', \
        'deposit_rent_1e4', 'month_rent_1e4', 'build_yyyy', 'floor']]

    price_df = price_df.sort_values(by=['contract_yyyy', 'contract_mm', 'contract_dd']).reset_index(drop=True)

    return price_df
    