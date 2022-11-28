class Product():

    def __init__(self, id, product_id, product_name, product_price):
        self.id = id
        self.product_id = product_id
        self.product_name = product_name
        self.product_price = product_price

    def __str__(self):
        return str(self.id) + ' ' + self.product_id + ' ' + self.product_name + ' ' + str(self.product_price)

    # def products(id, product_id, product_name, product_price):
    #     return Product(id, product_id, product_name, product_price)

