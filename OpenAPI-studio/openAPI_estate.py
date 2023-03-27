# 오피스텔 거래 내역

# https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15059249
import numpy as np
import openpyxl
import requests
import xmltodict
import json
import matplotlib.pyplot as plt
import pandas as pd

# 그래프 한글 사용
from matplotlib import font_manager, rc
rc('font',family ='AppleGothic')

# 지역이름 -> 법정동코드 변환 코드

data = {
    '연도' : [],
    '오피스텔명' : [],
    '계약기간' : [],
    '보증금' : [],
    '월세' : [],
    '층' : [],
    '전용면적' : []
}

def searchLawdCd(locate_nm):
    raw = pd.read_csv('./dongCode.txt', sep="\t", encoding="CP949")
    realdata = raw[raw['폐지여부'] == '존재']
    strcode = realdata['법정동코드'].astype(str).apply(lambda x: x[:5])
    lawd_cd = strcode[realdata['법정동명'] == locate_nm].values[0]
    return lawd_cd

# 거래내역 추출 코드
def printOfficeTransaction(dongCode, apartName, sDate):

    url = 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcOffiRent'
    LAWD_CD = dongCode # LAWD_CD는 법정동 코드 10자리 중 5자리
    DEAL_YMD = sDate # 해당 월부터 1년

    DATE = []
    avgDeposit = [] # 평균 보증ㄱ므
    avgFee = [] # 평균 월세

    deposit = [] # 보증금
    fee = [] # 월세
    floor = [] # 층
    area = []

    # apartName = '불당아리스타팰리스' # 오피스텔 이름
    for i in range(DEAL_YMD, DEAL_YMD-12, -1):
        DATE.append(DEAL_YMD)
        DEAL_YMD = str(i)
        print("=======================================================================")
        print(DEAL_YMD[:4] + "년" + DEAL_YMD[4:] + "월")
        params ={'serviceKey' : 'GpHkMo6DWA2mcDd7OWQuStcVgZ+WjtRLNAcfBC6sgnghQrgGi48vHixwmvhy1+AlRgDZiclDBdglJj8F7EmNsw==', 'LAWD_CD' : LAWD_CD, 'DEAL_YMD' : DEAL_YMD }

        response = requests.get(url, params=params)
        dict_data = xmltodict.parse(response.text)
        json_data = json.dumps(dict_data, ensure_ascii=False)
        # print(json_data)

        d = dict_data['response']['body']['items']['item']
        m_deposit = []  # 월별 보증금
        m_fee = []  # 월별 월세
        print("len(d):",len(d))
        for i in range(len(d)):
            for k in d[i].keys():
                if d[i].get('단지') == apartName:
                    deposit.append(int(d[i].get('보증금').replace(',', '')))
                    fee.append(int(d[i].get('월세')))
                    m_deposit.append(int(d[i].get('보증금').replace(',', '')))
                    m_fee.append(int(d[i].get('월세')))

                    print(k, d[i].get(k))
                # print(k, d[i].get(k))
            data.get('오피스텔명').append(apartName)
            data.get('연도').append(DEAL_YMD)
            data.get('계약기간').append(d[i].get('계약기간'))
            data.get('보증금').append(d[i].get('보증금'))
            data.get('월세').append(d[i].get('월세'))
            data.get('층').append(d[i].get('층'))
            data.get('전용면적').append(d[i].get('전용면적'))
            print("\n")

        m_deposit = np.array(m_deposit)
        m_fee = np.array(m_fee)
        avgDeposit.append(np.mean(m_deposit))
        avgFee.append(np.mean(m_fee))

    # 엑셀 추출
    df = pd.DataFrame(data, index=data['연도'])  # index추가할 수 있음
    df.to_excel('studio_deal_info.xlsx', index=False)

    deposit = np.array(deposit)
    fee = np.array(fee)

    workbook = openpyxl.load_workbook('studio_deal_info.xlsx')
    sheet = workbook.active
    sheet['I1'] = "평균 보증금: "+ str(np.mean(deposit))
    sheet['I2'] = "평균 월세: "+ str(np.mean(fee))
    workbook.save('studio_deal_info.xlsx')

    print(apartName, "평균 보증금: ", np.mean(deposit), "평균 월세: ", np.mean(fee))

    # # 거래량
    # g = np.arange(0, len(fee))

    plt.figure()
    plt.scatter(deposit, fee, color='black')
    plt.axis([0, 5000, 0, 100])
    plt.xlabel('보증금')
    plt.ylabel('월세')
    plt.title(apartName + ' 보증금별 월세')
    plt.show()

    # 날짜별 보증금
    plt.figure()
    plt.plot(DATE, avgDeposit, color='black')
    plt.xticks(rotation=90)
    plt.xlabel('날짜')
    plt.ylabel('보증금')
    plt.show()

    # 날짜별 월세
    plt.figure()
    plt.plot(DATE, avgFee, color='black')
    plt.xticks(rotation=90)
    plt.xlabel('날짜')
    plt.ylabel('월세')
    plt.show()

    # print(response.text)

    # def stringNumberToInt(stringNumber):
    #     return int(stringNumber.replace(',', ''))


dongCode = searchLawdCd('충청남도 천안시 서북구 불당동')
print(dongCode)
printOfficeTransaction(dongCode, "불당아리스타팰리스", 202212)