import flask
import flask_admin
import flask_admin.contrib.sqla as sqla
import flask_login

import jobhunter.daos.sql as daos


app = flask.Flask(__name__)
app.config['FLASK_ADMIN_SWATCH'] = 'simplex'
admin = flask_admin.Admin(app, name='jobhunter', template_mode='bootstrap3')
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

admin.add_view(daos.JobView)
    

if __name__ == "__main__":
    app.run(debug=True)
