from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import psycopg2

def create_sell_blueprint(app):
    sell_bp = Blueprint('sell', __name__)

    conn = psycopg2.connect(
        dbname="zxc",
        user="postgres",
        password="39423942",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    @app.route('/sell', methods=['GET', 'POST'])
    def sell_item():
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            price = request.form['price']
            dota_login = request.form['dota_login']
            dota_password = request.form['dota_password']
            user_id = session['user_id']
            mmr = request.form['mmr']

            if not title or not description or not price or not dota_login or not dota_password or not mmr:
                # return "Введите все поля"
                flash('Заполните все поля', 'error')
                return redirect(url_for('sell_item'))

            cur.execute("INSERT INTO items (user_id, title, description, price, dota_login, dota_password, mmr) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                         (user_id, title, description, price, dota_login, dota_password, mmr))
            conn.commit()
            return redirect('http://127.0.0.1:5000/profile')

        return render_template('sell_form.html')

    app.register_blueprint(sell_bp)

    return sell_bp
