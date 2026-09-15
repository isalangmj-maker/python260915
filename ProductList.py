from pathlib import Path
import sqlite3


DATABASE_PATH = Path(__file__).with_name("MyProduct.db")


class ProductDatabase:
    def __init__(self, database_path=DATABASE_PATH):
        self.database_path = Path(database_path)
        self.connection = sqlite3.connect(self.database_path)
        self.create_table()

    def create_table(self):
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS Products (
                productID INTEGER PRIMARY KEY,
                productName TEXT NOT NULL,
                productPrice INTEGER NOT NULL
            )
            """
        )
        self.connection.commit()

    def insert_product(self, product_name, product_price):
        cursor = self.connection.execute(
            "INSERT INTO Products (productName, productPrice) VALUES (?, ?)",
            (product_name, product_price),
        )
        self.connection.commit()
        return cursor.lastrowid

    def update_product(self, product_id, product_name, product_price):
        cursor = self.connection.execute(
            """
            UPDATE Products
            SET productName = ?, productPrice = ?
            WHERE productID = ?
            """,
            (product_name, product_price, product_id),
        )
        self.connection.commit()
        return cursor.rowcount > 0

    def delete_product(self, product_id):
        cursor = self.connection.execute(
            "DELETE FROM Products WHERE productID = ?",
            (product_id,),
        )
        self.connection.commit()
        return cursor.rowcount > 0

    def select_products(self, product_id=None):
        if product_id is None:
            cursor = self.connection.execute(
                "SELECT productID, productName, productPrice "
                "FROM Products ORDER BY productID"
            )
        else:
            cursor = self.connection.execute(
                "SELECT productID, productName, productPrice "
                "FROM Products WHERE productID = ?",
                (product_id,),
            )
        return cursor.fetchall()

    def insert_sample_products(self, total_count=1000):
        current_count = self.connection.execute(
            "SELECT COUNT(*) FROM Products"
        ).fetchone()[0]
        products_to_add = total_count - current_count
        if products_to_add <= 0:
            return 0

        start_number = current_count + 1
        products = [
            (f"전자제품 {number:04d}", number * 1000)
            for number in range(start_number, total_count + 1)
        ]
        self.connection.executemany(
            "INSERT INTO Products (productName, productPrice) VALUES (?, ?)",
            products,
        )
        self.connection.commit()
        return products_to_add

    def close(self):
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


def main():
    with ProductDatabase() as database:
        added_count = database.insert_sample_products(1000)
        products = database.select_products()
        print(f"데이터베이스: {DATABASE_PATH}")
        print(f"새로 추가한 샘플 데이터: {added_count}개")
        print(f"Products 테이블 전체 데이터: {len(products)}개")
        print("첫 번째 제품:", products[0])

        new_product_id = database.insert_product("신규 노트북", 1500000)
        database.update_product(new_product_id, "업데이트된 노트북", 1450000)
        print("CRUD 샘플 조회:", database.select_products(new_product_id)[0])
        database.delete_product(new_product_id)


if __name__ == "__main__":
    main()