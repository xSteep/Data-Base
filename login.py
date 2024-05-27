from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask import Blueprint, render_template

import psycopg2

login_bp = Blueprint('login', __name__)

app = Flask(__name__)
app.secret_key = 'ASbDUI2GqiuGUIWSDBAJKsbdASIdbAshjDBASJKbdjkBASJbk'  

conn = psycopg2.connect(
    dbname="zxc",
    user="postgres",
    password="39423942",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('Заполните все поля', 'error')
            return redirect(url_for('login.login'))
        
        cur.execute("SELECT id FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        if user:
            session['username'] = username  
            session['user_id'] = user[0]  
            return redirect(url_for('home'))  
        else:
            # return "Неправильное имя пользователя или пароль!"
            flash('Неправильное имя пользователя или пароль!', 'error')
            return redirect(url_for('login.login'))
        
    return render_template('login.html')

@login_bp.route('/profile/')
def profile():
    if 'username' in session:
        username = session['username']
        user_id = session['user_id']

        cur.execute("SELECT id, title, description, price, sold, mmr FROM items WHERE user_id = %s", (user_id,))
        items = cur.fetchall()

        cur.execute("SELECT items.id, items.title, items.description, items.price, items.dota_login, items.dota_password FROM items INNER JOIN purchases ON items.id = purchases.item_id WHERE purchases.user_id = %s", (user_id,))
        purchased_items = cur.fetchall()


        return render_template('profile.html', username=username, user_id=user_id, items=items, purchased_items=purchased_items)
    else:
        return redirect(url_for('login'))
    
    
@login_bp.route('/delete_item', methods=['POST'])
def delete_item():
    if 'username' in session:
        user_id = session['user_id']
        item_id = request.form['item_id']

        cur.execute("SELECT * FROM items WHERE id = %s AND user_id = %s", (item_id, user_id))
        item = cur.fetchone()
        if item:
            cur.execute("DELETE FROM items WHERE id = %s", (item_id,))
            conn.commit()
            return redirect('http://127.0.0.1:5000/profile')
        else:
            return "Этот товар не принадлежит вам"
    else:
        return redirect(url_for('login'))

@login_bp.route('/logout')
def logout():
    session.pop('username', None) 
    session.pop('user_id', None)  
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
