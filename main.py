from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:goodpass@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog', methods=['POST', 'GET'])
def index():
    blogs = Blog.query.all()
    
    return render_template('blogs.html', header='Blogs', blogs=blogs)

@app.route('/readblog', methods=['GET'])
def view_blog():
#    blogs = Blog.query.all()
#    blog_id = int(request.form['blog-id'])
    blog_id = request.args.get('blog_id')
    blog = Blog.query.get(blog_id)
#    blog_title = blog.title
#    blog_body = blog.body
    return render_template('readblog.html', header='Read Blog', blog=blog)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
#    blog_title = ''
#    blog_body = ''
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
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            blog_id = new_blog.id
            return redirect('/readblog?blog_id={0}'.format(blog_id))
        else:
            return render_template('newpost.html', blog_title=blog_title, blog_body=blog_body, title_error=title_error, 
                                    body_error=body_error)
    return render_template('newpost.html')
    

if __name__ == '__main__':
    app.run()