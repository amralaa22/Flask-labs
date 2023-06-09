from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
UPLOAD_FOLDER = os.path.join('static/uploads')
ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
migrate = Migrate(app, db)
@app.before_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(100), nullable=False, default='default.jpg')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Post('{self.title}', '{self.created_at}')"

def upload_file(image):
    if image.filename != '':
            img_name = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], img_name))
    return img_name


@app.route('/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        image = request.files['image']
        img_name=upload_file(image)
        post = Post(title=title, body=body, image=img_name)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('new_post.html')

@app.route('/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return post



@app.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_post(id):
    post = get_post(id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.body = request.form['body']
        post.image = upload_file(request.files['image'])
        post.updated_at = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit_post.html', post=post)

@app.route('/<int:id>/delete', methods=['GET'])
def delete_post(id):
    post_id =id
    post =  Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
