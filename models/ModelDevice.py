from .entities.Device import Device



class ModelDevice():

    @classmethod
    def get_all_devices(self, db):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT * FROM devices"""
            cursor.execute(sql)
            rows = cursor.fetchall()
            devices = []
            for row in rows:
                device = Device(row[0], row[1], row[2], row[3], row[4])
                devices.append(device)
            return devices
        except Exception as e:
            raise Exception(e)

    # @classmethod
    # def get_device_by_id(self, db, id):
    #     try:
    #         cursor = db.connection.cursor()
    #         sql = """SELECT * FROM devices WHERE chipID = '{}'""".format(id)
    #         cursor.execute(sql)
    #         row = cursor.fetchone()
    #         if row is not None:
    #             device = Device(row[0], row[1], row[2])
    #             return device
    #         else:
    #             return None
    #     except Exception as e:
    #         raise Exception(e)
        
    @classmethod
    def count_device(self, db):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT COUNT(id) FROM devices"""
            cursor.execute(sql)
            count = cursor.fetchone()
            for i in count:
                count = i
            
            return count
        except Exception as e:
            raise Exception(e)
        
    @classmethod
    def statusON_device(self, db):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT COUNT(id) FROM devices WHERE status = 1"""
            cursor.execute(sql)
            on_status = cursor.fetchone()
            for i in on_status:
                on_status = i
            return on_status
        except Exception as e:
            raise Exception(e)
        
    @classmethod
    def statusOFF_device(self, db):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT COUNT(id) FROM devices WHERE status = 0"""
            cursor.execute(sql)
            off_status = cursor.fetchone()
            for i in off_status:
                off_status = i
            return off_status
        except Exception as e:
            raise Exception(e)
        
        