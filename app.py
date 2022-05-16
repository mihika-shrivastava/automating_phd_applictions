from flask import Flask, render_template, request, url_for, redirect, session, flash
import pymongo as pym
import bcrypt as bc
from flask_mail import *
from random import *
import gridfs

app = Flask(__name__)

app.config.update(dict(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME='dr.phdbot@gmail.com',
    MAIL_PASSWORD='phdbot123',
))

mail = Mail(app)
otp = randint(000000, 999999)
app.secret_key = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<\
!\xd5\xa2\xa0\x9fR"\xa1\xa8'


client = pym.MongoClient("mongodb://localhost:27017")
# atlas: mongodb+srv://rohit:1122@cluster0.8qt0c.mongodb.net/myFirstDatabase?retryWrites=true&w=majority
# "mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false"

db = client.phd  # for atlas db: test
reg = db.reg_details
det = db.basic_details
docv = db.doc_vault
fs = gridfs.GridFS(db, str("doc_vault"))


@app.route("/", methods=['post', 'get'])
def signin():
    session["logged_in"] = False
    message = ''
    if request.method == 'POST':
        username = request.form.get("name")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user_found = reg.find_one({"name": username})
        email_found = reg.find_one({"email": email})

        if user_found:
            message = 'This username is already registered'
            return render_template('views/signin.html', message=message)
        if email_found:
            message = 'This email is already registered'
            return render_template('views/signin.html', message=message)

        if password1 != password2:
            message = 'Both the passwords do not match'
            return render_template('views/signin.html', message=message)

        else:
            hashed = bc.hashpw(password2.encode('utf-8'), bc.gensalt())
            user_input = {'name': username, 'email': email, 'password': hashed}
            # reg.insert_one(user_input)

            # user_data = reg.find_one({'email': email})
            # new_email = user_data['email']
            session["in_email"] = email
            session["username"] = user_input['name']
            session["pass"] = hashed
            return render_template('views/verify.html')
    return render_template('views/signin.html')


@app.route("/verify", methods=['post'])
def verify_mail():
    email = request.form["email"]
    msg = Message('OTP', sender='dr.phdbot@gmail.com', recipients=[email])
    msg.body = 'Your one time password is: '+str(otp)
    mail.send(msg)
    session['forgotEmail'] = email
    return render_template('views/validate.html', email=email)


@app.route('/validate', methods=["POST"])
def validate():
    user_otp = request.form['otp']
    if otp == int(user_otp):
        if session['forgot'] == True:
            return render_template('views/forgotpass.html')
        else:
            user_input = {'name': session['username'],
                          'email': session['in_email'], 'password': session['pass']}
            reg.insert_one(user_input)
            session["email"] = session['in_email']
            session["logged_in"] = True
            return "<h3> Email  verification is  successfull </h3><br><a href='/details'>continue</a>"

    return render_template('views/signin.html', message="otp doesnt match try again")


@app.route('/forgotPassword', methods=['GET'])
def forgotp():
    session['forgot'] = True
    return render_template('views/verify.html')


@app.route('/changedpass', methods=['post'])
def changepassword():
    newpass = request.form.get("newpass")
    hashed = bc.hashpw(newpass.encode('utf-8'), bc.gensalt())
    filt = {"email": session['forgotEmail']}
    upda = {'$set': {"password": hashed}}
    reg.find_one_and_update(filt, upda)
    session['forgot'] = False
    msg = "Password updated"
    return render_template('views/login.html', message=msg)


@ app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if session["logged_in"]:
        return render_template('views/home.html')

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
                session["logged_in"] = True
                return redirect(url_for('home'))
            else:
                if "email" in session:
                    return redirect(url_for("home"))
                message = 'Wrong password'
                return render_template('views/login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('views/login.html', message=message)

    return render_template('views/login.html', message=message)


@ app.route("/details", methods=["POST", "GET"])
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

        return render_template('views/home.html')
    return render_template('views/basic_details.html', email_val=session['email'])


@ app.route("/logout", methods=["POST", "GET"])
def logout():
    if session["logged_in"]:
        session.pop("email", None)
        session["logged_in"] = False
        return render_template("views/login.html")
    else:
        return render_template('views/signin.html')


@ app.route("/dashboard")
def home():
    if session["logged_in"]:
        return render_template('views/home.html', msg="is-completed")
    else:
        return redirect('login')


@ app.route("/profile")
def user_profile():
    if session["logged_in"]:
        finder = det.find_one({'name': session['username']})
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
        return render_template('views/profile.html', fname=fname, lname=lname, email=email, phno=phno, birthdate=birthdate, gender=gender, citi=citi, batch=batch, inst=inst, year=year)

    else:
        return redirect('login')


@ app.route("/user_documents")
def doc_vault():
    return render_template('views/documents.html')


@ app.route("/documents", methods=['post'])
def doc_load():
    if 'ug_ms' in request.files:
        ugms = request.files['ug_ms']
        fs.put(ugms, filename=ugms.filename)
        docv.insert_one(
            {"username": session['username'], "filename": ugms.filename, "type": ugms.content_type})
        flash('ug uploaded')

    if 'pg_ms' in request.files:
        pgms = request.files['pg_ms']
        fs.put(pgms, filename=ugms.filename)
        docv.insert_one(
            {"email": session['email'], "filename": pgms.filename, "type": pgms.content_type})
        flash('pg uploaded')

    if 'pap' in request.files:
        pap = request.files['pap']
        fs.put(pap, filename=pap.filename)
        docv.insert_one(
            {"username": session['username'], "filename": pap.filename, "type": pap.content_type})
        flash('paper uploaded')
    return render_template('views/documents.html')


@app.route("/edit_profile")
def edit_profile():
    finder = det.find_one({'name': session['username']})
    fname = finder['fname']
    lname = finder['lname']
    email = finder['email']
    phno = finder['phno']
    inst = finder['inst']
    year = finder['year']
    return render_template('views/editpage.html', username=session['username'], fname=fname, lname=lname, email=email, phno=phno, inst=inst, year=year)


@app.route("/details_update", methods=["post"])
def commit_profile():
    fname = request.form.get("firstname")
    lname = request.form.get("lastname")
    phno = request.form.get("contactnumber")
    gender = request.form.get('gender')
    birthdate = request.form.get('birthdate')
    citizenship = request.form.get('citizenship')
    batch = request.form.get('edu')
    inst = request.form.get('institution')
    year = request.form.get('year')
    filt = {"name": session['username']}
    upda = {'$set': {"fname": fname, "lname": lname, "phno": phno, "gender": gender, "birthdate": birthdate,
                     "citizenship": citizenship, "batch": batch, "institution": inst, "year": year}}
    det.find_one_and_update(filt, upda)
    return redirect(url_for('user_profile'))


if __name__ == "__main__":
    app.run()
