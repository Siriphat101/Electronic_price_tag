from .entities.Device import Device

class ModelDevice():

    @classmethod
    def get_all_devices(self, db):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT * FROM esp32"""
            cursor.execute(sql)
            rows = cursor.fetchall()
            devices = []
            for row in rows:
                device = Device(row[0], row[1], row[2])
                devices.append(device)
            return devices
        except Exception as e:
            raise Exception(e)

    @classmethod
    def get_device_by_id(self, db, id):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT * FROM esp32 WHERE esp_chip_id = '{}'""".format(id)
            cursor.execute(sql)
            row = cursor.fetchone()
            if row is not None:
                device = Device(row[0], row[1], row[2])
                return device
            else:
                return None
        except Exception as e:
            raise Exception(e)