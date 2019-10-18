import flask_admin
import flask_login



class AuthenticatedMenuLink(flask_admin.base.MenuLink):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated


class UnauthenticatedMenuLink(flask_admin.base.MenuLink):
    def is_accessible(self):
        return not flask_login.current_user.is_authenticated


LOGIN_LINK = UnauthenticatedMenuLink(name='Login', endpoint='login')
LOGOUT_LINK = AuthenticatedMenuLink(name='Logout', endpoint='logout')
