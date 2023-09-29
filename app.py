from flask import Flask, render_template, request, jsonify
from genplot import generate_plot

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot():
    selected_date_range = request.form.get('date_range')
    selected_vendor = request.form.get('vendor')
    selected_model = request.form.get('model')
    selected_dealer = request.form.get('dealer')

    fig_json, mean, pchange = generate_plot(
        selected_date_range=selected_date_range,
        selected_vendor=selected_vendor,
        selected_model=selected_model,
        selected_dealer=selected_dealer
    )

    return jsonify({'fig_json': fig_json, 'mean': mean, 'pchange': pchange})

if __name__ == '__main__':
    app.run(debug=True)
