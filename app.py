from flask import Flask, render_template, request, redirect, abort, flash, session, g, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime


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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


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
            g.user = user  # Сохраняем информацию о пользователе в объекте запроса g
            flash(f'Добро пожаловать, {user.name}!', 'success')  # Добавляем сообщение приветствия
            print(g.user)  # Добавим эту строку для диагностики
            next_url = request.args.get('next') or url_for('index')
            return redirect(next_url)

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
    if 'user_id' not in session:
        flash('You need to be logged in to create a post', 'error')
        return render_template("create.html", empty=True)

    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        full_content = request.form['full_content']
        image_url = request.form.get('image_url')
        user_id = session['user_id']

        if not title or not text or not full_content:
            flash('Please fill out all the fields.', 'error')
            return render_template("create.html")

        post = Post(title=title, text=text, full_content=full_content, image_url=image_url, author_id=user_id)

        try:
            db.session.add(post)
            db.session.commit()
            flash('Post created successfully!', 'success')
            return redirect('/')
        except:
            flash('An error occurred while adding the post!', 'error')
            return render_template("create.html")

    else:
        return render_template("create.html")

@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get(post_id)

    if not post:
        abort(404, description="Пост не найден")

    if 'user_id' not in session or g.user.id != post.author.id:
        flash('You do not have permission to edit this post', 'error')
        return redirect(url_for('post', post_id=post_id))

    if request.method == 'POST':
        # Обработка данных из формы редактирования
        post.title = request.form['title']
        post.text = request.form['text']
        post.full_content = request.form['full_content']
        post.image_url = request.form['image_url']

        try:
            db.session.commit()
            flash('Post updated successfully!', 'success')
            return redirect(url_for('post', post_id=post_id))
        except:
            flash('An error occurred while updating the post', 'error')

    return render_template('edit_post.html', post=post)
@app.route('/post/<int:post_id>/delete', methods=['GET', 'POST'])
def delete_post_confirm(post_id):
    post = Post.query.get(post_id)

    if not post:
        abort(404, description="Пост не найден")

    if 'user_id' not in session or g.user.id != post.author.id:
        flash('You do not have permission to delete this post', 'error')
        return redirect(url_for('post', post_id=post_id))

    if request.method == 'POST':
        # Удаление поста из базы данных
        try:
            db.session.delete(post)
            db.session.commit()
            flash('Post deleted successfully!', 'success')
            return redirect(url_for('posts'))
        except:
            flash('An error occurred while deleting the post', 'error')

    return render_template('delete_post.html', post=post)




@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get(post_id)
    if post:
        author = User.query.get(post.author_id)
        return render_template('post.html', post=post, author=author)
    else:
        abort(404, description="Пост не найден")

def current_user():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    g.user = user  # Обновляем g.user для использования в шаблонах
    return user

app.jinja_env.globals.update(current_user=current_user)

@app.before_request #благодаря этому можено использовать информацию g.user в шаблонах
def before_request():
    user_id = session.get('user_id')
    g.user = User.query.get(user_id) if user_id else None


if __name__ == "__main__":
    app.run(debug=True)
