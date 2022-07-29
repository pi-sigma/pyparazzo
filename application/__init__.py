from flask import Flask
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import LoginManager
from flaskext.markdown import Markdown
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from . routes import main_bp
from . models import db, User


ckeditor = CKEditor()
csrf = CSRFProtect()
gravatar = Gravatar(
    size=100,
    rating='g',
    default='retro',
    force_default=False,
    force_lower=False,
    use_ssl=False,
    base_url=None
)
login_manager = LoginManager()


def create_app():
    # Initialize core application
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    # Initialize plugins
    csrf.init_app(app)

    db.init_app(app)

    login_manager.init_app(app)
    ckeditor.init_app(app)
    Bootstrap(app)
    Markdown(app)
    gravatar.init_app(app)

    # Include routes
    with app.app_context():
        from . import routes
        app.register_blueprint(main_bp)
        Migrate(app, db)
        db.create_all()

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
