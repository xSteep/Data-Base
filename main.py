from flask import Flask, render_template, request, session, redirect, url_for, flash
import psycopg2
from register import register_bp
from login import login_bp
from sell import create_sell_blueprint

conn = psycopg2.connect(
    dbname="zxc",
    user="postgres",
    password="39423942",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

app = Flask(__name__)
app.secret_key = 'ASbDUI2GqiuGUIWSDBAJKsbdASIdbAshjDBASJKbdjkBASJbk'
app.register_blueprint(register_bp)
app.register_blueprint(login_bp)
sell_bp = create_sell_blueprint(app)

@app.route('/')
def home():
    sort_by = request.args.get('sort_by', 'price_asc')

    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    min_mmr = request.args.get('min_mmr')
    max_mmr = request.args.get('max_mmr')

    cur.execute("SELECT reviews.id, reviews.text, reviews.created_at, users.username, COUNT(likes.id) AS likes \
                  FROM reviews \
                  LEFT JOIN likes ON reviews.id = likes.review_id \
                  JOIN users ON reviews.user_id = users.id \
                  GROUP BY reviews.id, users.username \
                  ORDER BY reviews.created_at DESC")
    reviews = cur.fetchall()

    cur.execute("SELECT id, title, description, price, sold, mmr, created_at FROM items")
    items = cur.fetchall()

    if min_price:
        items = [item for item in items if item[3] >= int(min_price)]  
    if max_price:
        items = [item for item in items if item[3] <= int(max_price)]
    if min_mmr:
        items = [item for item in items if item[5] >= int(min_mmr)]  
    if max_mmr:
        items = [item for item in items if item[5] <= int(max_mmr)]  

    sort_options = {
        'price_asc': lambda x: x[3],
        'price_desc': lambda x: x[3],
        'mmr_asc': lambda x: x[5],
        'mmr_desc': lambda x: x[5],
        'created_asc': lambda x: x[6],
        'created_desc': lambda x: x[6]
    }

    reverse_sort = sort_by.endswith('_desc')
    sort_key = sort_options.get(sort_by)

    if sort_key:
        items = sorted(items, key=sort_key, reverse=reverse_sort)

    # if sort_by == 'price_asc':
    #     items = sorted(items, key=lambda x: x[3])  
    # elif sort_by == 'price_desc':
    #     items = sorted(items, key=lambda x: x[3], reverse=True)  
    # elif sort_by == 'mmr_asc':
    #     items = sorted(items, key=lambda x: x[5])  
    # elif sort_by == 'mmr_desc':
    #     items = sorted(items, key=lambda x: x[5], reverse=True)  
    # elif sort_by == 'created_asc':
    #     items = sorted(items, key=lambda x: x[6])
    # elif sort_by == 'created_desc':
    #     items = sorted(items, key=lambda x: x[6], reverse=True)

    # if sort_by == 'price_asc':
    #     cur.execute("SELECT id, title, description, price, sold, mmr, created_at FROM items ORDER BY price ASC")
    #     items = cur.fetchall()
    # elif sort_by == 'price_desc':
    #     cur.execute("SELECT id, title, description, price, sold, mmr, created_at FROM items ORDER BY price DESC")
    #     items = cur.fetchall()

    query = request.args.get('query')
    if query:
        items = [item for item in items if query.lower() in item[1].lower() or query.lower() in item[2].lower()]
    # if query:
    #     cur.execute("SELECT id, title, description, price, sold, mmr FROM items WHERE title ILIKE %s OR description ILIKE %s", (f'%{query}%', f'%{query}%'))
    #     items = cur.fetchall()    

    return render_template('main.html', items=items, reviews=reviews)

@app.route('/leave_review', methods=['POST'])
def leave_review():
    if 'user_id' in session:
        user_id = session['user_id']
        text = request.form['text']
        cur.execute("INSERT INTO reviews (user_id, text) VALUES (%s, %s)", (user_id, text))
        conn.commit()
    return redirect(url_for('home'))

@app.route('/like_review/<int:review_id>', methods=['POST'])
def like_review(review_id):
    if 'user_id' in session:
        user_id = session['user_id']
        cur.execute("SELECT * FROM likes WHERE user_id = %s AND review_id = %s", (user_id, review_id))
        if not cur.fetchone():
            cur.execute("INSERT INTO likes (user_id, review_id) VALUES (%s, %s)", (user_id, review_id))
            conn.commit()
            cur.execute("UPDATE reviews SET likes_count = likes_count + 1 WHERE id = %s", (review_id,))
            conn.commit()
            flash('Вы успешно поставили лайк!', 'success')
        else:
            flash('Вы уже поставили лайк', 'error')
    return redirect(url_for('home'))

@app.route('/delete_review/<int:review_id>', methods=['POST'])
def delete_review(review_id):
    if 'user_id' in session:
        user_id = session['user_id']
        cur.execute("SELECT * FROM reviews WHERE id = %s AND user_id = %s", (review_id, user_id))
        review = cur.fetchone()
        if review:
            cur.execute("DELETE FROM likes WHERE review_id = %s", (review_id,))
            cur.execute("DELETE FROM reviews WHERE id = %s", (review_id,))
            conn.commit()
    return redirect(url_for('home'))

@app.route('/buy', methods=['POST'])
def buy():
    if 'username' in session:
        user_id = session['user_id']
        item_id = request.form['item_id']
        
        cur.execute("SELECT sold FROM items WHERE id = %s", (item_id,))
        sold = cur.fetchone()[0]
        if sold:
            return "Этот товар уже продан"
        
        cur.execute("INSERT INTO purchases (user_id, item_id) VALUES (%s, %s)", (user_id, item_id))
        
        cur.execute("UPDATE items SET sold = TRUE WHERE id = %s", (item_id,))
        
        cur.execute("SELECT title, dota_login, dota_password FROM items WHERE id = %s", (item_id,))
        item_info = cur.fetchone()
        title, dota_login, dota_password = item_info
        
        conn.commit()
        
        return f"Вы купили товар '{title}'. Логин от Dota 2: {dota_login}, Пароль от Dota 2: {dota_password}"
    
    return redirect(url_for('login')) 

if __name__ == '__main__':
    app.run(debug=True)










