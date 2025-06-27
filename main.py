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

def fetch_naver_news(stock_code):
    url = f"https://m.stock.naver.com/domestic/stock/{stock_code}/news"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    news_list = []

    for li in soup.select("ul.NewsList_list__YIK1t > li.NewsList_item__rFMSZ"):
        # 광고 제외
        if "NewsList_item_ad__vUmaD" in li.get("class", []):
            continue

        # 링크와 제목 추출
        link_tag = li.find("a")
        if not link_tag:
            continue
        link = link_tag["href"]
        title = link_tag.get_text(strip=True)

        news_list.append({
            "title": title,
            "url": f"https://m.stock.naver.com{link}"
        })

    return news_list[:5]  # 상위 5개만 반환


@app.get("/stock", response_class=JSONResponse)
def get_stock(ticker: str = Query(..., description="종목 코드 (예: 005930)")):
    price = get_price_from_naver(ticker)
    news = fetch_naver_news(ticker)
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
