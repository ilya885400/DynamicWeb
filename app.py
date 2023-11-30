from flask import Flask, render_template, request, redirect, abort, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = '69'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newflask.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Увеличил размер хранения хеша пароля
    email = db.Column(db.String(32), nullable=False, unique=True)  # Добавил уникальность для email


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    full_content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(300))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref='posts')


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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        user = User.query.filter_by(name=name).first()

        if user and check_password_hash(user.password, password):
            # Успешная аутентификация
            session['user_id'] = user.id  # Устанавливаем информацию о пользователе в сессию
            return redirect('/')
        else:
            flash('Неверное имя пользователя или пароль.', 'error')
            return render_template('login.html')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id  # Устанавливаем информацию о новом пользователе в сессию
            return redirect('/')
        except:
            flash('Ошибка при регистрации пользователя', 'error')
            return render_template('signup.html')

    return render_template('signup.html')


@app.teardown_request
def remove_session(ex=None):
    # Выход из системы при завершении сессии
    session.clear()

@app.route('/logout')
def logout():
    # Выход из системы при закрытии вкладки
    session.clear()
    return redirect('/')
@app.route("/create", methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        full_content = request.form['full_content']
        image_url = request.form.get('image_url')
        user_id = session['user_id']  # Используем id пользователя из сессии

        if not title or not text or not full_content:
            flash('Please fill out all the fields.', 'error')
            return render_template("create.html")

        if 'user_id' not in session:
            flash('You need to be logged in to create a post', 'error')
            return render_template('login.html')

        post = Post(title=title, text=text, full_content=full_content, image_url=image_url, author_id=user_id)

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
    post = Post.query.get(post_id)
    if post:
        author = User.query.get(post.author_id)
        return render_template('post.html', post=post, author=author)
    else:
        abort(404, description="Пост не найден")

if __name__ == "__main__":
    app.run(debug=True)
