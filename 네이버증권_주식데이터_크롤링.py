import csv
from pathlib import Path

import requests
from bs4 import BeautifulSoup


PAGE_URL = "https://stock.naver.com/market/stock/kr"
API_URL = "https://stock.naver.com/api/domestic/market/stock/default"
OUTPUT_FILE = Path("naver_stock_data.csv")
PAGE_COUNT = 20
PAGE_SIZE = 100

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Referer": PAGE_URL,
}


def get_page_soup(session):
    """BeautifulSoup으로 네이버 증권 페이지의 HTML을 읽는다."""
    response = session.get(PAGE_URL, timeout=15)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    return BeautifulSoup(response.text, "html.parser")


def get_stock_data(
    session,
    start_index,
    market_type="ALL",
    order_type="marketSum",
    page_size=PAGE_SIZE,
):
    """네이버 증권 화면이 사용하는 국내 주식 목록 API를 호출한다."""
    params = {
        "tradeType": "KRX",
        "marketType": market_type,
        "orderType": order_type,
        "startIdx": start_index,
        "pageSize": page_size,
    }
    response = session.get(API_URL, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def get_all_stock_data(session):
    """시가총액순으로 최대 20페이지의 국내 주식 데이터를 수집한다."""
    all_stocks = []
    seen_codes = set()

    for page_number in range(PAGE_COUNT):
        page_stocks = get_stock_data(session, start_index=page_number)

        if not page_stocks:
            print(f"{page_number + 1}페이지부터 데이터가 없어 수집을 종료합니다.")
            break

        new_stocks = [
            stock
            for stock in page_stocks
            if stock.get("itemcode") and stock["itemcode"] not in seen_codes
        ]
        all_stocks.extend(new_stocks)
        seen_codes.update(stock["itemcode"] for stock in new_stocks)
        print(
            f"{page_number + 1}/{PAGE_COUNT}페이지 수집 완료 "
            f"({len(new_stocks)}개, 누적 {len(all_stocks)}개)"
        )

    return all_stocks


def to_number(value):
    """빈 값은 그대로 두고 숫자 문자열은 CSV에서 보기 좋게 변환한다."""
    if value in (None, ""):
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return value
    return int(number) if number.is_integer() else number


def save_csv(stock_data):
    fields = [
        ("종목명", "itemname"),
        ("종목코드", "itemcode"),
        ("현재가", "nowPrice"),
        ("전일대비", "prevChangePrice"),
        ("등락률(%)", "prevChangeRate"),
        ("거래량", "tradeVolume"),
        ("거래대금", "tradeAmount"),
        ("외국인보유율(%)", "frgnHoldRate"),
        ("시가총액", "marketSum"),
    ]

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow([label for label, _ in fields])
        for stock in stock_data:
            writer.writerow(
                [
                    stock.get(key, "")
                    if key in ("itemname", "itemcode")
                    else to_number(stock.get(key))
                    for _, key in fields
                ]
            )


def main():
    with requests.Session() as session:
        page_soup = get_page_soup(session)
        stock_data = get_all_stock_data(session)

    if not stock_data:
        print("주식 데이터를 찾지 못했습니다.")
        return

    # 현재 페이지의 제목은 BeautifulSoup으로 확인한다.
    page_title = page_soup.title.get_text(strip=True) if page_soup.title else PAGE_URL
    save_csv(stock_data)

    print(f"페이지: {page_title}")
    print(f"총 {len(stock_data)}개 종목을 수집했습니다.")
    print(f"저장 파일: {OUTPUT_FILE.resolve()}")
    print("상위 5개 종목:")
    for stock in stock_data[:5]:
        print(
            f"- {stock['itemname']}: {to_number(stock.get('nowPrice')):,}원 "
            f"({stock.get('prevChangeRate', '')}%)"
        )


if __name__ == "__main__":
    main()