import sqlite3
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle

# Set background to a modern dark slate tone
Window.clearcolor = (0.07, 0.10, 0.15, 1)

class ModernCard(BoxLayout):
    """Custom container that draws a styled card with rounded corners."""
    def __init__(self, bg_color=(0.12, 0.16, 0.23, 1), radius=14, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.radius = radius
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size

class HopeTerrazzoApp(App):
    def build(self):
        self.init_db()
        
        # Root layout with mobile padding
        root = BoxLayout(orientation='vertical', padding=20, spacing=14)
        
        # 1. Header Card
        header_card = ModernCard(
            bg_color=(0.13, 0.18, 0.27, 1),
            orientation='vertical',
            size_hint_y=None,
            height=85,
            padding=[16, 12, 16, 12],
            spacing=4
        )
        header_title = Label(
            text="HOPE TERRAZZO",
            font_size='22sp',
            bold=True,
            color=(0.95, 0.96, 0.98, 1),
            size_hint_y=None,
            height=30
        )
        header_subtitle = Label(
            text="Sales & Inventory Dashboard",
            font_size='13sp',
            color=(0.55, 0.65, 0.78, 1),
            size_hint_y=None,
            height=20
        )
        header_card.add_widget(header_title)
        header_card.add_widget(header_subtitle)
        root.add_widget(header_card)

        # 2. Main Form Card
        form_card = ModernCard(
            bg_color=(0.11, 0.14, 0.20, 1),
            orientation='vertical',
            size_hint_y=None,
            height=260,
            padding=16,
            spacing=10
        )
        
        # Product Dropdown
        dropdown_label = Label(
            text="PRODUCT CATALOG",
            font_size='11sp',
            bold=True,
            color=(0.45, 0.55, 0.70, 1),
            size_hint_y=None,
            height=18,
            halign='left'
        )
        dropdown_label.bind(size=dropdown_label.setter('text_size'))
        form_card.add_widget(dropdown_label)
        
        self.spinner = Spinner(
            text='Select Product...',
            values=self.get_products(),
            size_hint_y=None,
            height=46,
            background_normal='',
            background_color=(0.18, 0.23, 0.32, 1),
            color=(0.9, 0.92, 0.96, 1),
            font_size='14sp'
        )
        form_card.add_widget(self.spinner)

        # Quantity Input
        qty_label = Label(
            text="QUANTITY",
            font_size='11sp',
            bold=True,
            color=(0.45, 0.55, 0.70, 1),
            size_hint_y=None,
            height=18,
            halign='left'
        )
        qty_label.bind(size=qty_label.setter('text_size'))
        form_card.add_widget(qty_label)
        
        self.qty_input = TextInput(
            hint_text='Enter number of units',
            input_filter='int',
            multiline=False,
            size_hint_y=None,
            height=46,
            font_size='15sp',
            padding=[12, 12, 12, 12],
            background_normal='',
            background_color=(0.18, 0.23, 0.32, 1),
            foreground_color=(0.95, 0.95, 0.95, 1),
            hint_text_color=(0.45, 0.50, 0.60, 1)
        )
        form_card.add_widget(self.qty_input)

        # Action Buttons
        btn_layout = BoxLayout(size_hint_y=None, height=48, spacing=10)
        
        btn_sale = Button(
            text="RECORD SALE",
            font_size='13sp',
            bold=True,
            background_normal='',
            background_color=(0.06, 0.72, 0.50, 1),  # Vibrant Emerald
            color=(1, 1, 1, 1),
            on_press=self.record_sale
        )
        
        btn_stock = Button(
            text="ADD STOCK",
            font_size='13sp',
            bold=True,
            background_normal='',
            background_color=(0.25, 0.47, 0.95, 1),  # Electric Indigo
            color=(1, 1, 1, 1),
            on_press=self.add_stock
        )
        
        btn_layout.add_widget(btn_sale)
        btn_layout.add_widget(btn_stock)
        form_card.add_widget(btn_layout)
        
        root.add_widget(form_card)

        # 3. Output Status Card
        status_card = ModernCard(
            bg_color=(0.13, 0.18, 0.27, 1),
            orientation='vertical',
            size_hint_y=None,
            height=90,
            padding=12
        )
        self.log_label = Label(
            text="System Ready\nSelect a product to begin transaction.",
            font_size='13sp',
            color=(0.7, 0.78, 0.88, 1),
            halign='center',
            valign='middle'
        )
        self.log_label.bind(size=self.log_label.setter('text_size'))
        status_card.add_widget(self.log_label)
        root.add_widget(status_card)

        # Bottom Spacer (Pushes cards to top cleanly)
        root.add_widget(Widget())

        return root

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
        if prod == 'Select Product...' or not qty_text:
            self.log_label.text = "⚠️ Please select a product\nand enter quantity."
            return
        qty = int(qty_text)
        conn = sqlite3.connect("terrazzo.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, buying_price, selling_price, stock FROM products WHERE name=?", (prod,))
        item = cursor.fetchone()
        if not item or item[3] < qty:
            self.log_label.text = f"⚠️ Insufficient stock!\nAvailable: {item[3] if item else 0} units"
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
        self.log_label.text = f"✔ Sale Recorded!\nRevenue: KES {rev:,.2f} | Profit: KES {profit:,.2f}"
        self.qty_input.text = ""

    def add_stock(self, instance):
        prod, qty_text = self.spinner.text, self.qty_input.text
        if prod == 'Select Product...' or not qty_text: 
            self.log_label.text = "⚠️ Please select a product\nand enter quantity."
            return
        conn = sqlite3.connect("terrazzo.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET stock = stock + ? WHERE name=?", (int(qty_text), prod))
        conn.commit()
        conn.close()
        self.log_label.text = f"✔ Stock Updated!\nAdded {qty_text} units to {prod}."
        self.qty_input.text = ""

if __name__ == "__main__":
    HopeTerrazzoApp().run()
