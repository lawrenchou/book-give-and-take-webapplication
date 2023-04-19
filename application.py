import os
import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("apology.html", apology="Missing Username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("apology.html", apology="Must Provide Password")

        # Query database for username
        rows = db.execute("SELECT * FROM basic WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash_pw"], request.form.get("password")):
            return render_template("apology.html", apology="Invalid Username and/or Password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        # check if the username typed in
        if not request.form.get("first_name"):
            return render_template("apology.html", apology="Missing First Name")

        if not request.form.get("last_name"):
            return render_template("apology.html", apology="Please Type In Last Name")

        if not request.form.get("username"):
            return render_template("apology.html", apology="Missing Username")

        if not request.form.get("email"):
            return render_template("apology.html", apology="Please Type In Email")

        if not request.form.get("location"):
            return render_template("apology.html", apology="Where do you live in?")

        # check if the password and confirmation typed in
        if not request.form.get("password") or not request.form.get("confirmation"):
            return render_template("apology.html", apology="Missing Password")

        # check if the password and the confirmation match
        if request.form.get("password") != request.form.get("confirmation"):
            return render_template("apology.html", apology="Cannot Confirm Password")


        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        username = request.form.get('username')
        email = request.form.get('email')
        location = request.form.get("location")
        hash_pw = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)


        usernames = db.execute('SELECT username FROM basic')
        for name in usernames:
            if username == name['username']:
                return render_template("apology.html", apology="This Username Is Already In Use")


        emails = db.execute('SELECT email FROM basic')
        for e_address in emails:
            if email == e_address['email']:
                return render_template("apology.html", apology="Emails Is Used")

        db.execute("INSERT INTO basic (username, email, hash_pw) VALUES(?, ?, ?)", username, email, hash_pw)
        user_id = db.execute("SELECT id FROM basic WHERE username = ?", username)[0]['id']
        db.execute("INSERT INTO personal (user_id, first_name, last_name, location) VALUES(?, ?, ?, ?)", user_id, first_name, last_name, location)

        return redirect("/login")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/giving", methods=['GET', 'POST'])
@login_required
def giving():
    user_id = session.get("user_id")
    GENRES = ["Literary Fiction", "Mystery", "Thriller", "Horror", "Historical", "Romance", "Western", "Bildungsroman",
            'Speculative Fiction', 'Science Fiction', 'Fantasy', 'Dystopian', 'Magical Realism', 'Realist Literature']
    if request.method == "GET":
        return render_template("giving.html", genres=GENRES)
    else:
        time = datetime.datetime.now()
        if not request.form.get("bookname"):
            return render_template("apology.html", apology="Missing Book's Name")

        if not request.form.get("author"):
            return render_template("apology.html", apology="Missing Author's Name")

        if not request.form.get("img-source"):
            return render_template("apology.html", apology="Missing Book's Photo")

        if not request.form.get("language"):
            return render_template("apology.html", apology="What Is The Language The Book Written In?")

        if not request.form.get("genres"):
            return render_template("apology.html", apology="Missing Book Genres")

        if not request.form.get("confirm"):
            return render_template("apology.html", apology="Enter The Password To Confirm The Donation")

        # Query database for username
        rows = db.execute("SELECT * FROM basic WHERE id = ?", user_id)
        
        # Ensure password is correct
        if not check_password_hash(rows[0]["hash_pw"], request.form.get("confirm")):
            return render_template("apology.html", apology="Cannot Confirm Giving")

        bookname = request.form.get("bookname")
        author = request.form.get("author")
        genres = request.form.get("genres")
        photo = request.form.get("img-source")
        language = request.form.get("language")


        db.execute("INSERT INTO books (user_id, bookname, author, genres, bookphoto, language) VALUES(?, ?, ?, ?, ?, ?)",
                  user_id, bookname, author, genres, photo, language)
                  
        db.execute("INSERT INTO history (action, user_id, bookname, datetime) VALUES(?, ?, ?, ?)", 'posted', user_id, bookname, time)

        return redirect("/thankyou")


@app.route("/gallery", methods=['GET', 'POST'])
@login_required
def gallery():
    user_id = session.get("user_id")
    
    if request.method == "GET":
        books = db.execute("SELECT * FROM books JOIN personal ON personal.user_id = books.user_id WHERE location = (SELECT location FROM personal WHERE user_id = ?)", user_id) 
        return render_template("gallery.html", books=books)
    else:
        book_id =request.form.get('book_id')
        book_info = db.execute('SELECT * FROM books WHERE id =?', book_id)[0]
        giver_id = book_info['user_id']
        giver = db.execute('SELECT * FROM personal WHERE user_id = ?', giver_id)
        return render_template("information.html", book_info=book_info, giver=giver[0])

@app.route("/storing-message", methods=['POST'])
@login_required
def storing():
    time = datetime.datetime.now()
    sender_id = session.get("user_id")
    sender = db.execute("SELECT username FROM basic WHERE id = ?", sender_id)[0]['username']
    
    book_id = int(request.form.get('message'))
    bookname = db.execute('SELECT bookname FROM books WHERE id = ?', book_id)[0]['bookname']
    
    reciever_id = int(db.execute("SELECT user_id FROM books WHERE id = ?", book_id)[0]['user_id'])
    reciever = db.execute('SELECT username FROM basic WHERE id = ?', reciever_id)[0]['username']
    message = request.form.get("request-text")
    db.execute("INSERT INTO history (action, user_id, reciever, bookname, datetime) VALUES(?,?,?,?,?)", 'request', sender_id, reciever, bookname, time)
    db.execute("INSERT INTO messages (book_id, bookname, sender, reciever, message, action) VALUES(?, ?, ?, ?, ?, ?)", book_id, bookname, sender, reciever, message, "ask for")
    return redirect("/")
        
        
@app.route("/request", methods=['POST'])
@login_required
def requests():
    book_id = request.form.get('book_id')
    return render_template("request.html", book_id=book_id)
        
        
@app.route("/thankyou", methods=["GET", 'POST'])
@login_required
def thankyou():
    if request.method == "GET":
        return render_template("thankyou.html")
    else:
        return redirect("/")
        
        
@app.route("/notification", methods=["GET", 'POST'])
@login_required
def notification():
    user_id = session.get("user_id")
    username = db.execute("SELECT username FROM basic WHERE id=?", user_id)[0]['username']
    notifications = db.execute("SELECT * FROM messages WHERE reciever=?", username)
    if request.method == "GET":
        return render_template("notification.html", notifications=notifications)
    
    else:
        if request.form.get('accept'):
            time = datetime.datetime.now()
            message_id = request.form.get('accept')
            
            book_id = db.execute("SELECT book_id FROM messages WHERE id = ?", message_id)[0]['book_id']
            
            bookname = db.execute("SELECT bookname FROM books WHERE id = ?", book_id)[0]['bookname']
            
            sender = db.execute("SELECT reciever FROM messages WHERE id = ?", message_id)[0]['reciever']
            
            reciever = db.execute("SELECT sender FROM messages WHERE id = ?", message_id)[0]['sender']
            reciever_id = db.execute('SELECT id FROM basic WHERE username = ?', reciever)[0]['id']
            
            db.execute("INSERT INTO history (action, user_id, reciever, bookname, datetime) VALUES(?, ?, ?, ?, ?)", 'gave', user_id, reciever, bookname, time)
            db.execute("INSERT INTO history (action, user_id, giver, bookname, datetime) VALUES(?, ?, ?, ?, ?)", 'got', reciever_id, sender, bookname, time)
            
            db.execute("UPDATE messages SET book_id = NULL, bookname=?, sender =?, reciever =?, action =? WHERE id = ?", bookname,  sender, reciever, "response", message_id)
            db.execute("DELETE FROM messages WHERE book_id = ? AND action = 'ask for'", book_id)
            db.execute("DELETE FROM books WHERE id = ?", book_id)
            
            return redirect("/notification")
            
        elif request.form.get('deny'):
            message_id = request.form.get('deny')
            db.execute("DELETE FROM messages WHERE id = ?", message_id)
            return redirect("/notification")
            
        else:
            message_id = request.form.get('getit')
            db.execute("DELETE FROM messages WHERE id = ?", message_id)
            return redirect('/notification')


@app.route("/blogs", methods=["GET", 'POST'])
@login_required
def blogs():
    if request.method == 'GET':
        blogs = db.execute('SELECT * FROM blogs')
        return render_template("blogs.html", blogs=blogs)
    else:
        time = datetime.datetime.now()
        user_id = session.get("user_id")
        username = db.execute('SELECT username FROM basic WHERE id = ?', user_id)[0]['username']
        share = request.form.get('share')
        db.execute('INSERT INTO blogs (user_id, username, datetime, shares) VALUES(?,?,?,?)', user_id, username, time, share)
        return redirect('/blogs')
        

@app.route("/history")
@login_required
def history():
    history = db.execute('SELECT * FROM history WHERE user_id = ?', session.get('user_id'))
    return render_template("history.html", history=history)
    

    
@app.route("/account")
@login_required
def account():
    user_id = session.get("user_id")
    user_info = db.execute("SELECT * FROM personal WHERE user_id =?", user_id)[0]
    user_acc = db.execute('SELECT * FROM basic WHERE id =?', user_id)[0]
    user_book = db.execute('SELECT * FROM books WHERE user_id =?', user_id)
    
    return render_template("account.html", user_info=user_info, user_basic=user_acc, book_info=user_book)


