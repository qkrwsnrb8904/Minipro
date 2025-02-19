import requests
from bs4 import BeautifulSoup
import pandas as pd

def crawl_single_household_data(url):
    # 웹 페이지 요청
    response = requests.get(url)
    
    # BeautifulSoup으로 HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 원하는 데이터 추출 (예시)
    data = []
    for item in soup.find_all('div', class_='single-household-item'):
        title = item.find('h2').text.strip()
        description = item.find('p').text.strip()
        data.append({'Title': title, 'Description': description})
    
    # DataFrame으로 변환
    df = pd.DataFrame(data)
    return df

# 크롤링할 웹사이트 URL (예시)
url = 'https://example.com/single-household-data'

# 크롤링 실행
result = crawl_single_household_data(url)

# 결과를 CSV 파일로 저장
result.to_csv('single_household_data.csv', index=False)
