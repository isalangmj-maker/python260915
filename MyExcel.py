from pathlib import Path

import openpyxl
from openpyxl.styles import Font


OUTPUT_FILE = Path(__file__).with_name("ProductList.xlsx")


def create_product_list():
    product_names = [
        "노트북", "태블릿", "스마트폰", "스마트워치", "무선이어폰",
        "블루투스 스피커", "모니터", "키보드", "마우스", "웹캠",
        "프린터", "스캐너", "공유기", "외장하드", "USB 메모리",
        "보조배터리", "충전기", "전자책 리더기", "디지털카메라", "액션캠",
    ]

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "전자제품 목록"

    headers = ["제품ID", "제품명", "가격", "수량"]
    worksheet.append(headers)

    for cell in worksheet[1]:
        cell.font = Font(bold=True)

    for product_id in range(1, 101):
        product_name = f"{product_names[(product_id - 1) % len(product_names)]} {product_id:03d}"
        price = 10000 + product_id * 15000
        quantity = (product_id * 7) % 50 + 1
        worksheet.append([product_id, product_name, price, quantity])

    worksheet.column_dimensions["A"].width = 12
    worksheet.column_dimensions["B"].width = 24
    worksheet.column_dimensions["C"].width = 14
    worksheet.column_dimensions["D"].width = 12

    for cell in worksheet["C"][1:]:
        cell.number_format = '#,##0'

    workbook.save(OUTPUT_FILE)
    print(f"{OUTPUT_FILE}에 전자제품 {len(worksheet['A']) - 1}개를 저장했습니다.")


if __name__ == "__main__":
    create_product_list()
