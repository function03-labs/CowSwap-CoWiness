import os

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


def fetch_order(oid):
    orderbook_url = os.getenv("ORDERBOOK_URL")
    url = orderbook_url + f"/api/v1/orders/{oid}"
    return requests.get(url).json()
