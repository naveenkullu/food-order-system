from flask import Flask, render_template, request, redirect, url_for, session
import json
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-this-in-production'  # Change this to a random string

menu = {
    "Pasta": 120,
    "Coffee": 80,
    "Momos": 160,
    "Dosa": 40,
    "Water": 30,
    "Samosa": 34,
    "Burger": 50
}

# Initialize database
def init_db():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            customer_name TEXT,
            customer_phone TEXT,
            items TEXT,
            total INTEGER,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

@app.route('/', methods=['GET', 'POST'])
def home():
    order_placed = request.args.get('success') == 'true'
    total = 0
    ordered_items = {}

    if request.method == 'POST':
        # Get customer details
        customer_name = request.form.get('customerName', '').strip()
        customer_phone = request.form.get('customerPhone', '').strip()
        
        # Get ordered items
        for item in menu.keys():
            qty = request.form.get(item)
            if qty and qty.isdigit() and int(qty) > 0:
                qty = int(qty)
                ordered_items[item] = qty
                total += menu[item] * qty
        
        # Save order to database if there are items
        if ordered_items and customer_name and customer_phone:
            order_id = datetime.now().strftime("%Y%m%d%H%M%S")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save to database
            conn = sqlite3.connect('orders.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO orders (order_id, customer_name, customer_phone, items, total, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (order_id, customer_name, customer_phone, json.dumps(ordered_items), total, timestamp))
            conn.commit()
            conn.close()
            
            print(f"✅ Order saved to database! Order ID: {order_id}")
            
            # Redirect with success parameter
            return redirect(url_for('home', success='true'))

    return render_template('index.html', menu=menu, total=0, ordered_items={}, order_placed=order_placed)

@app.route('/orders')
def view_orders():
    """View all orders - optional feature"""
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('SELECT * FROM orders ORDER BY id DESC')
    orders = c.fetchall()
    conn.close()
    
    orders_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>All Orders</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background: #f5f5f5;
            }
            .order {
                background: white;
                padding: 20px;
                margin: 10px 0;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            h1 { color: #667eea; }
            .order-header { 
                font-weight: bold; 
                color: #667eea;
                margin-bottom: 10px;
            }
            .item { margin: 5px 0; }
            .total { 
                font-size: 1.2em; 
                font-weight: bold; 
                color: #764ba2;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <h1>📋 All Orders</h1>
        <a href="/">← Back to Menu</a>
        <hr>
    """
    
    if orders:
        for order in orders:
            items = json.loads(order[4])
            orders_html += f"""
            <div class="order">
                <div class="order-header">Order ID: {order[1]}</div>
                <div><strong>Customer:</strong> {order[2]} | <strong>Phone:</strong> {order[3]}</div>
                <div><strong>Date:</strong> {order[6]}</div>
                <div style="margin-top: 10px;"><strong>Items:</strong></div>
            """
            for item, qty in items.items():
                orders_html += f'<div class="item">  • {item}: {qty} x Rs.{menu[item]} = Rs.{qty * menu[item]}</div>'
            orders_html += f'<div class="total">Total: Rs.{order[5]}</div></div>'
    else:
        orders_html += "<p>No orders yet!</p>"
    
    orders_html += "</body></html>"
    return orders_html

if __name__ == '__main__':
    app.run(debug=True)
