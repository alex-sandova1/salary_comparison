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
    """Connect to the salary database and verify the salaries table exists."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            "salaries.db was not found. Run start.py first to build the database."
        )

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("SELECT 1 FROM salaries LIMIT 1")
    except sqlite3.Error as ex:
        conn.close()
        raise RuntimeError(
            "salaries table is missing. Run start.py first to rebuild salaries.db."
        ) from ex
    return conn


class SalaryApp(tk.Tk):
    """Main GUI application for salary data exploration. """
    
    def __init__(self):
        """Initialize the Salary Analysis application and set up the GUI."""
        super().__init__()
        self.title("Salary Atlas")
        self.geometry("1040x700")
        self.minsize(860, 580)
        self.configure(bg="#F4F7FB")

        self.colors = {
            "navy": "#102A43",
            "navy_light": "#173F5F",
            "ink": "#243B53",
            "muted": "#627D98",
            "canvas": "#F4F7FB",
            "card": "#FFFFFF",
            "accent": "#E76F51",
            "accent_hover": "#D85C3D",
            "soft_accent": "#FFF0EC",
            "line": "#D9E2EC",
            "table_alt": "#F8FAFC",
        }

        # Database connection and state tracking
        self.conn = connect_existing_database()
        self.current_continent = None
        self.current_countries = []
        self.pie_host = None

        self._configure_style()

        self._build_header()
        self.container = ttk.Frame(self, style="App.TFrame", padding=(28, 24, 28, 28))
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
        """Set a clean, card-based visual language for the application."""
        style = ttk.Style(self)
        themes = style.theme_names()
        if "clam" in themes:
            style.theme_use("clam")
        elif "default" in themes:
            style.theme_use("default")

        c = self.colors
        style.configure("App.TFrame", background=c["canvas"])
        style.configure("Card.TFrame", background=c["card"])
        style.configure("Card.TLabelframe", background=c["card"], borderwidth=0, relief="flat")
        style.configure(
            "Card.TLabelframe.Label", background=c["card"], foreground=c["ink"],
            font=("Helvetica", 11, "bold")
        )
        style.configure("Title.TLabel", background=c["canvas"], foreground=c["ink"], font=("Helvetica", 22, "bold"))
        style.configure("PageTitle.TLabel", background=c["canvas"], foreground=c["ink"], font=("Helvetica", 17, "bold"))
        style.configure("Subtitle.TLabel", background=c["canvas"], foreground=c["muted"], font=("Helvetica", 10))
        style.configure("CardTitle.TLabel", background=c["card"], foreground=c["ink"], font=("Helvetica", 11, "bold"))
        style.configure("CardText.TLabel", background=c["card"], foreground=c["muted"], font=("Helvetica", 10))
        style.configure("Header.TFrame", background=c["navy"])
        style.configure("HeaderBrand.TLabel", background=c["navy"], foreground="#FFFFFF", font=("Helvetica", 16, "bold"))
        style.configure("HeaderText.TLabel", background=c["navy"], foreground="#BFD7EA", font=("Helvetica", 10))
        style.configure("Accent.TButton", background=c["accent"], foreground="#FFFFFF", borderwidth=0, font=("Helvetica", 10, "bold"), padding=(14, 9))
        style.map("Accent.TButton", background=[("active", c["accent_hover"]), ("pressed", c["accent_hover"])])
        style.configure("Secondary.TButton", background=c["card"], foreground=c["navy_light"], borderwidth=0, font=("Helvetica", 10, "bold"), padding=(12, 8))
        style.map("Secondary.TButton", background=[("active", c["soft_accent"]), ("pressed", c["soft_accent"])])
        style.configure("Continent.TButton", background=c["card"], foreground=c["navy_light"], borderwidth=0, font=("Helvetica", 11, "bold"), padding=(12, 11), anchor="w")
        style.map("Continent.TButton", background=[("active", c["soft_accent"]), ("pressed", c["soft_accent"])], foreground=[("active", c["accent"])])
        style.configure("TCombobox", fieldbackground="#FFFFFF", background="#FFFFFF", foreground=c["ink"], padding=7)
        style.configure("Treeview", background="#FFFFFF", fieldbackground="#FFFFFF", foreground=c["ink"], rowheight=32, borderwidth=0, font=("Helvetica", 10))
        style.configure("Treeview.Heading", background=c["navy_light"], foreground="#FFFFFF", relief="flat", font=("Helvetica", 10, "bold"), padding=(10, 9))
        style.map("Treeview", background=[("selected", "#D8EAF5")], foreground=[("selected", c["navy"])])
        style.configure("TScrollbar", background=c["line"], troughcolor=c["canvas"], borderwidth=0, arrowsize=12)

    def _build_header(self):
        """Build the persistent application header."""
        header = ttk.Frame(self, style="Header.TFrame", padding=(28, 15))
        header.pack(fill=tk.X)
        ttk.Label(header, text="SALARY ATLAS", style="HeaderBrand.TLabel").pack(side=tk.LEFT)
        ttk.Label(header, text="Explore data science pay, one market at a time", style="HeaderText.TLabel").pack(side=tk.LEFT, padx=(16, 0))

    def _clear_container(self):
        """Clear all widgets from the main container frame."""
        for child in self.container.winfo_children():
            child.pack_forget()

    def _build_home_view(self):
        """Build the home view with continent selection buttons and refresh control."""
        top = ttk.Frame(self.home_frame, style="App.TFrame")
        top.pack(fill=tk.X, pady=(0, 22))

        # Title label
        self.home_title_var = tk.StringVar(value="Choose a region")
        ttk.Label(
            top,
            textvariable=self.home_title_var,
            style="Title.TLabel"
        ).pack(side=tk.LEFT)

        # Refresh button to reload continents
        ttk.Button(top, text="Refresh data", style="Secondary.TButton", command=self.refresh_continent_buttons).pack(side=tk.RIGHT)

        ttk.Label(self.home_frame, text="Select a region to compare countries, roles, and salary ranges.", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 18))

        remote_card = ttk.Frame(self.home_frame, style="Card.TFrame", padding=(18, 14))
        remote_card.pack(fill=tk.X, pady=(0, 18))
        remote_copy = ttk.Frame(remote_card, style="Card.TFrame")
        remote_copy.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(remote_copy, text="Remote jobs", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(
            remote_copy,
            text="Compare remote opportunities across countries and salary ranges.",
            style="CardText.TLabel",
        ).pack(anchor="w", pady=(3, 0))
        ttk.Button(remote_card, text="Explore remote jobs", style="Accent.TButton", command=self.on_show_remote_jobs).pack(side=tk.RIGHT, padx=(18, 0))

        # Container for continent buttons
        self.home_buttons_frame = ttk.Frame(self.home_frame, style="App.TFrame")
        self.home_buttons_frame.pack(fill=tk.BOTH, expand=True)

        # Status label showing count of loaded continents
        self.home_status_var = tk.StringVar(value="")
        ttk.Label(self.home_frame, textvariable=self.home_status_var, style="Subtitle.TLabel").pack(anchor="w", pady=(16, 0))

    def show_home(self):
        """Display the home view with continent selection."""
        self._clear_container()
        self.home_frame.pack(fill=tk.BOTH, expand=True)
        self.refresh_continent_buttons()

    def show_continent_page(self, continent):
        """Display the continent view with country selection options."""
        self.current_continent = continent
        self.continent_title_var.set(f"Continent: {continent}")

        # Load countries within this continent
        try:
            countries_df = count_jobs_by_country_in_continent(self.conn, continent)
            self.current_countries = countries_df["location"].dropna().tolist()
        except Exception as ex:
            messagebox.showerror("Load Error", str(ex))
            self.current_countries = []

        # Populate country dropdown
        self.country_combo["values"] = self.current_countries
        self.country_var.set(self.current_countries[0] if self.current_countries else "")

        self._clear_container()
        self.continent_frame.pack(fill=tk.BOTH, expand=True)

    def show_data_page(self, title, dataframe, pie_df=None, pie_title=None, stats_df=None):
        """Display the data view with a table, optional pie chart, and salary statistics. """
        self.data_title_var.set(title)
        self._render_table(dataframe)
        self._render_pie(pie_df=pie_df, pie_title=pie_title)
        # Use stats_df if provided, otherwise fall back to main dataframe
        self._render_stats(stats_df if stats_df is not None else dataframe)

        self._clear_container()
        self.data_frame.pack(fill=tk.BOTH, expand=True)

    def _build_data_view(self):
        """Build the data view with table, pie chart, and salary statistics."""
        # Top bar with title and back button
        top = ttk.Frame(self.data_frame, style="App.TFrame")
        top.pack(fill=tk.X, pady=(0, 10))
    
        self.data_title_var = tk.StringVar(value="Results")
        ttk.Label(top, textvariable=self.data_title_var, style="PageTitle.TLabel").pack(side=tk.LEFT)
        ttk.Button(top, text="← Back", style="Secondary.TButton", command=self.back_from_data).pack(side=tk.RIGHT)
    
        # Main content: table on left (3/4 width), pie chart on right (1/4 width)
        content = ttk.Frame(self.data_frame, style="App.TFrame")
        content.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        content.rowconfigure(0, weight=1)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
    
        # Left side: scrollable table with data
        table_wrap = ttk.Frame(content, style="Card.TFrame", padding=1)
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
    
        # Right side: pie chart container
        self.pie_host = ttk.Frame(content, style="Card.TFrame", padding=10)
        self.pie_host.grid(row=0, column=1, sticky="nsew")
        
        # Bottom: salary statistics summary panel
        self.stats_frame = ttk.LabelFrame(self.data_frame, text="Salary summary", style="Card.TLabelframe", padding=16)
        self.stats_frame.pack(fill=tk.X, padx=0, pady=(0, 0))

    def refresh_continent_buttons(self):
        """Reload continent buttons from the database in a 3-column grid layout."""
        # Clear existing buttons
        for child in self.home_buttons_frame.winfo_children():
            child.destroy()

        # Fetch continents from database
        try:
            continents_df = get_continents(self.conn)
            continents = continents_df["continent"].dropna().tolist()
        except Exception as ex:
            messagebox.showerror("Load Error", str(ex))
            continents = []

        # Handle empty result
        if not continents:
            ttk.Label(self.home_buttons_frame, text="No regions found in the current database.", style="Subtitle.TLabel").pack(anchor="w", pady=6)
            self.home_status_var.set("No continents loaded")
            return

        # Create buttons in a 3-column grid
        cols = 3
        for i, continent in enumerate(continents):
            row = i // cols
            col = i % cols

            b = ttk.Button(
                self.home_buttons_frame,
                text=continent,
                command=lambda c=continent: self.show_continent_page(c),
                style="Continent.TButton",
            )
            b.grid(row=row, column=col, padx=5, pady=5, sticky="ew")

        for col in range(cols):
            self.home_buttons_frame.grid_columnconfigure(col, weight=1)

        self.home_status_var.set(f"{len(continents)} regions available")

    def _build_continent_view(self):
        """Build the continent view with country selection and action buttons."""
        # Top bar with continent title and back button
        top = ttk.Frame(self.continent_frame, style="App.TFrame")
        top.pack(fill=tk.X, pady=(0, 10))

        self.continent_title_var = tk.StringVar(value="Continent")
        ttk.Label(
            top,
            textvariable=self.continent_title_var,
            style="PageTitle.TLabel"
        ).pack(side=tk.LEFT)

        ttk.Button(top, text="← All regions", style="Secondary.TButton", command=self.show_home).pack(side=tk.RIGHT)

        # Action card with buttons and country selection
        card = ttk.Frame(self.continent_frame, style="Card.TFrame", padding=22)
        card.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(card, text="Explore this region", style="CardTitle.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 8)
        )

        # Button: Show overall statistics for the continent
        ttk.Button(
            card,
            text="View country distribution",
            command=self.on_show_overall,
            style="Accent.TButton",
        ).grid(row=1, column=0, sticky="w", padx=(0, 10))

        # Country selection dropdown
        self.country_var = tk.StringVar(value="")
        self.country_combo = ttk.Combobox(
            card,
            textvariable=self.country_var,
            state="readonly",
            width=30
        )
        self.country_combo.grid(row=1, column=1, sticky="w", padx=(0, 8))

        # Button: Open detailed view for selected country
        ttk.Button(card, text="Open country", style="Secondary.TButton", command=self.on_open_country).grid(
            row=1, column=2, sticky="w"
        )

        # Help text explaining the two options
        info = "View the regional distribution, or choose a country for a detailed role and experience breakdown."
        ttk.Label(self.continent_frame, text=info, style="Subtitle.TLabel", justify=tk.LEFT, wraplength=720).pack(anchor="w", pady=(16, 0))

    def on_show_overall(self):
        """Load and display overall job count by country for the current continent."""
        if not self.current_continent:
            return
        try:
            # Fetch job counts grouped by country
            df = count_jobs_by_country_in_continent(self.conn, self.current_continent)
            # Fetch individual salary records for statistics
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

    def on_show_remote_jobs(self):
        """Display country distribution and salary statistics for remote jobs."""
        try:
            remote_df = count_remote_jobs_by_country(self.conn)
            salary_df = get_remote_salaries(self.conn)
            self.current_continent = None
            self.show_data_page(
                "Remote jobs",
                remote_df,
                pie_df=remote_df,
                pie_title="Remote jobs by country",
                stats_df=salary_df,
            )
        except Exception as ex:
            messagebox.showerror("Query Error", str(ex))

    def on_open_country(self):
        """Load and display job summary by location, role, and experience for the selected country."""
        country = self.country_var.get().strip()
        if not country:
            messagebox.showwarning("Selection Required", "Pick a country first.")
            return

        try:
            # Fetch detailed job summary for the country
            df = job_summary_by_location_in_country(self.conn, country)
            # Fetch individual salary records for statistics
            stats_df = get_salaries_by_country(self.conn, country)
            self.show_data_page(
                f"{country} - Location/Role/Experience Summary",
                df,
                stats_df=stats_df
            )
        except Exception as ex:
            messagebox.showerror("Query Error", str(ex))

    def back_from_data(self):
        """Return from data view to continent page or home depending on navigation state."""
        if self.current_continent:
            self.show_continent_page(self.current_continent)
        else:
            self.show_home()

    def _render_table(self, df):
        """Populate the table widget with data from a DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame to display. If empty, shows a message.
        """
        # Clear existing rows
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ()

        # Handle empty dataframe
        if df is None or df.empty:
            self.tree["columns"] = ("message",)
            self.tree.heading("message", text="Message")
            self.tree.column("message", width=500, anchor="w")
            self.tree.insert("", tk.END, values=("No data found for this selection.",))
            return

        # Configure columns
        cols = list(df.columns)
        self.tree["columns"] = cols

        for col in cols:
            self.tree.heading(col, text=col)
            width = 160 if col not in {"job_title"} else 240
            self.tree.column(col, width=width, anchor="center")

        # Populate rows from dataframe
        for row in df.itertuples(index=False):
            tag = "even" if len(self.tree.get_children()) % 2 == 0 else "odd"
            self.tree.insert("", tk.END, values=list(row), tags=(tag,))
        self.tree.tag_configure("even", background="#FFFFFF")
        self.tree.tag_configure("odd", background=self.colors["table_alt"])
    
    def _render_pie(self, pie_df=None, pie_title=None):
        """Render a pie chart showing job distribution by location."""
        if self.pie_host is None:
            return

        # Clear previous chart
        for child in self.pie_host.winfo_children():
            child.destroy()

        # Handle missing data
        if pie_df is None or pie_df.empty:
            ttk.Label(
                self.pie_host,
                text="Pie chart is shown for Overall view.",
                style="CardText.TLabel",
                justify=tk.CENTER,
            ).pack(expand=True)
            return

        # Validate required columns
        if "location" not in pie_df.columns or "job_count" not in pie_df.columns:
            ttk.Label(
                self.pie_host,
                text="No pie data available for this view.",
                style="CardText.TLabel",
                justify=tk.CENTER,
            ).pack(expand=True)
            return

        # Generate and display pie chart
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
        """Display salary statistics (average, highest, lowest) in the stats panel."""

        if not hasattr(self, 'stats_frame'):
            return
        
        # Clear previous stats
        for child in self.stats_frame.winfo_children():
            child.destroy()
        
        try:
            # Calculate salary statistics
            stats = get_salary_stats(df)
            avg = stats.get("avg_salary", 0)
            highest = stats.get("highest_pay")
            lowest = stats.get("lowest_pay")
            
            # Create three columns for the stats display
            cols = ttk.Frame(self.stats_frame, style="Card.TFrame")
            cols.pack(fill=tk.X)
            
            # Average salary column
            avg_frame = ttk.Frame(cols, style="Card.TFrame")
            avg_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))
            ttk.Label(avg_frame, text="AVERAGE SALARY", style="CardText.TLabel").pack(anchor="w")
            ttk.Label(avg_frame, text=f"${avg:,.0f}" if avg else "N/A", style="CardTitle.TLabel", font=("Helvetica", 18, "bold")).pack(anchor="w", pady=(4, 0))
            
            # Highest salary column with job context
            high_frame = ttk.Frame(cols, style="Card.TFrame")
            high_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))
            ttk.Label(high_frame, text="HIGHEST SALARY", style="CardText.TLabel").pack(anchor="w")
            if highest:
                salary = highest.get("salary", "N/A")
                title = highest.get("job_title", "")
                exp = highest.get("experience_level", "")
                # Show location context (country for continent view, location for country view)
                context = highest.get("country") or highest.get("location", "")
                detail_parts = [p for p in [context, title, exp] if p]
                detail = " | ".join(detail_parts)
                ttk.Label(high_frame, text=f"${salary:,.0f}" if salary else "N/A", style="CardTitle.TLabel", font=("Helvetica", 18, "bold")).pack(anchor="w", pady=(4, 0))
                ttk.Label(high_frame, text=detail, style="CardText.TLabel", justify=tk.LEFT, wraplength=240).pack(anchor="w", pady=(3, 0))
            else:
                ttk.Label(high_frame, text="N/A").pack()
            
            # Lowest salary column with job context
            low_frame = ttk.Frame(cols, style="Card.TFrame")
            low_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            ttk.Label(low_frame, text="LOWEST SALARY", style="CardText.TLabel").pack(anchor="w")
            if lowest:
                salary = lowest.get("salary", "N/A")
                title = lowest.get("job_title", "")
                exp = lowest.get("experience_level", "")
                # Show location context (country for continent view, location for country view)
                context = lowest.get("country") or lowest.get("location", "")
                detail_parts = [p for p in [context, title, exp] if p]
                detail = " | ".join(detail_parts)
                ttk.Label(low_frame, text=f"${salary:,.0f}" if salary else "N/A", style="CardTitle.TLabel", font=("Helvetica", 18, "bold")).pack(anchor="w", pady=(4, 0))
                ttk.Label(low_frame, text=detail, style="CardText.TLabel", justify=tk.LEFT, wraplength=240).pack(anchor="w", pady=(3, 0))
            else:
                ttk.Label(low_frame, text="N/A").pack()
        except Exception as ex:
            ttk.Label(self.stats_frame, text=f"Error loading stats: {ex}").pack()

    def on_close(self):
        """Clean up database connection and close the application."""
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
