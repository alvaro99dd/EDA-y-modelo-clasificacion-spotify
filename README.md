# EDA y modelo clasificacion Spotify
![Alt text](https://haulixdaily.com/wp-content/uploads/2019/12/Screen-Shot-2019-12-12-at-12.34.54-PM.png "haulixdaily.com")
En este proyecto hemos hecho un análisis sobre una muestra de más de 1 millón de canciones de spotify. Entrenando además a un modelo de clasificación, para que prediga la popularidad de una canción según ciertos parámetros.

### Descripción del proyecto
Utilizando el siguiente [dataset](https://www.kaggle.com/datasets/ziriantahirli/million-song-data-analysis-2) de Kaggle, hemos realizado preprocesamiento, EDA y modelo predictivo para averiguar si una futura canción podría ser o no un "hit". En esta [aplicación](https://spotifyanalytics.streamlit.app/) se puede ver todo el proceso realizado. Se han analizado las distintas métricas con las que la plataforma de Spotify clasifica a las canciones.
Además del modelo de machine learning, se ha trabajado con la API de Spotify para realizar recomendar cuatro canciones según los parámetros que el usuario indique y uno o varios géneros musicales.

### Las métricas
![Alt text](https://miro.medium.com/v2/resize:fit:1200/1*11PPfOeamPrWUeP4O5Riug.png "lab.songstats.com")
A continuación os mostramos una lista con las métricas analizadas y una breve descripción de cada una:
* popularity: Popularidad de la pista en el momento en el que se recopilaron los datos.
* genre: Género de la pista.
* danceability: Cómo de bailable es la pista basado en elementos como el tempo, el ritmo, la fuerza del beat y su regularidad. Todo en una escala del 0 al 1.
* energy: Es una medida del 0 al 1 que describe la intensidad y energía de una pista. Se basa en valores como el ruido o la rapidez.
* key: La escala en la que está la pista. Por ejemplo 0 es C, 1 es C#... etc.
* loudness: Volumen de la pista medido en decibelios. El volumen se promedia a lo largo de la pista y son útiles para comparar el volumen relativo de diferentes pistas
* mode: Indica la modalidad de la pista, 0 si es menor y 1 si es mayor.
* speechiness: Detecta la presencia de discursos en una pista, entendiendo como discurso palabras que no forman parte de una melodía. Valores cercanos al 0 representan música u otros tipos de pistas que no tienen discursos. Valores cercanos al 1 representan pistas con más discursos como audiolibros o podcasts.
* acousticness: En una escala del 0 al 1 mide si la pista es más o menos acústica.
* instrumentalness: Predice si una pista no tiene letra. Los sonidos como "ooh" y "aah" se tratan como instrumentos en este contexto. A más cerca del 1 más probable es que no contenga ningún tipo de letra, los valores por encima del 0.5 representan pistas instrumentales pero a medida que se acerca al 1 la confianza es mayor.
* liveness: Detecta la presencia de audiencia en la grabación, valores más altos representan una probabilidad mayor de que haya audiencia presente.
* valence: En una escala del 0 al 1 mide la positividad de la pista, a más cercano al 1 más positiva. Con positiva nos referimos a pistas eufóricas, alegres, animadas... Con negativas nos referimos a pistas más enfadadas, brutas o tristes.
* tempo: Los BPM (beats per minute) promedio de una pista, en musicología el tempo es la velocidad de una pieza.

### Eligiendo el modelo
![Alt text](https://cdn.analyticsvidhya.com/wp-content/uploads/2024/02/Azure-Machine-Learning.jpg "analyticsvidhya.com")
Tras realizar un buen prepocesamiento de cara al machine learning y hacer algunas pruebas en local, decidimos usar [Azure](https://portal.azure.com/#home) para encontrar el modelo más óptimo y con mejor precisión. Finalmente, el modelo utilizado ha sido VotingEnsemble

### Resultados
Hemos conseguido una precisión de más de un 70% usando tan sólo los parámetros de Spotify, el modelo predice con bastante lógica si según estas características una canción será popular o no. Hay que tener en cuenta que estas predicciones no tienen una causalidad directa, ya que no se tienen en cuenta cosas como la popularidad base del artista, sucesos sociales, viralidad, etc.
Ha sido un proyecto muy interesentante en el que hemos aprendido muchísimo sobre el manejo de APIs y ML.