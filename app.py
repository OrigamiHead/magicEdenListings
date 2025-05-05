from flask import Flask, render_template
import requests
import time

app = Flask(__name__)

API_KEY = "YOUR_API_KEY"

BASE_URL = "https://api-mainnet.magiceden.dev/v3/rtp/berachain/orders/asks/v5"
CONTRACT = "0x88888888A9361f15AAdBAca355A6B2938C6A674e"

HEADERS = {
    "accept": "*/*",
    "Authorization": f"Bearer {API_KEY}",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Encoding": "gzip, deflate"
}

def fetch_all_orders():
    clean_orders = []
    continuation = None

    with requests.Session() as session:
        session.headers.update(HEADERS)

        while True:
            params = {
                "contracts": CONTRACT,
                "includeCriteriaMetadata": "false",
                "includeRawData": "false",
                "includeDynamicPricing": "false",
                "excludeEOA": "false",
                "normalizeRoyalties": "false",
                "sortBy": "createdAt"
            }

            if continuation:
                params["continuation"] = continuation

            try:
                response = session.get(BASE_URL, params=params, timeout=5)
                response.raise_for_status()
                data = response.json()

                for order in data.get("orders", []):
                    clean_orders.append({
                        "tokenId": order["criteria"]["data"]["token"]["tokenId"],
                        "price": order["price"]["amount"]["decimal"],
                        "maker": order["maker"]
                    })

                continuation = data.get("continuation")
                if not continuation:
                    break

                time.sleep(2)

            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
                break

    return clean_orders

@app.route('/')
def index():
    orders = fetch_all_orders()
    total_orders = len(orders)  # Contamos la cantidad de órdenes
    return render_template('index.html', orders=orders, total_orders=total_orders)

if __name__ == '__main__':
    app.run(debug=True)
