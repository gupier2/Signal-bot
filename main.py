import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import os

# 텔레그램 토큰과 챗아이디를 환경변수로 불러오기
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def get_kospi():
    url = "https://finance.naver.com/sise/sise_index.naver?code=KOSPI"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    kospi_now = soup.select_one('.no_today .blind').text
    return float(kospi_now.replace(',', ''))

def get_kosdaq():
    url = "https://finance.naver.com/sise/sise_index.naver?code=KOSDAQ"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    kosdaq_now = soup.select_one('.no_today .blind').text
    return float(kosdaq_now.replace(',', ''))

def calculate_score(kospi, kosdaq):
    score_kospi = 0
    score_kosdaq = 0
    
    if kospi > 2600:
        score_kospi += 20
    else:
        score_kospi += 10

    if kosdaq > 850:
        score_kosdaq += 20
    else:
        score_kosdaq += 10

    score_kospi += 10  # 외국인 수급 등 추가 가정
    score_kosdaq += 10
    return score_kospi, score_kosdaq

def decide_signal(score):
    if score >= 80:
        return "초록불"
    elif 50 <= score < 80:
        return "노랑불"
    else:
        return "빨간불"

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.get(url, params=params)
    return response.json()

def main():
    kospi = get_kospi()
    kosdaq = get_kosdaq()
    
    score_kospi, score_kosdaq = calculate_score(kospi, kosdaq)
    
    kospi_signal = decide_signal(score_kospi)
    kosdaq_signal = decide_signal(score_kosdaq)
    
    message = f"오늘의 신호등 결과:\n\n코스피: {kospi_signal} (총점: {score_kospi}점)\n코스닥: {kosdaq_signal} (총점: {score_kosdaq}점)"
    
    send_telegram_message(BOT_TOKEN, CHAT_ID, message)

    today = datetime.date.today()
    data = {'날짜': [today], '코스피 총점': [score_kospi], '코스닥 총점': [score_kosdaq], '코스피 신호등': [kospi_signal], '코스닥 신호등': [kosdaq_signal]}
    df = pd.DataFrame(data)
    df.to_excel(f"지수신호등_{today}.xlsx", index=False)

if __name__ == "__main__":
    main()
