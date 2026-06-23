import os
os.environ["TK_SILENCE_DEPRECATION"] = "1"

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from query import *
from utils import *

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
        self.pie_host = None

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

    def _build_home_view(self):
        top = ttk.Frame(self.home_frame)
        top.pack(fill=tk.X, pady=(0, 10))

        self.home_title_var = tk.StringVar(value="Choose a Continent")
        ttk.Label(
            top,
            textvariable=self.home_title_var,
            font=("TkDefaultFont", 14, "bold")
        ).pack(side=tk.LEFT)

        ttk.Button(top, text="Refresh", command=self.refresh_continent_buttons).pack(side=tk.RIGHT)

        self.home_buttons_frame = ttk.Frame(self.home_frame)
        self.home_buttons_frame.pack(fill=tk.BOTH, expand=True)

        self.home_status_var = tk.StringVar(value="")
        ttk.Label(self.home_frame, textvariable=self.home_status_var).pack(anchor="w", pady=(8, 0))

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

    def show_data_page(self, title, dataframe, pie_df=None, pie_title=None, stats_df=None):
        self.data_title_var.set(title)
        self._render_table(dataframe)
        self._render_pie(pie_df=pie_df, pie_title=pie_title)
        # Use stats_df if provided, otherwise fall back to main dataframe
        self._render_stats(stats_df if stats_df is not None else dataframe)

        self._clear_container()
        self.data_frame.pack(fill=tk.BOTH, expand=True)

    def _build_data_view(self):
        top = ttk.Frame(self.data_frame)
        top.pack(fill=tk.X, pady=(0, 10))
    
        self.data_title_var = tk.StringVar(value="Results")
        ttk.Label(top, textvariable=self.data_title_var, font=("TkDefaultFont", 12, "bold")).pack(side=tk.LEFT)
        ttk.Button(top, text="Back", command=self.back_from_data).pack(side=tk.RIGHT)
    
        # Main content: table and chart
        content = ttk.Frame(self.data_frame)
        content.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        content.rowconfigure(0, weight=1)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
    
        # Left: table
        table_wrap = ttk.Frame(content)
        table_wrap.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        table_wrap.rowconfigure(0, weight=1)
        table_wrap.columnconfigure(0, weight=1)
    
        self.tree = ttk.Treeview(table_wrap, show="headings")
        yscroll = ttk.Scrollbar(table_wrap, orient=tk.VERTICAL, command=self.tree.yview)
        xscroll = ttk.Scrollbar(table_wrap, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
    
        # Right: pie chart
        self.pie_host = ttk.Frame(content)
        self.pie_host.grid(row=0, column=1, sticky="nsew")
        
        # Bottom: salary stats panel
        self.stats_frame = ttk.LabelFrame(self.data_frame, text="Salary Summary", padding=10)
        self.stats_frame.pack(fill=tk.X, padx=0, pady=(0, 0))

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
            stats_df = get_salaries_by_continent(self.conn, self.current_continent)
            self.show_data_page(
                f"Overall - {self.current_continent} (Country Job Counts)",
                df,
                pie_df=df,
                pie_title=f"{self.current_continent}: Country Distribution",
                stats_df=stats_df
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
            stats_df = get_salaries_by_country(self.conn, country)
            self.show_data_page(
                f"{country} - Location/Role/Experience Summary",
                df,
                stats_df=stats_df
            )
        except Exception as ex:
            messagebox.showerror("Query Error", str(ex))

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
    
    def _render_pie(self, pie_df=None, pie_title=None):
        if self.pie_host is None:
            return

        for child in self.pie_host.winfo_children():
            child.destroy()

        if pie_df is None or pie_df.empty:
            ttk.Label(
                self.pie_host,
                text="Pie chart is shown for Overall view.",
                justify=tk.CENTER,
            ).pack(expand=True)
            return

        if "location" not in pie_df.columns or "job_count" not in pie_df.columns:
            ttk.Label(
                self.pie_host,
                text="No pie data available for this view.",
                justify=tk.CENTER,
            ).pack(expand=True)
            return

        try:
            fig = pie_graph(pie_df)
            if pie_title:
                fig.axes[0].set_title(pie_title)
            canvas = FigureCanvasTkAgg(fig, master=self.pie_host)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        except Exception as ex:
            messagebox.showerror("Pie Chart Error", str(ex))
    
    def _render_stats(self, df):
        if not hasattr(self, 'stats_frame'):
            return
        
        for child in self.stats_frame.winfo_children():
            child.destroy()
        
        try:
            stats = get_salary_stats(df)
            avg = stats.get("avg_salary", 0)
            highest = stats.get("highest_pay")
            lowest = stats.get("lowest_pay")
            
            # Create three columns for the stats
            cols = ttk.Frame(self.stats_frame)
            cols.pack(fill=tk.X)
            
            # Average salary
            avg_frame = ttk.Frame(cols)
            avg_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))
            ttk.Label(avg_frame, text="Average Salary", font=("TkDefaultFont", 10, "bold")).pack()
            ttk.Label(avg_frame, text=f"${avg:,.2f}" if avg else "N/A", font=("TkDefaultFont", 11)).pack()
            
            # Highest salary
            high_frame = ttk.Frame(cols)
            high_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))
            ttk.Label(high_frame, text="Highest Salary", font=("TkDefaultFont", 10, "bold")).pack()
            if highest:
                salary = highest.get("salary", "N/A")
                title = highest.get("job_title", "")
                exp = highest.get("experience_level", "")
                # Show location context (country for continent view, location for country view)
                context = highest.get("country") or highest.get("location", "")
                detail_parts = [p for p in [context, title, exp] if p]
                detail = " | ".join(detail_parts)
                ttk.Label(high_frame, text=f"${salary:,.2f}" if salary else "N/A").pack()
                ttk.Label(high_frame, text=detail, font=("TkDefaultFont", 9), justify=tk.LEFT, wraplength=200).pack()
            else:
                ttk.Label(high_frame, text="N/A").pack()
            
            # Lowest salary
            low_frame = ttk.Frame(cols)
            low_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            ttk.Label(low_frame, text="Lowest Salary", font=("TkDefaultFont", 10, "bold")).pack()
            if lowest:
                salary = lowest.get("salary", "N/A")
                title = lowest.get("job_title", "")
                exp = lowest.get("experience_level", "")
                # Show location context (country for continent view, location for country view)
                context = lowest.get("country") or lowest.get("location", "")
                detail_parts = [p for p in [context, title, exp] if p]
                detail = " | ".join(detail_parts)
                ttk.Label(low_frame, text=f"${salary:,.2f}" if salary else "N/A").pack()
                ttk.Label(low_frame, text=detail, font=("TkDefaultFont", 9), justify=tk.LEFT, wraplength=200).pack()
            else:
                ttk.Label(low_frame, text="N/A").pack()
        except Exception as ex:
            ttk.Label(self.stats_frame, text=f"Error loading stats: {ex}").pack()

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