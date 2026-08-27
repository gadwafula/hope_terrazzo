import sqlite3
import os
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line

# Set app background color
Window.clearcolor = (0.91, 0.92, 0.94, 1)

class DesktopCard(BoxLayout):
    """Card container with background and border."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            Color(0.75, 0.78, 0.82, 1)
            self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=1)
        self.bind(pos=self._update_graphics, size=self._update_graphics)

    def _update_graphics(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.border.rectangle = (self.x, self.y, self.width, self.height)

class HopeTerrazzoApp(App):
    def build(self):
        self.init_db()
        
        root = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(6))
        
        # Top Header Bar
        header = BoxLayout(size_hint_y=None, height=dp(48), padding=[dp(10), 0])
        with header.canvas.before:
            Color(0.22, 0.25, 0.30, 1)
            self.header_bg = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda inst, val: setattr(self.header_bg, 'pos', header.pos),
                    size=lambda inst, val: setattr(self.header_bg, 'size', header.size))
        
        header_title = Label(
            text="HOPE TERRAZZO INVENTORY & SALES",
            font_size=sp(14),
            bold=True,
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle'
        )
        header_title.bind(size=header_title.setter('text_size'))
        header.add_widget(header_title)
        root.add_widget(header)

        # Tab Bar
        self.tab_bar = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(2))
        
        self.btn_tab_sale = Button(text="Record Sale", font_size=sp(11), bold=True, on_press=lambda x: self.switch_tab('sale'))
        self.btn_tab_stock = Button(text="Add Stock", font_size=sp(11), bold=True, on_press=lambda x: self.switch_tab('stock'))
        self.btn_tab_view = Button(text="View Inventory", font_size=sp(10), bold=True, on_press=lambda x: self.switch_tab('inventory'))
        self.btn_tab_report = Button(text="Sales & Report", font_size=sp(10), bold=True, on_press=lambda x: self.switch_tab('report'))

        for btn in [self.btn_tab_sale, self.btn_tab_stock, self.btn_tab_view, self.btn_tab_report]:
            self.tab_bar.add_widget(btn)
        root.add_widget(self.tab_bar)

        # Tab Content Manager
        self.sm = ScreenManager()
        self.sm.add_widget(self.create_sale_screen())
        self.sm.add_widget(self.create_stock_screen())
        self.sm.add_widget(self.create_inventory_screen())
        self.sm.add_widget(self.create_report_screen())

        root.add_widget(self.sm)
        self.switch_tab('sale')
        return root

    def get_db_path(self):
        """Returns safe internal app data storage path for Android."""
        return os.path.join(self.user_data_dir, "terrazzo.db")

    def set_tab_colors(self, active_tab):
        tabs = {
            'sale': self.btn_tab_sale,
            'stock': self.btn_tab_stock,
            'inventory': self.btn_tab_view,
            'report': self.btn_tab_report
        }
        for key, btn in tabs.items():
            if key == active_tab:
                btn.background_normal = ''
                btn.background_color = (0.35, 0.42, 0.50, 1)
                btn.color = (1, 1, 1, 1)
            else:
                btn.background_normal = ''
                btn.background_color = (0.82, 0.85, 0.88, 1)
                btn.color = (0.2, 0.2, 0.2, 1)

    def switch_tab(self, tab_name):
        self.set_tab_colors(tab_name)
        if tab_name == 'inventory':
            self.refresh_inventory_table()
        elif tab_name == 'report':
            self.refresh_report_table()
        self.refresh_spinners()
        self.sm.current = tab_name

    def create_sale_screen(self):
        screen = Screen(name='sale')
        card = DesktopCard(orientation='vertical', padding=dp(16), spacing=dp(12), size_hint=(1, 1))
        
        card.add_widget(Label(
            text="Record Daily Transaction",
            font_size=sp(14), bold=True, color=(0.15, 0.2, 0.3, 1),
            size_hint_y=None, height=dp(25), halign='left'
        ))
        
        grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(90))
        grid.add_widget(Label(text="Select Product:", font_size=sp(12), color=(0.1, 0.1, 0.1, 1), halign='left'))
        
        self.sale_spinner = Spinner(
            text='Select Product...', values=self.get_product_options(),
            size_hint_y=None, height=dp(38), font_size=sp(11)
        )
        grid.add_widget(self.sale_spinner)

        grid.add_widget(Label(text="Quantity Sold:", font_size=sp(12), color=(0.1, 0.1, 0.1, 1), halign='left'))
        self.sale_qty_input = TextInput(
            input_filter='int', multiline=False, size_hint_y=None, height=dp(38), font_size=sp(13)
        )
        grid.add_widget(self.sale_qty_input)
        card.add_widget(grid)

        btn_sale = Button(
            text="Record Sale", font_size=sp(12), bold=True,
            size_hint=(None, None), size=(dp(130), dp(36)), pos_hint={'center_x': 0.5},
            background_normal='', background_color=(0.25, 0.50, 0.85, 1), color=(1, 1, 1, 1),
            on_press=self.record_sale
        )
        card.add_widget(btn_sale)

        self.sale_log = Label(text="", font_size=sp(12), color=(0.2, 0.4, 0.2, 1), size_hint_y=None, height=dp(40))
        card.add_widget(self.sale_log)
        screen.add_widget(card)
        return screen

    def create_stock_screen(self):
        screen = Screen(name='stock')
        card = DesktopCard(orientation='vertical', padding=dp(16), spacing=dp(12), size_hint=(1, 1))
        
        card.add_widget(Label(
            text="Add Inventory Stock",
            font_size=sp(14), bold=True, color=(0.15, 0.2, 0.3, 1),
            size_hint_y=None, height=dp(25), halign='left'
        ))
        
        grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(90))
        grid.add_widget(Label(text="Select Product:", font_size=sp(12), color=(0.1, 0.1, 0.1, 1), halign='left'))
        
        self.stock_spinner = Spinner(
            text='Select Product...', values=self.get_product_options(),
            size_hint_y=None, height=dp(38), font_size=sp(11)
        )
        grid.add_widget(self.stock_spinner)

        grid.add_widget(Label(text="Quantity to Add:", font_size=sp(12), color=(0.1, 0.1, 0.1, 1), halign='left'))
        self.stock_qty_input = TextInput(
            input_filter='int', multiline=False, size_hint_y=None, height=dp(38), font_size=sp(13)
        )
        grid.add_widget(self.stock_qty_input)
        card.add_widget(grid)

        btn_stock = Button(
            text="Add Stock", font_size=sp(12), bold=True,
            size_hint=(None, None), size=(dp(130), dp(36)), pos_hint={'center_x': 0.5},
            background_normal='', background_color=(0.20, 0.60, 0.35, 1), color=(1, 1, 1, 1),
            on_press=self.add_stock
        )
        card.add_widget(btn_stock)

        self.stock_log = Label(text="", font_size=sp(12), color=(0.2, 0.4, 0.2, 1), size_hint_y=None, height=dp(40))
        card.add_widget(self.stock_log)
        screen.add_widget(card)
        return screen

    def create_inventory_screen(self):
        screen = Screen(name='inventory')
        card = DesktopCard(orientation='vertical', padding=dp(12), spacing=dp(8), size_hint=(1, 1))
        
        card.add_widget(Label(
            text="Current Stock Levels", font_size=sp(14), bold=True,
            color=(0.15, 0.2, 0.3, 1), size_hint_y=None, height=dp(25)
        ))

        scroll = ScrollView(size_hint=(1, 1))
        self.inventory_grid = GridLayout(cols=4, spacing=dp(4), size_hint_y=None)
        self.inventory_grid.bind(minimum_height=self.inventory_grid.setter('height'))
        scroll.add_widget(self.inventory_grid)
        
        card.add_widget(scroll)
        screen.add_widget(card)
        return screen

    def create_report_screen(self):
        screen = Screen(name='report')
        card = DesktopCard(orientation='vertical', padding=dp(12), spacing=dp(8), size_hint=(1, 1))
        
        card.add_widget(Label(
            text="Sales & Profit Log", font_size=sp(14), bold=True,
            color=(0.15, 0.2, 0.3, 1), size_hint_y=None, height=dp(25)
        ))

        scroll = ScrollView(size_hint=(1, 1))
        self.report_grid = GridLayout(cols=4, spacing=dp(4), size_hint_y=None)
        self.report_grid.bind(minimum_height=self.report_grid.setter('height'))
        scroll.add_widget(self.report_grid)
        
        card.add_widget(scroll)
        screen.add_widget(card)
        return screen

    def init_db(self):
        conn = sqlite3.connect(self.get_db_path())
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

    def get_product_options(self):
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, stock FROM products")
        rows = cursor.fetchall()
        conn.close()
        return [f"{r[0]} - {r[1]} (Stock: {r[2]})" for r in rows]

    def refresh_spinners(self):
        opts = self.get_product_options()
        self.sale_spinner.values = opts
        self.stock_spinner.values = opts

    def record_sale(self, instance):
        prod_text, qty_text = self.sale_spinner.text, self.sale_qty_input.text
        if 'Select' in prod_text or not qty_text:
            self.sale_log.text = "⚠️ Select product & enter quantity."
            return
        prod_id = int(prod_text.split(" - ")[0])
        qty = int(qty_text)
        
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT name, buying_price, selling_price, stock FROM products WHERE id=?", (prod_id,))
        item = cursor.fetchone()
        
        if not item or item[3] < qty:
            self.sale_log.text = f"⚠️ Insufficient stock! Available: {item[3] if item else 0}"
            conn.close()
            return
            
        cost, rev = item[1] * qty, item[2] * qty
        profit = rev - cost
        today = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute("INSERT INTO sales (product_name, quantity, total_cost, total_revenue, profit, date) VALUES (?, ?, ?, ?, ?, ?)",
                       (item[0], qty, cost, rev, profit, today))
        cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, prod_id))
        conn.commit()
        conn.close()
        
        self.sale_log.text = f"✔ Recorded! Revenue: KES {rev:,.0f} | Profit: KES {profit:,.0f}"
        self.sale_qty_input.text = ""
        self.refresh_spinners()

    def add_stock(self, instance):
        prod_text, qty_text = self.stock_spinner.text, self.stock_qty_input.text
        if 'Select' in prod_text or not qty_text:
            self.stock_log.text = "⚠️ Select product & enter quantity."
            return
        prod_id = int(prod_text.split(" - ")[0])
        qty = int(qty_text)
        
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET stock = stock + ? WHERE id=?", (qty, prod_id))
        conn.commit()
        conn.close()
        
        self.stock_log.text = f"✔ Added {qty} units to stock."
        self.stock_qty_input.text = ""
        self.refresh_spinners()

    def refresh_inventory_table(self):
        self.inventory_grid.clear_widgets()
        headers = ["ID", "Product Name", "Price (KES)", "Stock"]
        for h in headers:
            self.inventory_grid.add_widget(Label(text=h, bold=True, font_size=sp(11), color=(0.1, 0.1, 0.1, 1), size_hint_y=None, height=dp(28)))
            
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, selling_price, stock FROM products")
        for r in cursor.fetchall():
            self.inventory_grid.add_widget(Label(text=str(r[0]), font_size=sp(11), color=(0.2, 0.2, 0.2, 1), size_hint_y=None, height=dp(24)))
            self.inventory_grid.add_widget(Label(text=str(r[1]), font_size=sp(11), color=(0.2, 0.2, 0.2, 1), size_hint_y=None, height=dp(24)))
            self.inventory_grid.add_widget(Label(text=f"{r[2]:,.0f}", font_size=sp(11), color=(0.2, 0.2, 0.2, 1), size_hint_y=None, height=dp(24)))
            self.inventory_grid.add_widget(Label(text=str(r[3]), font_size=sp(11), color=(0.2, 0.2, 0.2, 1), size_hint_y=None, height=dp(24)))
        conn.close()

    def refresh_report_table(self):
        self.report_grid.clear_widgets()
        headers = ["Date", "Product", "Qty", "Profit (KES)"]
        for h in headers:
            self.report_grid.add_widget(Label(text=h, bold=True, font_size=sp(11), color=(0.1, 0.1, 0.1, 1), size_hint_y=None, height=dp(28)))
            
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT date, product_name, quantity, profit FROM sales ORDER BY id DESC")
        for r in cursor.fetchall():
            self.report_grid.add_widget(Label(text=str(r[0]), font_size=sp(10), color=(0.2, 0.2, 0.2, 1), size_hint_y=None, height=dp(24)))
            self.report_grid.add_widget(Label(text=str(r[1]), font_size=sp(10), color=(0.2, 0.2, 0.2, 1), size_hint_y=None, height=dp(24)))
            self.report_grid.add_widget(Label(text=str(r[2]), font_size=sp(10), color=(0.2, 0.2, 0.2, 1), size_hint_y=None, height=dp(24)))
            self.report_grid.add_widget(Label(text=f"{r[3]:,.0f}", font_size=sp(10), color=(0.2, 0.2, 0.2, 1), size_hint_y=None, height=dp(24)))
        conn.close()

if __name__ == "__main__":
    HopeTerrazzoApp().run()
