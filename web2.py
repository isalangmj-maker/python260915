#web2.py

#크롤링을 위한 선언
from bs4 import BeautifulSoup
import urllib.request
#정규표현식
import re

#파일에 저장
f = open("clien.txt", "wt", encoding="UTF-8")


hdr = {'User-Agent': 'Mozilla/5.0'}
#페이징처리
for i in range(0, 10):
    url = f"https://www.clien.net/service/board/sold?&od=T31&category=0&p={i}"
    print(url)
    #요청객체
    req = urllib.request.Request(url, headers=hdr)
    data = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(data, "html.parser")

    for tag in soup.find_all("span", attrs={"data-role": "list-title-text"}):
        title = tag.text.strip()  #strip() : 문자열 양쪽 공백 제거
        title = title.replace("\n", "")  #문자열 내부의 줄바꿈 제거
        if re.search("애플", title):  #정규표현식으로 아이폰이 포함된 문자열만 검색
            print(title)
            f.write(title + "\n")

f.close()

# <span class="subject_fixed" data-role="list-title-text" title="아이폰 17프로 512 실버 팝니다 (상태 최상)">
# 							아이폰 17프로 512 실버 팝니다 (상태 최상)
# 						</span>