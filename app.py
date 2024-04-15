from flask import Flask, render_template, request
import battery_calculation
import plot_creation

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        date = request.form['date']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        initial_battery_charge = float(request.form['initial_battery_charge'])
        power_consumption_rate = float(request.form['power_consumption_rate'])
        mode = request.form['mode']
        # getting processed data for battery charge and discharge
        data = battery_calculation.battery_calculation(initial_battery_charge, latitude, longitude,
                                                       date, power_consumption_rate, mode)
        # print(data)
        graphs = plot_creation.get_graph(data)
    return render_template('result.html', graphs=graphs)


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
