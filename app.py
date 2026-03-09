from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import string
import random
import validators

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500))
    short_code = db.Column(db.String(10), unique=True)
    clicks = db.Column(db.Integer, default=0)


def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':

        original_url = request.form['url']

        if not validators.url(original_url):
            return "Invalid URL"

        short_code = generate_short_code()

        new_link = URL(
            original_url=original_url,
            short_code=short_code
        )

        db.session.add(new_link)
        db.session.commit()

    links = URL.query.all()

    return render_template("index.html", links=links)


@app.route('/<short_code>')
def redirect_url(short_code):

    link = URL.query.filter_by(short_code=short_code).first()

    if link:
        link.clicks += 1
        db.session.commit()
        return redirect(link.original_url)

    return "Link not found"


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
