import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.request
import os
import ssl
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import toml
import streamlit.components.v1 as components


logo = 'imagenes/spotify.png'
st.set_page_config(page_title="Spotify", page_icon=logo ,layout="wide") #Configuración de la página
#Funciones
@st.cache_data(ttl=3600)
def cargar_datos():
    df = pd.read_csv("spotify_data_cleaned.zip", low_memory=False)
    return df

@st.cache_data(ttl=3600)
# 
def calcular_top_artistas(df, numero_artistas: int)->pd.DataFrame:
    """
    Función para calcular top n artistas de una canción con la media
    mas alta de popularidad.
    
    Args:
    - df (pd.Dataframe): dataframe 
    - numero_artistas(int): numero de artistas a mostrar
    
    Returns:
    - top_n_artists (pd.Dataframe): dataframe filtrado con los artistas
    """
    artist_info = df.groupby('artist_name').agg({
        'popularity': 'mean',
        'genre': 'first'  # Tomar el primer género encontrado para cada artista
    }).reset_index()
    artist_info.rename(columns={'popularity': 'average_popularity'}, inplace=True)
    top_n_artists = artist_info.sort_values(by='average_popularity', ascending=False).head(numero_artistas)
    top_n_artists['genre'] = top_n_artists['genre'].apply(lambda x: x.capitalize())
    return top_n_artists

@st.cache_data(ttl=3600)
def ordenar_por_popularidad(df, top):
    df = df.sort_values(by='popularity', ascending=False).head(top)
    return df

@st.cache_data(ttl=3600)
def artistas_con_mas_canciones(df, numero_artistas: int)->pd.DataFrame:
    """
    Función para calcular los artistas con más canciones en el dataset.

    Args:
    - df (pd.Dataframe): dataframe
    - numero_artistas (int): número de artistas a mostrar

    Returns:
    - top_50_artists (pd.Dataframe): dataframe con los artistas con más canciones
    """
    df_aux = df
    songs_per_artist = df_aux.groupby('artist_name', as_index=False)['track_name'].count()
    songs_per_artist.rename(columns={'track_name': 'song_count'}, inplace=True)
    top_50_artists = songs_per_artist.sort_values(by='song_count', ascending=False).head(numero_artistas)
    return top_50_artists

@st.cache_data(ttl=3600)
def cargar_html(ruta_archivo):
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        html_content = f.read()
    return html_content

def clean_outliers(df_aux, columns: list)->pd.DataFrame:
    """
    Función para eliminar los outliers de un dataframe usando el rango intercuartílico.
    
    Args:
    - df_aux (pd.Dataframe): dataframe a limpiar
    - columns(list): lista de columnas a limpiar
    
    Returns:
    - df_aux (pd.Dataframe): dataframe sin outliers
    """
    for column in columns:
        Q1 = df_aux[column].quantile(0.25)
        Q3 = df_aux[column].quantile(0.75)
        IQR = Q3 - Q1
        df_aux = df_aux[(df_aux[column] >= Q1-1.5*IQR) & (df_aux[column] <= Q3 + 1.5*IQR)]
    return df_aux

df = cargar_datos()

# Centrar el título de la página
st.markdown(
    """
    <style>
    .title {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Título de la página
st.markdown("<h1 class='title'>Análisis de canciones en Spotify</h1>", unsafe_allow_html=True)
st.divider()

# Icono de Spotify
st.sidebar.markdown("""
    <img src="https://cdn.icon-icons.com/icons2/3041/PNG/512/spotify_logo_icon_189218.png" 
         style="display: block; margin-left: auto; margin-right: auto; width: 75%;" 
         alt="logo spotify">
    """, unsafe_allow_html=True)

st.sidebar.title("Secciones")
pestaña = st.sidebar.radio("Selecciona una opción:", ("Inicio", "Distribución variables", "Popularidad", "Características de la canción", "Informe", "Predicción de popularidad"))

if pestaña == "Inicio":
    cols = st.columns(2)
    with cols[0]:
        st.markdown("#####", unsafe_allow_html=True)
        # Descripción del proyecto
        st.markdown("""
        En este estudio descubriremos cómo crear un nuevo hit ayudándonos de los parámetros que utiliza spotify para clasificar sus canciones.

        ### Objetivo
        - Analizar las características de las canciones en Spotify.
        - Identificar las características que hacen que una canción sea popular.
        - Poder crear un hit utilizando las características analizadas.
        - **Fuente de datos:** [Kaggle](https://www.kaggle.com/ziriantahirli/million-song-data-analysis-2)
        
        
        ### Secciones
        - **Distribución de Variables:** Visualizar la distribución de las características principales de las canciones.
        - **Popularidad:** Explorar qué artistas y canciones son los más populares, junto con diversas métricas de popularidad.
        - **Características de la Canción:** Analizar las características específicas de las canciones, como volumen, tempo, y más.
        - **Informe:** Acceder a un informe interactivo detallado generado con Power BI.
        - **Predicción de Popularidad:** Predecir la popularidad de una canción en base a sus características.
    """)
    with cols[1]:
        st.image('imagenes/inicio.png', caption="eyeofthehurricane.news",)

elif pestaña == "Distribución variables":
    tabsInicio = st.tabs(["Variables continuas", "Correlación de Spearman"])
    with tabsInicio[0]:
        # Distribución de las variables continuas
        st.image('imagenes/distribucion.png')
    with tabsInicio[1]:
        # Correlación de Spearman
        st.image('imagenes/spearman.png')

elif pestaña == "Popularidad":
    st.sidebar.divider()
    st.sidebar.markdown("### Configuración")
    # Número de artistas y canciones a mostrar en las gráficas interactivas
    numero_artistas = st.sidebar.slider("Número de artistas", 1, 50, 10, key="artistas")
    numero_canciones = st.sidebar.slider("Número de canciones", 1, 50, 10, key="canciones")

    tabsPopularidad = st.tabs([f"Top Artistas y Canciones", "Bailable", "Género", "Energía", "Positividad"])
    with tabsPopularidad[0]:
        # Gráfica top n artistas con la media más alta de popularidad
        top_n_artists = calcular_top_artistas(df, numero_artistas)
        fig = px.treemap(top_n_artists,  
                        path=['artist_name'], 
                        values='average_popularity',
                        color='average_popularity', 
                        color_continuous_scale='RdYlGn',
                        title=f'Top {numero_artistas} Artistas con la media más alta de popularidad',
                        custom_data=['genre'],
                        labels={'average_popularity': 'Popularidad Media', 'artist_name': 'Artista', 'genre': 'Género'})
        fig.update_traces(hovertemplate='Artista: %{label}<br>Popularidad Media: %{value:.2f}<br>Género(s): %{customdata[0]}')
        st.plotly_chart(fig)

        cols = st.columns(2)
        with cols[0]:
            # Media de la popularidad en base al modo
            st.image('imagenes/modopopularidad.png')
        with cols[1]:
            # Media de la popularidad en base a la escala de la canción
            st.image('imagenes/escalapopularidad.png')

        # Grafica top canciones más populares y su camino hacia la popularidad
        df_aux = ordenar_por_popularidad(df, numero_canciones)
        fig = px.parallel_categories(df_aux
                                    ,dimensions=['genre', 'key', 'mode', 'popularity']
                                    ,color="popularity"
                                    ,color_continuous_scale=px.colors.sequential.Agsunset
                                    ,title=f'Top {numero_canciones} canciones y su camino hacia la popularidad'
                                    ,labels={"genre": "Género", "key": "Key", "mode": "Modo", "popularity": "Popularidad"})
        st.plotly_chart(fig)
    with tabsPopularidad[1]:
        # Grafica canciones más populares y su bailabilidad
        df_aux = ordenar_por_popularidad(df, numero_canciones)
        fig = px.area(df_aux, x='track_name', y='danceability', title=f'Top {numero_canciones} canciones con mayor popularidad y su bailabilidad'
                , hover_data=["artist_name", "popularity"], labels={"danceability": "Bailabilidad", "track_name": "Canción", "artist_name": "Artista", "popularity": "Popularidad"}
                , markers=True)
        st.plotly_chart(fig)
    with tabsPopularidad[2]:
        # Histograma de popularidad media por género y año
        html_content = cargar_html("html/popularidadgeneros.html")
        components.html(html_content, height=700)
    with tabsPopularidad[3]:
        # Histograma de la energía media en base a la popularidad segun el año
        html_content = cargar_html("html/energiapopularidad.html")
        components.html(html_content, height=700)
    with tabsPopularidad[4]:
        # Histograma de la positividad media en base a la popularidad segun el año
        html_content = cargar_html("html/positividadpopularidad.html")
        components.html(html_content, height=700)
elif pestaña == "Características de la canción":
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Configuración")
    # Número de artistas a mostrar en la gráfica
    numero_artistas = st.sidebar.slider("Número de artistas", 1, 50, 10, key="artistas")
    tabsCaracteristicas = st.tabs(["Artistas", "Volumen", "Tempo"])
    with tabsCaracteristicas[0]:
        # Grafico artistas con mas canciones
        top_50_artists = artistas_con_mas_canciones(df, numero_artistas)

        fig = px.treemap(top_50_artists, 
                        path=['artist_name'], 
                        values='song_count',
                        color='song_count', 
                        color_continuous_scale='RdYlGn',
                        title=f'Top {numero_artistas} artistas con más canciones',
                        labels={'song_count': 'Total Canciones'})
        fig.update_traces(hovertemplate='Artista: %{label}<br>Número de Canciones: %{value}')
        st.plotly_chart(fig)
    with tabsCaracteristicas[1]:
        # Histograma del volumen con la energía promedio
        with open("html/volumenenergia.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        components.html(html_content, height=700)

    with tabsCaracteristicas[2]:
        # Histograma bailabilidad en base al tempo de las canciones
        html_content = cargar_html("html/tempobailable.html")
        components.html(html_content, height=500)
        st.image('imagenes/tempobailable.png')  
elif pestaña == "Informe":
    # Informe Power BI
    codigo_iframe = '''<iframe title="spotify" width="1320" height="700"
    src="https://app.powerbi.com/view?r=eyJrIjoiMTk5Njg1NjYtYWI5OS00OTg4LTg4OGYtOTE4ZGM3OTFlNWUzIiwidCI6IjhhZWJkZGI2LTM0MTgtNDNhMS1hMjU1LWI5NjQxODZlY2M2NCIsImMiOjl9"
    frameborder="0" allowFullScreen="true"></iframe>'''
    components.html(codigo_iframe, width=1320, height=1250)
elif pestaña == "Predicción de popularidad":
    st.sidebar.divider()
    st.markdown("### Predicción de la popularidad")
    with st.form(key="form"):
        cols = st.columns(3)
        # Sliders de las características de la canción para predecir la popularidad
        with cols[0]:
            energy = st.slider("Energía", 0.0, 1.0, 0.5, 0.01, key="energy")
            danceability = st.slider("Bailabilidad", 0.0, 1.0, 0.5, 0.01, key="danceability")
            valence = st.slider("Positividad", 0.0, 1.0, 0.5, 0.01, key="valence")
        with cols[2]:
            instrumentalness = st.slider("Instrumentalidad", 0.0, 1.0, 0.5, 0.01, key="instrumentalness")
            acousticness = st.slider("Acústica", 0.0, 1.0, 0.5, 0.01, key="acousticness")
            tempo = st.slider("Tempo", 0.0, 250.0, 120.0, 0.01, key="tempo")
        with cols[1]:
            loudness = st.slider("Volumen", -60.0, 0.0, -20.0, 0.01, key="loudness")
            speechiness = st.slider("Discurso", 0.0, 1.0, 0.5, 0.01, key="speechiness")
            # Cambiamos el color del botón
            m = st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: rgb(29, 185, 84);
                margin-top: 10px;
            }
            </style>""", unsafe_allow_html=True)
            # Botón para predecir la popularidad de la canción
            b = st.form_submit_button("Predecir", use_container_width=True)
            if b:
                # Código para predecir la popularidad de la canción realizando un modelo de despliegue en Azure Machine Learning
                def allowSelfSignedHttps(allowed):
                    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
                        ssl._create_default_https_context = ssl._create_unverified_context

                allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

                data =  {
                "input_data": {
                    "columns": [
                        "danceability",
                        "energy",
                        "loudness",
                        "speechiness",
                        "acousticness",
                        "instrumentalness",
                        "valence",
                        "tempo"
                        ],
                    "index": [0],
                    "data": [[danceability, energy, loudness, speechiness, acousticness, instrumentalness, valence, tempo]]
                }
                }

                body = str.encode(json.dumps(data))

                url = st.secrets['azure']['url']
                # Replace this with the primary/secondary key, AMLToken, or Microsoft Entra ID token for the endpoint
                api_key = st.secrets['azure']['api_key']
                if not api_key:
                    raise Exception("A key should be provided to invoke the endpoint")

                # The azureml-model-deployment header will force the request to go to a specific deployment.
                # Remove this header to have the request observe the endpoint traffic rules
                headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': 'spotifyfinal40-1' }

                req = urllib.request.Request(url, body, headers)

                try:
                    response = urllib.request.urlopen(req)

                    result = json.loads(response.read())
                    color = "#1DB954" 
                    if result[0] == 'Baja popularidad':
                        color = "#e81434"

                    st.markdown(f"""
                    <div style='text-align: center; font-size: 20px; margin: 20px 0;'>
                        <h3>Esta canción tendría una <h3 style='color:{color}'>{result[0].lower()}</h3></h3>
                    </div>
                    """, unsafe_allow_html=True)
                except urllib.error.HTTPError as error:
                    print("The request failed with status code: " + str(error.code))
                    print(error.info())
                    print(error.read().decode("utf8", 'ignore'))
    # Usamos las credenciales de cliente para acceder a la API de Spotify
    auth_manager=SpotifyClientCredentials(client_id=st.secrets["spotify"]["client_id"], client_secret=st.secrets["spotify"]["client_secret"], requests_session=True)
    # Creamos un objeto de la clase Spotify usando las credenciales anteriores
    sp = spotipy.Spotify(auth_manager=auth_manager)

    # Cambiamos el color de los multiselect
    st.markdown("""
    <style>        
    
    [data-baseweb="tag"] {
    background-color: #1DB954;
    color: white;
    }            
    </style>
    """, unsafe_allow_html=True)

    # Multiselect para seleccionar los géneros y hacemos una petición a la API de Spotify para obtener los géneros disponibles
    genres = st.multiselect("Selecciona de uno a tres géneros para obtener canciones similares ", sp.recommendation_genre_seeds()["genres"], max_selections=3)
    parameters_list= ["danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "valence", "tempo"]
    st.sidebar.markdown("### Parámetros")
    # Multiselect para seleccionar los parámetros de la canción
    parameters = st.sidebar.multiselect("Seleccione de uno a tres parámetros", parameters_list, max_selections=3)

    if genres:
        # Parámetros para obtener recomendaciones de canciones similares, lo iremos actualizando con los parámetros seleccionados
        args_recomendaciones = {
            "seed_genres": genres, 
            "limit": 4
        }
        
        for parameter in parameters:
            match parameter:
                case "danceability":
                    args_recomendaciones.update({
                        "min_danceability": danceability-0.05, 
                        "max_danceability": danceability+0.05, 
                        "target_danceability": danceability
                    })
                case "energy":
                    args_recomendaciones.update({
                        "min_energy": energy-0.05, 
                        "max_energy": energy+0.05, 
                        "target_energy": energy
                    })
                case "loudness":
                    args_recomendaciones.update({
                        "min_loudness": loudness-5, 
                        "max_loudness": loudness+5, 
                        "target_loudness": loudness
                    })
                case "speechiness":
                    args_recomendaciones.update({
                        "min_speechiness": speechiness-0.05, 
                        "max_speechiness": speechiness+0.05, 
                        "target_speechiness": speechiness
                    })
                case "acousticness":
                    args_recomendaciones.update({
                        "min_acousticness": acousticness-0.05, 
                        "max_acousticness": acousticness+0.05, 
                        "target_acousticness": acousticness
                    })
                case "instrumentalness":
                    args_recomendaciones.update({
                        "min_instrumentalness": instrumentalness-0.05, 
                        "max_instrumentalness": instrumentalness+0.05, 
                        "target_instrumentalness": instrumentalness
                    })
                case "valence":
                    args_recomendaciones.update({
                        "min_valence": valence-0.05, 
                        "max_valence": valence+0.05, 
                        "target_valence": valence
                    })
                case "tempo":
                    args_recomendaciones.update({
                        "min_tempo": tempo-10, 
                        "max_tempo": tempo+10, 
                        "target_tempo": tempo
                    })
        # Obtenemos las recomendaciones de canciones similares haciendo una petición a la API de Spotify        
        results = sp.recommendations(**args_recomendaciones)

        # Mostramos las recomendaciones de canciones similares recorriendo results
        cols = st.columns(4)
        for i in range(len(results["tracks"])):
            with cols[i]:
                # Obtenemos la URL de Spotify
                spotify_url = results["tracks"][i]["external_urls"]["spotify"]
                if spotify_url:
                    if 'track' in spotify_url:
                        # Obtenemos el ID de la canción
                        track_id = spotify_url.split('/')[-1].split('?')[0]
                        # Le pasamos el ID de la canción a la URL de Spotify para obtener el embed
                        embed_url = f"https://open.spotify.com/embed/track/{track_id}"
                    else:
                        embed_url = None

                    if embed_url:
                        components.iframe(embed_url, width=300, height=380)
                    else:
                        st.write("La URL proporcionada no es válida. Asegúrate de que sea una URL de pista o lista de reproducción de Spotify.")