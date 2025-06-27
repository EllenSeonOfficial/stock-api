from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI()

def get_price_from_naver(ticker: str) -> str:
    url = f"https://finance.naver.com/item/main.naver?code={ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    price_tag = soup.select_one("p.no_today span.blind")
    return price_tag.text.strip() if price_tag else "N/A"

def get_news_from_naver(ticker: str):
    url = f"https://search.naver.com/search.naver?where=news&query={ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    news_list = []
    for tag in soup.select(".news_tit")[:3]:
        news_list.append({
            "title": tag.get("title"),
            "url": tag.get("href")
        })
    return news_list

@app.get("/stock", response_class=JSONResponse, summary="주가 및 뉴스 조회")
def get_stock(
    ticker: str = Query(..., description="주식 종목 코드 또는 이름")
):
    """
    티커를 입력하면 해당 주식의 현재가와 관련 뉴스 3개를 반환합니다.
    """
    price = get_price_from_naver(ticker)
    news = get_news_from_naver(ticker)
    return {
        "ticker": ticker,
        "price": price,
        "news": news
    }


if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
