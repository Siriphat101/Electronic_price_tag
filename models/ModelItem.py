from .entities.ItemData import ItemData

class ModelItem:
    
    @classmethod
    def getItem(self,db):
        try:
            cur = db.connection.cursor()
            cur.execute("SELECT devices.name as Node, products.product_name as Product, products.product_price as Price, devices.status as Status FROM devices INNER JOIN products ON devices.product_id = products.product_id")
            rows = cur.fetchall()
            item = []
            for row in rows:
                item.append(ItemData(row[0],row[1],row[2],row[3]))
            
            return item
        except Exception as e:
            raise Exception(e)
    