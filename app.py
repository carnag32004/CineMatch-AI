import pickle
import requests
import streamlit as st
from recommender import get_recommendations

OMDB_API_KEY = 'd6789371'
PLACEHOLDER_POSTER = 'https://via.placeholder.com/500x750?text=No+Poster'

st.set_page_config(page_title='CineMatch AI', page_icon='🎬', layout='wide')
st.title('🎬 CineMatch AI')
st.caption('Content-based movie recommendation engine')


@st.cache_resource
def load_movies():
  return pickle.load(open('movies.pkl', 'rb'))


movies = load_movies()


def format_fallback_actors(actors_str):
  if not isinstance(actors_str, str) or not actors_str.strip():
    return 'N/A'
  words = actors_str.split()
  names = [' '.join(words[i : i + 2]) for i in range(0, min(len(words), 8), 2)]
  return ', '.join(names)


@st.cache_data(show_spinner=False)
def fetch_movie_details(title, fallback_actors=''):
  try:
    url = f'http://www.omdbapi.com/?t={requests.utils.quote(title)}&apikey={OMDB_API_KEY}'
    data = requests.get(url, timeout=5).json()
    if data.get('Response') == 'True':
      poster = data.get('Poster')
      omdb_actors = data.get('Actors')
      return {
          'poster': (
              poster if poster and poster != 'N/A' else PLACEHOLDER_POSTER
          ),
          'year': data.get('Year', 'N/A'),
          'rating': data.get('imdbRating', 'N/A'),
          'actors': (
              omdb_actors
              if omdb_actors and omdb_actors != 'N/A'
              else format_fallback_actors(fallback_actors)
          ),
          'plot': data.get('Plot', 'No plot summary available.'),
      }
  except Exception:
    pass
  return {
      'poster': PLACEHOLDER_POSTER,
      'year': 'N/A',
      'rating': 'N/A',
      'actors': format_fallback_actors(fallback_actors),
      'plot': 'No plot summary available.',
  }


selected_movie = st.selectbox(
    'Select or type a movie you like:', movies['title'].values
)

if st.button('Recommend', type='primary'):
  with st.spinner('Finding best matches...'):
    results = get_recommendations(selected_movie)

  if isinstance(results, str):
    st.warning(results)
  else:
    cols = st.columns(5)
    for idx, (_, row) in enumerate(results.iterrows()):
      raw_actors = row['actors'] if 'actors' in row else ''
      details = fetch_movie_details(row['title'], raw_actors)

      with cols[idx]:
        st.image(details['poster'], use_container_width=True)
        st.subheader(row['title'])
        st.caption(f"⭐ {details['rating']}  |  📅 {details['year']}")
        st.caption(f"Cast: {details['actors']}")
        with st.expander('Plot'):
          st.write(details['plot'])