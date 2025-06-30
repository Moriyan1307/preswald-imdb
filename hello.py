import pandas as pd
import plotly.express as px
import preswald
from preswald import get_df, table , query ,connect


data = get_df("imdb")

sql = "SELECT * FROM imdb WHERE IMDB_Rating > 8.5 AND Released_Year >= 2000"
filtered_df = query(sql, "imdb")

# Convert types
data["IMDB_Rating"] = pd.to_numeric(data["IMDB_Rating"], errors='coerce')
data["Released_Year"] = pd.to_numeric(data["Released_Year"], errors='coerce')
data["Runtime"] = data["Runtime"].astype(str).str.replace(" min", "", regex=False)
data["Runtime"] = pd.to_numeric(data["Runtime"], errors='coerce')

data["Gross_Clean"] = (
    data["Gross"]
    .astype(str)
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .str.replace("nan", "", regex=False)
)
data["Gross_Clean"] = pd.to_numeric(data["Gross_Clean"], errors='coerce')

# Filter for meaningful data
data = data.dropna(subset=["IMDB_Rating", "Released_Year", "Runtime", "Genre"])


# Top 20 rated movies
top_rated = data.sort_values("IMDB_Rating", ascending=False).head(20)
fig_top_rated = px.bar(
    top_rated,
    x="Series_Title",
    y="IMDB_Rating",
    hover_data=["Released_Year", "Genre", "Director"],
    title="Top 20 IMDb Rated Movies",
    color="IMDB_Rating"
)
fig_top_rated.update_layout(xaxis_tickangle=-45)

# Genre distribution (top 10)
genre_series = data["Genre"].str.split(", ").explode()
genre_counts = genre_series.value_counts().reset_index()
genre_counts.columns = ["Genre", "Count"]
fig_genre_dist = px.pie(
    genre_counts.head(10),
    values="Count",
    names="Genre",
    title="Top 10 Genres Distribution"
)

# Ratings over years
ratings_year = (
    data[data["Released_Year"].between(1950, 2025)]
    .groupby("Released_Year")["IMDB_Rating"]
    .mean()
    .reset_index()
)
fig_ratings_year = px.line(
    ratings_year,
    x="Released_Year",
    y="IMDB_Rating",
    title="Average IMDb Rating Over Years",
    markers=True
)

# Runtime vs IMDb Rating
fig_runtime_rating = px.scatter(
    data,
    x="Runtime",
    y="IMDB_Rating",
    color=data["Genre"].str.split(", ").str[0],
    hover_data=["Series_Title", "Released_Year", "Director"],
    title="Runtime vs IMDb Rating",
)

# Top directors
top_directors = data["Director"].value_counts().head(15).reset_index()
top_directors.columns = ["Director", "Movie_Count"]
fig_top_directors = px.bar(
    top_directors,
    x="Director",
    y="Movie_Count",
    title="Top Directors by Number of Movies",
    color="Movie_Count"
)
fig_top_directors.update_layout(xaxis_tickangle=-45)

# Gross earnings vs rating
gross_data = data.dropna(subset=["Gross_Clean"])
fig_gross_rating = px.scatter(
    gross_data,
    x="Gross_Clean",
    y="IMDB_Rating",
    hover_data=["Series_Title", "Director", "Released_Year"],
    title="Gross Earnings vs IMDb Rating",
    log_x=True,
    color="IMDB_Rating"
)


director_heat = (
    data.groupby("Director")["IMDB_Rating"]
    .mean()
    .reset_index()
    .sort_values(by="IMDB_Rating", ascending=False)
    .head(20)
)
fig_director_heat = px.bar(
    director_heat,
    x="Director",
    y="IMDB_Rating",
    title="Top 20 Directors by Average IMDb Rating",
    color="IMDB_Rating"
)
fig_director_heat.update_layout(xaxis_tickangle=-45)


genre_exploded = data.copy()
genre_exploded["Primary_Genre"] = genre_exploded["Genre"].astype(str).str.split(", ").str[0]
genre_rating = genre_exploded.groupby("Primary_Genre")["IMDB_Rating"].mean().reset_index()
genre_rating = genre_rating.sort_values(by="IMDB_Rating", ascending=False)


# Display all charts
preswald.text("# 🎬 IMDb Top 1000 Movies: Data Dashboard")

preswald.text("## 🏆 Top Rated Movies")
preswald.plotly(fig_top_rated)

preswald.text("## 🎯 Top Directors by Average IMDb Rating")
preswald.plotly(fig_director_heat)


preswald.text("## 🎭 Genre Distribution")
preswald.plotly(fig_genre_dist)

preswald.text("## 📈 Rating Trends by Year")
preswald.plotly(fig_ratings_year)

preswald.text("## ⏱ Runtime vs Rating")
preswald.plotly(fig_runtime_rating)

preswald.text("## 🎬 Most Prolific Directors")
preswald.plotly(fig_top_directors)

preswald.text("## 💰 Gross Earnings vs Rating")
preswald.plotly(fig_gross_rating)
