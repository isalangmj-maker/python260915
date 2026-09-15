#db1.py
import sqlite3

#연결객체(일단 메모리에 저장)
conn = sqlite3.connect(':memory:')

#커서객체 생성
cur = conn.cursor()


#테이블 생성하는데 존재하지 않으면 생성
cur.execute("create table if not exists PhoneBbook (name text, phone text);")

#1건 입력
cur.execute("insert into PhoneBbook (name, phone) values ('홍길동', '010-1234-5678');")
#입력 매개변수 처리
name = '김철수'
phone = '010-9876-5432' 
cur.execute("insert into PhoneBbook (name, phone) values (?, ?);", (name, phone))
#여러건 입력
datalist = [('이영희', '010-1111-2222'), ('박민수', '010-3333-4444')]
cur.executemany("insert into PhoneBbook (name, phone) values (?, ?);", datalist)

#검색
cur.execute("select * from PhoneBbook;")
for row in cur:
    # print(row)
    print(f"이름: {row[0]}, 전화번호: {row[1]}")

print("---fetchone()---")
print(cur.fetchone())
print("---fetchmany()---")
print(cur.fetchmany(2))
print("---fetchall()---")
print(cur.fetchall())