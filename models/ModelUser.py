from .entities.User import User


class ModelUser():

    @classmethod
    def login(self, db, user):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT id, username, password, fullname FROM user WHERE username = '{}'""".format(user.username)
            cursor.execute(sql)
            row = cursor.fetchone()
            if row is not None:
                user = User(row[0], row[1], User.check_password(row[2], user.password), row[3])
                return user
            else:
                return None
        except Exception as e:
            raise Exception(e)

    @classmethod
    def get_by_id(self, db, id):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT id, username, password, fullname FROM user WHERE id = '{}'""".format(id)
            cursor.execute(sql)
            row = cursor.fetchone()
            if row is not None:
                return User(row[0], row[1], None, row[3])

            else:
                return None
        except Exception as e:
            raise Exception(e)
