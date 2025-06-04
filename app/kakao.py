import requests, os
from dotenv import load_dotenv

load_dotenv()
KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")

def search_photo_studios(query: str, page: int, size: int):
    headers = {"Authorization": KAKAO_API_KEY}
    params = {
        "query": query,
        "page": page,
        "size": size
    }

    res = requests.get("https://dapi.kakao.com/v2/local/search/keyword.json", headers=headers, params=params)

    print("=== Kakao API response ===")
    print(res.status_code)
    print(res.json())

    return res.json()
