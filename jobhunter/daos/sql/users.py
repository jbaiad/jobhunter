import flask_login
import werkzeug.security as wkzg_sec

import jobhunter.daos.interfaces.users as interfaces
from jobhunter.daos.sql import common
from jobhunter.daos.sql import schemata


class User(schemata.User, flask_login.UserMixin, interfaces.AbstractUser):
    @staticmethod
    def get_user(username):
        return common.Session().query(User).filter_by(username=username).first()

    @staticmethod
    def get_user_by_email(email):
        return common.Session().query(User).filter_by(email=email).first()

    @staticmethod
    def get_user_by_id(id):
        return common.Session().query(User).filter_by(id=id).first()

    @staticmethod
    def create_user(username, email, password):
        user = User(username=username, email=email)
        user.set_password(password)
        session = common.Session()
        session.add(user)
        session.commit()

    def set_password(self, password):
        self.password_hash = wkzg_sec.generate_password_hash(password)

    def check_password(self, password):
        return wkzg_sec.check_password_hash(self.password_hash, password)


__all__ = ['User']
