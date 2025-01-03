from flask import Flask, render_template, request
from amazon_paapi import AmazonApi

app = Flask(__name__)

# Amazon APIクレデンシャル (ダミーデータ)
ACCESS_KEY = "YOUR_AMAZON_ACCESS_KEY"
SECRET_KEY = "YOUR_AMAZON_SECRET_KEY"
PARTNER_TAG = "YOUR_PARTNER_TAG"
REGION = "JP"

# Amazon APIインスタンス
amazon_api = AmazonApi(ACCESS_KEY, SECRET_KEY, PARTNER_TAG, REGION)

# 商品検索関数
def search_products(keyword):
    try:
        response = amazon_api.search_items(keywords=keyword, search_index="All")
        products = []
        for item in response["SearchResult"]["Items"]:
            products.append({
                "title": item["ItemInfo"]["Title"]["DisplayValue"],
                "price": item.get("Offers", {}).get("Listings", [{}])[0].get("Price", {}).get("DisplayAmount", "N/A"),
                "url": item["DetailPageURL"],
                "image": item.get("Images", {}).get("Primary", {}).get("Medium", {}).get("URL", ""),
            })
        return products
    except Exception as e:
        print(f"APIエラー: {e}")
        return []

@app.route("/", methods=["GET", "POST"])
def index():
    keyword = None
    products = []
    if request.method == "POST":
        keyword = request.form["keyword"]
        products = search_products(keyword)
    return render_template("index.html", products=products, keyword=keyword)

if __name__ == "__main__":
    app.run(debug=True)
