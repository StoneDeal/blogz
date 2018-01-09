from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:great@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'list_blogs', 'index']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')

@app.route("/", methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['user'] = user.username
                flash('welcome back, '+user.username)
                return redirect("/newpost")
        flash('bad username or password')
        return redirect("/login")

def valid_user(string):
    error_count = 0

    if string == '':
        error_count += 1
    for char in string:
        if char == ' ':
            error_count += 1
    u_len = len(string)
    if u_len > 20 or u_len < 3:
        error_count += 1
    if error_count == 0:
        return True
    else:
        return False

def valid_pass(string):
    error_count = 0

    for char in string:
        if char == ' ':
            error_count += 1
    p_len = len(string)
    if p_len > 20 or p_len < 3:
        error_count += 1
    if error_count == 0:
        return True
    else:
        return False    

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        if valid_user(username) == False:
            flash('Please enter a valid username')
            return redirect('/signup')
        user_db_count = User.query.filter_by(username=username).count()
        if user_db_count > 0:
            flash('yikes! "' + username + '" is already taken and password reminders are not implemented')
            return redirect('/signup')
        if valid_pass(password) == False:
            flash('Please enter a valid password')
            return redirect('/signup')
        if password != verify:
            flash('passwords did not match')
            return redirect('/signup')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.username
        return redirect("/blog")
    else:
        return render_template('signup.html')


@app.route('/blog', methods=['POST', 'GET'])
def list_blogs():
    blogs = Blog.query.all()
    users = User.query.all()
    
    return render_template('blogs.html', blogs=blogs)

@app.route('/userpage', methods=['GET'])
def user_blogs():
    id = request.args.get('user_id')
    user_works = Blog.query.filter_by(id=id)
    return render_template('userpage.html', user_works=user_works)

@app.route('/readblog', methods=['GET'])
def view_blog():
    blog_id = request.args.get('blog_id')
    blog = Blog.query.get(blog_id)
    return render_template('readblog.html', header='Read Blog', blog=blog)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        title_error = ''
        body_error = ''
        error_count = 0

        if blog_title == '':
            title_error = 'Please enter text into the title'
            error_count += 1
        if blog_body == '':
            body_error = 'Please enter text into the body'
            error_count += 1

        if error_count == 0:
            owner = User.query.filter_by(username=session['user']).first()
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            blog_id = new_blog.id
            return redirect('/readblog?blog_id={0}'.format(blog_id))
        else:
            return render_template('newpost.html', blog_title=blog_title, blog_body=blog_body, title_error=title_error, 
                                    body_error=body_error)
    return render_template('newpost.html')

@app.route("/logout", methods=['POST'])
def logout():
    del session['user']
    return redirect("/login")



    

if __name__ == '__main__':
    app.run()