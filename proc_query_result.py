""" 
[branch: change_cmd_arg]

commit [1] message

(1) 아파트 거래에서 "동"이 지정된 경우, 해당 "동"과 관련된 거래만 추출함
(2) 아파트 거래에서 "아파트"가 지정된 경우, 해당 "아파트"와 관련된 거래만 추출함
(3) 아파트 거래에서 컬럼명을 영문으로 바꾸지 않음(원래 한글 컬럼명으로 유지)
(4) 아파트 전세에서 '계약기간', '계약구분', '갱신요구권사용', '종전계약보증금', '종전계약월세' 컬럼 유지
(5) 다가구 거래에서 컬럼명을 영문으로 바꾸지 않음(원래 한글 컬럼명으로 유지)
(6) 다가구 매매에서 '주택유형', '거래유형' 유지
(7) 다가구 전세에서 '계약기간', '계약구분', '갱신요구권사용', '종전계약보증금', '종전계약월세' 컬럼 유지
"""

import pandas as pd

def process_single_rent(price_df, dong, apt=''):

    price_df = price_df.drop(['지역코드'], axis=1)

    """ price_df = price_df.rename(columns={'계약면적':'area_m2', '법정동':'dong', \
        '년':'contract_yyyy', '월':'contract_mm', '일':'contract_dd', \
            '보증금액':'deposit_rent_1e4', '월세금액':'month_rent_1e4', '건축년도':'build_yyyy'}) """

    if dong:
        price_df = price_df[price_df['법정동'] == dong].reset_index(drop=True)

    # if build year is empty, set to 0
    mask = price_df['건축년도'].isna()
    price_df.loc[mask, '건축년도'] = 0

    price_df['건축년도'] = price_df['건축년도'].astype(int)

    price_df['계약면적'] = price_df['계약면적'].astype(float)

    price_df['년'] = price_df['년'].astype(int)
    price_df['월'] = price_df['월'].astype(int)
    price_df['일'] = price_df['일'].astype(int)

    price_df['월세금액'] = price_df['월세금액'].astype(int)

    price_df['종전계약월세'] = price_df['종전계약월세'].str.replace(',','')
    price_df['종전계약월세'] = price_df['종전계약월세'].\
        apply(lambda x: int(x) if not pd.isnull(x) and x != '' else x)

    # remove thousand comma in string, and convert to integer
    price_df['보증금액'] = price_df['보증금액'].str.replace(',','').astype(int)

    price_df['종전계약보증금'] = price_df['종전계약보증금'].str.replace(',','')
    price_df['종전계약보증금'] = price_df['종전계약보증금'].\
        apply(lambda x: int(x) if not pd.isnull(x) and x != '' else x)

    price_df = price_df.loc[:, ['법정동', '계약면적', '년', '월', '일', '계약기간', \
        '보증금액', '월세금액', '종전계약보증금', '종전계약월세', '계약구분', '갱신요구권사용', '건축년도']]

    price_df = price_df.sort_values(by=['년','월','일']).reset_index(drop=True)

    return price_df

def process_single_sale(price_df, dong, apt=''):

    #### '해제여부' == 'O' 인 경우, 계약무효로 간주하여 삭제
    price_df = price_df[price_df['해제여부'] != 'O'].reset_index(drop=True)

    if dong:
        price_df = price_df[price_df['법정동'] == dong].reset_index(drop=True)

    #### 문지동 사업을 위한 것이므로, '주택유형' == '다가구'인 것만 고려('주택유형' == '단독'인 경우 배제)
    price_df = price_df[price_df['주택유형'] == '다가구'].reset_index(drop=True)

    price_df = price_df.drop(['중개사소재지', '해제사유발생일', '지역코드', '해제여부', '지번'], axis=1)

    mask = price_df['건축년도'].isna()
    price_df.loc[mask, ['건축년도']] = 0

    price_df['건축년도'] = price_df['건축년도'].astype(int)

    price_df['대지면적'] = price_df['대지면적'].astype(float)
    price_df['연면적'] = price_df['연면적'].astype(float)

    price_df['년'] = price_df['년'].astype(int)
    price_df['월'] = price_df['월'].astype(int)
    price_df['일'] = price_df['일'].astype(int)

    # remove thousand comma in string, and convert to integer
    price_df['거래금액'] = price_df['거래금액'].str.replace(',','').astype(int)

    price_df = price_df.loc[:, ['법정동', '주택유형', '대지면적', '연면적', '거래금액', '년', '월', '일', \
        '거래유형']]

    price_df = price_df.sort_values(by=['년','월','일']).reset_index(drop=True)

    return price_df

def process_apt_sale(price_df, dong, apt):

    price_df = price_df[price_df['해제여부'] != 'O'].reset_index(drop=True)

    if dong:
        price_df = price_df[price_df['법정동'] == dong].reset_index(drop=True)
        # price_df = price_df.drop(['법정동'], axis=1)

    if apt:
        price_df = price_df[price_df['아파트'] == apt].reset_index(drop=True)
        # price_df = price_df.drop(['아파트'], axis=1)

    price_df = price_df.drop(['거래유형', '중개사소재지', '해제사유발생일', '지역코드', '해제여부', '지번'], axis=1)

    price_df['건축년도'] = price_df['건축년도'].astype(int)
    price_df['층'] = price_df['층'].astype(int)

    price_df['전용면적'] = price_df['전용면적'].astype(float)

    price_df['년'] = price_df['년'].astype(int)
    price_df['월'] = price_df['월'].astype(int)
    price_df['일'] = price_df['일'].astype(int)

    # remove thousand comma in string, and convert to integer
    price_df['거래금액'] = price_df['거래금액'].str.replace(',','').astype(int)

    price_df = price_df.loc[:, ['법정동', '아파트', '전용면적', '년', '월', '일', \
        '거래금액', '건축년도', '층']]

    price_df = price_df.sort_values(by=['년','월','일']).reset_index(drop=True)

    return price_df

def process_apt_rent(price_df, dong, apt):

    if dong:
        price_df = price_df[price_df['법정동'] == dong].reset_index(drop=True)

    if apt:
        price_df = price_df[price_df['아파트'] == apt].reset_index(drop=True)

    price_df = price_df.drop(['지역코드', '지번'], axis=1)

    price_df['건축년도'] = price_df['건축년도'].astype(int)
    price_df['층'] = price_df['층'].astype(int)

    price_df['전용면적'] = price_df['전용면적'].astype(float)

    price_df['년'] = price_df['년'].astype(int)
    price_df['월'] = price_df['월'].astype(int)
    price_df['일'] = price_df['일'].astype(int)

    price_df['월세금액'] = price_df['월세금액'].astype(int)

    price_df['종전계약월세'] = price_df['종전계약월세'].str.replace(',','')
    price_df['종전계약월세'] = price_df['종전계약월세'].\
        apply(lambda x: int(x) if not pd.isnull(x) and x != '' else x)

    # remove thousand comma in string, and convert to integer
    price_df['보증금액'] = price_df['보증금액'].str.replace(',','').astype(int)

    price_df['종전계약보증금'] = price_df['종전계약보증금'].str.replace(',','')
    price_df['종전계약보증금'] = price_df['종전계약보증금'].\
        apply(lambda x: int(x) if not pd.isnull(x) and x != '' else x)

    price_df = price_df.loc[:, ['법정동', '아파트', '전용면적', '년', '월', '일', '계약기간', \
        '보증금액', '월세금액', '종전계약보증금', '종전계약월세', '계약구분', '갱신요구권사용', '건축년도', '층']]

    price_df = price_df.sort_values(by=['년','월','일']).reset_index(drop=True)

    return price_df

def process_land_sale(price_df, dong, use_area, land_purpose):

    # remove row where '해제여부' column have 'O'
    #### '해제여부' == 'O' 인 경우, 계약무효로 간주하여 삭제
    price_df = price_df[price_df['해제여부'] != 'O'].reset_index(drop=True)

    # remove row where '구분' column have '지분'
    price_df = price_df[price_df['구분'] != '지분'].reset_index(drop=True)

    # remove row where '용도지역' column have '용도미지정'
    price_df = price_df[price_df['용도지역'] != '용도미지정'].reset_index(drop=True)

    if dong:
        price_df = price_df[price_df['법정동'] == dong].reset_index(drop=True)

    if use_area:
        price_df = price_df[price_df['용도지역'] == use_area].reset_index(drop=True)

    if land_purpose:
        price_df = price_df[price_df['지목'] == land_purpose].reset_index(drop=True)

    # drop not useful column
    price_df = price_df.drop(columns=['중개사소재지', '지역코드', '해제사유발생일', '해제여부', '구분', '지번'])

    """
    # drop not useful column
    if '시군구' in price_df.columns:
        price_df = price_df.drop(columns=['거래유형', '시군구', '중개사소재지', '지역코드', \
            '해제사유발생일', '해제여부', '구분'])
    else:
        price_df = price_df.drop(columns=['거래유형', '중개사소재지', '지역코드', '해제사유발생일', \
            '해제여부', '구분'])
    """

    price_df['거래금액'] = price_df['거래금액'].str.replace(',','').astype(int)
    price_df['거래면적'] = price_df['거래면적'].str.replace(',','').astype(float)
    price_df['년'] = price_df['년'].astype(int)
    price_df['월'] = price_df['월'].astype(int)
    price_df['일'] = price_df['일'].astype(int)

    # '시군구' 컬럼이 없는 경우 있음: '세종' 
    if '시군구' in price_df.columns:
        price_df = price_df.loc[:, ['용도지역', '지목', '거래면적', '거래금액', '시군구', '법정동', \
            '년', '월', '일']]
    else:
        price_df = price_df.loc[:, ['용도지역', '지목', '거래면적', '거래금액', '법정동', \
            '년', '월', '일']]

    price_df = price_df.sort_values(by=['년', '월', '일']).reset_index(drop=True)

    return price_df


""" 
#### chatgpt code 1:

import pandas as pd

# Sample DataFrame
data = {'Your_Column_Name': ['123', '', '456', '789', '']}
df = pd.DataFrame(data)

# Define a custom function to convert a string to an integer, or return None if the string is empty
def convert_to_integer_or_none(value):
    try:
        return int(value)
    except ValueError:
        return None

# Use the apply method to apply the custom function to the specified column
df['Your_Column_Name'] = df['Your_Column_Name'].apply(lambda x: convert_to_integer_or_none(x) if x != '' else x)

# Print the updated DataFrame
print(df) """


""" 
#### chatgpt code 2:

import pandas as pd
import numpy as np

# Sample DataFrame
data = {'Your_Column_Name': ['123', '', '456', '789', '']}
df = pd.DataFrame(data)

# Replace empty strings with NaN in the specified column
df['Your_Column_Name'] = df['Your_Column_Name'].replace('', np.nan)

# Use astype(int) to convert non-NaN values to integers
df['Your_Column_Name'] = df['Your_Column_Name'].astype(float).astype(pd.Int64Dtype(), errors='ignore')

# Print the updated DataFrame
print(df) """


""" 
#### chatgpt code 3:

import pandas as pd

# Sample DataFrame
data = {'Your_Column_Name': ['123', '', '456', '789', '']}
df = pd.DataFrame(data)

# Use pd.isnull() to identify NaN values and apply the conversion conditionally
df['Your_Column_Name'] = df['Your_Column_Name'].apply(lambda x: int(x) if not pd.isnull(x) and x != '' else x)

# Print the updated DataFrame
print(df) """


    