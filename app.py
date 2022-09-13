from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return render_template('layout.html')


@app.route('/dashboard')
def Dashboard():
    return render_template('dashboard.html')


@app.route('/product')
def Product():
    return render_template('product.html')


@app.route('/help')
def Help():
    return render_template('help.html')


@app.route('/setting')
def Setting():
    return render_template('setting.html')


if __name__ == '__main__':
    app.run()
