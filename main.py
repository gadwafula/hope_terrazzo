import sqlite3
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner

class HopeTerrazzoApp(App):
    def build(self):
        self.init_db()
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        layout.add_widget(Label(text="HOPE TERRAZZO MANAGEMENT", font_size=18, size_hint_y=None, height=40))
        
        self.spinner = Spinner(text='Select Product', values=self.get_products(), size_hint_y=None, height=44)
        layout.add_widget(self.spinner)
        
        self.qty_input = TextInput(hint_text='Quantity', input_filter='int', multiline=False, size_hint_y=None, height=44)
        layout.add_widget(self.qty_input)
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_sale = Button(text="Record Sale", on_press=self.record_sale)
        btn_stock = Button(text="Add Stock", on_press=self.add_stock)
        btn_layout.add_widget(btn_sale)
        btn_layout.add_widget(btn_stock)
        layout.add_widget(btn_layout)
        
        self.log_label = Label(text="System Ready", size_hint_y=None, height=80)
        layout.add_widget(self.log_label)
        
        return layout

    def init_db(self):
        conn = sqlite3.connect("terrazzo.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS products 
                          (id INTEGER PRIMARY KEY, name TEXT UNIQUE, buying_price REAL, selling_price REAL, stock INTEGER)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS sales 
                          (id INTEGER PRIMARY KEY, product_name TEXT, quantity INTEGER, total_cost REAL, total_revenue REAL, profit REAL, date TEXT)''')
        catalog = [
            ("Black Terrazzo", 265.0, 400.0), ("White Terrazzo", 300.0, 550.0),
            ("Cream Terrazzo", 510.0, 650.0), ("Polish", 1300.0, 2500.0),
            ("Strips", 23.0, 50.0), ("Diamond", 1500.0, 5000.0),
            ("Diamond Machine", 3000.0, 9000.0)
        ]
        for name, buy, sell in catalog:
            cursor.execute("INSERT INTO products (name, buying_price, selling_price, stock) VALUES (?, ?, ?, 0) ON CONFLICT(name) DO NOTHING", (name, buy, sell))
        conn.commit()
        conn.close()

    def get_products(self):
        conn = sqlite3.connect("terrazzo.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM products")
        names = [r[0] for r in cursor.fetchall()]
        conn.close()
        return names

    def record_sale(self, instance):
        prod, qty_text = self.spinner.text, self.qty_input.text
        if prod == 'Select Product' or not qty_text:
            self.log_label.text = "Select a product and enter quantity."
            return
        qty = int(qty_text)
        conn = sqlite3.connect("terrazzo.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, buying_price, selling_price, stock FROM products WHERE name=?", (prod,))
        item = cursor.fetchone()
        if not item or item[3] < qty:
            self.log_label.text = f"Insufficient stock! Available: {item[3] if item else 0}"
            conn.close()
            return
        cost, rev = item[1] * qty, item[2] * qty
        profit = rev - cost
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("INSERT INTO sales (product_name, quantity, total_cost, total_revenue, profit, date) VALUES (?, ?, ?, ?, ?, ?)",
                       (prod, qty, cost, rev, profit, today))
        cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, item[0]))
        conn.commit()
        conn.close()
        self.log_label.text = f"Sale Saved!\nRevenue: KES {rev:,.2f} | Profit: KES {profit:,.2f}"
        self.qty_input.text = ""

    def add_stock(self, instance):
        prod, qty_text = self.spinner.text, self.qty_input.text
        if prod == 'Select Product' or not qty_text: return
        conn = sqlite3.connect("terrazzo.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET stock = stock + ? WHERE name=?", (int(qty_text), prod))
        conn.commit()
        conn.close()
        self.log_label.text = f"Added {qty_text} units to {prod}."
        self.qty_input.text = ""

if __name__ == "__main__":
    HopeTerrazzoApp().run()