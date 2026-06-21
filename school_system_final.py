"""
PROFESSIONAL SCHOOL MANAGEMENT SYSTEM – SIERRA LEONE (SDG 4)
FULL CRUD WITH EXPLICIT EDIT/DELETE BUTTONS, MODERN CHARTS, CALENDAR PICKERS
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from fpdf import FPDF
import hashlib
import os
import calendar

# ---------- COLOUR SCHEME (MODERN) ----------
COLOURS = {
    'bg': '#E8F4F8',
    'card': '#FFFFFF',
    'primary': '#00ACC1',
    'primary_dark': '#00838F',
    'secondary': '#26C6DA',
    'success': '#4CAF50',
    'warning': '#FF9800',
    'danger': '#F44336',
    'text_dark': '#006064',
    'text_light': '#546E7A',
    'chart_bg': '#F9F9F9'
}

# ---------- DATABASE ----------
DB_FILE = "school.db"

def init_database():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        full_name TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        gender TEXT NOT NULL,
        status TEXT NOT NULL,
        created_date DATE NOT NULL,
        contact TEXT
    )''')
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        admin_pass = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, role, full_name) VALUES (?,?,?,?)",
                  ("admin", admin_pass, "admin", "System Administrator"))
    c.execute("SELECT * FROM users WHERE username='teacher'")
    if not c.fetchone():
        teacher_pass = hashlib.sha256("teacher123".encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, role, full_name) VALUES (?,?,?,?)",
                  ("teacher", teacher_pass, "teacher", "John Bangura"))
    c.execute("SELECT COUNT(*) FROM records")
    if c.fetchone()[0] == 0:
        first_names = ["Mariama", "Mohamed", "Fatmata", "Amara", "Isatu", "Sahr", "Hawa", "Alusine",
                       "Kadiatu", "Ibrahim", "Zainab", "Sulaiman", "Mabinty", "Osman", "Aminata",
                       "Lansana", "Mariatu", "Abu", "Sia", "Emmanuel"]
        last_names = ["Jalloh", "Bangura", "Koroma", "Sesay", "Kamara", "Conteh", "Turay", "Fofana",
                      "Mansaray", "Kargbo", "Bah", "Samura", "Kallon", "Foday"]
        base_date = datetime(2025, 1, 1)
        for i in range(1, 21):
            name = f"{first_names[i-1]} {last_names[i % len(last_names)]}"
            gender = "Male" if i % 2 == 0 else "Female"
            if i % 5 == 0:
                status = "Pending"
            elif i % 7 == 0:
                status = "Inactive"
            else:
                status = "Active"
            created = (base_date + timedelta(days=(i*3) % 365)).strftime("%Y-%m-%d")
            contact = f"+23276{i:05d}"
            c.execute("INSERT INTO records (full_name, gender, status, created_date, contact) VALUES (?,?,?,?,?)",
                      (name, gender, status, created, contact))
    conn.commit()
    conn.close()

def authenticate(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    hashed = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT role, full_name FROM users WHERE username=? AND password=?", (username, hashed))
    user = c.fetchone()
    conn.close()
    return user

# ---------- LOGIN WINDOW ----------
class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("School Management System - Login")
        self.root.geometry("450x400")
        self.root.resizable(False, False)
        self.root.configure(bg=COLOURS['bg'])
        self.root.eval('tk::PlaceWindow . center')
        main = tk.Frame(self.root, bg=COLOURS['bg'])
        main.pack(expand=True, fill='both')
        card = tk.Frame(main, bg=COLOURS['card'], relief='ridge', bd=2,
                        highlightbackground=COLOURS['primary'], highlightthickness=2)
        card.pack(padx=30, pady=40, ipadx=20, ipady=20, fill='both', expand=True)
        tk.Label(card, text="📚", font=("Segoe UI", 40), bg=COLOURS['card'], fg=COLOURS['primary']).pack(pady=(0,5))
        tk.Label(card, text="School Management System", font=("Segoe UI", 16, "bold"),
                 bg=COLOURS['card'], fg=COLOURS['text_dark']).pack()
        tk.Label(card, text="Sierra Leone - SDG 4 (Quality Education)", font=("Segoe UI", 10),
                 bg=COLOURS['card'], fg=COLOURS['text_light']).pack(pady=(0,20))
        tk.Label(card, text="Username", font=("Segoe UI", 10, "bold"), bg=COLOURS['card'], anchor='w').pack(fill='x', pady=(10,0))
        self.username_entry = tk.Entry(card, font=("Segoe UI", 10), bd=1, relief='solid')
        self.username_entry.pack(fill='x', pady=5, ipady=5)
        tk.Label(card, text="Password", font=("Segoe UI", 10, "bold"), bg=COLOURS['card'], anchor='w').pack(fill='x', pady=(10,0))
        self.password_entry = tk.Entry(card, show="*", font=("Segoe UI", 10), bd=1, relief='solid')
        self.password_entry.pack(fill='x', pady=5, ipady=5)
        btn_frame = tk.Frame(card, bg=COLOURS['card'])
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="🔐 LOGIN", command=self.login, bg=COLOURS['primary'], fg='white',
                  font=("Segoe UI", 11, "bold"), bd=0, padx=15, pady=5, cursor='hand2',
                  activebackground=COLOURS['primary_dark']).pack(side='left', padx=5)
        tk.Button(btn_frame, text="❓ Forgot Password", command=self.forgot_password,
                  bg=COLOURS['card'], fg=COLOURS['primary'], bd=0, cursor='hand2',
                  font=("Segoe UI", 9)).pack(side='left', padx=5)
        tk.Label(card, text="Demo: admin / admin123  |  teacher / teacher123",
                 font=("Segoe UI", 8), bg=COLOURS['card'], fg=COLOURS['text_light']).pack()
        self.password_entry.bind("<Return>", lambda e: self.login())

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user = authenticate(username, password)
        if user:
            role, full_name = user
            self.root.destroy()
            app = MainApplication(role, full_name, username)
            app.run()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def forgot_password(self):
        messagebox.showinfo("Forgot Password", "Please contact the system administrator.\n\nDemo: admin/admin123")

    def run(self):
        self.root.mainloop()

# ---------- MAIN APPLICATION ----------
class MainApplication:
    def __init__(self, role, full_name, username):
        self.role = role
        self.full_name = full_name
        self.username = username
        self.root = tk.Tk()
        self.root.title(f"School Management System - {full_name} ({role})")
        self.root.geometry("1300x800")
        self.root.state('zoomed')
        self.root.configure(bg=COLOURS['bg'])

        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief="sunken", anchor="w",
                                   font=("Segoe UI", 9), bg=COLOURS['primary_dark'], fg="white")
        self.status_bar.pack(side="bottom", fill="x")

        self.setup_styles()
        self.create_menu()
        self.create_notebook()
        self.refresh_all()

    def update_status(self, msg):
        if hasattr(self, 'status_bar') and self.status_bar:
            self.status_bar.config(text=msg)
            self.root.update_idletasks()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TNotebook", background=COLOURS['bg'], borderwidth=0)
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[15, 5],
                             background=COLOURS['bg'], foreground=COLOURS['text_dark'])
        self.style.map("TNotebook.Tab", background=[("selected", COLOURS['primary']), ("active", COLOURS['secondary'])],
                       foreground=[("selected", "white"), ("active", "white")])
        self.style.configure("Treeview", font=("Segoe UI", 9), rowheight=28,
                             fieldbackground=COLOURS['card'], background=COLOURS['card'],
                             foreground=COLOURS['text_dark'])
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                             background=COLOURS['primary'], foreground="white", relief="flat")

    def create_menu(self):
        menubar = tk.Menu(self.root, bg=COLOURS['primary'], fg="white", activebackground=COLOURS['primary_dark'])
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0, bg=COLOURS['card'], fg=COLOURS['text_dark'])
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="📎 Export CSV", command=self.export_csv)
        file_menu.add_command(label="💾 Backup Database", command=self.backup_db)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Logout", command=self.logout)
        file_menu.add_command(label="❌ Exit", command=self.root.quit)
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="ℹ️ About", command=self.about)

    def create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=15)
        self.dashboard_tab = tk.Frame(self.notebook, bg=COLOURS['bg'])
        self.records_tab = tk.Frame(self.notebook, bg=COLOURS['bg'])
        self.analytics_tab = tk.Frame(self.notebook, bg=COLOURS['bg'])
        self.reports_tab = tk.Frame(self.notebook, bg=COLOURS['bg'])
        self.notebook.add(self.dashboard_tab, text="📊 Dashboard")
        self.notebook.add(self.records_tab, text="📋 Student Records")
        self.notebook.add(self.analytics_tab, text="📈 Analytics")
        self.notebook.add(self.reports_tab, text="📄 PDF Reports")
        self.setup_dashboard()
        self.setup_records_tab()
        self.setup_analytics_tab()
        self.setup_reports_tab()

    def _create_button(self, parent, text, command, colour, padx=12, pady=5):
        return tk.Button(parent, text=text, command=command, bg=colour, fg="white",
                         font=("Segoe UI", 10, "bold"), bd=0, padx=padx, pady=pady, cursor="hand2",
                         activebackground=self._darken(colour))

    def _darken(self, hex_col):
        mapping = {COLOURS['success']: "#388E3C", COLOURS['primary']: "#00838F",
                   COLOURS['warning']: "#EF6C00", COLOURS['danger']: "#C62828"}
        return mapping.get(hex_col, "#555555")

    # ---------- DASHBOARD ----------
    def setup_dashboard(self):
        kpi_frame = tk.Frame(self.dashboard_tab, bg=COLOURS['bg'])
        kpi_frame.pack(fill="x", padx=20, pady=20)
        self.kpi_total = self._create_card(kpi_frame, "Total Records", "0", COLOURS['primary'], 0)
        self.kpi_active = self._create_card(kpi_frame, "Active", "0", COLOURS['success'], 1)
        self.kpi_inactive = self._create_card(kpi_frame, "Inactive", "0", COLOURS['warning'], 2)
        self.kpi_pending = self._create_card(kpi_frame, "Pending", "0", COLOURS['danger'], 3)
        recent_frame = tk.LabelFrame(self.dashboard_tab, text="🔹 Recently Added Records (last 10)",
                                     font=("Segoe UI", 11, "bold"), bg=COLOURS['card'],
                                     fg=COLOURS['text_dark'], padx=5, pady=5)
        recent_frame.pack(fill="both", expand=True, padx=20, pady=10)
        cols = ("ID", "Full Name", "Gender", "Status", "Created Date", "Contact")
        self.recent_tree = ttk.Treeview(recent_frame, columns=cols, show="headings", height=8)
        for col in cols:
            self.recent_tree.heading(col, text=col)
            self.recent_tree.column(col, width=120 if col != "Full Name" else 180, anchor="center")
        scroll = ttk.Scrollbar(recent_frame, orient="vertical", command=self.recent_tree.yview)
        self.recent_tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.recent_tree.pack(fill="both", expand=True)
        btn_frame = tk.Frame(self.dashboard_tab, bg=COLOURS['bg'])
        btn_frame.pack(pady=15)
        self._create_button(btn_frame, "➕ Add Record", self.add_record, COLOURS['success']).pack(side="left", padx=10)
        self._create_button(btn_frame, "📊 Go to Analytics", lambda: self.notebook.select(self.analytics_tab), COLOURS['primary']).pack(side="left", padx=10)
        self._create_button(btn_frame, "📄 Weekly Report", lambda: self.quick_report("weekly"), COLOURS['warning']).pack(side="left", padx=10)

    def _create_card(self, parent, title, value, colour, col):
        card = tk.Frame(parent, bg=COLOURS['card'], relief="ridge", bd=1,
                        highlightbackground=COLOURS['primary'], highlightthickness=1)
        card.grid(row=0, column=col, padx=15, pady=5, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)
        tk.Label(card, text=title, font=("Segoe UI", 12, "bold"), bg=COLOURS['card'], fg=COLOURS['text_dark']).pack(pady=(15,5))
        lbl_val = tk.Label(card, text=value, font=("Segoe UI", 32, "bold"), bg=COLOURS['card'], fg=colour)
        lbl_val.pack(pady=(0,15))
        return lbl_val

    def refresh_dashboard(self):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM records")
        total = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM records WHERE status='Active'")
        active = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM records WHERE status='Inactive'")
        inactive = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM records WHERE status='Pending'")
        pending = c.fetchone()[0]
        c.execute("SELECT id, full_name, gender, status, created_date, contact FROM records ORDER BY created_date DESC LIMIT 10")
        recent = c.fetchall()
        conn.close()
        self.kpi_total.config(text=str(total))
        self.kpi_active.config(text=str(active))
        self.kpi_inactive.config(text=str(inactive))
        self.kpi_pending.config(text=str(pending))
        for row in self.recent_tree.get_children():
            self.recent_tree.delete(row)
        for r in recent:
            self.recent_tree.insert("", "end", values=r)
        self.update_status(f"Dashboard updated – Total: {total} | Active: {active} | Inactive: {inactive} | Pending: {pending}")

    # ---------- RECORDS TAB (WITH EXPLICIT EDIT/DELETE BUTTONS) ----------
    def setup_records_tab(self):
        # Top control bar with search, filters, and CRUD buttons
        ctrl_frame = tk.Frame(self.records_tab, bg=COLOURS['bg'], pady=8)
        ctrl_frame.pack(fill="x", padx=15, pady=5)

        # Search row
        tk.Label(ctrl_frame, text="🔍 Search:", bg=COLOURS['bg'], font=("Segoe UI", 10)).pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(ctrl_frame, textvariable=self.search_var, width=20, font=("Segoe UI", 10), bd=1, relief="solid")
        self.search_entry.pack(side="left", padx=5)
        self._create_button(ctrl_frame, "Search", self.apply_filters, COLOURS['primary'], padx=8, pady=2).pack(side="left", padx=5)

        # Filters
        tk.Label(ctrl_frame, text="Gender:", bg=COLOURS['bg'], font=("Segoe UI", 10)).pack(side="left", padx=(20,5))
        self.gender_filter = ttk.Combobox(ctrl_frame, values=["All", "Male", "Female"], width=8, state="readonly")
        self.gender_filter.set("All")
        self.gender_filter.pack(side="left")
        self.gender_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        tk.Label(ctrl_frame, text="Status:", bg=COLOURS['bg'], font=("Segoe UI", 10)).pack(side="left", padx=(10,5))
        self.status_filter = ttk.Combobox(ctrl_frame, values=["All", "Active", "Inactive", "Pending"], width=10, state="readonly")
        self.status_filter.set("All")
        self.status_filter.pack(side="left")
        self.status_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        tk.Label(ctrl_frame, text="Date:", bg=COLOURS['bg'], font=("Segoe UI", 10)).pack(side="left", padx=(10,5))
        self.date_filter = ttk.Combobox(ctrl_frame, values=["All", "Today", "This Week", "This Month", "This Year"], width=12, state="readonly")
        self.date_filter.set("All")
        self.date_filter.pack(side="left")
        self.date_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # CRUD action buttons (explicit)
        self._create_button(ctrl_frame, "✏️ Edit Selected", self.edit_record, COLOURS['primary'], padx=8, pady=2).pack(side="right", padx=5)
        self._create_button(ctrl_frame, "🗑️ Delete Selected", self.delete_record, COLOURS['danger'], padx=8, pady=2).pack(side="right", padx=5)
        self._create_button(ctrl_frame, "➕ Add Record", self.add_record, COLOURS['success']).pack(side="right", padx=5)
        self._create_button(ctrl_frame, "📎 Export CSV", self.export_csv, "#607D8B", padx=8, pady=2).pack(side="right", padx=5)

        # Treeview (full list)
        tree_frame = tk.Frame(self.records_tab, bg=COLOURS['bg'])
        tree_frame.pack(fill="both", expand=True, padx=15, pady=5)
        cols = ("id", "Full Name", "Gender", "Status", "Created Date", "Contact")
        self.record_tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=20)
        for col in cols:
            self.record_tree.heading(col, text=col.title())
            self.record_tree.column(col, width=120 if col != "Full Name" else 180, anchor="center")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.record_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.record_tree.xview)
        self.record_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.record_tree.pack(fill="both", expand=True)

        # Pagination
        pag_frame = tk.Frame(self.records_tab, bg=COLOURS['bg'])
        pag_frame.pack(fill="x", pady=8)
        self._create_button(pag_frame, "◀ Previous", self.prev_page, COLOURS['primary']).pack(side="left", padx=5)
        self.page_label = tk.Label(pag_frame, text="Page 1", font=("Segoe UI", 10, "bold"), bg=COLOURS['bg'], fg=COLOURS['primary_dark'])
        self.page_label.pack(side="left", padx=15)
        self._create_button(pag_frame, "Next ▶", self.next_page, COLOURS['primary']).pack(side="left", padx=5)

        # Right‑click menu as alternative
        self.context_menu = tk.Menu(self.record_tree, tearoff=0)
        self.context_menu.add_command(label="✏️ Edit", command=self.edit_record)
        self.context_menu.add_command(label="🗑️ Delete", command=self.delete_record)
        self.record_tree.bind("<Button-3>", self.show_context_menu)

        self.current_page = 1
        self.page_size = 20
        self.total_records = 0
        self.current_filters = {}
        self.refresh_records_table()

    def apply_filters(self):
        self.current_filters = {
            'search': self.search_var.get().strip(),
            'gender': self.gender_filter.get(),
            'status': self.status_filter.get(),
            'date': self.date_filter.get()
        }
        self.current_page = 1
        self.refresh_records_table()

    def refresh_records_table(self, page=None):
        if page: self.current_page = page
        conn = sqlite3.connect(DB_FILE)
        query = "SELECT id, full_name, gender, status, created_date, contact FROM records WHERE 1=1"
        params = []
        search_term = self.current_filters.get('search', '')
        if search_term:
            if search_term.isdigit():
                query += " AND id = ?"
                params.append(int(search_term))
            else:
                query += " AND full_name LIKE ?"
                params.append(f"%{search_term}%")
        if self.current_filters.get('gender') and self.current_filters['gender'] != 'All':
            query += " AND gender = ?"
            params.append(self.current_filters['gender'])
        if self.current_filters.get('status') and self.current_filters['status'] != 'All':
            query += " AND status = ?"
            params.append(self.current_filters['status'])
        date_opt = self.current_filters.get('date')
        today = datetime.now().date()
        if date_opt == "Today":
            query += " AND created_date = ?"
            params.append(today.strftime("%Y-%m-%d"))
        elif date_opt == "This Week":
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
            query += " AND created_date BETWEEN ? AND ?"
            params.extend([start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")])
        elif date_opt == "This Month":
            start = today.replace(day=1)
            next_month = start + timedelta(days=32)
            end = next_month.replace(day=1) - timedelta(days=1)
            query += " AND created_date BETWEEN ? AND ?"
            params.extend([start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")])
        elif date_opt == "This Year":
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)
            query += " AND created_date BETWEEN ? AND ?"
            params.extend([start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")])
        c = conn.cursor()
        count_query = query.replace("SELECT id, full_name, gender, status, created_date, contact", "SELECT COUNT(*)")
        c.execute(count_query, params)
        self.total_records = c.fetchone()[0]
        offset = (self.current_page - 1) * self.page_size
        query += " ORDER BY created_date DESC LIMIT ? OFFSET ?"
        params.extend([self.page_size, offset])
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        for row in self.record_tree.get_children():
            self.record_tree.delete(row)
        for row in rows:
            self.record_tree.insert("", "end", values=row)
        total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)
        self.page_label.config(text=f"Page {self.current_page} of {total_pages}")
        self.update_status(f"Showing {len(rows)} of {self.total_records} records")

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_records_table()
    def next_page(self):
        total_pages = (self.total_records + self.page_size - 1) // self.page_size
        if self.current_page < total_pages:
            self.current_page += 1
            self.refresh_records_table()
    def show_context_menu(self, event):
        item = self.record_tree.identify_row(event.y)
        if item:
            self.record_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    # ---------- CRUD OPERATIONS (explicit functions) ----------
    def add_record(self):
        self.open_record_form()

    def edit_record(self):
        selected = self.record_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record to edit.")
            return
        item = self.record_tree.item(selected[0])
        record_id = item['values'][0]  # first column is id
        self.open_record_form(record_id)

    def delete_record(self):
        selected = self.record_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record to delete.")
            return
        if messagebox.askyesno("Confirm Delete", "Permanently delete this record? This cannot be undone."):
            item = self.record_tree.item(selected[0])
            record_id = item['values'][0]
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("DELETE FROM records WHERE id=?", (record_id,))
            conn.commit()
            conn.close()
            self.update_status(f"Deleted record ID {record_id}")
            self.refresh_records_table()
            self.refresh_dashboard()
            self.refresh_charts()

    # ---------- CALENDAR PICKER (improved) ----------
    def _open_calendar(self, date_entry):
        top = tk.Toplevel()
        top.title("Select Date")
        top.geometry("320x340")
        top.configure(bg=COLOURS['bg'])
        top.grab_set()
        top.resizable(False, False)
        now = datetime.now()
        year_var = tk.IntVar(value=now.year)
        month_var = tk.IntVar(value=now.month)

        sel_frame = tk.Frame(top, bg=COLOURS['bg'])
        sel_frame.pack(pady=10)
        tk.Label(sel_frame, text="Year:", font=("Segoe UI", 10), bg=COLOURS['bg']).pack(side="left", padx=5)
        year_spin = tk.Spinbox(sel_frame, from_=2000, to=2030, textvariable=year_var, width=6,
                               font=("Segoe UI", 10), command=lambda: update_calendar())
        year_spin.pack(side="left", padx=5)
        tk.Label(sel_frame, text="Month:", font=("Segoe UI", 10), bg=COLOURS['bg']).pack(side="left", padx=5)
        month_spin = tk.Spinbox(sel_frame, from_=1, to=12, textvariable=month_var, width=4,
                                font=("Segoe UI", 10), command=lambda: update_calendar())
        month_spin.pack(side="left", padx=5)

        cal_frame = tk.Frame(top, bg=COLOURS['card'])
        cal_frame.pack(pady=10, padx=10, fill="both", expand=True)

        def update_calendar():
            for widget in cal_frame.winfo_children():
                widget.destroy()
            year = year_var.get()
            month = month_var.get()
            month_name = calendar.month_name[month]
            tk.Label(cal_frame, text=f"{month_name} {year}", font=("Segoe UI", 12, "bold"),
                     bg=COLOURS['primary'], fg="white", pady=5).grid(row=0, column=0, columnspan=7, sticky="ew")
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            for i, d in enumerate(days):
                tk.Label(cal_frame, text=d, font=("Segoe UI", 9, "bold"), bg=COLOURS['secondary'], fg="white",
                         width=4, anchor="center").grid(row=1, column=i, padx=1, pady=1, sticky="nsew")
            cal = calendar.monthcalendar(year, month)
            for week_num, week in enumerate(cal, start=2):
                for day_num, day in enumerate(week):
                    if day == 0:
                        tk.Label(cal_frame, text="", width=4, bg=COLOURS['card']).grid(row=week_num, column=day_num, padx=1, pady=1, sticky="nsew")
                    else:
                        btn = tk.Button(cal_frame, text=str(day), width=4, height=1,
                                        bg=COLOURS['card'], fg=COLOURS['text_dark'],
                                        font=("Segoe UI", 9), relief="flat",
                                        command=lambda d=day: select_date(d, year, month))
                        btn.grid(row=week_num, column=day_num, padx=1, pady=1, sticky="nsew")
            for i in range(7):
                cal_frame.columnconfigure(i, weight=1)
            for i in range(2, 8):
                cal_frame.rowconfigure(i, weight=1)

        def select_date(day, year, month):
            selected = f"{year}-{month:02d}-{day:02d}"
            date_entry.delete(0, tk.END)
            date_entry.insert(0, selected)
            top.destroy()

        update_calendar()
        tk.Button(top, text="Today", command=lambda: select_date(now.day, now.year, now.month),
                  bg=COLOURS['primary'], fg="white", font=("Segoe UI", 10, "bold"),
                  padx=10, pady=3, cursor="hand2").pack(pady=10)

    # ---------- RECORD FORM (Add/Edit) ----------
    def open_record_form(self, record_id=None):
        form = tk.Toplevel(self.root)
        form.title("Student Record Form")
        form.geometry("600x520")
        form.configure(bg=COLOURS['bg'])
        form.grab_set()
        form.resizable(False, False)
        main = tk.Frame(form, bg=COLOURS['bg'], padx=20, pady=20)
        main.pack(fill="both", expand=True)
        tk.Label(main, text="✏️ Student Record", font=("Segoe UI", 16, "bold"),
                 bg=COLOURS['bg'], fg=COLOURS['text_dark']).pack(pady=(0,15))
        fields = {}
        labels = [("Full Name *", "full_name"), ("Gender *", "gender"),
                  ("Status *", "status"), ("Created Date", "created_date"),
                  ("Contact", "contact")]
        grid_frame = tk.Frame(main, bg=COLOURS['bg'])
        grid_frame.pack(fill="both", expand=True)
        grid_frame.columnconfigure(0, weight=0)
        grid_frame.columnconfigure(1, weight=1)
        for i, (text, key) in enumerate(labels):
            tk.Label(grid_frame, text=text, font=("Segoe UI", 10, "bold"),
                     bg=COLOURS['bg'], anchor="e", width=18).grid(row=i, column=0, padx=5, pady=8, sticky="e")
            if key == "gender":
                entry = ttk.Combobox(grid_frame, values=["Male", "Female"], width=30, state="readonly")
                entry.grid(row=i, column=1, padx=5, pady=8, sticky="ew")
            elif key == "status":
                entry = ttk.Combobox(grid_frame, values=["Active", "Inactive", "Pending"], width=30, state="readonly")
                entry.grid(row=i, column=1, padx=5, pady=8, sticky="ew")
            elif key == "created_date":
                frame_date = tk.Frame(grid_frame, bg=COLOURS['bg'])
                frame_date.grid(row=i, column=1, padx=5, pady=8, sticky="ew")
                entry = tk.Entry(frame_date, width=28, font=("Segoe UI", 10), bd=1, relief="solid")
                entry.pack(side="left", fill="x", expand=True)
                btn_cal = tk.Button(frame_date, text="📅", command=lambda e=entry: self._open_calendar(e),
                                    bg=COLOURS['primary'], fg="white", bd=0, padx=5, cursor="hand2")
                btn_cal.pack(side="right", padx=(5,0))
                if not record_id:
                    entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
            else:
                entry = tk.Entry(grid_frame, width=35, font=("Segoe UI", 10), bd=1, relief="solid")
                entry.grid(row=i, column=1, padx=5, pady=8, sticky="ew")
            fields[key] = entry
        if record_id:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT full_name, gender, status, created_date, contact FROM records WHERE id=?", (record_id,))
            data = c.fetchone()
            conn.close()
            if data:
                fields['full_name'].insert(0, data[0])
                fields['gender'].set(data[1])
                fields['status'].set(data[2])
                fields['created_date'].delete(0, tk.END)
                fields['created_date'].insert(0, data[3])
                fields['contact'].insert(0, data[4] if data[4] else "")
        def save():
            full_name = fields['full_name'].get().strip()
            gender = fields['gender'].get()
            status = fields['status'].get()
            created_date = fields['created_date'].get().strip()
            contact = fields['contact'].get().strip()
            if not full_name or not gender or not status:
                messagebox.showerror("Error", "Full Name, Gender and Status are required.")
                return
            if not created_date:
                created_date = datetime.now().strftime("%Y-%m-%d")
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            try:
                if record_id:
                    c.execute('''UPDATE records SET full_name=?, gender=?, status=?, created_date=?, contact=?
                                 WHERE id=?''',
                              (full_name, gender, status, created_date, contact, record_id))
                else:
                    c.execute('''INSERT INTO records (full_name, gender, status, created_date, contact)
                                 VALUES (?,?,?,?,?)''',
                              (full_name, gender, status, created_date, contact))
                conn.commit()
                self.update_status(f"Record saved: {full_name}")
                form.destroy()
                self.refresh_records_table()
                self.refresh_dashboard()
                self.refresh_charts()
            except Exception as e:
                messagebox.showerror("Database Error", str(e))
            finally:
                conn.close()
        btn_frame = tk.Frame(main, bg=COLOURS['bg'])
        btn_frame.pack(pady=15)
        self._create_button(btn_frame, "💾 SAVE", save, COLOURS['success']).pack(side="left", padx=10)
        self._create_button(btn_frame, "❌ CANCEL", form.destroy, COLOURS['danger']).pack(side="left", padx=10)

    # ---------- ANALYTICS (SMOOTH, TOP-CLASS CHARTS) ----------
    def setup_analytics_tab(self):
        notebook2 = ttk.Notebook(self.analytics_tab)
        notebook2.pack(fill="both", expand=True, padx=10, pady=10)
        self.gender_pie_frame = tk.Frame(notebook2, bg=COLOURS['bg'])
        self.status_pie_frame = tk.Frame(notebook2, bg=COLOURS['bg'])
        self.bar_frame = tk.Frame(notebook2, bg=COLOURS['bg'])
        self.line_frame = tk.Frame(notebook2, bg=COLOURS['bg'])
        notebook2.add(self.gender_pie_frame, text="Gender Distribution (Pie)")
        notebook2.add(self.status_pie_frame, text="Status Distribution (Pie)")
        notebook2.add(self.bar_frame, text="Bar Charts")
        notebook2.add(self.line_frame, text="Monthly Trend")
        self.refresh_charts()

    def refresh_charts(self):
        for f in [self.gender_pie_frame, self.status_pie_frame, self.bar_frame, self.line_frame]:
            for w in f.winfo_children():
                w.destroy()
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT gender, status, created_date FROM records", conn)
        conn.close()
        if df.empty:
            for frame in [self.gender_pie_frame, self.status_pie_frame, self.bar_frame, self.line_frame]:
                tk.Label(frame, text="No data available", bg=COLOURS['bg'], font=("Segoe UI", 12)).pack(expand=True)
            return

        # Style for all charts
        plt.style.use('seaborn-v0_8-darkgrid')
        plt.rcParams['font.family'] = 'Segoe UI'
        plt.rcParams['font.size'] = 10
        plt.rcParams['figure.facecolor'] = COLOURS['chart_bg']
        plt.rcParams['axes.facecolor'] = COLOURS['chart_bg']

        # ---- Gender Pie ----
        gender_counts = df['gender'].value_counts()
        fig1, ax1 = plt.subplots(figsize=(5, 3), dpi=100)
        colors_pie = [COLOURS['primary'], COLOURS['warning']]
        wedges, texts, autotexts = ax1.pie(gender_counts.values, labels=gender_counts.index,
                                            autopct='%1.1f%%', colors=colors_pie,
                                            textprops={'fontsize': 9}, startangle=90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        ax1.set_title("Gender Distribution", fontsize=12, fontweight='bold')
        canvas1 = FigureCanvasTkAgg(fig1, self.gender_pie_frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True)

        # ---- Status Pie ----
        status_counts = df['status'].value_counts()
        fig2, ax2 = plt.subplots(figsize=(5, 3), dpi=100)
        colors_status = [COLOURS['success'], COLOURS['danger'], COLOURS['warning']]
        wedges, texts, autotexts = ax2.pie(status_counts.values, labels=status_counts.index,
                                            autopct='%1.1f%%', colors=colors_status,
                                            textprops={'fontsize': 9}, startangle=90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        ax2.set_title("Status Distribution", fontsize=12, fontweight='bold')
        canvas2 = FigureCanvasTkAgg(fig2, self.status_pie_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True)

        # ---- Bar Charts (side‑by‑side) ----
        fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(8, 3.5), dpi=100)
        ax3a.bar(status_counts.index, status_counts.values,
                 color=[COLOURS['success'], COLOURS['danger'], COLOURS['warning']],
                 edgecolor='black', linewidth=0.5)
        ax3a.set_title("By Status", fontsize=11, fontweight='bold')
        ax3a.set_ylabel("Count")
        ax3a.grid(axis='y', linestyle='--', alpha=0.6)
        ax3b.bar(gender_counts.index, gender_counts.values,
                 color=[COLOURS['primary'], COLOURS['warning']],
                 edgecolor='black', linewidth=0.5)
        ax3b.set_title("By Gender", fontsize=11, fontweight='bold')
        ax3b.set_ylabel("Count")
        ax3b.grid(axis='y', linestyle='--', alpha=0.6)
        fig3.tight_layout()
        canvas3 = FigureCanvasTkAgg(fig3, self.bar_frame)
        canvas3.draw()
        canvas3.get_tk_widget().pack(fill="both", expand=True)

        # ---- Line Chart (monthly trend) ----
        if 'created_date' in df.columns and not df['created_date'].isnull().all():
            df_date = df.dropna(subset=['created_date'])
            df_date['created_date'] = pd.to_datetime(df_date['created_date'])
            df_date['month'] = df_date['created_date'].dt.to_period('M')
            monthly = df_date.groupby('month').size()
            fig4, ax4 = plt.subplots(figsize=(6, 3.5), dpi=100)
            ax4.plot(monthly.index.astype(str), monthly.values, marker='o', linewidth=2,
                     markersize=6, color=COLOURS['primary'], markerfacecolor=COLOURS['primary_dark'])
            ax4.set_title("Monthly Registration Trend", fontsize=12, fontweight='bold')
            ax4.set_xlabel("Month")
            ax4.set_ylabel("New Records")
            ax4.grid(True, linestyle='--', alpha=0.5)
            plt.xticks(rotation=45, ha='right')
            fig4.tight_layout()
            canvas4 = FigureCanvasTkAgg(fig4, self.line_frame)
            canvas4.draw()
            canvas4.get_tk_widget().pack(fill="both", expand=True)
        else:
            tk.Label(self.line_frame, text="Insufficient date data for trend", bg=COLOURS['bg'], font=("Segoe UI", 12)).pack(expand=True)

    # ---------- PDF REPORTS (with calendar pickers) ----------
    def setup_reports_tab(self):
        frame = tk.Frame(self.reports_tab, bg=COLOURS['bg'], padx=30, pady=30)
        frame.pack(expand=True)
        tk.Label(frame, text="📄 Generate PDF Report", font=("Segoe UI", 18, "bold"), bg=COLOURS['bg'], fg=COLOURS['text_dark']).pack(pady=10)
        dr_frame = tk.Frame(frame, bg=COLOURS['bg'])
        dr_frame.pack(pady=20)
        # Start Date
        tk.Label(dr_frame, text="Start Date (YYYY-MM-DD):", font=("Segoe UI", 11), bg=COLOURS['bg']).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        start_frame = tk.Frame(dr_frame, bg=COLOURS['bg'])
        start_frame.grid(row=0, column=1, padx=5, pady=5)
        self.start_entry = tk.Entry(start_frame, width=15, font=("Segoe UI", 10), bd=1, relief="solid")
        self.start_entry.pack(side="left")
        self._create_button(start_frame, "📅", lambda: self._open_calendar(self.start_entry), COLOURS['primary'], padx=5, pady=2).pack(side="left", padx=(5,0))
        # End Date
        tk.Label(dr_frame, text="End Date:", font=("Segoe UI", 11), bg=COLOURS['bg']).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        end_frame = tk.Frame(dr_frame, bg=COLOURS['bg'])
        end_frame.grid(row=0, column=3, padx=5, pady=5)
        self.end_entry = tk.Entry(end_frame, width=15, font=("Segoe UI", 10), bd=1, relief="solid")
        self.end_entry.pack(side="left")
        self._create_button(end_frame, "📅", lambda: self._open_calendar(self.end_entry), COLOURS['primary'], padx=5, pady=2).pack(side="left", padx=(5,0))
        self._create_button(dr_frame, "Generate PDF", self.generate_pdf_custom, COLOURS['success']).grid(row=0, column=4, padx=10)

        qf = tk.LabelFrame(frame, text="Quick Reports", font=("Segoe UI", 11, "bold"), bg=COLOURS['card'], fg=COLOURS['text_dark'])
        qf.pack(pady=20, fill="x")
        self._create_button(qf, "Weekly Report", lambda: self.quick_report("weekly"), COLOURS['primary']).pack(side="left", padx=15, pady=10)
        self._create_button(qf, "Monthly Report", lambda: self.quick_report("monthly"), COLOURS['primary']).pack(side="left", padx=15, pady=10)
        self._create_button(qf, "Yearly Report", lambda: self.quick_report("yearly"), COLOURS['primary']).pack(side="left", padx=15, pady=10)

    def get_records_in_range(self, start, end):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, full_name, gender, status, created_date, contact FROM records WHERE created_date BETWEEN ? AND ? ORDER BY created_date", (start, end))
        rows = c.fetchall()
        conn.close()
        return rows

    def generate_pdf_custom(self):
        start = self.start_entry.get().strip()
        end = self.end_entry.get().strip()
        if not start or not end:
            messagebox.showerror("Error", "Enter both start and end dates")
            return
        self._generate_pdf(start, end)

    def quick_report(self, period):
        today = datetime.now().date()
        if period == "weekly":
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
        elif period == "monthly":
            start = today.replace(day=1)
            next_month = start + timedelta(days=32)
            end = next_month.replace(day=1) - timedelta(days=1)
        else:
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)
        self._generate_pdf(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

    def _generate_pdf(self, start, end):
        records = self.get_records_in_range(start, end)
        if not records:
            messagebox.showinfo("No Data", f"No records from {start} to {end}")
            return
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="School Management Report", ln=1, align='C')
        pdf.cell(200, 10, txt=f"Date Range: {start} to {end}", ln=1, align='C')
        pdf.cell(200, 10, txt=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=1, align='C')
        pdf.ln(10)
        total = len(records)
        active = sum(1 for r in records if r[3] == 'Active')
        inactive = sum(1 for r in records if r[3] == 'Inactive')
        pending = sum(1 for r in records if r[3] == 'Pending')
        female = sum(1 for r in records if r[2] == 'Female')
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 8, txt=f"Total Records: {total}", ln=1)
        pdf.cell(200, 8, txt=f"Active: {active}  |  Inactive: {inactive}  |  Pending: {pending}", ln=1)
        pdf.cell(200, 8, txt=f"Female: {female}  |  Male: {total-female}", ln=1)
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 9)
        headers = ["ID", "Name", "Gender", "Status", "Created", "Contact"]
        col_w = [20, 60, 25, 25, 30, 40]
        for i, h in enumerate(headers):
            pdf.cell(col_w[i], 8, h, border=1)
        pdf.ln()
        pdf.set_font("Arial", size=8)
        for rec in records:
            pdf.cell(col_w[0], 8, str(rec[0]), border=1)
            pdf.cell(col_w[1], 8, rec[1][:25], border=1)
            pdf.cell(col_w[2], 8, rec[2], border=1)
            pdf.cell(col_w[3], 8, rec[3], border=1)
            pdf.cell(col_w[4], 8, rec[4], border=1)
            pdf.cell(col_w[5], 8, rec[5] or "", border=1)
            pdf.ln()
        filename = f"report_{start}_to_{end}.pdf"
        pdf.output(filename)
        messagebox.showinfo("PDF Created", f"Saved as {os.path.abspath(filename)}")
        self.update_status(f"PDF report generated: {filename}")

    # ---------- UTILITIES ----------
    def export_csv(self):
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT id, full_name, gender, status, created_date, contact FROM records", conn)
        conn.close()
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if filepath:
            df.to_csv(filepath, index=False)
            messagebox.showinfo("Export", f"Exported {len(df)} records")
            self.update_status(f"Exported {len(df)} records to CSV")

    def backup_db(self):
        import shutil
        backup_path = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy(DB_FILE, backup_path)
        messagebox.showinfo("Backup", f"Backup saved as {backup_path}")
        self.update_status(f"Database backed up to {backup_path}")

    def about(self):
        messagebox.showinfo("About", "School Management System for Sierra Leone\nSDG 4 - Quality Education\n\nFull CRUD, explicit Edit/Delete buttons, improved charts, calendar pickers, and all required features.")

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure?"):
            self.root.destroy()
            login = LoginWindow()
            login.run()

    def refresh_all(self):
        self.refresh_dashboard()
        self.refresh_records_table()
        self.refresh_charts()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    init_database()
    app = LoginWindow()
    app.run()   