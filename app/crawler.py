import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def fetch_reviews_with_scroll(driver, place_url, max_scrolls=5):
    driver.get(f"{place_url}#comment")

    wait = WebDriverWait(driver, 10)
    try:
        # 리뷰 목록이 보일 때까지 대기
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.list_review")))
    except Exception as e:
        print(f"[{place_url}] 리뷰 영역 로딩 실패 {e}")
        return []

    scroll_container = driver.find_element(By.CSS_SELECTOR, "ul.list_review")

    # 스크롤 반복
    last_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
    for _ in range(max_scrolls):
        driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", scroll_container)
        time.sleep(1.5)
        new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
        if new_height == last_height:
            break
        last_height = new_height

    # BeautifulSoup으로 파싱
    soup = BeautifulSoup(driver.page_source, "html.parser")
    reviews = []

    for li in soup.select("ul.list_review > li"):
        review_box = li.select_one("div.inner_review")
        if not review_box:
            continue

        content_tag = review_box.select_one("div.review_detail > div.wrap_review > .link_review > p.desc_review")
        date_tag = review_box.select_one("div.review_detail > .info_grade > .txt_date")
        rating_tag = review_box.select("div.review_detail > .info_grade > span.starred_grade > span.screen_out")

        content = content_tag.get_text(strip=True) if content_tag else None
        date = date_tag.get_text(strip=True) if date_tag else None
        rating = rating_tag[1].get_text(strip=True) if len(rating_tag) >= 2 else None

        reviews.append({
            "content": content,
            "date": date,
            "rating": rating
        })

    return reviews


def extract_place_details(place_url: str) -> dict:
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    drv = webdriver.Chrome(options=opts)
    try:
        drv.set_page_load_timeout(20)
        drv.get(f"{place_url}#home")
        time.sleep(4)
        drv.execute_script("window.scrollTo(0, 600)")   # lazy-load 트리거
        time.sleep(2)

        soup = BeautifulSoup(drv.page_source, "html.parser")

        hp_tag = soup.select_one(".detail_info.info_suggest > .row_detail > .link_detail")
        homepage = hp_tag["href"] if hp_tag else None

        oh = soup.select_one(".line_fold > .txt_detail")
        open_hour = oh.get_text(" ", strip=True) if oh else None


        reviews = fetch_reviews_with_scroll(drv, place_url)

        return {"open_hour": open_hour, "homepage": homepage, "reviews": reviews}
    finally:
        drv.quit()


# if __name__ == "__main__":
#     from selenium import webdriver
#
#     options = webdriver.ChromeOptions()
#     options.add_argument("--headless")  # 필요시 주석
#     driver = webdriver.Chrome(options=options)
#
#     try:
#         reviews = fetch_reviews_with_scroll(driver, "459560376")
#         for r in reviews:
#             print(r)
#     finally:
#         driver.quit()