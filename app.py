from flask import Flask, render_template, request, jsonify, g, flash, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import plotly.graph_objects as go
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import indexes
from DBInteract import IDAtaBase
from UserLogin import UserLogin

# Настройка flask-приложения
app = Flask(__name__)
app.config.from_object('config.Config')
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'users.db')))
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Авторизуйтесь для полного доступа к функционалу сайта'


# Функция для установления соединения с базой данных
def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


# Функция для инициализации базы данных (создание таблицы, если она не существует)
def init_db():
    with app.app_context():
        conn = connect_db()
        with app.open_resource('sq_db.sql', mode='r') as f:
            conn.cursor().executescript(f.read())
        conn.commit()
        conn.close()


def get_db():
    # Соединение с бд если оно еще не установлено
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    dbase = IDAtaBase(db)
    return UserLogin().fromDB(user_id, dbase)


@app.teardown_appcontext
def close_db(errors):  # закрываем соединение с бд
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route('/')  # Главная страница (index.html)
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])  # Страница с входом
def login():
    if request.method == 'POST':
        db = get_db()
        dbase = IDAtaBase(db)
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['password'], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(url_for('analysis'))

        flash("Неверная почта/пароль")

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/reg', methods=['POST', 'GET'])  # Страница с регистрацией
def registration():
    db = get_db()
    dbase = IDAtaBase(db)
    if request.method == 'POST':
        if len(request.form['login']) > 1 and len(request.form['email']) > 5 and len(request.form['psw']) > 5:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['login'], request.form['email'], hash)
            if res:
                flash("Вы успешно зарегистрировались")
                return redirect(url_for('login'))
            else:
                flash("Ошибка регистрации")
        else:
            flash("Неверно заполнены поля")

    return render_template('registration.html')


# TODO сделать в качестве словаря: {'марка': ['модель', 'модель']}
vendors = ['Audi', 'SUZUKI', 'SsangYong',
           'Hyundai']  # TODO сделать чтобы подгружалось из excel (чтобы пользователю было удобно добавлять новые марки)


@app.route('/help')  # Страница "about"
def help():
    return render_template('help.html')


@app.route('/analysis')  # Страница с графиками/данными
@login_required
def analysis():
    if current_user.type_ == 'v':  # Если сторонний пользователь
        return render_template('analysis.html', vendors=vendors)
    else:
        return render_template('analysis_d.html', vendors=vendors)


@app.route('/plot', methods=['POST'])  # через эту функцию строятся графики
def plot():
    # Сбор данных с формы
    ind = request.form['ind']
    type_ = request.form['type']
    vendor = request.form['vendor']
    if vendor == 'all_v':
        vendor = None
    dealer = None
    startdate = request.form['startdate']
    enddate = request.form['enddate']

    # Постройка графиков в зависимости от выбранного индекса
    if ind == 'Ins_mov':
        data = indexes.instant_moving_index_interval(type_, startdate, enddate, dealer, vendor)
    elif ind == 'Ins_y-y':
        data = indexes.instant_year_year_index_interval(type_, startdate, enddate, dealer, vendor)
    elif ind == 'Cur_mov':
        data = indexes.current_moving_index_interval(type_, startdate, enddate, dealer, vendor)
    elif ind == 'Cur_y-y':
        data = indexes.current_year_year_index_interval(type_, startdate, enddate, dealer, vendor)
    elif ind == 'Long_mov':
        data = indexes.long_moving_index_interval(type_, startdate, enddate, dealer, vendor)
    elif ind == 'Long_y-y':
        data = indexes.long_year_year_index_interval(type_, startdate, enddate, dealer, vendor)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['date'], y=data['index'], name='График индексов общего рынка'))

    fig_json = fig.to_json()
    return jsonify({'fig_json': fig_json})


@app.route('/compare', methods=['POST'])
def compare():
    # Сбор данных с формы
    ind = request.form['ind']
    type_ = request.form['type']
    vendor = request.form['vendor']
    if vendor == 'all_v':
        vendor = None
    dealer = int(current_user.type_[1:])
    startdate = request.form['startdate']
    enddate = request.form['enddate']

    # Постройка графиков в зависимости от выбранного индекса
    if ind == 'Ins_mov':
        data = indexes.instant_moving_index_interval(type_, startdate, enddate, dealer, vendor)
    elif ind == 'Ins_y-y':
        data = indexes.instant_year_year_index_interval(type_, startdate, enddate, dealer, vendor)
    elif ind == 'Cur_mov':
        data = indexes.current_moving_index_interval(type_, startdate, enddate, dealer, vendor)
    elif ind == 'Cur_y-y':
        data = indexes.current_year_year_index_interval(type_, startdate, enddate, dealer, vendor)
    elif ind == 'Long_mov':
        data = indexes.long_moving_index_interval(type_, startdate, enddate, dealer, vendor)
    elif ind == 'Long_y-y':
        data = indexes.long_year_year_index_interval(type_, startdate, enddate, dealer, vendor)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['date'], y=data['index'], name='График сравнения'))
    fig.update_layout(
        legend=dict(
            x=-10,  # Указывает позицию по горизонтали (1 = крайнее правое положение)
            y=1,  # Указывает позицию по вертикали (1 = крайнее верхнее положение)
        )
    )
    fig_json = fig.to_json()

    return jsonify({'fig_json': fig_json})


if __name__ == '__main__':
    app.run()
