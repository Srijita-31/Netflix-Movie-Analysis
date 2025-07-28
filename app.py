import pandas as pd
from flask import Flask, render_template, request
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)

# Load the datasets from CSV files using pandas
try:
    titles_df = pd.read_csv('data/titles.csv')
    credits_df = pd.read_csv('data/credits.csv')
except FileNotFoundError:
    print("Please make sure 'titles.csv' and 'credits.csv' are in the 'data' folder.")
    exit()

# Pre-process genres
titles_df['genres'] = titles_df['genres'].apply(lambda x: eval(x) if isinstance(x, str) and '[' in x else [x])
all_genres = titles_df.explode('genres')['genres'].dropna().unique()
all_genres.sort()

# Function to get Top 10 Movies by IMDB Score
def get_top_10_movies_imdb():
    top_movies = titles_df[
        (titles_df['imdb_score'] >= 8.0) & (titles_df['type'] == 'MOVIE')
    ].sort_values(by='imdb_score', ascending=False).head(10)
    return top_movies[['title', 'type', 'imdb_score']].to_dict(orient='records')

def get_release_year_trend_plot():
    release_trend_data = titles_df.groupby('release_year').size().reset_index(name='title_count')
    current_year = pd.Timestamp.now().year
    release_trend_data = release_trend_data[
        (release_trend_data['release_year'] >= 1900) & (release_trend_data['release_year'] <= current_year)
    ]
    release_trend_data = release_trend_data.sort_values(by='release_year', ascending=True)

    num_years = len(release_trend_data)
    plot_height = max(600, num_years * 18)

    fig = px.bar(
        release_trend_data,
        y='release_year',
        x='title_count',
        orientation='h',
        title='Total Titles Released Per Year',
        labels={'release_year': 'Release Year', 'title_count': 'Number of Titles'},
        hover_data={'release_year': True, 'title_count': True},
        color_discrete_sequence=['#3b82f6'],
        height=plot_height 
    )

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#edf2f7',
        title_font_color='#3b82f6',
        xaxis_title_font_color='#edf2f7',
        yaxis_title_font_color='#edf2f7',
        xaxis=dict(
            showgrid=False,
            zeroline=True,
            zerolinecolor='#4a5568',
            showline=True,
            linecolor='#4a5568'
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=True,
            zerolinecolor='#4a5568',
            showline=True,
            linecolor='#4a5568',
        ),
        bargap=0.2,
        margin=dict(l=100, r=50, t=80, b=50),
        
        width=900 
    )

    return pio.to_json(fig)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/movies_shows', methods=['GET'])
def movies_shows():
    selected_genre = request.args.get('genre')
    search_query = request.args.get('search_query')

    top_movies_data = get_top_10_movies_imdb()

    filtered_titles_df = titles_df.copy()
    if selected_genre and selected_genre != 'All':
        filtered_titles_df = filtered_titles_df[
            filtered_titles_df['genres'].apply(lambda x: selected_genre in x if isinstance(x, list) else False)
        ]

    if search_query:
        filtered_titles_df = filtered_titles_df[
            filtered_titles_df['title'].str.contains(search_query, case=False, na=False)
        ]

    display_titles = filtered_titles_df[['title', 'type', 'release_year', 'genres', 'imdb_score']].head(50).to_dict(orient='records')

    return render_template(
        'movies_shows.html',
        top_movies=top_movies_data,
        all_genres=all_genres,
        selected_genre=selected_genre,
        search_query=search_query,
        display_titles=display_titles
    )

@app.route('/trends')
def trends():
    release_year_plot_json = get_release_year_trend_plot()
    return render_template(
        'trends.html',
        release_year_plot=release_year_plot_json
    )

if __name__ == '__main__':
    app.run(debug=True)
