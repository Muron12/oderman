from flask import Flask, render_template, request, redirect, url_for, flash
from forms import FeedbackForm
import sqlite3
import os

app = Flask(__name__)
app.secret_key = '1234'

def insert_feedback(name, rating, comment):
    conn = sqlite3.connect('oderman.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO feedbacks (name, rating, comment) VALUES (?, ?, ?)",
                   (name, rating, comment))
    conn.commit()
    conn.close()

def get_all_feedbacks():
    conn = sqlite3.connect('oderman.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, rating, comment FROM feedbacks")
    feedbacks = cursor.fetchall()
    conn.close()
    return feedbacks

def get_db_connection():
    conn = sqlite3.connect('oderman.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        insert_feedback(form.name.data, form.rating.data, form.comment.data)
        flash('Відгук надіслано!', 'success')
        return redirect(url_for('show_feedbacks'))
    return render_template('feedback.html', form=form)

@app.route('/reviews')
def show_feedbacks():
    rows = get_all_feedbacks()
    feedbacks = [{'name': row[0], 'rating': row[1], 'comment': row[2]} for row in rows]
    return render_template('reviews.html', feedbacks=feedbacks)

@app.route('/poll', methods=['GET', 'POST'])
def poll():
    conn = get_db_connection()
    pizzas = conn.execute('SELECT name FROM menu_items').fetchall()

    if request.method == 'POST':
        selected_dish = request.form['dish']
        conn.execute('INSERT INTO votes (dish_name) VALUES (?)', (selected_dish,))
        conn.commit()
        conn.close()
        return redirect(url_for('results'))

    conn.close()
    return render_template('poll.html', pizzas=pizzas)

@app.route('/results')
def results():
    conn = get_db_connection()
    votes = conn.execute('SELECT dish_name, COUNT(*) as count FROM votes GROUP BY dish_name ORDER BY count DESC').fetchall()
    conn.close()
    return render_template('results.html', votes=votes)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu')
def menu():
    sort_order = request.args.get('sort', default='none')
    conn = get_db_connection()
    pizzas = conn.execute('SELECT * FROM menu_items').fetchall()
    conn.close()

    if sort_order == 'asc':
        pizzas = sorted(pizzas, key=lambda x: x['price'])
    elif sort_order == 'desc':
        pizzas = sorted(pizzas, key=lambda x: x['price'], reverse=True)

    return render_template('menu.html', pizzas=pizzas)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = get_db_connection()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])

        conn.execute(
            'INSERT INTO menu_items (name, description, price) VALUES (?, ?, ?)',
            (name, description, price)
        )
        conn.commit()

    pizzas = conn.execute('SELECT * FROM menu_items').fetchall()
    conn.close()
    return render_template('admin.html', pizzas=pizzas)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    pizza = conn.execute('SELECT * FROM menu_items WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        description = request.form['description']
        conn.execute('UPDATE menu_items SET description = ? WHERE id = ?', (description, id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))

    conn.close()
    return render_template('edit.html', pizza=pizza)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM menu_items WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
