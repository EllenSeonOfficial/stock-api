from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def home():
    return "Korean Stock API is running"

@app.route('/stock', methods=['POST'])
def get_stock():
    data = request.get_json()
    ticker = data.get("ticker", "")[:6]  # 티커 앞 6자리만 사용

    url = f"https://finance.naver.com/item/main.nhn?code={ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    try:
        price = soup.select_one("p.no_today span.blind").text.replace(",", "")
        return jsonify({"price": float(price)})
    except:
        return jsonify({"error": "Unable to fetch price"}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
