from flask import Flask, render_template, redirect, request
app = Flask(__name__)
import model

@app.route("/")
def index():
    user_list = model.session.query(model.User).limit(5).all()
    return render_template("user_list.html", users=user_list)

if __name__ == "__main__":
    app.run(debug = True)