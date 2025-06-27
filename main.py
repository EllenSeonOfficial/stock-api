from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
import uvicorn


app = FastAPI()

def get_price_from_naver(ticker: str) -> str:
    url = f"https://finance.naver.com/item/main.naver?code={ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    price_tag = soup.select_one("p.no_today span.blind")
    return int(price_tag.text.replace(",", "").strip()) if price_tag else "N/A"

def get_news_from_naver_mobile(ticker: str):
    url = f"https://m.stock.naver.com/domestic/stock/{ticker}/news"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    news_list = []
    for item in soup.select("ul.NewsList_list__YIK1t li")[:3]:
        a_tag = item.select_one("a")
        title_tag = item.select_one("strong")
        if a_tag and title_tag:
            news_list.append({
                "title": title_tag.text.strip(),
                "url": "https://m.stock.naver.com" + a_tag.get("href")
            })
    return news_list

@app.get("/stock", response_class=JSONResponse)
def get_stock(ticker: str = Query(..., description="종목 코드 (예: 005930)")):
    price = get_price_from_naver(ticker)
    news = get_news_from_naver_mobile(ticker)
    return {
        "ticker": ticker,
        "price": price,
        "news": news
    }

@app.get("/")
def read_root():
    return {"message": "Hello, world!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
