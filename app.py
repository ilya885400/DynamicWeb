from flask import Flask, render_template,\
    request, redirect, abort, flash

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = '69'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newflask.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), nullable=False)
    password = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(32), nullable=False)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    full_content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(300))


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/posts")
def posts():
    posts = Post.query.all()
    return render_template('posts.html', posts=reversed(posts))


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/create", methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        full_content = request.form['full_content']
        image_url = request.form.get('image_url')

        if not title or not text or not full_content:
            flash('Please fill out all the fields.', 'error')
            return render_template("create.html")

        post = Post(title=title, text=text, full_content=full_content, image_url=image_url)

        try:
            db.session.add(post)
            db.session.commit()
            return redirect('/')
        except:
            flash('An error occurred while adding the post!', 'error')
            return render_template("create.html")

    else:
        return render_template("create.html")


@app.route('/post/<int:post_id>')
def post(post_id):
    # Находите пост по идентификатору (здесь просто фильтрация по id)
    post = Post.query.get(post_id)

    if post:
        return render_template('post.html', post=post)
    else:
        # Обработка ситуации, если пост не найден
        abort(404, description="Пост не найден")


if __name__ == "__main__":
    app.run(debug=True)
