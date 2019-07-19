import os

from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'EventCal.sqlite'),
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db, auth, calendarview

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(calendarview.bp)
    app.add_url_rule('/', endpoint='index')
    return app

app = create_app()

@app.before_first_request
def on_startup():
    from . import db
    # db.update_db()
