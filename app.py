from crypt import methods
from flask import Flask, render_template, request, url_for, redirect, session
import pymongo as pym
import bcrypt as bc

app = Flask(__name__)
app.secret_key = "verymuchsecret"

client = pym.MongoClient(
    "mongodb+srv://rohit:1122@cluster0.8qt0c.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

# "mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false"

db = client.test
reg = db.reg_details
det = db.basic_details


@app.route("/", methods=['post', 'get'])
def signin():
    message = ''
    if "email" in session:
        return redirect(url_for("home"))
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
            session["email"] = new_email
            session["username"] = user_input['name']
            return render_template('basic_details.html', email_val=new_email)
    return render_template('signin.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return render_template('home.html')

    if request.method == "POST":
        username = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        email_found = reg.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']

            if bc.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                session["username"] = email_found['name']
                return redirect(url_for('home'))
            else:
                if "email" in session:
                    return redirect(url_for("home"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)

    return render_template('login.html', message=message)


@app.route("/details", methods=["POST", "GET"])
def logged_in():
    if request.method == 'POST':
        fname = request.form.get("firstname")
        lname = request.form.get("lastname")
        email = request.form.get("email")
        phno = request.form.get("contactnumber")
        gender = request.form.get('gender')
        birthdate = request.form.get('birthdate')
        citizenship = request.form.get('citizenship')
        batch = request.form.get('batch')
        inst = request.form.get('institution')
        year = request.form.get('year')

        user_details = {'name': session['username'], 'fname': fname, 'lname': lname, 'email': email, 'phno': phno,
                        'gender': gender, 'birthdate': birthdate, 'citizenship': citizenship, 'batch': batch, 'inst': inst, 'year': year}

        det.insert_one(user_details)

        session['details'] = True

        return render_template('home.html')
    return render_template('basic_details.html', email_val=session['email'])


@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("login.html")
    else:
        return render_template('signin.html')


@app.route("/dashboard")
def home():
    return render_template('home.html')


@app.route("/profile")
def user_profile():
    finder = det.find_one({'name': session['username']})
    if session['details']:
        fname = finder['fname']
        lname = finder['lname']
        email = finder['email']
        phno = finder['phno']
        birthdate = finder['birthdate']
        gender = finder['gender']
        citi = finder['citizenship']
        batch = finder['batch']
        inst = finder['inst']
        year = finder['year']
        return render_template('profile.html', fname=fname, lname=lname, email=email, phno=phno, birthdate=birthdate, gender=gender, citi=citi, batch=batch, inst=inst, year=year)

    return render_template('profile.html')


if __name__ == "__main__":
    app.run()
