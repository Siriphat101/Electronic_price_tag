# from flask import jsonify

from .entities.Product import Product


class ModelProduct:

    @classmethod
    def get_all_products(self, db):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT id, product_id, product_name, product_price FROM products"""
            cursor.execute(sql)
            rows = cursor.fetchall()
            products = []
            for row in rows:
                products.append(Product(row[0], row[1], row[2], row[3]))
                # print("Product: ", row[0], row[1], row[2], row[3])
            return products
        except Exception as e:
            raise Exception(e)
        
    # @classmethod
    # def get_all_product_id(self, db):
    #     try:
    #         cursor = db.connection.cursor()
    #         sql = """SELECT product_id FROM products"""
    #         cursor.execute(sql)
    #         rows = cursor.fetchall()
    #         all_id_product = []
    #         for row in rows:
    #             all_id_product.append(row[0])
    #             print(all_id_product)
    #         return all_id_product
    #     except Exception as e:
    #         raise Exception(e)

    @classmethod
    def get_by_id(self, db, id):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT id, product_id, product_name, product_price FROM products WHERE id = '{}'""".format(id)
            cursor.execute(sql)
            row = cursor.fetchone()
            if row is not None:
                return Product(row[0], row[1], row[2], row[3])
            else:
                return None
        except Exception as e:
            raise Exception(e)

#    add_product to database
    @classmethod
    def add_product(self, db, product):
        try:
            cursor = db.connection.cursor()
            sql = """INSERT INTO products (product_id, product_name, product_price) VALUES ('{}', '{}', '{}')""".format(
                product.product_id, product.product_name, product.product_price)
            cursor.execute(sql)
            db.connection.commit()
        except Exception as e:
            raise Exception(e)
        
        
    
            
