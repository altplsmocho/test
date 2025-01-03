# ファイル: app.py

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from amazon_paapi import AmazonApi, SearchItemsRequest
import datetime

app = Flask(__name__)

# データベース設定
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///search_history.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# データベースモデル
class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# 初回実行時にデータベース作成
with app.app_context():
    db.create_all()

# Amazon Product Advertising APIクレデンシャル
#ACCESS_KEY = "YOUR_AMAZON_ACCESS_KEY"
#SECRET_KEY = "YOUR_AMAZON_SECRET_KEY"
#PARTNER_TAG = "YOUR_PARTNER_TAG"
#REGION = "JP"

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
            # 検索履歴を保存
            new_history = SearchHistory(keyword=keyword)
            db.session.add(new_history)
            db.session.commit()
            # 商品検索
            products = search_products(keyword)

    # 履歴取得
    search_history = SearchHistory.query.order_by(SearchHistory.timestamp.desc()).all()
    return render_template("index.html", products=products, history=search_history)

# 再検索ルート
@app.route("/search/<keyword>")
def search_again(keyword):
    products = search_products(keyword)
    search_history = SearchHistory.query.order_by(SearchHistory.timestamp.desc()).all()
    return render_template("index.html", products=products, history=search_history)

# 個別履歴削除
@app.route("/delete/<int:history_id>")
def delete_history(history_id):
    history = SearchHistory.query.get(history_id)
    if history:
        db.session.delete(history)
        db.session.commit()
    return redirect(url_for("index"))

# 全履歴削除
@app.route("/delete_all")
def delete_all_history():
    db.session.query(SearchHistory).delete()
    db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
