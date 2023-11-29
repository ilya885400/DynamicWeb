from flask import Flask, render_template,\
    request, redirect, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
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
        if not title or not text or not full_content:
            return 'Please fill out all the fields.'

        post = Post(title=title, text=text, full_content=full_content)

        try:
            db.session.add(post)
            db.session.commit()
            return redirect('/')
        except:
            return 'При добавлении статьи произошла ошибка!'
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
