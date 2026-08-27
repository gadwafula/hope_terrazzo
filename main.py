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
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line

# Modern dark slate background
Window.clearcolor = (0.10, 0.12, 0.16, 1)

class ModernCard(BoxLayout):
    """Custom styled card container with subtle borders for high contrast."""
    def __init__(self, bg_color=(0.16, 0.20, 0.27, 1), **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
            Color(0.25, 0.30, 0.40, 1)
            self.border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(8)), width=dp(1))
        self.bind(pos=self._update_graphics, size=self._update_graphics)

    def _update_graphics(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(8))

class HopeTerrazzoApp(App):
    def build(self):
        self.init_db()
        
        root = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(6))
        
        # 1. Header Bar
        header = BoxLayout(size_hint_y=None, height=dp(48), padding=[dp(10), 0])
        with header.canvas.before:
            Color(0.14, 0.17, 0.23, 1)
            self.header_bg = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda inst, val: setattr(self.header_bg, 'pos', header.pos),
                    size=lambda inst, val: setattr(self.header_bg, 'size', header.size))
        
        header_title = Label(
            text="HOPE TERRAZZO INVENTORY & SALES",
            font_size=sp(13),
            bold=True,
            color=(0.90, 0.94, 1.0, 1),
            halign='center',
            valign='middle'
        )
        header_title.bind(size=header_title.setter('text_size'))
        header.add_widget(header_title)
        root.add_widget(header)

        # 2. Navigation Tab Bar (5 Tabs)
        self.tab_bar = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(2))
        
        self.btn_tab_sale = Button(text="Sale", font_size=sp(10), bold=True, on_press=lambda x: self.switch_tab('sale'))
        self.btn_tab_stock = Button(text="Stock", font_size=sp(10), bold=True, on_press=lambda x: self.switch_tab('stock'))
        self.btn_tab_view = Button(text="Inventory", font_size=sp(10), bold=True, on_press=lambda x: self.switch_tab('inventory'))
        self.btn_tab_manage = Button(text="Manage", font_size=sp(10), bold=True, on_press=lambda x: self.switch_tab('manage'))
        self.btn_tab_report = Button(text="Report", font_size=sp(10), bold=True, on_press=lambda x: self.switch_tab('report'))

        for btn in [self.btn_tab_sale, self.btn_tab_stock, self.btn_tab_view, self.btn_tab_manage, self.btn_tab_report]:
            self.tab_bar.add_widget(btn)
        root.add_widget(self.tab_bar)

        # 3. Screen Manager
        self.sm = ScreenManager()
        self.sm.add_widget(self.create_sale_screen())
        self.sm.add_widget(self.create_stock_screen())
        self.sm.add_widget(self.create_inventory_screen())
        self.sm.add_widget(self.create_manage_screen())
        self.sm.add_widget(self.create_report_screen())

        root.add_widget(self.sm)
        self.switch_tab('sale')
        return root

    def get_db_path(self):
        return os.path.join(self.user_data_dir, "terrazzo.db")

    def set_tab_colors(self, active_tab):
        tabs = {
            'sale': self.btn_tab_sale,
            'stock': self.btn_tab_stock,
            'inventory': self.btn_tab_view,
            'manage': self.btn_tab_manage,
            'report': self.btn_tab_report
        }
        for key, btn in tabs.items():
            if key == active_tab:
                btn.background_normal = ''
                btn.background_color = (0.22, 0.45, 0.85, 1)  # Active Accent Blue
                btn.color = (1, 1, 1, 1)
            else:
                btn.background_normal = ''
                btn.background_color = (0.16, 0.20, 0.26, 1)  # Inactive Dark Slate
                btn.color = (0.7, 0.75, 0.85, 1)

    def switch_tab(self, tab_name):
        self.set_tab_colors(tab_name)
        if tab_name == 'inventory':
            self.refresh_inventory_table()
        elif tab_name == 'report':
            self.refresh_report_table()
        self.refresh_spinners()
        self.sm.current = tab_name

    # --- TAB 1: RECORD SALE ---
    def create_sale_screen(self):
        screen = Screen(name='sale')
        card = ModernCard(orientation='vertical', padding=dp(14), spacing=dp(10), size_hint=(1, 1))
        
        card.add_widget(Label(
            text="Record Daily Transaction", font_size=sp(13), bold=True,
            color=(0.9, 0.95, 1, 1), size_hint_y=None, height=dp(25)
        ))
        
        grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(85))
        grid.add_widget(Label(text="Select Product:", font_size=sp(11), color=(0.75, 0.8, 0.9, 1)))
        
        self.sale_spinner = Spinner(
            text='Select Product...', values=self.get_product_options(),
            size_hint_y=None, height=dp(36), font_size=sp(11)
        )
        grid.add_widget(self.sale_spinner)

        grid.add_widget(Label(text="Quantity Sold:", font_size=sp(11), color=(0.75, 0.8, 0.9, 1)))
        self.sale_qty_input = TextInput(
            input_filter='int', multiline=False, size_hint_y=None, height=dp(36), font_size=sp(12)
        )
        grid.add_widget(self.sale_qty_input)
        card.add_widget(grid)

        btn_sale = Button(
            text="Record Sale", font_size=sp(12), bold=True,
            size_hint=(None, None), size=(dp(140), dp(36)), pos_hint={'center_x': 0.5},
            background_normal='', background_color=(0.10, 0.65, 0.45, 1), color=(1, 1, 1, 1),
            on_press=self.record_sale
        )
        card.add_widget(btn_sale)

        self.sale_log = Label(text="", font_size=sp(11), color=(0.4, 0.9, 0.6, 1), size_hint_y=None, height=dp(35))
        card.add_widget(self.sale_log)
        screen.add_widget(card)
        return screen

    # --- TAB 2: ADD STOCK ---
    def create_stock_screen(self):
        screen = Screen(name='stock')
        card = ModernCard(orientation='vertical', padding=dp(14), spacing=dp(10), size_hint=(1, 1))
        
        card.add_widget(Label(
            text="Add Inventory Stock", font_size=sp(13), bold=True,
            color=(0.9, 0.95, 1, 1), size_hint_y=None, height=dp(25)
        ))
        
        grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(85))
        grid.add_widget(Label(text="Select Product:", font_size=sp(11), color=(0.75, 0.8, 0.9, 1)))
        
        self.stock_spinner = Spinner(
            text='Select Product...', values=self.get_product_options(),
            size_hint_y=None, height=dp(36), font_size=sp(11)
        )
        grid.add_widget(self.stock_spinner)

        grid.add_widget(Label(text="Quantity to Add:", font_size=sp(11), color=(0.75, 0.8, 0.9, 1)))
        self.stock_qty_input = TextInput(
            input_filter='int', multiline=False, size_hint_y=None, height=dp(36), font_size=sp(12)
        )
        grid.add_widget(self.stock_qty_input)
        card.add_widget(grid)

        btn_stock = Button(
            text="Add Stock", font_size=sp(12), bold=True,
            size_hint=(None, None), size=(dp(140), dp(36)), pos_hint={'center_x': 0.5},
            background_normal='', background_color=(0.20, 0.55, 0.85, 1), color=(1, 1, 1, 1),
            on_press=self.add_stock
        )
        card.add_widget(btn_stock)

        self.stock_log = Label(text="", font_size=sp(11), color=(0.4, 0.9, 0.6, 1), size_hint_y=None, height=dp(35))
        card.add_widget(self.stock_log)
        screen.add_widget(card)
        return screen

    # --- TAB 3: VIEW INVENTORY ---
    def create_inventory_screen(self):
        screen = Screen(name='inventory')
        card = ModernCard(orientation='vertical', padding=dp(10), spacing=dp(6), size_hint=(1, 1))
        
        card.add_widget(Label(
            text="Current Stock & Pricing Catalog", font_size=sp(13), bold=True,
            color=(0.9, 0.95, 1, 1), size_hint_y=None, height=dp(25)
        ))

        scroll = ScrollView(size_hint=(1, 1))
        self.inventory_grid = GridLayout(cols=5, spacing=dp(3), size_hint_y=None)
        self.inventory_grid.bind(minimum_height=self.inventory_grid.setter('height'))
        scroll.add_widget(self.inventory_grid)
        
        card.add_widget(scroll)
        screen.add_widget(card)
        return screen

    # --- TAB 4: MANAGE PRODUCTS & PRICES ---
    def create_manage_screen(self):
        screen = Screen(name='manage')
        scroll = ScrollView(size_hint=(1, 1))
        container = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, padding=dp(2))
        container.bind(minimum_height=container.setter('height'))

        # Card A: Add New Product
        card_add = ModernCard(orientation='vertical', padding=dp(12), spacing=dp(8), size_hint_y=None, height=dp(200))
        card_add.add_widget(Label(
            text="➕ Add New Product", font_size=sp(12), bold=True,
            color=(0.9, 0.95, 1, 1), size_hint_y=None, height=dp(22)
        ))
        
        grid_add = GridLayout(cols=2, spacing=dp(6), size_hint_y=None, height=dp(105))
        grid_add.add_widget(Label(text="Name:", font_size=sp(10), color=(0.75, 0.8, 0.9, 1)))
        self.new_name_input = TextInput(multiline=False, size_hint_y=None, height=dp(32), font_size=sp(11))
        grid_add.add_widget(self.new_name_input)

        grid_add.add_widget(Label(text="Buying Price (KES):", font_size=sp(10), color=(0.75, 0.8, 0.9, 1)))
        self.new_buy_input = TextInput(input_filter='float', multiline=False, size_hint_y=None, height=dp(32), font_size=sp(11))
        grid_add.add_widget(self.new_buy_input)

        grid_add.add_widget(Label(text="Selling Price (KES):", font_size=sp(10), color=(0.75, 0.8, 0.9, 1)))
        self.new_sell_input = TextInput(input_filter='float', multiline=False, size_hint_y=None, height=dp(32), font_size=sp(11))
        grid_add.add_widget(self.new_sell_input)

        card_add.add_widget(grid_add)
        btn_add = Button(
            text="Create Product", font_size=sp(11), bold=True, size_hint_y=None, height=dp(32),
            background_normal='', background_color=(0.15, 0.60, 0.45, 1), color=(1, 1, 1, 1),
            on_press=self.add_new_product
        )
        card_add.add_widget(btn_add)
        container.add_widget(card_add)

        # Card B: Modify Existing Prices
        card_edit = ModernCard(orientation='vertical', padding=dp(12), spacing=dp(8), size_hint_y=None, height=dp(210))
        card_edit.add_widget(Label(
            text="✏️ Edit Product Prices", font_size=sp(12), bold=True,
            color=(0.9, 0.95, 1, 1), size_hint_y=None, height=dp(22)
        ))

        grid_edit = GridLayout(cols=2, spacing=dp(6), size_hint_y=None, height=dp(115))
        grid_edit.add_widget(Label(text="Select Product:", font_size=sp(10), color=(0.75, 0.8, 0.9, 1)))
        self.manage_spinner = Spinner(
            text='Select Product...', values=self.get_product_options(),
            size_hint_y=None, height=dp(34), font_size=sp(10)
        )
        grid_edit.add_widget(self.manage_spinner)

        grid_edit.add_widget(Label(text="New Buying Price:", font_size=sp(10), color=(0.75, 0.8, 0.9, 1)))
        self.edit_buy_input = TextInput(input_filter='float', multiline=False, size_hint_y=None, height=dp(32), font_size=sp(11))
        grid_edit.add_widget(self.edit_buy_input)

        grid_edit.add_widget(Label(text="New Selling Price:", font_size=sp(10), color=(0.75, 0.8, 0.9, 1)))
        self.edit_sell_input = TextInput(input_filter='float', multiline=False, size_hint_y=None, height=dp(32), font_size=sp(11))
        grid_edit.add_widget(self.edit_sell_input)

        card_edit.add_widget(grid_edit)
        btn_update = Button(
            text="Update Prices", font_size=sp(11), bold=True, size_hint_y=None, height=dp(32),
            background_normal='', background_color=(0.80, 0.45, 0.15, 1), color=(1, 1, 1, 1),
            on_press=self.update_product_prices
        )
        card_edit.add_widget(btn_update)
        container.add_widget(card_edit)

        self.manage_log = Label(text="", font_size=sp(11), color=(0.4, 0.9, 0.6, 1), size_hint_y=None, height=dp(30))
        container.add_widget(self.manage_log)

        scroll.add_widget(container)
        screen.add_widget(scroll)
        return screen

    # --- TAB 5: SALES & PROFIT REPORT ---
    def create_report_screen(self):
        screen = Screen(name='report')
        card = ModernCard(orientation='vertical', padding=dp(10), spacing=dp(6), size_hint=(1, 1))
        
        # Total Summary Header Banner
        summary_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(50), padding=[dp(8), dp(4)])
        with summary_box.canvas.before:
            Color(0.20, 0.26, 0.36, 1)
            self.sum_rect = RoundedRectangle(pos=summary_box.pos, size=summary_box.size, radius=[dp(6)])
        summary_box.bind(pos=lambda inst, val: setattr(self.sum_rect, 'pos', summary_box.pos),
                         size=lambda inst, val: setattr(self.sum_rect, 'size', summary_box.size))

        self.total_revenue_label = Label(text="Total Revenue: KES 0.00", font_size=sp(11), color=(0.75, 0.85, 1, 1))
        self.total_profit_label = Label(text="TOTAL PROFIT: KES 0.00", font_size=sp(12), bold=True, color=(0.3, 0.95, 0.5, 1))
        summary_box.add_widget(self.total_revenue_label)
        summary_box.add_widget(self.total_profit_label)
        card.add_widget(summary_box)

        scroll = ScrollView(size_hint=(1, 1))
        self.report_grid = GridLayout(cols=4, spacing=dp(3), size_hint_y=None)
        self.report_grid.bind(minimum_height=self.report_grid.setter('height'))
        scroll.add_widget(self.report_grid)
        
        card.add_widget(scroll)
        screen.add_widget(card)
        return screen

    # --- DATABASE METHODS ---
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
        self.manage_spinner.values = opts

    def add_new_product(self, instance):
        name = self.new_name_input.text.strip()
        buy_text = self.new_buy_input.text.strip()
        sell_text = self.new_sell_input.text.strip()

        if not name or not buy_text or not sell_text:
            self.manage_log.text = "⚠️ Please fill all fields to create a product."
            return

        try:
            buy_p = float(buy_text)
            sell_p = float(sell_text)
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (name, buying_price, selling_price, stock) VALUES (?, ?, ?, 0)",
                           (name, buy_p, sell_p))
            conn.commit()
            conn.close()
            
            self.manage_log.text = f"✔ Added new product '{name}'!"
            self.new_name_input.text = ""
            self.new_buy_input.text = ""
            self.new_sell_input.text = ""
            self.refresh_spinners()
        except sqlite3.IntegrityError:
            self.manage_log.text = "⚠️ Product name already exists."
        except ValueError:
            self.manage_log.text = "⚠️ Invalid price values."

    def update_product_prices(self, instance):
        prod_text = self.manage_spinner.text
        buy_text = self.edit_buy_input.text.strip()
        sell_text = self.edit_sell_input.text.strip()

        if 'Select' in prod_text or (not buy_text and not sell_text):
            self.manage_log.text = "⚠️ Select a product and enter at least one new price."
            return

        prod_id = int(prod_text.split(" - ")[0])
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()

        try:
            if buy_text:
                cursor.execute("UPDATE products SET buying_price = ? WHERE id = ?", (float(buy_text), prod_id))
            if sell_text:
                cursor.execute("UPDATE products SET selling_price = ? WHERE id = ?", (float(sell_text), prod_id))
            
            conn.commit()
            conn.close()
            
            self.manage_log.text = "✔ Product prices updated successfully!"
            self.edit_buy_input.text = ""
            self.edit_sell_input.text = ""
            self.refresh_spinners()
        except ValueError:
            self.manage_log.text = "⚠️ Invalid price entries."
            conn.close()

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
        headers = ["ID", "Name", "Buy (KES)", "Sell (KES)", "Stock"]
        for h in headers:
            self.inventory_grid.add_widget(Label(text=h, bold=True, font_size=sp(10), color=(0.85, 0.9, 1, 1), size_hint_y=None, height=dp(26)))
            
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, buying_price, selling_price, stock FROM products")
        for r in cursor.fetchall():
            self.inventory_grid.add_widget(Label(text=str(r[0]), font_size=sp(10), color=(0.7, 0.75, 0.85, 1), size_hint_y=None, height=dp(24)))
            self.inventory_grid.add_widget(Label(text=str(r[1]), font_size=sp(10), color=(0.7, 0.75, 0.85, 1), size_hint_y=None, height=dp(24)))
            self.inventory_grid.add_widget(Label(text=f"{r[2]:,.0f}", font_size=sp(10), color=(0.7, 0.75, 0.85, 1), size_hint_y=None, height=dp(24)))
            self.inventory_grid.add_widget(Label(text=f"{r[3]:,.0f}", font_size=sp(10), color=(0.7, 0.75, 0.85, 1), size_hint_y=None, height=dp(24)))
            self.inventory_grid.add_widget(Label(text=str(r[4]), font_size=sp(10), color=(0.7, 0.75, 0.85, 1), size_hint_y=None, height=dp(24)))
        conn.close()

    def refresh_report_table(self):
        self.report_grid.clear_widgets()
        headers = ["Date", "Product", "Qty", "Profit (KES)"]
        for h in headers:
            self.report_grid.add_widget(Label(text=h, bold=True, font_size=sp(10), color=(0.85, 0.9, 1, 1), size_hint_y=None, height=dp(26)))
            
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()
        
        # Calculate Total Revenue & Total Profit
        cursor.execute("SELECT SUM(total_revenue), SUM(profit) FROM sales")
        totals = cursor.fetchone()
        tot_rev = totals[0] if totals[0] is not None else 0.0
        tot_prof = totals[1] if totals[1] is not None else 0.0
        
        self.total_revenue_label.text = f"Total Revenue: KES {tot_rev:,.2f}"
        self.total_profit_label.text = f"TOTAL PROFIT: KES {tot_prof:,.2f}"

        # Populate transaction rows
        cursor.execute("SELECT date, product_name, quantity, profit FROM sales ORDER BY id DESC")
        for r in cursor.fetchall():
            self.report_grid.add_widget(Label(text=str(r[0]), font_size=sp(9), color=(0.7, 0.75, 0.85, 1), size_hint_y=None, height=dp(24)))
            self.report_grid.add_widget(Label(text=str(r[1]), font_size=sp(9), color=(0.7, 0.75, 0.85, 1), size_hint_y=None, height=dp(24)))
            self.report_grid.add_widget(Label(text=str(r[2]), font_size=sp(9), color=(0.7, 0.75, 0.85, 1), size_hint_y=None, height=dp(24)))
            self.report_grid.add_widget(Label(text=f"{r[3]:,.0f}", font_size=sp(9), color=(0.4, 0.9, 0.6, 1), size_hint_y=None, height=dp(24)))
        conn.close()

if __name__ == "__main__":
    HopeTerrazzoApp().run()
