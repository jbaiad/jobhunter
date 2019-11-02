import http
import os

import flask
import flask_login
import werkzeug.urls as wkzg_urls

from jobhunter.app import forms
from jobhunter.daos import sql as daos


def attach_favicons(app):
    @app.route('/favicon.ico')
    def favicon():
        return flask.send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

    @app.route('/android-icon-36x36.png')
    def android_icon_36x36():
        return flask.send_from_directory(os.path.join(app.root_path, 'static'), 'android-icon-36x36.png')

    @app.route('/android-icon-48x48.png')
    def android_icon_48x48():
        return flask.send_from_directory(os.path.join(app.root_path, 'static'), 'android-icon-48x48.png')

    @app.route('/android-icon-72x72.png')
    def android_icon_72x72():
        return flask.send_from_directory(os.path.join(app.root_path, 'static'), 'android-icon-72x72.png')

    @app.route('/android-icon-96x96.png')
    def android_icon_96x96():
        return flask.send_from_directory(os.path.join(app.root_path, 'static'), 'android-icon-96x96.png')

    @app.route('/android-icon-144x144.png')
    def android_icon_144x144():
        return flask.send_from_directory(os.path.join(app.root_path, 'static'), 'android-icon-144x144.png')

    @app.route('/android-icon-192x192.png')
    def android_icon_192x192():
        return flask.send_from_directory(os.path.join(app.root_path, 'static'), 'android-icon-192x192.png')

    @app.route('/browserconfig.xml')
    def browser_config_xml():
        return flask.send_from_directory(os.path.join(app.root_path, 'static'), 'browserconfig.xml')

    @app.route('/ms-icon-70x70.png')
    def ms_icon_70x70():
        return flask.send_from_directory(os.path.join(app.root_path, 'static'), 'ms-icon-70x70.png')

    @app.route('/ms-icon-144x144.png')
    def ms_icon_144x144():
        return flask.send_from_directory(os.path.join(app.root_path, 'static'), 'ms-icon-144x144.png')

    @app.route('/ms-icon-150x150.png')
    def ms_icon_150x150():
        return flask.send_from_directory(os.path.join(app.root_path, 'static'), 'ms-icon-150x150.png')

    @app.route('/ms-icon-310x310.png')
    def ms_icon_310x310():
        return flask.send_from_directory(os.path.join(app.root_path, 'static'), 'ms-icon-310x310.png')


def attach(app):
    attach_favicons(app)


    @app.route('/logout')
    def logout():
        flask_login.logout_user()
        return flask.redirect('/')


    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if flask_login.current_user.is_authenticated:
            return flask.redirect(flask.url_for('admin.index'))
        else:
            form = forms.LoginForm()
            if form.validate_on_submit():
                user = daos.User.get_user(form.username.data)
                if user is None or not user.check_password(form.password.data):
                    flask.flash('Invalid username or password', category='error')
                    return flask.redirect(flask.url_for('login'))
                else:
                    flask_login.login_user(user, remember=form.remember_me.data)
                    flask.flash('Welcome, {}'.format(form.username.data))
                    next_page = flask.request.args.get('next')
                    if not next_page or wkzg_urls.url_parse(next_page).netloc != '':
                        next_page = flask.url_for('admin.index')
                    return flask.redirect(next_page)

            return flask.render_template('login.html', title='Sign In', form=form)


    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if flask_login.current_user.is_authenticated:
            return flask.redirect('/')
        form = forms.RegistrationForm()
        if form.validate_on_submit():
            daos.User.create_user(form.username.data, form.email.data, form.password.data)
            flask.flash('Congratulations, you are now a registered user!')
            return flask.redirect(flask.url_for('login'))

        return flask.render_template('register.html', title='Register', form=form)


    @app.route('/watch')
    def watch():
        job_id = flask.request.args.get('id').split(',')[0]
        daos.JobWatchWriter.add_to_watchlist(user=flask_login.current_user.username, job_id=job_id)
        return '', http.HTTPStatus.NO_CONTENT


    @app.route('/unwatch')
    def unwatch():
        job_id = flask.request.args.get('id').split(',')[0]
        daos.JobWatchWriter.remove_from_watchlist(user=flask_login.current_user.username, job_id=job_id)

        return '', http.HTTPStatus.NO_CONTENT


    @app.route('/iswatched')
    def is_watched():
        job_id = flask.request.args.get('id').split(',')[0]
        is_watched = daos.JobWatchReader.job_is_watched_by_user(user=flask_login.current_user.username, job_id=job_id)

        if is_watched:
            return '', http.HTTPStatus.OK
        else:
            return '', http.HTTPStatus.NO_CONTENT
