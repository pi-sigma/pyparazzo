from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship


db = SQLAlchemy(session_options={"autoflush": False})


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="author")


class BlogPost(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(250), nullable=False)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=True)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=True)
    date = db.Column(db.String(250), nullable=False)
    author = relationship("User", back_populates="posts")
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # plural (> tablename)
    comments = relationship("Comment", back_populates="post")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author = relationship("User", back_populates="comments")
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # plural (> tablename)
    post = relationship("BlogPost", back_populates="comments")
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))  # plural (> tablename)
