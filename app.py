import os
import smtplib
from email.message import EmailMessage
from datetime import datetime

from flask import Flask, render_template, redirect, request, url_for, flash
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flaskext.markdown import Markdown
from flask_wtf.csrf import CSRFProtect
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from flask_gravatar import Gravatar
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash

from forms import RegisterForm, LoginForm, CreatePostForm, CommentForm, EmailForm
from utils import sanitize_html, admin_only

app = Flask(__name__)

# Configure db
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL_FIXED", "sqlite:///blog.db"  # "postgres" < "postgresql"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import db + models here to avoid circular deps
from models import db, User, BlogPost, Comment

# Configure secret key
SECRET_KEY = os.environ.get("SECRET_KEY", "hush-hush")
app.config["SECRET_KEY"] = SECRET_KEY

# Configure mail
MY_EMAIL = os.environ.get("MY_EMAIL")
GMAIL_PWD = os.environ.get("GMAIL_PWD")

app.config["CKEDITOR_ENABLE_CODESNIPPET"] = True

# Register extensions
csrf = CSRFProtect(app)
csrf.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
ckeditor = CKEditor(app)
Bootstrap(app)
Markdown(app)
gravatar = Gravatar(
    app,
    size=100,
    rating='g',
    default='retro',
    force_default=False,
    force_lower=False,
    use_ssl=False,
    base_url=None
)


# Helper functions
############################################
@app.before_first_request
def initialize_database():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
############################################


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/delete/comment/<int:comment_id>", methods=["GET", "POST"])
@login_required
def comment_delete(comment_id):
    comment = Comment.query.get(comment_id)
    post = comment.post
    if request.method == "POST":
        db.session.delete(comment)
        db.session.commit()
        return redirect(url_for("post_detail", post_id=post.id))
    return render_template("comment_delete.html", comment_id=comment_id, post_id=post.id)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = EmailForm()
    if request.method == "POST":
        msg = EmailMessage()
        msg['Subject'] = form.subject.data
        msg['From'] = form.email.data
        msg['To'] = MY_EMAIL
        msg.set_content(form.message.data)

        with smtplib.SMTP("smtp.gmail.com", port=587) as server:
            server.starttls()
            server.login(user=MY_EMAIL, password=GMAIL_PWD)
            server.send_message(msg)
        return redirect(url_for("contact"))
    return render_template("contact.html", form=form)


@app.route('/')
def home():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash("Invalid credentials: check email and/or password", "error")
            return redirect(url_for("login"))
        else:
            user.authenticated = True
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            return redirect(url_for("home"))
    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def post_detail(post_id):
    requested_post = BlogPost.query.get(post_id)
    mkd = markdown(requested_post.body, extensions=['fenced_code', 'codehilite'])
    comments = Comment.query.all()
    form = CommentForm()
    if request.method == "POST":
        if not current_user.is_authenticated:
            flash("Must be logged in for this", "error")
            return redirect(url_for("login"))
        new_comment = Comment(
            post=requested_post,
            author=current_user,
            text=sanitize_html(form.body.data)
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("post_detail", post_id=requested_post.id))
    return render_template("post_detail.html", markdown=mkd, post=requested_post, comments=comments, form=form)


@app.route("/post/new", methods=["GET", "POST"])
@admin_only
def post_create():
    form = CreatePostForm()
    if request.method == "POST":
        new_post = BlogPost(
            author=current_user,
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=sanitize_html(form.body.data),
            img_url=form.img_url.data,
            date=datetime.now().strftime("%B %d, %Y"),
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("post_create.html", form=form)


@app.route("/delete/post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def post_delete(post_id):
    post = BlogPost.query.get(post_id)
    if request.method == "POST":
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("post_delete.html", post_id=post_id)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def post_edit(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        author=post.author.name,
        title=post.title,
        subtitle=post.subtitle,
        body=post.body,
        img_url=post.img_url,
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = post.author
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("post_detail", post_id=post.id))

    return render_template("post_create.html", form=edit_form, is_edit=True)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST" and form.validate():
        email = form.email.data
        if User.query.filter_by(email=email).first() is not None:
            flash("A user with that email already exists. You can login below.", "error")
            return redirect(url_for("login"))
        password = form.password.data
        password_hashed_salted = generate_password_hash(
            password,
            method="pbkdf2:sha256",
            salt_length=10,
        )
        new_user = User(
            name=form.name.data,
            email=email,
            password=password_hashed_salted,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        return redirect(url_for("home"))
    return render_template("register.html", form=form)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
