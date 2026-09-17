import sqlite3
import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


DATABASE_PATH = "MyProduct2.db"


class ProductDatabase:
    def __init__(self, database_path=DATABASE_PATH):
        self.connection = sqlite3.connect(database_path)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS MyProduct (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price INTEGER NOT NULL
            )
            """
        )
        self.connection.commit()

    def add_product(self, name, price):
        cursor = self.connection.execute(
            "INSERT INTO MyProduct (name, price) VALUES (?, ?)",
            (name, price),
        )
        self.connection.commit()
        return cursor.lastrowid

    def update_product(self, product_id, name, price):
        cursor = self.connection.execute(
            "UPDATE MyProduct SET name = ?, price = ? WHERE id = ?",
            (name, price, product_id),
        )
        self.connection.commit()
        return cursor.rowcount > 0

    def delete_product(self, product_id):
        cursor = self.connection.execute(
            "DELETE FROM MyProduct WHERE id = ?",
            (product_id,),
        )
        self.connection.commit()
        return cursor.rowcount > 0

    def find_products(self, keyword=""):
        keyword = keyword.strip()
        if not keyword:
            cursor = self.connection.execute(
                "SELECT id, name, price FROM MyProduct ORDER BY id"
            )
        elif keyword.isdigit():
            cursor = self.connection.execute(
                "SELECT id, name, price FROM MyProduct "
                "WHERE id = ? OR name LIKE ? ORDER BY id",
                (int(keyword), f"%{keyword}%"),
            )
        else:
            cursor = self.connection.execute(
                "SELECT id, name, price FROM MyProduct "
                "WHERE name LIKE ? ORDER BY id",
                (f"%{keyword}%",),
            )
        return cursor.fetchall()

    def close(self):
        self.connection.close()


class ProductWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.database = ProductDatabase()
        self.setWindowTitle("자전거용품 관리")
        self.resize(780, 620)
        self.build_ui()
        self.load_products()

    def build_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(28, 24, 28, 28)
        main_layout.setSpacing(16)

        title = QLabel("자전거용품 관리")
        title.setObjectName("titleLabel")
        subtitle = QLabel("라이딩에 필요한 장비를 한눈에 관리하세요")
        subtitle.setObjectName("subtitleLabel")
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        form_layout = QFormLayout()
        form_layout.setContentsMargins(18, 14, 18, 14)
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(10)
        form_layout.setObjectName("formPanel")
        self.id_input = QLineEdit()
        self.id_input.setObjectName("idInput")
        self.id_input.setReadOnly(True)
        self.name_input = QLineEdit()
        self.name_input.setObjectName("nameInput")
        self.price_input = QLineEdit()
        self.price_input.setObjectName("priceInput")
        self.price_input.setPlaceholderText("숫자만 입력")
        form_layout.addRow("ID", self.id_input)
        form_layout.addRow("상품명", self.name_input)
        form_layout.addRow("가격", self.price_input)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        self.add_button = QPushButton("입력")
        self.add_button.setObjectName("addButton")
        self.update_button = QPushButton("수정")
        self.update_button.setObjectName("updateButton")
        self.delete_button = QPushButton("삭제")
        self.delete_button.setObjectName("deleteButton")
        self.clear_button = QPushButton("초기화")
        self.clear_button.setObjectName("clearButton")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)

        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(18, 0, 18, 0)
        search_layout.setSpacing(10)
        search_layout.addWidget(QLabel("검색"))
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("상품명 또는 ID")
        self.search_button = QPushButton("검색")
        self.search_button.setObjectName("searchButton")
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)

        self.table_widget = QTableWidget(0, 3)
        self.table_widget.setObjectName("productTable")
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setShowGrid(False)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setMinimumHeight(280)
        self.table_widget.setHorizontalHeaderLabels(["ID", "상품명", "가격"])
        self.table_widget.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table_widget.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.table_widget.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table_widget.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table_widget.cellClicked.connect(self.select_product)

        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.table_widget)
        self.setCentralWidget(central_widget)

        self.add_button.clicked.connect(self.add_product)
        self.update_button.clicked.connect(self.update_product)
        self.delete_button.clicked.connect(self.delete_product)
        self.clear_button.clicked.connect(self.clear_inputs)
        self.search_button.clicked.connect(self.search_products)
        self.search_input.returnPressed.connect(self.search_products)

        self.setStyleSheet(
            """
            QMainWindow {
                background: #e8f3f1;
            }
            QWidget#centralWidget {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #e9f7f4, stop: 0.55 #f5f8f4, stop: 1 #fff4df
                );
            }
            QLabel#titleLabel {
                color: #123b42;
                font-size: 30px;
                font-weight: 800;
                padding-top: 4px;
            }
            QLabel#subtitleLabel {
                color: #668080;
                font-size: 13px;
                padding-bottom: 4px;
            }
            QFormLayout {
                background: rgba(255, 255, 255, 225);
                border: 1px solid #cce2dd;
                border-radius: 14px;
            }
            QFormLayout QLabel {
                color: #31575a;
                font-size: 13px;
                font-weight: 700;
            }
            QLineEdit {
                min-height: 34px;
                padding: 0 12px;
                color: #173d42;
                background: #ffffff;
                border: 1px solid #c5d9d5;
                border-radius: 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #16a6a0;
                background: #f7fffd;
            }
            QLineEdit#idInput {
                color: #819999;
                background: #edf4f2;
            }
            QPushButton {
                min-height: 38px;
                padding: 0 20px;
                border: none;
                border-radius: 9px;
                color: white;
                font-size: 13px;
                font-weight: 700;
            }
            QPushButton:hover {
                padding-bottom: 2px;
            }
            QPushButton#addButton {
                background: #149e96;
            }
            QPushButton#addButton:hover {
                background: #0e827b;
            }
            QPushButton#updateButton {
                background: #3578bd;
            }
            QPushButton#updateButton:hover {
                background: #28629c;
            }
            QPushButton#deleteButton {
                background: #d95f5f;
            }
            QPushButton#deleteButton:hover {
                background: #ba4949;
            }
            QPushButton#clearButton {
                color: #31575a;
                background: #dce9e5;
            }
            QPushButton#clearButton:hover {
                background: #c9ddd8;
            }
            QPushButton#searchButton {
                min-width: 72px;
                background: #f29a4a;
            }
            QPushButton#searchButton:hover {
                background: #d98032;
            }
            QTableWidget#productTable {
                background: rgba(255, 255, 255, 240);
                alternate-background-color: #f0f8f6;
                border: 1px solid #cce2dd;
                border-radius: 12px;
                color: #24484c;
                font-size: 13px;
                selection-background-color: #bde9e1;
                selection-color: #123b42;
            }
            QHeaderView::section {
                min-height: 36px;
                padding: 0 10px;
                color: white;
                background: #1d6067;
                border: none;
                font-size: 13px;
                font-weight: 700;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e0eeeb;
            }
            QScrollBar:vertical {
                width: 10px;
                margin: 4px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                min-height: 30px;
                background: #a8cbc5;
                border-radius: 5px;
            }
            """
        )

    def read_product_inputs(self):
        name = self.name_input.text().strip()
        price_text = self.price_input.text().strip()
        if not name:
            QMessageBox.warning(self, "입력 오류", "상품명을 입력하세요.")
            return None
        if not price_text.isdigit():
            QMessageBox.warning(self, "입력 오류", "가격은 0 이상의 정수여야 합니다.")
            return None
        return name, int(price_text)

    def add_product(self):
        product = self.read_product_inputs()
        if product is None:
            return
        self.database.add_product(*product)
        self.load_products()
        self.clear_inputs()

    def update_product(self):
        product = self.read_product_inputs()
        product_id = self.id_input.text().strip()
        if product is None or not product_id.isdigit():
            if product is not None:
                QMessageBox.warning(self, "수정 오류", "수정할 상품을 선택하세요.")
            return
        self.database.update_product(int(product_id), *product)
        self.load_products()
        self.clear_inputs()

    def delete_product(self):
        product_id = self.id_input.text().strip()
        if not product_id.isdigit():
            QMessageBox.warning(self, "삭제 오류", "삭제할 상품을 선택하세요.")
            return
        answer = QMessageBox.question(
            self,
            "삭제 확인",
            "선택한 상품을 삭제하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.database.delete_product(int(product_id))
            self.load_products()
            self.clear_inputs()

    def search_products(self):
        self.load_products(self.search_input.text())

    def load_products(self, keyword=""):
        products = self.database.find_products(keyword)
        self.table_widget.setRowCount(len(products))
        for row, (product_id, name, price) in enumerate(products):
            id_item = QTableWidgetItem(str(product_id))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            price_item = QTableWidgetItem(f"{price:,}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table_widget.setItem(row, 0, id_item)
            self.table_widget.setItem(row, 1, QTableWidgetItem(name))
            self.table_widget.setItem(row, 2, price_item)

    def select_product(self, row, _column):
        self.id_input.setText(self.table_widget.item(row, 0).text())
        self.name_input.setText(self.table_widget.item(row, 1).text())
        self.price_input.setText(self.table_widget.item(row, 2).text().replace(",", ""))

    def clear_inputs(self):
        self.id_input.clear()
        self.name_input.clear()
        self.price_input.clear()

    def closeEvent(self, event):
        self.database.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductWindow()
    window.show()
    sys.exit(app.exec())