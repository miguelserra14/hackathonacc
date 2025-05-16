# app.py (Flask login page with modern UI)

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email and password:
            return redirect(url_for('dashboard', user=email))
        else:
            error = "Please enter both email and password."
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    user = request.args.get('user', 'User')
    return render_template('dashboard.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
