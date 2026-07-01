import os
import requests
import xmltodict
from dotenv import load_dotenv

load_dotenv()

CUSTOMS_API_KEY = os.getenv("CUSTOMS_API_KEY")
CUSTOMS_BASE_URL = "https://apis.data.go.kr/1220000/Itemtrade/getItemtradeList"


def get_customs_import_export(strtYymm: int, endYymm: int, hsSgn: int | None = None):
    params = {
        "serviceKey": CUSTOMS_API_KEY,
        "strtYymm": strtYymm,
        "endYymm": endYymm,
    }

    if hsSgn:
        params["hsSgn"] = hsSgn

    response = requests.get(CUSTOMS_BASE_URL, params=params, timeout=10)

    if response.status_code != 200:
        raise Exception(f"Customs API error: {response.status_code}")

    data = xmltodict.parse(response.text)

    return data