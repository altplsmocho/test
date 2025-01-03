from flask import Flask, render_template

app = Flask(__name__)

# 商品データ
products = [
    {
        "name": "Product 1",
        "description": "Amazing product for daily use!",
        "link": "https://www.amazon.com/"
    },
    {
        "name": "Product 2",
        "description": "Another great item I recommend!",
        "link": "https://www.amazon.com/"
    }
]

@app.route('/')
def home():
    return render_template("index.html", products=products)

if __name__ == '__main__':
    app.run(debug=True)
