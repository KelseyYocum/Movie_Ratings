from flask import Flask, render_template, redirect, request, url_for, flash, session
import model

app = Flask(__name__)
app.secret_key = "shhhhthisisasecret"

@app.route("/")
def index():
    if session.get("id"):
        user = model.getUserFromId(session["id"])
        return redirect(url_for("profile", user_id =user.id))
    else:
        return render_template("index.html", user_id=None)

@app.route("/", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    user_id = model.authenticate(email, password)
    if user_id == None:
        flash("User does not exist")
        return redirect(url_for("index"))
    else:
        session['id'] = user_id
        return redirect(url_for("profile", user_id =user_id))


@app.route("/clear")
def clear_session():
    session.clear()
    return redirect(url_for ("index"))

@app.route("/profile/<user_id>")
def profile(user_id):
    profile_link = my_profile_link()
    user = model.getUserFromId(user_id)
    movie_ratings = model.get_movie_list(user_id)
    if session.get('id'):
        if session['id'] == int(user_id):
            return render_template("profile.html", user_id=user_id, email = user.email, 
                                    movie_ratings=movie_ratings, profile_link=profile_link)
        else:
            return render_template("user_profile.html", user_id=user_id, email = user.email, 
                        movie_ratings=movie_ratings, profile_link=profile_link)
    else:
        return render_template("user_profile.html", user_id=user_id, email = user.email, 
                        movie_ratings=movie_ratings, profile_link=profile_link)

        

@app.route("/profile/<user_id>", methods=["POST"])
def add_rating(user_id):
    movie_name = request.form.get("movie_name")
    rating = request.form.get("rating")
    if model.movie_does_not_exist(movie_name):
        flash("Movie not in database")
        return redirect(url_for("profile", user_id=user_id))
    else:
        movie_id = model.get_movieid_from_name(movie_name)
        if model.user_rated_movie(movie_id, user_id):
            model.change_rating(user_id, movie_id, rating)
        elif movie_name == "":
            flash("Please enter a movie name...")
        elif rating == None:
            flash("...Rating?")
        else: 
            model.add_movie_rating(user_id, movie_id, rating)
        return redirect(url_for("profile", user_id=user_id))

def my_profile_link():
    if session.get('id'):
        profile_link = session['id']
    else:
        profile_link = None
    return profile_link

@app.route("/show_users/")
@app.route("/show_users/<int:page_id>")
def show_users(page_id=0):
    profile_link = my_profile_link()
    user_list = model.session.query(model.User).filter(model.User.id > page_id).limit(30).all()
    return render_template("user_list.html", users=user_list, page_id=page_id, profile_link = profile_link)


@app.route("/show_movies/")
@app.route("/show_movies/<int:page_id>")
def show_movies(page_id=0):
    profile_link = my_profile_link()
    movie_list = model.session.query(model.Movie).filter(model.Movie.id > page_id).limit(30).all()
    return render_template("movie_list.html", movies=movie_list, page_id=page_id, profile_link = profile_link)

@app.route("/movie_title/<movie_name>")
def movie_profile(movie_name):
    profile_link = my_profile_link()
    user_ratings = model.get_users_ratings(movie_name)
    return render_template("movie_profile.html", profile_link=profile_link, user_ratings=user_ratings, movie_name=movie_name)
@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def make_new_user():
    email = request.form.get("email")
    age = request.form.get("age")
    zipcode = request.form.get("zipcode")
    password = request.form.get("password")
    verify_password = request.form.get("password_verify")
    
    if password != verify_password:
        flash("Passwords do not match")
        return redirect(url_for("register"))
    if model.userExists(email):
        flash("Account already exists for user email") 
        return redirect(url_for("register"))

    model.make_new_user(email, password, age, zipcode)
    flash("You've successfully made an account!")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug = True)