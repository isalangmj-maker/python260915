import re
import time
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup


SEARCH_WORD = "반도체"
ARTICLE_COUNT = 10
SEARCH_URL = (
    "https://search.naver.com/search.naver?where=news&sm=tab_jum&query="
    + quote_plus(SEARCH_WORD)
)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
}


def get_soup(url):
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def get_article_links(search_soup):
    """검색 결과에서 네이버 뉴스 원문 링크만 중복 없이 가져온다."""
    links = []
    seen = set()

    for link_tag in search_soup.select('a[href*="n.news.naver.com/mnews/article/"]'):
        link = link_tag.get("href")
        if link and link not in seen:
            seen.add(link)
            links.append(link)

    return links[:ARTICLE_COUNT]


def get_title(article_soup):
    title_tag = article_soup.select_one("h2#title_area, h2.media_end_head_headline")
    return title_tag.get_text(" ", strip=True) if title_tag else "제목 없음"


def get_content(article_soup):
    content_tag = article_soup.select_one(
        "#dic_area, article#dic_area, div._article_content"
    )
    if content_tag is None:
        return "본문을 찾지 못했습니다."

    for tag in content_tag.select("script, style, .byline, .copyright, .reporter_area"):
        tag.decompose()

    content = content_tag.get_text("\n", strip=True)
    return re.sub(r"\n{2,}", "\n", content)


def main():
    search_soup = get_soup(SEARCH_URL)
    article_links = get_article_links(search_soup)

    if not article_links:
        print("네이버 뉴스 링크를 찾지 못했습니다.")
        return

    with open(f"{SEARCH_WORD}_뉴스기사.txt", "w", encoding="utf-8") as file:
        for number, article_link in enumerate(article_links, start=1):
            try:
                article_soup = get_soup(article_link)
                title = get_title(article_soup)
                content = get_content(article_soup)

                file.write(f"[{number}] {title}\n")
                file.write(f"URL: {article_link}\n")
                file.write(content + "\n")
                file.write("=" * 80 + "\n\n")
                print(f"{number}번째 기사 수집 완료: {title}")
                time.sleep(0.5)
            except requests.RequestException as error:
                print(f"기사 요청 실패: {article_link}\n{error}")

    print(f"총 {len(article_links)}개 기사를 {SEARCH_WORD}_뉴스기사.txt에 저장했습니다.")


if __name__ == "__main__":
    main()