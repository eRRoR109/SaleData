from flask import Flask, render_template, request, jsonify
import indexes
import plotly.express as pe

app = Flask(__name__)


@app.route('/')  # Главная страница (index.html)
def index():
    return render_template('index.html')


@app.route('/login')  # Страница с входом
def login():
    return render_template('login.html')


@app.route('/reg')  # Страница с регистрацией
def registration():
    return render_template('registration.html')


@app.route('/analysis')  # Страница с графиками/данными
def analysis():
    return render_template('analysis.html')


@app.route('/help')  # Страница "about"
def help():
    return render_template('help.html')


@app.route('/plot', methods=['POST'])  # через эту функцию строятся графики
def plot():
    # Сбор данных с формы
    ind = request.form['ind']
    type_ = request.form['type']
    vendor = request.form['vendor']
    if vendor == 'all_v':
        vendor = None
    dealer = request.form['dealer']
    if dealer == 'all_d':
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

    fig = pe.line(x=data['date'], y=data['index'])

    fig_json = fig.to_json()
    return jsonify({'fig_json': fig_json})


if __name__ == '__main__':
    app.run(debug=True)
