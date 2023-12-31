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


# Функция для установления соединения с базой данных (sqlite)
def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    # Соединение с бд если оно еще не установлено
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@login_manager.user_loader
def load_user(user_id):
    # Загрузка пользователя в текущей сессии
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
        user = dbase.getUserByEmail(request.form['email'])  # получаем данные пользователя из бд по введенной почте
        if user and check_password_hash(user['password'],
                                        request.form['psw']):  # если совпал пароль и данные в бд не пустые
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False  # чекбокс запомнить меня
            login_user(userlogin, remember=rm)
            return redirect(url_for('analysis'))  # в случае если все правильго перенаправляем на /analysis

        flash("Неверная почта/пароль")  # Сообщение пользователю при неправильном вводе

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    # функция выхода из аккаунта
    logout_user()
    return redirect(url_for('login'))


@app.route('/reg', methods=['POST', 'GET'])  # Страница с регистрацией
def registration():
    db = get_db()
    dbase = IDAtaBase(db)
    if request.method == 'POST':
        # Проверки что login > 1 знака, почта > 5, пароль > 5
        if len(request.form['login']) > 1 and len(request.form['email']) > 5 and len(request.form['psw']) > 5:
            hash_ = generate_password_hash(request.form['psw'])  # кодируем пароль пользователя для безопасности
            # добавление пользователя в бд
            res = dbase.addUser(request.form['login'], request.form['email'], hash_)
            if res:
                flash("Вы успешно зарегистрировались")
                return redirect(url_for('login'))
            else:
                flash("Ошибка регистрации")
        else:
            flash("Неверно заполнены поля")

    return render_template('registration.html')


@app.route('/help')  # Страница "about"
def help_():
    return render_template('help.html')


data = indexes.items
vendors = list(data.keys())


@app.route('/analysis')  # Страница с графиками/данными
@login_required
def analysis():
    if current_user.type_ == 'v':  # Если сторонний пользователь
        return render_template('analysis.html', vendors=vendors, data=data)
    else:
        return render_template('analysis_d.html', vendors=vendors, data=data)  # страница если авторизирован дилер


@app.route('/plot', methods=['POST'])  # через эту функцию строятся графики
def plot():
    # Сбор данных с формы
    ind = request.form['ind']
    type_ = request.form['type']
    vendor = request.form.getlist('vendor')
    if vendor == ['all_v']:
        vendor = None
    dealer = None
    model = request.form.getlist('model')
    if model == [] or model == ['all_m']:
        model = None
    startdate = request.form['startdate']
    enddate = request.form['enddate']

    # Постройка графиков в зависимости от выбранного индекса
    if ind == 'Ins_mov':
        data = indexes.instant_moving_index_interval(type_, startdate, enddate, dealer, vendor, model)
    elif ind == 'Ins_y-y':
        data = indexes.instant_year_year_index_interval(type_, startdate, enddate, dealer, vendor, model)
    elif ind == 'Cur_mov':
        data = indexes.current_moving_index_interval(type_, startdate, enddate, dealer, vendor, model)
    elif ind == 'Cur_y-y':
        data = indexes.current_year_year_index_interval(type_, startdate, enddate, dealer, vendor, model)
    elif ind == 'Long_mov':
        data = indexes.long_moving_index_interval(type_, startdate, enddate, dealer, vendor, model)
    elif ind == 'Long_y-y':
        data = indexes.long_year_year_index_interval(type_, startdate, enddate, dealer, vendor, model)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['date'], y=data['index'], name='График индексов общего рынка'))
    fig.update_xaxes(title_text='Дата')
    fig.update_yaxes(title_text='Индекс%')
    fig.update_layout(legend=dict(x=0.5, y=1.1, traceorder='normal', orientation='h'))

    fig_json = fig.to_json()
    return jsonify({'fig_json': fig_json})


@app.route('/compare', methods=['POST'])
def compare():  # сравнение графиков
    # Сбор данных с формы
    ind = request.form['ind']
    type_ = request.form['type']
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
    fig.add_trace(go.Scatter(x=data['date'], y=data['index'], name='График вашего индекса'))
    fig.update_xaxes(title_text='Дата')
    fig.update_yaxes(title_text='Индекс%')
    fig.update_layout(legend=dict(x=0.5, y=1.1, traceorder='normal', orientation='h'))

    fig_json = fig.to_json()

    return jsonify({'fig_json': fig_json})


if __name__ == '__main__':
    app.run()
