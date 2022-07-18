from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
import sqlalchemy
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired,Optional
import requests




app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
db = app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///My_movies.db'
db = SQLAlchemy(app)
movie_list = []

class Update_form(FlaskForm):
    rating = StringField("Your rating out of 10. eg:- 7.5", validators=[Optional()])
    review = StringField("Your review", validators=[DataRequired()])
    submit = SubmitField("Done")

class Add_form(FlaskForm):
    name = StringField("Movie Tile", validators=[DataRequired()])
    submit = SubmitField("Add Movie")

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String, nullable = False , unique=True)
    year = db.Column(db.Integer, nullable = False )
    description = db.Column(db.Text, nullable = False )
    rating = db.Column(db.Float, nullable = False )
    ranking = db.Column(db.Integer, nullable = False )
    review = db.Column(db.String, nullable = False )
    img_url = db.Column(db.String, nullable = False )

    def __repr__(self):
        return f'<Movie {self.title}>'

new_movie = Movie(
    title="Phone Booth",
    year=2002,
    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    rating=7.3,
    ranking=10,
    review="My favourite character was the caller.",
    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
)

db.create_all()
# db.session.add(new_movie)
# db.session.commit()


@app.route("/")
def home():
    movie_list = Movie.query.order_by( Movie.rating.desc())
    return render_template("index.html", movies = movie_list)

@app.route("/edit/<int:id>", methods=['POST','GET'])
def update(id):
    movie_to_update = Movie.query.get(id)
    form = Update_form()
    if request.method == "GET":
        return render_template('edit.html', name = movie_to_update.title, form = form)
    else:
        if form.validate_on_submit():
            rate = form.rating.data
            review = form.review.data
            if rate != "":
                movie_to_update.rating = rate
            movie_to_update.review = review
            db.session.commit()
            return redirect(url_for('home'))

@app.route("/delete/<int:id>")
def delete_movie(id):
    movie_to_delete = Movie.query.get(id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect( url_for("home"))

@app.route("/add", methods = ["POST", "GET"])
def add_movie():
    form = Add_form()
    if request.method == "GET":
        return render_template('add.html',form = form)
    else:
        if form.validate_on_submit():
            url_id = f"https://imdb-api.com/en/API/Search/k_kwrejoq4/{form.name.data}"
            response = requests.get(url=url_id)
            select_movie = response.json()
            # print(select_movie)
            return render_template("select.html", movies=select_movie["results"])

@app.route("/added/movie/<id>")
def select_movie(id):
    url = f"https://imdb-api.com/en/API/Title/k_kwrejoq4/{id}"
    response = requests.get(url = url)
    movie = response.json()
    new_movie = Movie(
    title=movie["title"],
    year=int(movie["year"]),
    description=movie["plot"],
    rating=float(movie["imDbRating"]),
    ranking=10,
    review="",
    img_url=movie["image"]
    )
    db.session.add(new_movie)
    db.session.commit()
    movie_to_edit = Movie.query.filter_by(title=movie["title"]).first()
    print(movie_to_edit.id)
    return redirect(url_for('update',id=movie_to_edit.id))


if __name__ == '__main__':
    app.run(debug=True)
