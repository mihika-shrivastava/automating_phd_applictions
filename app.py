from crypt import methods
from flask import Flask, render_template, request, url_for, redirect, session
import pymongo as pym
import bcrypt as bc

app = Flask(__name__)
app.secret_key = "verymuchsecret"
client = pym.MongoClient(
    "mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")
db = client.get_database('test')
reg = db.reg_details


@app.route("/", methods=['post', 'get'])
def index():
    return render_template('profile.html')


@app.route("/signin", methods=['post', 'get'])
def signin():
    message = ''
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == 'POST':
        username = request.form.get("name")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user_found = reg.find_one({"name": username})
        email_found = reg.find_one({"email": email})

        if user_found:
            message = 'This username is already registered'
            return render_template('signin.html', message=message)
        if email_found:
            message = 'This email is already registered'
            return render_template('signin.html', message=message)

        if password1 != password2:
            message = 'Both the passwords do not match'
            return render_template('signin.html', message=message)

        else:
            hashed = bc.hashpw(password2.encode('utf-8'), bc.gensalt())
            user_input = {'name': username, 'email': email, 'password': hashed}
            reg.insert_one(user_input)

            user_data = reg.find_one({'email': email})
            new_email = user_data['email']
            return render_template('land.html', email=new_email)
    return render_template('signin.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return render_template('land.html')

    if request.method == "POST":
        username = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        name_found = reg.find_one({"name": username})
        email_found = reg.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']

            if bc.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return render_template('land.html', email=email_val)
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)

    return render_template('login.html', message=message)


@app.route("/dashboard")
def logged_in():
    return render_template('home.html')


if __name__ == "__main__":
    app.run()
