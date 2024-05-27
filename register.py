from flask import Flask, render_template, request, redirect, url_for, flash
from flask import Blueprint, render_template
import psycopg2

register_bp = Blueprint('register_bp', __name__)

app = Flask(__name__)

conn = psycopg2.connect(
    dbname="zxc",
    user="postgres",
    password="39423942",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if not username or not email or not password:
            flash('Заполните все поля', 'error')
            return redirect(url_for('register_bp.register'))
        
        cur.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cur.fetchone()
        if existing_user:
            flash('Пользователь с таким именем или почтой уже существует', 'error')
            return redirect(url_for('register_bp.register'))
        
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
        conn.commit()
        
        flash('Регистрация прошла успешно', 'success')
        # return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/success')
def success():
    return "регистрция прошала успешно"

if __name__ == '__main__':
    app.run(debug=True)
