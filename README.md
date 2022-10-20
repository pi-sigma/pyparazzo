# Pyperazzo

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue)](https://www.python.org/downloads/release/python-3100/)
[![Flask 2.1](https://img.shields.io/badge/flask-2.1-blue)](https://flask.palletsprojects.com/en/2.1.x/)


## Overview
Personal blog application.
Creation of blog posts restricted to admin, other users can post comments.

Design adapted from the [Clean Blog](https://startbootstrap.com/theme/clean-blog) Bootstrap template.

## Installation
Clone the repository into a directory of your choice.
```sh
mkdir MYAPPDIR
git clone https://github.com/pi-sigma/pyperazzo.git MYAPPDIR
```

Create a virtual environment in the root directory of the app and activate it:
```sh
python3.10 -m venv venv
. venv/bin/activate
```

Install the requirements:
```sh
python -m pip install -r requirements.txt
```

## Usage
Start the app:
```sh
python run.py
```

Manipulation of blog posts is restricted to the user with id 1 (usually the admin) via a custom decorator (the code is in [application/utils.py](https://github.com/pi-sigma/pyperazzo/blob/main/application/utils.py)).
In order to allow other users to create, update, and delete posts, remove the `@admin_only` decorator from `post_create`, `post_delete`, `post_edit` in [application/routes.py](https://github.com/pi-sigma/pyperazzo/blob/main/application/routes.py) and add the `@login_required` decorator instead.
