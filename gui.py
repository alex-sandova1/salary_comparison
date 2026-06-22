import os
os.environ["TK_SILENCE_DEPRECATION"] = "1"

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

from query import *

DB_PATH = "salaries.db"


def connect_existing_database():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            "salaries.db was not found. Run [start.py](http://_vscodecontentref_/1) first to build the database."
        )

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("SELECT 1 FROM salaries LIMIT 1")
    except sqlite3.Error as ex:
        conn.close()
        raise RuntimeError(
            "salaries table is missing. Run [start.py](http://_vscodecontentref_/2) first to rebuild salaries.db."
        ) from ex
    return conn


class SalaryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Salary Analysis Report")
        self.geometry("900x620")
        self.minsize(760, 500)

        self.conn = connect_existing_database()
        self.current_continent = None
        self.current_countries = []

        self._configure_style()

        self.container = ttk.Frame(self, padding=12)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.home_frame = ttk.Frame(self.container)
        self.continent_frame = ttk.Frame(self.container)
        self.data_frame = ttk.Frame(self.container)

        self._build_home_view()
        self._build_continent_view()
        self._build_data_view()

        self.show_home()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _configure_style(self):
        style = ttk.Style(self)
        themes = style.theme_names()
        if "clam" in themes:
            style.theme_use("clam")
        elif "default" in themes:
            style.theme_use("default")

    def _clear_container(self):
        for child in self.container.winfo_children():
            child.pack_forget()

    def show_home(self):
        self._clear_container()
        self.home_frame.pack(fill=tk.BOTH, expand=True)
        self.refresh_continent_buttons()

    def show_continent_page(self, continent):
        self.current_continent = continent
        self.continent_title_var.set(f"Continent: {continent}")

        try:
            countries_df = count_jobs_by_country_in_continent(self.conn, continent)
            self.current_countries = countries_df["location"].dropna().tolist()
        except Exception as ex:
            messagebox.showerror("Load Error", str(ex))
            self.current_countries = []

        self.country_combo["values"] = self.current_countries
        self.country_var.set(self.current_countries[0] if self.current_countries else "")

        self._clear_container()
        self.continent_frame.pack(fill=tk.BOTH, expand=True)

    def show_data_page(self, title, dataframe):
        self.data_title_var.set(title)
        self._render_table(dataframe)

        self._clear_container()
        self.data_frame.pack(fill=tk.BOTH, expand=True)

    def _build_home_view(self):
        header = ttk.Frame(self.home_frame)
        header.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(
            header,
            text="Choose a Continent",
            font=("TkDefaultFont", 14, "bold")
        ).pack(side=tk.LEFT)

        ttk.Button(header, text="Refresh", command=self.refresh_continent_buttons).pack(side=tk.RIGHT)

        self.home_buttons_frame = ttk.Frame(self.home_frame)
        self.home_buttons_frame.pack(fill=tk.BOTH, expand=True)

        self.home_status_var = tk.StringVar(value="")
        ttk.Label(self.home_frame, textvariable=self.home_status_var).pack(anchor="w", pady=(8, 0))

    def refresh_continent_buttons(self):
        for child in self.home_buttons_frame.winfo_children():
            child.destroy()

        try:
            continents_df = get_continents(self.conn)
            continents = continents_df["continent"].dropna().tolist()
        except Exception as ex:
            messagebox.showerror("Load Error", str(ex))
            continents = []

        if not continents:
            ttk.Label(self.home_buttons_frame, text="No continents found").pack(anchor="w", pady=6)
            self.home_status_var.set("No continents loaded")
            return

        cols = 3
        for i, continent in enumerate(continents):
            row = i // cols
            col = i % cols

            b = ttk.Button(
                self.home_buttons_frame,
                text=continent,
                command=lambda c=continent: self.show_continent_page(c),
                width=22,
            )
            b.grid(row=row, column=col, padx=6, pady=6, sticky="ew")

        for col in range(cols):
            self.home_buttons_frame.grid_columnconfigure(col, weight=1)

        self.home_status_var.set(f"Loaded {len(continents)} continents")

    def _build_continent_view(self):
        top = ttk.Frame(self.continent_frame)
        top.pack(fill=tk.X, pady=(0, 10))

        self.continent_title_var = tk.StringVar(value="Continent")
        ttk.Label(
            top,
            textvariable=self.continent_title_var,
            font=("TkDefaultFont", 13, "bold")
        ).pack(side=tk.LEFT)

        ttk.Button(top, text="Back", command=self.show_home).pack(side=tk.RIGHT)

        card = ttk.Frame(self.continent_frame, padding=10)
        card.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(card, text="Actions", font=("TkDefaultFont", 11, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 8)
        )

        ttk.Button(
            card,
            text="Overall (All Countries in this Continent)",
            command=self.on_show_overall,
            width=42
        ).grid(row=1, column=0, sticky="w", padx=(0, 10))

        self.country_var = tk.StringVar(value="")
        self.country_combo = ttk.Combobox(
            card,
            textvariable=self.country_var,
            state="readonly",
            width=28
        )
        self.country_combo.grid(row=1, column=1, sticky="w", padx=(0, 8))

        ttk.Button(card, text="Open Country", command=self.on_open_country).grid(
            row=1, column=2, sticky="w"
        )

        info = (
            "Overall shows job count by country for this continent.\n"
            "Open Country shows location/title/experience summary for the selected country."
        )
        ttk.Label(self.continent_frame, text=info, justify=tk.LEFT).pack(anchor="w", pady=(4, 0))

    def on_show_overall(self):
        if not self.current_continent:
            return
        try:
            df = count_jobs_by_country_in_continent(self.conn, self.current_continent)
            self.show_data_page(
                f"Overall - {self.current_continent} (Country Job Counts)",
                df
            )
        except Exception as ex:
            messagebox.showerror("Query Error", str(ex))

    def on_open_country(self):
        country = self.country_var.get().strip()
        if not country:
            messagebox.showwarning("Selection Required", "Pick a country first.")
            return

        try:
            df = job_summary_by_location_in_country(self.conn, country)
            self.show_data_page(
                f"{country} - Location/Role/Experience Summary",
                df
            )
        except Exception as ex:
            messagebox.showerror("Query Error", str(ex))

    def _build_data_view(self):
        top = ttk.Frame(self.data_frame)
        top.pack(fill=tk.X, pady=(0, 10))

        self.data_title_var = tk.StringVar(value="Results")
        ttk.Label(
            top,
            textvariable=self.data_title_var,
            font=("TkDefaultFont", 12, "bold")
        ).pack(side=tk.LEFT)

        ttk.Button(top, text="Back", command=self.back_from_data).pack(side=tk.RIGHT)

        table_wrap = ttk.Frame(self.data_frame)
        table_wrap.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(table_wrap, show="headings")
        yscroll = ttk.Scrollbar(table_wrap, orient=tk.VERTICAL, command=self.tree.yview)
        xscroll = ttk.Scrollbar(table_wrap, orient=tk.HORIZONTAL, command=self.tree.xview)

        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")

        table_wrap.rowconfigure(0, weight=1)
        table_wrap.columnconfigure(0, weight=1)

    def back_from_data(self):
        if self.current_continent:
            self.show_continent_page(self.current_continent)
        else:
            self.show_home()

    def _render_table(self, df):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ()

        if df is None or df.empty:
            self.tree["columns"] = ("message",)
            self.tree.heading("message", text="Message")
            self.tree.column("message", width=500, anchor="w")
            self.tree.insert("", tk.END, values=("No data found for this selection.",))
            return

        cols = list(df.columns)
        self.tree["columns"] = cols

        for col in cols:
            self.tree.heading(col, text=col)
            width = 160 if col not in {"job_title"} else 240
            self.tree.column(col, width=width, anchor="center")

        for row in df.itertuples(index=False):
            self.tree.insert("", tk.END, values=list(row))

    def on_close(self):
        try:
            if self.conn is not None:
                self.conn.close()
        finally:
            self.destroy()


def main():
    app = SalaryApp()
    app.mainloop()


if __name__ == "__main__":
    main()
    main()