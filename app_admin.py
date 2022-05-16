from flask import Flask, render_template, request, url_for, redirect, session
import pymongo as pym
import bcrypt as bc

app = Flask(__name__)
app.secret_key = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<\
!\xd5\xa2\xa0\x9fR"\xa1\xa8'
client = pym.MongoClient("mongodb://localhost:27017")

db = client.phd
reg = db.reg_details
det = db.basic_details


@app.route("/", methods=['post', 'get'])
def admin_render():
    return render_template("admin/admin.html")

# user operations


@app.route("/users", methods=['post', 'get'])
def list_users():
    users = det.find({})
    return render_template("admin/users/user_list.html", users=users)


@app.route("/create_user", methods=['post', 'get'])
def create_user():
    return render_template("admin/users/create_user.html")


@app.route("/user_created", methods=['post'])
def created_user():
    username = request.form.get("username")
    email = request.form.get("email")
    phno = request.form.get("number")
    gender = request.form.get('gender')
    birthdate = request.form.get('dob')
    citizenship = request.form.get('citizenship')
    batch = request.form.get('qualification')
    inst = request.form.get('institute_name')
    year = request.form.get('year')
    password2 = "1122"
    hashed = bc.hashpw(password2.encode('utf-8'), bc.gensalt())

    user_details = {'name': username, 'email': email, 'phno': phno, 'gender': gender,
                    'birthdate': birthdate, 'citizenship': citizenship, 'batch': batch, 'inst': inst, 'year': year}

    user_cred = {'name': username, 'email': email, 'password': hashed}

    det.insert_one(user_details)
    reg.insert_one(user_cred)
    return render_template("admin/users/create_user.html", status="user created succesfully")


@app.route("/delete_user", methods=['post', 'get'])
def delete_user():
    return render_template("admin/users/delete_user.html")


@app.route("/deleted_user", methods=['post', 'get'])
def deleted_user():
    status = ""
    c = ""
    username = request.form.get('username')
    email = request.form.get('email')
    if(reg.find_one({"name": username, "email": email}) and det.find_one({"name": username, "email": email})):
        reg.delete_one({"name": username, "email": email})
        det.delete_one({"name": username, "email": email})
        status = "Requested user deleted succesfully"
        c = "green"
    else:
        status = "Requested user not found"
        c = "red"

    return render_template("admin/users/delete_user.html", status=status, col=c)


@app.route("/edit_user", methods=['post', 'get'])
def edit_user():
    return render_template('admin/users/edit_user.html')


@app.route("/tests", methods=['post', 'get'])
def list_tests():
    return render_template("admin/tests/test_list.html")


@app.route("/create_test", methods=['post', 'get'])
def create_tests():
    return render_template("admin/tests/create_test.html")


if __name__ == "__main__":
    app.run(port=9000, debug=True)
