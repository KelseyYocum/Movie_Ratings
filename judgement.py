from flask import Flask, render_template, redirect, request, url_for, flash
import model

app = Flask(__name__)
app.secret_key = "shhhhthisisasecret"

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/show_users")
def show_users():
    user_list = model.session.query(model.User).limit(5).all()
    return render_template("user_list.html", users=user_list)

@app.route("/new_user", methods=["POST"])
def make_new_user():
    email = request.form.get("email")
    age = request.form.get("age")
    zipcode = request.form.get("zipcode")
    password = request.form.get("password")

    model.make_new_user(email, password, age, zipcode)
    flash("You've successfully made an account!")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug = True)