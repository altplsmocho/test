# ファイル: app.py

from flask import Flask, render_template, request
from amazon_paapi import AmazonApi, SearchItemsRequest

app = Flask(__name__)

# Amazon Product Advertising APIクレデンシャル
ACCESS_KEY = "YOUR_AMAZON_ACCESS_KEY"
SECRET_KEY = "YOUR_AMAZON_SECRET_KEY"
PARTNER_TAG = "YOUR_PARTNER_TAG"
REGION = "us-east-1"

# 商品検索関数
def search_products(keyword):
    amazon_api = AmazonApi(ACCESS_KEY, SECRET_KEY, PARTNER_TAG, REGION)
    product_details = []

    try:
        response = amazon_api.search_items(SearchItemsRequest(keywords=keyword, search_index="All"))
        for item in response["SearchResult"]["Items"]:
            product = {
                "asin": item["ASIN"],
                "title": item["ItemInfo"]["Title"]["DisplayValue"],
                "price": item.get("Offers", {}).get("Listings", [{}])[0].get("Price", {}).get("DisplayAmount", "N/A"),
                "url": item["DetailPageURL"],
                "image": item.get("Images", {}).get("Primary", {}).get("Medium", {}).get("URL", ""),
            }
            product_details.append(product)
    except Exception as e:
        print(f"エラーが発生しました: {e}")

    return product_details

# ホームページ
@app.route("/", methods=["GET", "POST"])
def index():
    products = []
    if request.method == "POST":
        keyword = request.form.get("keyword")
        if keyword:
            products = search_products(keyword)

    return render_template("index.html", products=products)

if __name__ == "__main__":
    app.run(debug=True)
