from flask import Flask,render_template,flash,session,logging,redirect, url_for, request
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import InputRequired, Email
from wtforms import Form,StringField,TextAreaField,PasswordField,validators ,ValidationError
from passlib.hash import sha256_crypt
from functools import wraps
import mysql.connector


app = Flask(__name__)
app.secret_key = "stulance"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "stulance"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


# Kullanıcı Giriş Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için lütfen giriş yapınız","danger")
            return redirect(url_for("login"))

        
    return decorated_function

# Kullanıcı Kayıt Formu
class RegisterForm(Form):
    name = StringField("İsim Soyisim",validators=[validators.Length(min=4,max=25)])
    username = StringField("Kullanıcı Adı",validators=[validators.Length(min=5,max=35)])
    email = StringField("Email Adresi",validators=[validators.Email(message="Lütfen Geçerli Bir Email Adresi Giriniz !!!")])
    password = PasswordField("Parola",validators=[
        validators.DataRequired(message="Lütfen bir parola belirleyin"),
        validators.EqualTo(fieldname="confirm",message="Parolanız Uyuşmuyor")
    ])
    confirm = PasswordField("Parola Doğrula")

# Login Form 
class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Parola")



@app.route("/")
def index():
   

    return render_template("new_index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

# Register -- Katıl Ol
@app.route("/register",methods=["GET","POST"])
def register():

    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data) 

        cursor = mysql.connection.cursor()

        sql = "INSERT INTO users(name,email,username,password) VALUES(%s,%s,%s,%s)"
        value = (name,email,username,password)
        cursor.execute(sql,value)
        mysql.connection.commit()

        cursor.close()
        flash("Başarıyla Kayıt Oldunuz","success")
        return redirect(url_for("login"))
    else:
        return render_template("register.html",form=form)
    
# Login - Giriş
@app.route("/login",methods = ["GET","POST"])
def login():

    form = LoginForm(request.form)

    if request.method == "POST" :
        username = form.username.data
        password_entered = form.password.data

        cursor = mysql.connection.cursor()

        sql = "Select * From users where username = %s "
        value =(username,)
        result =  cursor.execute(sql,value)

        if result > 0:
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered,real_password):
                flash("Giriş Başarılı","success")

                session["logged_in"] = True
                session["username"] = username


                return redirect(url_for("index"))
            else:
                flash("Parola Yanlış","danger")
                return redirect(url_for("login"))

        else:
            flash("Kullanıcı Adı Bulunmuyor","danger")
            return redirect(url_for("login"))


        mysql.connection.commit()
        cursor.close()

    return render_template("login.html",form=form)

# Log Out - Çıkış
@app.route("/logout")
def log_out():
    session.clear()
    return redirect(url_for("index"))

# Add Work - İş Ekleme
@app.route("/add_works",methods=["POST","GET"])
def addWork():
    form = WorkForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data


        cursor = mysql.connection.cursor()

        sql = "INSERT INTO freelance(title,student,content) VALUES(%s,%s,%s)"
        value =(title,session["username"],content)
        cursor.execute(sql,value)
        mysql.connection.commit()
        cursor.close()

        flash("Yetenek Başarı İle Eklendi","success")
        return redirect(url_for("dashboard"))
    else:
        return render_template("add_work.html",form=form)


# Work Form - İş Form
class WorkForm(Form):
    title = StringField("Yetenek",validators=[validators.length(min=5,max=100)])
    content = TextAreaField("Yetenek İçeriği",validators=[validators.length(min=10)])

# Work Page - İş Sayfası 
@app.route("/works")
def works():
    cursor = mysql.connection.cursor()

    sql = "Select * From freelance"
    result = cursor.execute(sql)

    if result > 0:
        work = cursor.fetchall()
        return render_template("works.html",works = work)
    else:
        return render_template("works.html")

   
# Search Box - Arama Kutusu
@app.route("/search",methods=["POST","GET"])
def search():
    if request.method =="GET":
        return redirect(url_for("index"))
    else:
        keyword = request.form.get("keyword")

        cursor = mysql.connection.cursor()
        sql = "Select * From freelance Where title Like '%"+ keyword + "%'"
        result = cursor.execute(sql)

        if result == 0:
            flash("Arana kelime uygun Freelance bulunamadı...","warning")
            return redirect(url_for("works"))
        
        else:
            work = cursor.fetchall()
            return render_template("works.html",works = work)
if __name__=="__main__":
    app.run(debug=True)

















