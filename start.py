import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from utils import remove_duplicates, update_database, get_query_by_label
from matplotlib.backends.backend_pdf import PdfPages

# Load CSV data
DF_PATH = "datascience_salaries.csv"
DB_PATH = "salaries.db"
REPORT_PATH = "salary_report.pdf"


df = pd.read_csv(DF_PATH)
conn = sqlite3.connect(DB_PATH)

# Clean duplicates and persist to SQLite
clean_df = remove_duplicates(df)
update_database(clean_df, conn, "salaries")

# ----------------------- query data -----------------------

# Jobs by country and continent
country_df = pd.read_sql_query(
	get_query_by_label("queries.sql", "jobs based on country"), conn
)
continent_df = pd.read_sql_query(
	get_query_by_label("queries.sql", "jobs based on continent"), conn
)

# Experience distributions and salary summaries
experience_df = pd.read_sql_query(
	get_query_by_label(
		"queries.sql", "experience level distribution  grouped by country then experience level"
	),
	conn,
)
average_pay_df = pd.read_sql_query(
	get_query_by_label("queries.sql", "average pay by job based on experience level"), conn
)

job_salary_count_df = pd.read_sql_query(
	get_query_by_label(
		"queries.sql", "count of job salary based on experience level and job title"
	),
	conn,
)

max_salary_exp_df = pd.read_sql_query(
	get_query_by_label(
		"queries.sql", "max salary by job title and experience level"
	),
	conn,
)
if "maximum_salary" in max_salary_exp_df.columns:
	max_salary_exp_df["maximum_salary"] = max_salary_exp_df["maximum_salary"].map(
		lambda x: f"{x:.2f}"
	)

min_salary_df = pd.read_sql_query(
	get_query_by_label("queries.sql", "min salary by job title"), conn
)
if "minimum_salary" in min_salary_df.columns:
	min_salary_df["minimum_salary"] = min_salary_df["minimum_salary"].map(
		lambda x: f"{x:.2f}"
	)

avg_salary_exp_df = pd.read_sql_query(
	get_query_by_label(
		"queries.sql", "average salary by job title and experience level"
	),
	conn,
)
if "average_salary" in avg_salary_exp_df.columns:
	avg_salary_exp_df["average_salary"] = avg_salary_exp_df["average_salary"].map(
		lambda x: f"{x:.2f}"
	)

# Salary differences between experience levels
entry_diff = average_pay_df.pivot(
	index="job_title", columns="experience_level", values="average_salary"
)
entry_diff["Mid_vs_Entry"] = entry_diff["Mid"] - entry_diff["Entry"]
entry_diff["Growth_%"] = entry_diff["Mid_vs_Entry"] / entry_diff["Entry"] * 100
entry_diff["Mid_vs_Entry"] = entry_diff["Mid_vs_Entry"].map(lambda x: f"{x:.2f}")
entry_diff["Growth_%"] = entry_diff["Growth_%"].map(lambda x: f"{x:.2f}%")

mid_diff = average_pay_df.pivot(
	index="job_title", columns="experience_level", values="average_salary"
)
mid_diff["Senior_vs_Mid"] = mid_diff["Senior"] - mid_diff["Mid"]
mid_diff["Growth_%"] = mid_diff["Senior_vs_Mid"] / mid_diff["Mid"] * 100
mid_diff["Senior_vs_Mid"] = mid_diff["Senior_vs_Mid"].map(lambda x: f"{x:.2f}")
mid_diff["Growth_%"] = mid_diff["Growth_%"].map(lambda x: f"{x:.2f}%")

# Location-specific queries
jobs_by_location_query = get_query_by_label(
	"queries.sql", "jobs based on a specific location"
)
info_by_location_query = get_query_by_label(
	"queries.sql", "job information based on specific location"
)

job_in_australia = pd.read_sql_query(
	jobs_by_location_query, conn, params=("Australia", None, None)
)
info_australia = pd.read_sql_query(info_by_location_query, conn, params=("Australia",))

job_in_africa = pd.read_sql_query(
	jobs_by_location_query, conn, params=("Africa", None, None)
)
info_africa = pd.read_sql_query(info_by_location_query, conn, params=("Africa",))

# ------------------------ generate pdf report -----------------------

with PdfPages(REPORT_PATH) as pdf:
	# Cover page
	cover = plt.figure(figsize=(11.69, 8.27))
	plt.axis("off")
	plt.text(0.5, 0.6, "Data Science Salary Report", fontsize=30, ha="center")
	plt.text(
		0.5,
		0.4,
		"Generated using Data Science Salaries Dataset",
		fontsize=16,
		ha="center",
	)
	pdf.savefig(cover)
	plt.close()

	# Intro text page
	fig, ax = plt.subplots(figsize=(8.5, 11))
	ax.axis("off")
	ax.text(
		0.03,
		0.5,
		"This report provides only graphs and charts to better visualize the data and does not include any raw data tables. "
		"The findings come from the Data Science Salaries dataset found on Kaggle. The dataset includes salaries for various data science roles across different countries and experience levels. "
		"The report highlights key insights such as salary distributions, average salaries by job title and experience level, and differences in pay between experience levels.",
		ha="left",
		va="top",
		fontsize=20,
		color="black",
		wrap=True,
	)
	fig.tight_layout(pad=2.0)
	pdf.savefig(fig)
	plt.close(fig)

	# Transition page
	fig, ax = plt.subplots(figsize=(8.5, 5))
	ax.axis("off")
	ax.text(
		0.03,
		0.5,
		"The following pages will contain various graphs and charts that will show various insights derived from the dataset overall, insights regarding regions and locations will follow.",
		ha="left",
		va="top",
		fontsize=16,
		color="black",
		wrap=True,
	)
	fig.tight_layout(pad=2.0)
	pdf.savefig(fig)
	plt.close(fig)

	# Bar graph: job distribution by continent
	fig, ax = plt.subplots(figsize=(8.5, 5))
	continents = continent_df["continent"]
	counts = continent_df["count"]
	bars = ax.bar(continents, counts, color="skyblue")
	ax.set_title("Job Distribution by Continent", fontsize=18)
	ax.set_xlabel("Continent", fontsize=14)
	ax.set_ylabel("Number of Jobs", fontsize=14)
	ax.tick_params(axis="x", rotation=0)
	ax.set_position([0.1, 0.1, 0.8, 0.8])
	for bar in bars:
		height = bar.get_height()
		ax.annotate(
			f"{height}",
			xy=(bar.get_x() + bar.get_width() / 2, height),
			xytext=(0, 3),
			textcoords="offset points",
			ha="center",
			va="bottom",
			fontsize=12,
			color="black",
		)
	fig.tight_layout(pad=1.0)
	pdf.savefig(fig)
	plt.close(fig)

	# Max/min salary tables
	plt.figure(figsize=(8.5, 11))
	plt.axis("off")
	plt.text(0.5, 1.03, "Max Salary by Job Title", ha="center", va="top", fontsize=16)
	plt.table(
		cellText=max_salary_exp_df.values,
		colLabels=max_salary_exp_df.columns,
		cellLoc="center",
		loc="upper center",
	)
	plt.text(0.5, 0.45, "Min Salary by Job Title", ha="center", va="top", fontsize=16)
	plt.table(
		cellText=min_salary_df.values,
		colLabels=min_salary_df.columns,
		cellLoc="center",
		loc="lower center",
	)
	pdf.savefig()
	plt.close()

	# Average salary by job title and experience level
	plt.figure(figsize=(8.5, 11))
	plt.axis("off")
	plt.text(
		0.5,
		1.03,
		"Average Salary by Job Title and Experience Level",
		ha="center",
		va="top",
		fontsize=16,
	)
	plt.table(
		cellText=avg_salary_exp_df.values,
		colLabels=avg_salary_exp_df.columns,
		cellLoc="center",
		loc="upper center",
	)
	plt.text(
		0.5,
		0.57,
		"*The average salary for entry and executive level Big Data, executive level for data scientist are not as accurate as other salaries given that the number of entries for these entries is lower.",
		ha="center",
		va="top",
		fontsize=8,
	)
	pdf.savefig()
	plt.close()

	# Difference in pay between experience levels for each job title
	plt.figure(figsize=(8.5, 11))
	plt.axis("off")
	plt.text(
		0.5,
		1.03,
		"Difference in Pay Between Experience Levels for Each Job Title",
		ha="center",
		va="top",
		fontsize=16,
	)

	table = plt.table(
		cellText=entry_diff[["Mid_vs_Entry", "Growth_%"]].reset_index().values,
		colLabels=["Job Title", "Mid vs Entry ($)", "Growth (%)"],
		cellLoc="center",
		loc="upper center",
	)
	for row in range(1, len(mid_diff) + 1):
		table[(row, 2)].set_facecolor("#1bd76c")

	plt.text(
		0.5,
		0.8,
		"The job with the biggest jump between entry and mid level is:\n Data analyst with a 88.37% increase followed by Big Data with a 43.817% increase in average salary",
		ha="center",
		va="center",
		fontsize=16,
	)

	table = plt.table(
		cellText=mid_diff[["Senior_vs_Mid", "Growth_%"]].reset_index().values,
		colLabels=["Job Title", "Senior vs Mid ($)", "Growth (%)"],
		cellLoc="center",
		loc="center",
	)
	for row in range(1, len(mid_diff) + 1):
		table[(row, 2)].set_facecolor("#1bd76c")

	plt.text(
		0.5,
		0.4,
		"The job with the biggest jump between mid and senior level is:\n Data Scientist followed with a 72.45% increase in average salary followed by ML Ops with a 66.53% increase",
		ha="center",
		va="center",
		fontsize=16,
	)
	pdf.savefig()
	plt.close()

	# Australia section
	fig, ax = plt.subplots(figsize=(8, 11))
	ax.axis("off")
	ax.text(
		0.5,
		0.95,
		"The following charts and graphs show the distribution of jobs in Australia and other insights.",
		ha="center",
		va="top",
		fontsize=10,
		wrap=True,
	)
	pdf.savefig(fig)
	plt.close(fig)

	if job_in_australia.empty:
		fig, ax = plt.subplots(figsize=(8.5, 3))
		ax.axis("equal")
		ax.text(
			0.5,
			0.5,
			"No Australia records were found in the dataset.",
			ha="center",
			va="center",
			fontsize=12,
		)
		pdf.savefig(fig)
		plt.close(fig)
	else:
		fig, ax = plt.subplots(figsize=(10, 5))
		ax.set_title("Job Distribution in Australia", fontsize=14, pad = 20)
		locations = job_in_australia["location"]
		counts = job_in_australia["job_count"]
		ax.pie(counts, labels=locations, autopct="%1.1f%%", startangle=140)
		pdf.savefig(fig)
		plt.close(fig)

		fig, ax = plt.subplots(figsize=(8.5, 11))
		ax.axis("off")
		ax.text(0.5, 0.95, "Information about Jobs in Australia", ha="center", va="top", fontsize=14)
		ax.table(
			cellText=info_australia.values,
			colLabels=info_australia.columns,
			cellLoc="center",
			loc="center",
		)
		total_jobs = int(job_in_australia["job_count"].sum())
		sydney_jobs_series = job_in_australia.loc[
			job_in_australia["location"] == "Sydney", "job_count"
		]
		sydney_jobs = int(sydney_jobs_series.iloc[0]) if not sydney_jobs_series.empty else 0
		ax.text(
			0.5,
			0.35,
			f"There are a total of {total_jobs} jobs with 3 having undisclosed locations. "
			f"Sydney has the highest number of jobs with {sydney_jobs}.",
			ha="center",
			va="top",
			fontsize=10,
			wrap=True,
		)
		pdf.savefig(fig)
		plt.close(fig)

	# Africa section
	fig, ax = plt.subplots(figsize=(8, 11))
	ax.axis("off")
	ax.text(
		0.5,
		0.95,
		"The following charts and graphs show the distribution of jobs in Africa and other insights.",
		ha="center",
		va="top",
		fontsize=10,
		wrap=True,
	)
	pdf.savefig(fig)
	plt.close(fig)

	if job_in_africa.empty:
		fig, ax = plt.subplots(figsize=(5, 3))
		ax.axis("equal")
		ax.text(
			0.5,
			0.5,
			"No Africa records were found in the dataset.",
			ha="center",
			va="center",
			fontsize=12,
		)
		pdf.savefig(fig)
		plt.close(fig)
	else:
		fig, ax = plt.subplots(figsize=(10, 5))
		ax.set_title("Job Distribution in Africa", fontsize=14, pad = 20)
		locations = job_in_africa["location"]
		counts = job_in_africa["job_count"]
		ax.pie(counts, labels=locations, autopct="%1.1f%%", startangle=140)
		pdf.savefig(fig)
		plt.close(fig)

		if info_africa.empty:
			fig, ax = plt.subplots(figsize=(8.5, 3))
			ax.axis("equal")
			ax.text(
				0.5,
				0.5,
				"No detailed Africa records were found in the dataset.",
				ha="center",
				va="center",
				fontsize=12,
			)
			pdf.savefig(fig)
			plt.close(fig)
		else:
			fig, ax = plt.subplots(figsize=(8.5, 11))
			ax.axis("off")
			ax.text(0.5, 0.95, "Information about Jobs in Africa", ha="center", va="top", fontsize=14)
			ax.table(
				cellText=info_africa.values,
				colLabels=info_africa.columns,
				cellLoc="center",
				loc="center",
			)
			pdf.savefig(fig)
			plt.close(fig)

conn.close()

