from flask import Flask, render_template, request
import json
from datetime import datetime
import os

app = Flask(__name__)

menu = {
    "Pasta": 120,
    "Coffee": 80,
    "Momos": 160,
    "Dosa": 40,
    "Water": 30,
    "Samosa": 34,
    "Burger": 50
}

# Create orders directory if it doesn't exist
if not os.path.exists('orders'):
    os.makedirs('orders')

@app.route('/', methods=['GET', 'POST'])
def home():
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
        
        # Save order to file if there are items
        if ordered_items and customer_name and customer_phone:
            order_data = {
                "order_id": datetime.now().strftime("%Y%m%d%H%M%S"),
                "customer_name": customer_name,
                "customer_phone": customer_phone,
                "items": ordered_items,
                "total": total,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Save to JSON file
            filename = f"orders/order_{order_data['order_id']}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(order_data, f, indent=4, ensure_ascii=False)
            
            # Also append to a master orders file
            with open('orders/all_orders.txt', 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"Order ID: {order_data['order_id']}\n")
                f.write(f"Date & Time: {order_data['timestamp']}\n")
                f.write(f"Customer Name: {customer_name}\n")
                f.write(f"Phone Number: {customer_phone}\n")
                f.write(f"\nOrdered Items:\n")
                for item, qty in ordered_items.items():
                    price = menu[item]
                    f.write(f"  - {item}: {qty} x Rs.{price} = Rs.{qty * price}\n")
                f.write(f"\nTotal Amount: Rs.{total}\n")
                f.write(f"{'='*60}\n")
            
            print(f"✅ Order saved successfully! Order ID: {order_data['order_id']}")

    return render_template('index.html', menu=menu, total=total, ordered_items=ordered_items)

if __name__ == '__main__':
    app.run(debug=True)
"dddddd"    