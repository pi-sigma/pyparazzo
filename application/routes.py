from datetime import datetime

from flask import Blueprint
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, current_user, logout_user
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash

from .forms import RegisterForm, LoginForm, CreatePostForm, CommentForm, EmailForm
from .utils import sanitize_html, admin_only, send_mail
from .models import db, User, BlogPost, Comment


main_bp = Blueprint('main_bp', __name__, template_folder='templates')


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/delete/comment/<int:comment_id>", methods=["GET", "POST"])
@login_required
def comment_delete(comment_id):
    comment = Comment.query.get(comment_id)
    post = comment.post
    if request.method == "POST":
        db.session.delete(comment)
        db.session.commit()
        return redirect(url_for("main_bp.post_detail", post_id=post.id))
    return render_template("comment_delete.html", comment_id=comment_id, post_id=post.id)


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = EmailForm()
    if request.method == "POST":
        subject = form.subject.data
        sender = form.email.data
        content = form.message.data
        send_mail(subject, sender, content)
        return redirect(url_for("main_bp.contact"))
    return render_template("contact.html", form=form)


@main_bp.route('/')
def index():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@main_bp.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash("Invalid credentials: check email and/or password", "error")
            return redirect(url_for("main_bp.login"))
        else:
            user.authenticated = True
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            return redirect(url_for("main_bp.index"))
    return render_template("login.html", form=form)


@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_bp.index'))


@main_bp.route("/post/<int:post_id>", methods=["GET", "POST"])
def post_detail(post_id):
    requested_post = BlogPost.query.get(post_id)
    mkd = markdown(requested_post.body, extensions=['fenced_code', 'codehilite'])
    comments = Comment.query.all()
    form = CommentForm()
    if request.method == "POST":
        if not current_user.is_authenticated:
            flash("Must be logged in for this", "error")
            return redirect(url_for("main_bp.login"))
        new_comment = Comment(
            post=requested_post,
            author=current_user,
            text=sanitize_html(form.body.data)
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("main_bp.post_detail", post_id=requested_post.id))
    return render_template("post_detail.html", markdown=mkd, post=requested_post, comments=comments, form=form)


@main_bp.route("/delete/post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def post_delete(post_id):
    post = BlogPost.query.get(post_id)
    if request.method == "POST":
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('main_bp.index'))
    return render_template("post_delete.html", post_id=post_id)


@main_bp.route("/post/new", methods=["GET", "POST"])
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
        return redirect(url_for('main_bp.index'))
    return render_template("post_create.html", form=form)


@main_bp.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
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
        return redirect(url_for("main_bp.post_detail", post_id=post.id))
    return render_template("post_create.html", form=edit_form, is_edit=True)


@main_bp.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST" and form.validate():
        email = form.email.data
        if User.query.filter_by(email=email).first() is not None:
            flash("A user with that email already exists. You can login below.", "error")
            return redirect(url_for("main_bp.login"))
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
        return redirect(url_for("main_bp.index"))
    return render_template("register.html", form=form)
