import logging

import flask
import flask_admin
import flask_login

from jobhunter import config
from jobhunter.app import links
from jobhunter.app import routes
from jobhunter.app import views
from jobhunter.daos import sql as daos


APP = flask.Flask(__name__)
APP.logger.handlers.extend(logging.getLogger('gunicorn.error').handlers)
APP.config.update(config.to_dict())                 # pylint: disable=no-member
APP.config['ENV'] = config.name                     # pylint: disable=no-member
routes.attach(APP)

ADMIN = flask_admin.Admin(APP, name=APP.config['APP_NAME'], template_mode='bootstrap3', url='/',
                          index_view=views.ADMIN_INDEX_VIEW)

ADMIN.add_view(views.JOB_VIEW)
ADMIN.add_view(views.JOB_WATCH_VIEW)
ADMIN.add_link(links.LOGIN_LINK)
ADMIN.add_link(links.LOGOUT_LINK)
LOGIN_MANAGER = flask_login.LoginManager(APP)

@LOGIN_MANAGER.user_loader
def load_user(identifier):
    return daos.User.get_user_by_id(identifier)     #pylint: disable=no-member

@APP.context_processor
def inject():
    return dict(admin=ADMIN, get_url=flask.url_for, h=flask_admin.helpers, _gettext=flask_admin.babel.gettext,
                _ngettext=flask_admin.babel.ngettext, log=print)
