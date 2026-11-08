"""Курстық жоба: «Кітапхана» ішкі жүйесі (10-нұсқа). Python + Tkinter + MS SQL Server.

Іске қосу:  python app.py
Алғаш іске қосқанда дерекқор schema.sql, data.sql, queries.sql файлдарынан өзі құрылады.
"""
import csv
import datetime
import decimal
import os
import re
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont

import pyodbc

# ==== ІШКІ ЖҮЙЕ БАПТАУЛАРЫ ====
TITLE = "Кітапхана"
SUBTITLE = "Кітаптар, оқырмандар және кітап беру есебі"
DB = "Biblioteka"
TABLES = ["Оқырмандар", "Кітаптар", "Авторлар", "Автор_аты_жөні", "Қор", "Қозғалыс", "Айыппұл",
          "Кітапханашылар", "Сақтау_орындары", "Баспалар", "Жіктеуіш"]
# (мәзір пункті, процедура, [параметрлер ретімен], тапсырма мәтіні, [батырма мәтіні])
ACTIONS = {
    "Сұраныстар": [
        ("1. Сөрелердегі кітаптар", "Сұраныс_1", [],
         "Әр сөредегі кітаптардың жалпы саны."),
        ("2. Оқырмандардағы кітаптар", "Сұраныс_2", [],
         "Оқырмандарда қандай кітаптың қанша данасы бар."),
        ("3. Автордың қайтарылмаған кітаптары", "Сұраныс_3", ["Автор коды"],
         "i-ші автордың оқырмандарға берілген және қайтарылмаған кітаптары."),
        ("4. Автордың кітаптары", "Сұраныс_4", ["Автордың аты-жөні"],
         "Авторы «…» болатын кітаптар тізімі. Тегінің бір бөлігін енгізуге болады."),
        ("5. Кәмелетке толмаған оқырмандар", "Сұраныс_5", [],
         "Кітапхананың кәмелетке толмаған оқырмандарының тізімі."),
    ],
    "Есептер": [
        ("1. Айлық қозғалыс", "Есеп_1", ["Кітапханашы коды", "Жыл", "Ай"],
         "i-ші кітапханашының j-ші айдағы кітап қозғалысы туралы есебі."),
        ("2. Қаржылық есеп", "Есеп_2", ["Кітапханашы коды"],
         "i-ші кітапханашының қаржылық есебі: қабылданған айыппұлдар."),
        ("3. Күнделікті оқырмандар", "Есеп_3", ["Күні"],
         "i-ші күні кітап алған оқырмандар тізімі."),
    ],
    "Тапсырмалар": [
        ("1. Кеш қайтарылған кітаптар", "Тапсырма_1", [],
         "Қозғалыс кестесінен қайтарылған күні > берілген күні болатын жолдарды таңдау."),
        ("2. Туған жылы бойынша", "Тапсырма_2", ["Туған жылы"],
         "Оқырмандар кестесінен … жылы туған оқырмандарды таңдау."),
        ("3. Жаңа авторлар", "Тапсырма_3", [],
         "Автор аты-жөні кестесіне үш жаңа жол қосу.", "Жолдарды қосу"),
        ("4. Кепілдік құны", "Тапсырма_4", ["Кітап коды"],
         "Кітаптың сөредегі даналарының кепілдік құны = қолжетімді саны × кепілдік құны."),
    ],
}
COLORS = dict(bg="#F2F4F1", side="#E6EAE4", surface="#FFFFFF", line="#D2D9D1", stripe="#F7F9F6",
              hover="#DBE2DA", tint="#E0EBE3", ink="#1F2A24", muted="#5E6B63",
              accent="#2F5D46", accent_dark="#234836", danger="#A5302B", danger_tint="#F9E9E7")


def draw_emblem(canvas, width):
    """Әр биіктіктегі кітап түбіршіктері тұрған сөре."""
    h = 52
    canvas.configure(height=h)
    spines = [(10, 30, "#2F5D46"), (7, 24, "#B8862F"), (12, 35, "#7A2E3A"), (6, 21, "#3E4C59"),
              (10, 28, "#2F5D46"), (8, 33, "#C9B79C"), (13, 26, "#7A2E3A"), (7, 31, "#B8862F"),
              (9, 23, "#3E4C59")]
    x, i = 24, 0
    while x + spines[i % len(spines)][0] <= width - 24:
        w, sh, color = spines[i % len(spines)]
        canvas.create_rectangle(x, h - 6 - sh, x + w, h - 6, fill=color, outline="")
        x, i = x + w + 2, i + 1
    canvas.create_rectangle(18, h - 6, width - 18, h - 3, fill=COLORS["ink"], outline="")
# ==== БАПТАУЛАРДЫҢ СОҢЫ ====

# Қосылу. Windows: SQL Server Express, Windows арқылы кіру. Mac: Docker ішіндегі SQL Server.
# Сервер басқа болса — төмендегі жолды өзгертіңіз немесе DB_SERVER айнымалысын орнатыңыз.
if sys.platform == "win32":
    SERVER, USER, PASSWORD = r"localhost\SQLEXPRESS", None, None
else:
    SERVER, USER, PASSWORD = "localhost,1433", "sa", "Kurs_Proekt_2026"
SERVER = os.getenv("DB_SERVER", SERVER)

# shortcut: Mac-тағы «ODBC Driver 18» Homebrew-тың OpenSSL 4 нұсқасын қолдамайды, сондықтан OpenSSL 3-пен
# қайта іске қосыламыз; Microsoft OpenSSL 4 қолдауын қосқанда алып тастау керек. Windows-та орындалмайды.
OPENSSL3 = "/opt/homebrew/opt/openssl@3/lib"
if sys.platform == "darwin" and os.path.isdir(OPENSSL3) and not os.getenv("KURS_OPENSSL3"):
    os.environ.update(KURS_OPENSSL3="1", DYLD_LIBRARY_PATH=OPENSSL3)
    os.execv(sys.executable, [sys.executable] + sys.argv)
HERE = os.path.dirname(os.path.abspath(__file__))
C = COLORS
BASE = 10 if sys.platform == "win32" else 13   # қаріп өлшемі: Windows-та пункттер ірірек
SIDE_W = 400
TODAY = datetime.date.today()
PARAM_DEFAULTS = {"Жыл": str(TODAY.year), "Ай": str(TODAY.month), "Күні": TODAY.strftime("%d.%m.%Y")}
TOTAL = "БАРЛЫҒЫ"   # есептердегі қорытынды жол


def connect(database):
    drivers = [d for d in pyodbc.drivers() if "SQL Server" in d]
    if not drivers:
        raise RuntimeError("SQL Server ODBC драйвері табылмады. «ODBC Driver 18 for SQL Server» орнатыңыз.")
    modern = [d for d in drivers if d.startswith("ODBC Driver")]
    driver = max(modern) if modern else drivers[0]
    login = f"UID={USER};PWD={PASSWORD};" if USER else "Trusted_Connection=yes;"
    return pyodbc.connect(f"DRIVER={{{driver}}};SERVER={SERVER};DATABASE={database};"
                          f"TrustServerCertificate=yes;{login}", autocommit=True, timeout=10)


def create_database_if_missing():
    con = connect("master")
    if con.execute("SELECT DB_ID(?)", DB).fetchone()[0] is None:
        for name in ("schema.sql", "data.sql", "queries.sql"):
            with open(os.path.join(HERE, name), encoding="utf-8-sig") as f:
                for batch in re.split(r"^\s*GO\s*$", f.read(), flags=re.M | re.I):
                    if batch.strip():
                        cur = con.execute(batch)
                        while cur.nextset():  # пакеттегі кез келген команданың қатесі жоғалмауы үшін
                            pass
    con.close()


# ---------- мәндер: дерекқор <-> экран ----------
def nice(name):
    return name.replace("_", " ")


def cell_text(v):
    """Мән кестеде қалай көрінеді."""
    if v is None:
        return ""
    if isinstance(v, bool):
        return "иә" if v else "жоқ"
    if isinstance(v, datetime.date):
        return v.strftime("%d.%m.%Y")
    if isinstance(v, decimal.Decimal):
        return f"{v:,.2f}".replace(",", " ")
    return str(v)


def field_text(v):
    """Мән енгізу өрісінде (және CSV-де) қалай көрінеді."""
    if v is None:
        return ""
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, datetime.date):
        return v.strftime("%d.%m.%Y")
    return str(v)


def sql_value(text):
    """Пайдаланушы енгізгені -> SQL параметрі: бос = NULL, КК.АА.ЖЖЖЖ -> ЖЖЖЖ-АА-КК, 12,5 -> 12.5."""
    text = text.strip()
    if not text:
        return None
    m = re.fullmatch(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", text)
    if m:
        return f"{m[3]}-{int(m[2]):02}-{int(m[1]):02}"
    if re.fullmatch(r"-?\d+,\d+", text):
        return text.replace(",", ".")
    return text


def is_number(v):
    return isinstance(v, (int, float, decimal.Decimal)) and not isinstance(v, bool)


def human_error(e):
    text = str(e.args[-1]) if isinstance(e, pyodbc.Error) and e.args else str(e)
    hints = [
        ("REFERENCE constraint", "Жазбаны жою мүмкін емес: оған басқа кестелердің жолдары сілтейді."),
        ("FOREIGN KEY constraint", "Байланысты кестеде мұндай коды бар жазба жоқ. Кодтарды тексеріңіз."),
        ("CHECK constraint", "Мән рұқсат етілген аралықтан тыс. Сандар мен мөлшерді тексеріңіз."),
        ("UNIQUE KEY constraint", "Мұндай жазба бұрыннан бар."),
        ("PRIMARY KEY constraint", "Мұндай кілті бар жазба бұрыннан бар."),
        ("Cannot insert the value NULL", "Міндетті өрістерді толтырыңыз."),
        ("Conversion failed", "Формат қате. Сандарды цифрмен, күнді КК.АА.ЖЖЖЖ түрінде енгізіңіз."),
        ("Error converting", "Формат қате. Сандарды цифрмен, күнді КК.АА.ЖЖЖЖ түрінде енгізіңіз."),
    ]
    for key, message in hints:
        if key in text:
            return message
    return re.sub(r"\[[^\]]*\]|\s*\(\w+\)\s*$", "", text).strip()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"«{TITLE}» ішкі жүйесі")
        self.geometry("1280x760")
        self.minsize(1000, 600)
        self.configure(bg=C["bg"])
        self.report_callback_exception = lambda *e: messagebox.showerror(TITLE, human_error(e[1]), parent=self)
        create_database_if_missing()
        self.con = connect(DB)
        self.table = None      # ашық кесте (сонда қосу/өзгерту/жою қолжетімді)
        self.action = None     # ашық сұраныс/есеп/тапсырма
        self.cols, self.rows = [], {}
        self.param_entries = []
        self.note_job = None
        self.make_fonts()
        self.make_styles()
        self.build_sidebar()
        self.build_main()
        self.select_group("Кестелер")

    # ---------- безендіру ----------
    def make_fonts(self):
        base = tkfont.nametofont("TkDefaultFont")

        def font(size, weight="normal"):
            f = base.copy()
            f.configure(size=size, weight=weight)
            return f
        self.f_title = font(BASE + 11, "bold")
        self.f_h1 = font(BASE + 8, "bold")
        self.f_h2 = font(BASE + 3, "bold")
        self.f_body = font(BASE)
        self.f_bold = font(BASE, "bold")
        self.f_small = font(BASE - 1)

    def make_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")  # Windows пен Mac-та бірдей боялатын жалғыз тақырып
        s.configure(".", background=C["bg"], foreground=C["ink"], font=self.f_body)

        def flat(color):
            return dict(background=color, bordercolor=color, lightcolor=color, darkcolor=color)

        def states(normal, active, pressed, disabled):
            return [("disabled", disabled), ("pressed", pressed), ("active", active), ("!disabled", normal)]

        s.configure("Primary.TButton", foreground="#FFFFFF", font=self.f_bold, padding=(18, 8),
                    focuscolor="#FFFFFF", **flat(C["accent"]))
        fill = states(C["accent"], C["accent_dark"], C["accent_dark"], C["line"])
        s.map("Primary.TButton", background=fill, bordercolor=fill, lightcolor=fill, darkcolor=fill,
              foreground=[("disabled", C["surface"])])
        for name, fg, hover in (("Ghost", C["ink"], C["tint"]), ("Danger", C["danger"], C["danger_tint"])):
            s.configure(f"{name}.TButton", foreground=fg, padding=(16, 8), focuscolor=fg,
                        background=C["surface"], bordercolor=C["line"],
                        lightcolor=C["surface"], darkcolor=C["surface"])
            fill = states(C["surface"], hover, hover, C["bg"])
            s.map(f"{name}.TButton", background=fill, lightcolor=fill, darkcolor=fill,
                  bordercolor=[("disabled", C["line"]), ("active", fg)],
                  foreground=[("disabled", C["line"])])
        s.configure("TEntry", fieldbackground=C["surface"], bordercolor=C["line"], lightcolor=C["surface"],
                    darkcolor=C["surface"], padding=(8, 6), insertcolor=C["ink"])
        s.map("TEntry", bordercolor=[("focus", C["accent"])], lightcolor=[("focus", C["accent"])])
        s.configure("Treeview", background=C["surface"], fieldbackground=C["surface"], foreground=C["ink"],
                    borderwidth=0, font=self.f_body, rowheight=int(self.f_body.metrics("linespace") * 2.1))
        s.map("Treeview", background=[("selected", C["tint"])], foreground=[("selected", C["ink"])])
        s.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])  # жиексіз
        s.configure("Treeview.Heading", background=C["surface"], foreground=C["muted"], font=self.f_bold,
                    padding=(10, 8), relief="flat", bordercolor=C["line"],
                    lightcolor=C["surface"], darkcolor=C["surface"])
        s.map("Treeview.Heading", background=[("active", C["stripe"])])
        s.configure("TScrollbar", troughcolor=C["surface"], background=C["line"], bordercolor=C["surface"],
                    lightcolor=C["line"], darkcolor=C["line"], gripcount=0, arrowsize=10)
        s.map("TScrollbar", background=[("active", C["muted"])])
        for o, sticky in (("Vertical", "ns"), ("Horizontal", "ew")):  # көрсеткісіз жұқа жолақ
            s.layout(f"{o}.TScrollbar", [(f"{o}.Scrollbar.trough", {"sticky": sticky, "children": [
                (f"{o}.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})]})])

    def clickable(self, parent, text, command, font, padx, pady):
        """Мәзір пункті: тінтуір, Tab + Enter/бос орын, фокус жиегі көрінеді."""
        label = tk.Label(parent, text=text, font=font, bg=C["side"], fg=C["ink"], anchor="w", cursor="hand2",
                         padx=padx, pady=pady, takefocus=1, highlightthickness=1,
                         highlightbackground=C["side"], highlightcolor=C["accent"])
        label.active = False
        label.bind("<Button-1>", lambda e: command())
        label.bind("<Return>", lambda e: command())
        label.bind("<space>", lambda e: command())
        label.bind("<Enter>", lambda e: label.active or label.configure(bg=C["hover"]))
        label.bind("<Leave>", lambda e: self.paint(label))
        return label

    def paint(self, label, active=None):
        if active is not None:
            label.active = active
        bg = C["surface"] if label.active else C["side"]
        label.configure(bg=bg, highlightbackground=bg, fg=C["accent"] if label.active else C["ink"])

    # ---------- терезе қаңқасы ----------
    def build_sidebar(self):
        side = tk.Frame(self, bg=C["side"], width=SIDE_W)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        emblem = tk.Canvas(side, bg=C["side"], width=SIDE_W, highlightthickness=0)
        emblem.pack(fill="x")
        draw_emblem(emblem, SIDE_W)
        tk.Label(side, text=TITLE, font=self.f_title, bg=C["side"], fg=C["ink"], anchor="w").pack(
            fill="x", padx=24, pady=(22, 0))
        tk.Label(side, text=SUBTITLE, font=self.f_small, bg=C["side"], fg=C["muted"], anchor="w").pack(
            fill="x", padx=24, pady=(2, 20))
        tabs = tk.Frame(side, bg=C["side"])
        tabs.pack(fill="x", padx=18)
        self.tabs = {}
        for group in ["Кестелер", *ACTIONS]:
            self.tabs[group] = self.clickable(tabs, group, lambda g=group: self.select_group(g),
                                              self.f_small, 8, 5)
            self.tabs[group].pack(side="left")
        tk.Frame(side, bg=C["line"], height=1).pack(fill="x", padx=24, pady=(12, 8))
        self.nav = tk.Frame(side, bg=C["side"])
        self.nav.pack(fill="both", expand=True, padx=14)
        tk.Label(side, text=f"Сервер {SERVER}, дерекқор {DB}", font=self.f_small, bg=C["side"],
                 fg=C["muted"], anchor="w").pack(fill="x", padx=24, pady=14)

    def build_main(self):
        main = tk.Frame(self, bg=C["bg"])
        main.pack(side="left", fill="both", expand=True)
        head = tk.Frame(main, bg=C["bg"])
        head.pack(fill="x", padx=32, pady=(26, 0))
        head.columnconfigure(0, weight=1)
        self.h_title = tk.Label(head, font=self.f_h1, bg=C["bg"], fg=C["ink"], anchor="w")
        self.h_title.grid(row=0, column=0, sticky="w")
        right = tk.Frame(head, bg=C["bg"])
        right.grid(row=0, column=1, sticky="e")
        self.note = tk.Label(right, font=self.f_small, bg=C["bg"], fg=C["accent"])
        self.note.pack(side="left", padx=(0, 16))
        self.h_count = tk.Label(right, font=self.f_small, bg=C["bg"], fg=C["muted"])
        self.h_count.pack(side="left")
        self.h_desc = tk.Label(head, font=self.f_body, bg=C["bg"], fg=C["muted"], anchor="w",
                               justify="left", wraplength=760)
        self.h_desc.grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))

        bar = tk.Frame(main, bg=C["bg"])
        bar.pack(fill="x", padx=32, pady=(18, 14))
        self.controls = tk.Frame(bar, bg=C["bg"])
        self.controls.pack(side="left", anchor="s")
        self.export_btn = ttk.Button(bar, text="CSV-ге экспорттау", style="Ghost.TButton",
                                     command=self.save_csv)
        self.export_btn.pack(side="right", anchor="s")

        card = tk.Frame(main, bg=C["surface"], highlightthickness=1, highlightbackground=C["line"])
        card.pack(fill="both", expand=True, padx=32, pady=(0, 28))
        card.rowconfigure(0, weight=1)
        card.columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(card, show="headings", selectmode="browse")
        ys = ttk.Scrollbar(card, orient="vertical", command=self.tree.yview)
        xs = ttk.Scrollbar(card, orient="horizontal", command=self.tree.xview)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=(4, 0))
        ys.grid(row=0, column=1, sticky="ns", padx=2, pady=2)
        xs.grid(row=1, column=0, sticky="ew", padx=2, pady=2)

        def autohide(bar):  # айналдыру жолағы тек айналдыратын нәрсе болғанда көрінеді
            def set_(lo, hi):
                bar.grid_remove() if float(lo) <= 0 and float(hi) >= 1 else bar.grid()
                bar.set(lo, hi)
            return set_
        self.tree.configure(yscrollcommand=autohide(ys), xscrollcommand=autohide(xs))
        self.tree.tag_configure("odd", background=C["stripe"])
        self.tree.tag_configure("total", font=self.f_bold, background=C["tint"])
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.update_buttons())
        self.tree.bind("<Double-1>", lambda e: self.table and self.selected_row() and self.edit())
        self.empty = tk.Label(card, font=self.f_body, bg=C["surface"], fg=C["muted"])

    # ---------- навигация ----------
    def select_group(self, group):
        for name, tab in self.tabs.items():
            self.paint(tab, name == group)
        for w in self.nav.winfo_children():
            w.destroy()
        items = TABLES if group == "Кестелер" else ACTIONS[group]
        self.nav_items = []
        for item in items:
            text = nice(item) if isinstance(item, str) else item[0]
            label = self.clickable(self.nav, text, lambda i=item: self.open(i), self.f_body, 12, 7)
            label.item = item
            label.pack(fill="x", pady=1)
            self.nav_items.append(label)
        self.open(items[0])

    def open(self, item):
        for label in self.nav_items:
            self.paint(label, label.item == item)
        for w in self.controls.winfo_children():
            w.destroy()
        self.param_entries = []
        if isinstance(item, str):
            self.table, self.action = item, None
            self.h_title.config(text=nice(item))
            self.h_desc.config(text="Жолды екі рет басса, ол өзгертуге ашылады.")
            ttk.Button(self.controls, text="Жазба қосу", style="Primary.TButton",
                       command=self.add).pack(side="left")
            self.edit_btn = ttk.Button(self.controls, text="Өзгерту", style="Ghost.TButton", command=self.edit)
            self.edit_btn.pack(side="left", padx=(8, 0))
            self.del_btn = ttk.Button(self.controls, text="Жою", style="Danger.TButton", command=self.delete)
            self.del_btn.pack(side="left", padx=(8, 0))
            self.fill(self.con.execute(f"SELECT * FROM [{item}]"))
            return
        self.table, self.action = None, item
        title, proc, params, description = item[:4]
        button = item[4] if len(item) > 4 else "Көрсету"
        self.h_title.config(text=title.split(". ", 1)[-1])
        self.h_desc.config(text=description)
        for label in params:
            box = tk.Frame(self.controls, bg=C["bg"])
            box.pack(side="left", padx=(0, 12))
            hint = " (КК.АА.ЖЖЖЖ)" if label == "Күні" else ""
            tk.Label(box, text=label + hint, font=self.f_small, bg=C["bg"], fg=C["muted"]).pack(anchor="w")
            entry = ttk.Entry(box, width=16, font=self.f_body)
            entry.insert(0, PARAM_DEFAULTS.get(label, ""))
            entry.pack(anchor="w", pady=(3, 0))
            entry.bind("<Return>", lambda e: self.run_action())
            self.param_entries.append(entry)
        ttk.Button(self.controls, text=button, style="Primary.TButton",
                   command=self.run_action).pack(side="left", anchor="s")
        if params:
            self.param_entries[0].focus_set()
        if not params and button == "Көрсету":
            self.run_action()
        else:
            self.fill(None, f"Параметрлерді енгізіп, «{button}» батырмасын басыңыз." if params
                      else f"«{button}» батырмасын басыңыз.")

    def run_action(self):
        title, proc, params = self.action[:3]
        values = [sql_value(e.get()) for e in self.param_entries]
        if None in values:
            self.flash("Барлық параметрлерді толтырыңыз.", error=True)
            return
        marks = ", ".join("?" * len(values))
        self.fill(self.con.execute(f"EXEC [{proc}] {marks}", values),
                  "Ештеңе табылмады. Параметрлерді өзгертіп, қайталап көріңіз.")
        if len(self.action) > 4:
            self.flash("Жолдар қосылды.")

    # ---------- нәтиже кестесі ----------
    def fill(self, cur, empty_text="Кесте бос. Алғашқы жазбаны қосыңыз."):
        if cur is not None:
            while cur.description is None and cur.nextset():
                pass
        self.cols = [d[0] for d in cur.description] if cur is not None and cur.description else []
        rows = cur.fetchall() if self.cols else []
        tree = self.tree
        tree.delete(*tree.get_children())
        tree["columns"] = self.cols
        texts = [[cell_text(v) for v in r] for r in rows]
        for i, col in enumerate(self.cols):
            numeric = any(is_number(r[i]) for r in rows) and all(r[i] is None or is_number(r[i]) for r in rows)
            width = max([self.f_bold.measure(nice(col))] + [self.f_body.measure(t[i]) for t in texts[:300]])
            tree.heading(col, text=nice(col), anchor="e" if numeric else "w")
            tree.column(col, width=min(width + 32, 380), minwidth=60, anchor="e" if numeric else "w",
                        stretch=i == len(self.cols) - 1)
        self.rows = {}
        for n, (row, text) in enumerate(zip(rows, texts)):
            tags = ("total",) if text and text[0] == TOTAL else ("odd",) if n % 2 else ()
            self.rows[tree.insert("", "end", values=text, tags=tags)] = row
        self.h_count.config(text=f"{len(rows)} жол" if cur is not None else "")
        if rows:
            self.empty.place_forget()
        else:
            self.empty.config(text=empty_text)
            self.empty.place(relx=0.5, rely=0.45, anchor="center")
        self.export_btn.state(["!disabled"] if rows else ["disabled"])
        self.update_buttons()

    def update_buttons(self):
        if self.table:
            state = ["!disabled"] if self.tree.selection() else ["disabled"]
            self.edit_btn.state(state)
            self.del_btn.state(state)

    def flash(self, text, error=False):
        self.note.config(text=text, fg=C["danger"] if error else C["accent"])
        if self.note_job:
            self.after_cancel(self.note_job)
        self.note_job = self.after(4000, lambda: self.note.config(text=""))

    # ---------- қосу / өзгерту / жою ----------
    def columns_info(self):
        """Ашық кестенің бағандары [(аты, identity?)] және бастапқы кілт бағандары."""
        cols = self.con.execute("SELECT name, is_identity FROM sys.columns WHERE object_id = OBJECT_ID(?) "
                                "ORDER BY column_id", self.table).fetchall()
        pk = [r[0] for r in self.con.execute(
            "SELECT k.COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE k "
            "JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS t ON t.CONSTRAINT_NAME = k.CONSTRAINT_NAME "
            "WHERE t.TABLE_NAME = ? AND t.CONSTRAINT_TYPE = 'PRIMARY KEY' ORDER BY k.ORDINAL_POSITION",
            self.table)]
        return cols, pk

    def selected_row(self):
        selection = self.tree.selection()
        return self.rows.get(selection[0]) if selection else None

    def form(self, title, names, values=(), submit="Сақтау"):
        """Өрістері бар терезе. SQL параметрлерінің тізімін, ал жабылса None қайтарады."""
        win = tk.Toplevel(self, bg=C["surface"], padx=28, pady=24)
        win.title(title)
        win.transient(self)
        win.resizable(False, False)
        tk.Label(win, text=title, font=self.f_h2, bg=C["surface"], fg=C["ink"]).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 16))
        entries, result = [], []
        for i, name in enumerate(names):
            tk.Label(win, text=nice(name), font=self.f_small, bg=C["surface"], fg=C["muted"]).grid(
                row=i + 1, column=0, sticky="w", padx=(0, 18), pady=5)
            entry = ttk.Entry(win, width=38, font=self.f_body)
            entry.grid(row=i + 1, column=1, sticky="ew", pady=5)
            if i < len(values):
                entry.insert(0, field_text(values[i]))
            entries.append(entry)
        tk.Label(win, text="Күнді КК.АА.ЖЖЖЖ түрінде енгізіңіз. Бос өріс NULL болып сақталады.",
                 font=self.f_small, bg=C["surface"], fg=C["muted"]).grid(
            row=len(names) + 1, column=0, columnspan=2, sticky="w", pady=(10, 0))

        def ok(*_):
            result.extend(sql_value(e.get()) for e in entries)
            win.destroy()
        buttons = tk.Frame(win, bg=C["surface"])
        buttons.grid(row=len(names) + 2, column=0, columnspan=2, sticky="e", pady=(20, 0))
        ttk.Button(buttons, text="Болдырмау", style="Ghost.TButton", command=win.destroy).pack(side="left")
        ttk.Button(buttons, text=submit, style="Primary.TButton", command=ok).pack(side="left", padx=(8, 0))
        win.bind("<Return>", ok)
        win.bind("<Escape>", lambda *_: win.destroy())
        entries[0].focus_set()
        win.wait_visibility()
        win.grab_set()
        self.wait_window(win)
        return result or None

    def add(self):
        cols, _ = self.columns_info()
        names = [n for n, identity in cols if not identity]  # IDENTITY санауыштарын сервер толтырады
        values = self.form(f"Жаңа жазба: {nice(self.table)}", names, submit="Қосу")
        if values is not None:
            self.con.execute(f"INSERT INTO [{self.table}] ({', '.join(f'[{n}]' for n in names)}) "
                             f"VALUES ({', '.join('?' * len(names))})", values)
            self.open(self.table)
            self.flash("Жазба қосылды.")

    def edit(self):
        row = self.selected_row()
        if row is None:
            return
        cols, pk = self.columns_info()
        all_names = [n for n, _ in cols]
        names = [n for n, identity in cols if not identity]
        values = self.form(f"Жазбаны өзгерту: {nice(self.table)}", names,
                           [row[all_names.index(n)] for n in names])
        if values is not None:
            sets = ", ".join(f"[{n}] = ?" for n in names)
            where = " AND ".join(f"[{k}] = ?" for k in pk)
            self.con.execute(f"UPDATE [{self.table}] SET {sets} WHERE {where}",
                             values + [row[all_names.index(k)] for k in pk])
            self.open(self.table)
            self.flash("Өзгерістер сақталды.")

    def delete(self):
        row = self.selected_row()
        if row is None or not messagebox.askyesno(
                TITLE, f"Таңдалған жазбаны «{nice(self.table)}» кестесінен жою керек пе?", parent=self):
            return
        cols, pk = self.columns_info()
        all_names = [n for n, _ in cols]
        self.con.execute(f"DELETE FROM [{self.table}] WHERE " + " AND ".join(f"[{k}] = ?" for k in pk),
                         [row[all_names.index(k)] for k in pk])
        self.open(self.table)
        self.flash("Жазба жойылды.")

    def save_csv(self):
        path = filedialog.asksaveasfilename(parent=self, defaultextension=".csv",
                                            initialfile=self.h_title.cget("text") + ".csv",
                                            filetypes=[("CSV (Excel)", "*.csv")])
        if path:
            # utf-8-sig пен ';' — Windows-тағы Excel қазақ әріптерін бағандар бойынша бірден ашуы үшін
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f, delimiter=";")
                w.writerow(nice(c) for c in self.cols)
                w.writerows([field_text(v) for v in r] for r in self.rows.values())
            self.flash("Файл сақталды.")


if __name__ == "__main__":
    try:
        App().mainloop()
    except (pyodbc.Error, RuntimeError, OSError) as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(TITLE, f"SQL Server-ге қосылу мүмкін болмады ({SERVER}).\n"
                                    f"Сервердің іске қосылғанын тексеріңіз.\n\n{human_error(e)}")
