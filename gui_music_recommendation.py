# -*- coding: utf-8 -*-
"""gui_music_recommendation.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1v3dG3c_i9vuc488WBGrnYvfGkNO6uCBx

# Data Collect
"""

import requests
import base64

# Ingresar el ID y el secret del cliente
CLIENT_ID = '13863bb0f23e4e49a02593bea4f5e032'
CLIENT_SECRET = '12f0b32c2795405fa6d3bacee11e91b0'

# Codificar el ID y el secret del cliente con Base64
client_credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
client_credentials_base64 = base64.b64encode(client_credentials.encode())

# Solicitar el token de acceso
token_url = 'https://accounts.spotify.com/api/token'
headers = {
    'Authorization': f'Basic {client_credentials_base64.decode()}'
}
data = {
    'grant_type': 'client_credentials'
}
response = requests.post(token_url, data=data, headers=headers)

if response.status_code == 200:
    access_token = response.json()['access_token']
    print("Token de acceso obtenido con éxito.")
else:
    print("¡Error! No se pudo obtener el token de acceso")
    exit()

import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def get_trending_playlist_data(playlist_id, access_token):
    # Configurar Spotipy con el token de acceso
    sp = spotipy.Spotify(auth=access_token)

    # Obtener las canciones de la playlist
    playlist_tracks = sp.playlist_tracks(playlist_id, fields='items(track(id, name, artists, album(id, name)))')

    # Extraer información relevante y guardarla en una lista de diccionarios
    music_data = []
    for track_info in playlist_tracks['items']:
        track = track_info['track']
        track_name = track['name']
        artists = ', '.join([artist['name'] for artist in track['artists']])
        album_name = track['album']['name']
        album_id = track['album']['id']
        track_id = track['id']

        # Obtener las características de audio por cada canción
        audio_features = sp.audio_features(track_id)[0] if track_id != 'Not available' else None

              # Obtener fecha de publicación del álbum
        try:
            album_info = sp.album(album_id) if album_id != 'Not available' else None
            release_date = album_info['release_date'] if album_info else None

            # Verificar el formato de la fecha
            if release_date:
                try:
                    # Intentar convertir la fecha con el formato completo
                    release_date_obj = datetime.strptime(release_date, '%Y-%m-%d')
                except ValueError:
                    try:
                        # Si falla, intentar convertir solo el año
                        release_date_obj = datetime.strptime(release_date, '%Y')
                        # Asignar el primer día de enero de ese año
                        release_date_obj = release_date_obj.replace(month=1, day=1)
                    except ValueError:
                        # Si también falla, asignar None
                        release_date_obj = None
                # Convertir la fecha a cadena en el formato deseado
                if release_date_obj:
                    release_date = release_date_obj.strftime('%Y-%m-%d')
                else:
                    release_date = None
        except:
            release_date = None

        # Obtener popularidad de la canción
        try:
            track_info = sp.track(track_id) if track_id != 'Not available' else None
            popularity = track_info['popularity'] if track_info else None
        except:
            popularity = None

        # Agregar información adicional a los datos de la canción
        track_data = {
            'Track Name': track_name,
            'Artists': artists,
            'Album Name': album_name,
            'Album ID': album_id,
            'Track ID': track_id,
            'Popularity': popularity,
            'Release Date': release_date,
            'Duration (ms)': audio_features['duration_ms'] if audio_features else None,
            'Explicit': track_info.get('explicit', None),
            'External URLs': track_info.get('external_urls', {}).get('spotify', None),
            'Danceability': audio_features['danceability'] if audio_features else None,
            'Energy': audio_features['energy'] if audio_features else None,
            'Key': audio_features['key'] if audio_features else None,
            'Loudness': audio_features['loudness'] if audio_features else None,
            'Mode': audio_features['mode'] if audio_features else None,
            'Speechiness': audio_features['speechiness'] if audio_features else None,
            'Acousticness': audio_features['acousticness'] if audio_features else None,
            'Instrumentalness': audio_features['instrumentalness'] if audio_features else None,
            'Liveness': audio_features['liveness'] if audio_features else None,
            'Valence': audio_features['valence'] if audio_features else None,
            'Tempo': audio_features['tempo'] if audio_features else None,
            # Es posible añadir más características
        }

        music_data.append(track_data)

    # Crear un DataFrame de pandas con la lista de diccionarios
    df = pd.DataFrame(music_data)

    return df

# Cargar el id de la playlist
playlist_id = '1HdKLVnxqjWuTucIRmAEEx'

# Guardar la información de la playlist en un DataFrame
music_df = get_trending_playlist_data(playlist_id, access_token)

# Mostrar el DataFrame
print(music_df)

"""# Data Quality & Cleaning"""

music_df.rename(columns = {
            'track_name':'Track Name',
            'artists':'Artists',
            'album_name':'Album Name',
            'album_id':'Album ID',
            'track_id':'Track ID',
            'popularity':'Popularity',
            'release_date':'Release Date',
            'audio_features':'Duration (ms)'
            }, inplace=True)
music_df

# Cargar el dataframe y analizamos la existencia previa de estas columnas
required_columns = [
    'Track Name',
    'Artists',
    'Album Name',
    'Album ID',
    'Track ID',
    'Popularity',
    'Release Date',
    'Duration (ms)',
    'Explicit',
    'External URLs',
    'Danceability',
    'Energy',
    'Key',
    'Loudness',
    'Mode',
    'Speechiness',
    'Acousticness',
    'Instrumentalness',
    'Liveness',
    'Valence',
    'Tempo'
]
missing_columns = [col for col in required_columns if col not in music_df.columns]

if not missing_columns:
   print("Todas las columnas requeridas están presentes en el DataFrame.")
else:
    print(f"Faltan las siguientes columnas en el DataFrame: {missing_columns}")

"""# Exploratory Data Analysis (EDA)"""

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.pyplot as plt
import scipy as scipy
import seaborn as sns
# %matplotlib inline

#Automcompletar rápido
# %config IPCompleter.greedy=True
#Desactivar la notación científica
pd.options.display.float_format = '{:.3f}'.format

# Separa los artistas de cada cadena
all_artists = [artist.strip() for sublist in music_df['Artists'].str.split(',') for artist in sublist]

# Calcula la frecuencia de cada artista
artist_freq = pd.Series(all_artists).value_counts()

top_artists = artist_freq.head(5)

# Graficar los cinco artistas principales
plt.figure(figsize=(10, 6))
sns.barplot(x=top_artists.index, y=top_artists.values)
plt.title('Frecuencia de canciones del Top 5 de Artistas')
plt.xlabel('Artistas')
plt.ylabel('Frecuencia')
plt.xticks(rotation=45)
plt.grid(True)
plt.show()

# Calcular el promedio de duración de canciones en (ms)
duration_mean_ms = music_df['Duration (ms)'].mean()

# Convierte los milisegundos a minutos con segundos
duration_mean_min = duration_mean_ms / 1000 / 60  # Convertir a minutos
remaining_seconds = (duration_mean_min - int(duration_mean_min)) * 60  # Obtener los segundos restantes

print("El promedio de duración de canciones es aproximadamente: {} minutos y {:.2f} segundos".format(int(duration_mean_min), remaining_seconds))

# Obtener los top 5 artistas
top_artists = music_df['Artists'].value_counts().head(5).index.tolist()

# Filtrar el DataFrame para incluir solo las canciones de los top 5 artistas
top_artists_df = music_df[music_df['Artists'].isin(top_artists)]

# Calcula el promedio de la duración para los top 5 artistas
avg_duration_per_artist = top_artists_df.groupby('Artists')['Duration (ms)'].mean()

# Convierte el promedio de duración a minutos con segundos
avg_duration_min_per_artist = avg_duration_per_artist / 1000 / 60
avg_remaining_seconds_per_artist = (avg_duration_min_per_artist - avg_duration_min_per_artist.astype(int)) * 60

# Grafica el promedio de duración por artista
plt.figure(figsize=(10, 6))
plt.bar(avg_duration_per_artist.index, avg_duration_min_per_artist)
plt.title('Promedio de Duración por Artista (Top 5)')
plt.xlabel('Artista')
plt.ylabel('Duración Promedio (minutos)')
plt.xticks(rotation=45)
plt.grid(True)
plt.show()

music_df['Decada'] = music_df['Release Date'].astype(str)
music_df['Decada'] = music_df['Decada'].str[:3] + '0s'
# Calcular la frecuencia de cada década
decada_freq = music_df['Decada'].value_counts()
# Seleccionar las 5 décadas con mayor frecuencia
top_decadas = decada_freq.head(5)

# Graficar la frecuencia de las 5 décadas principales
plt.figure(figsize=(10, 6))
sns.barplot(x=top_decadas.index, y=top_decadas.values)
plt.title('Cantidad de Lanzamientos por Década')
plt.xlabel('Década')
plt.ylabel('Frecuencia')
plt.xticks(rotation=45)
plt.grid(True)
plt.show()

"""# Data Transformation"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity

# Normalize the music features using Min-Max scaling
scaler = MinMaxScaler()
music_features = music_df[['Danceability', 'Energy', 'Key',
                           'Loudness', 'Mode', 'Speechiness', 'Acousticness',
                           'Instrumentalness', 'Liveness', 'Valence', 'Tempo']].values
music_features_scaled = scaler.fit_transform(music_features)

"""# Modelling

## Regresión Logística

### Preprocesamiento
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, precision_recall_curve, auc
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity

# Verificar y convertir todas las columnas a formato numérico (si es necesario)
music_temp_df = music_df.copy()
for column in music_temp_df.columns:
    if music_temp_df[column].dtype == 'object':
        try:
           music_temp_df[column] = music_temp_df[column].astype(float)
        except ValueError:
           music_temp_df.drop(column, axis=1, inplace=True)

# Dividir en características y objetivo
X = music_temp_df.drop('Energy', axis=1)

# Convertir a binario: energía > 0.7 es 1, de lo contrario 0
y = (music_temp_df['Energy'] > 0.7).astype(int)

# Verificar que y es binario
print("Valores únicos en y:", y.unique())

# Dividir las filas en entrenamiento (70%) y prueba (30%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Escalar las características
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

"""### Modelo"""

# Entrenamiento del modelo de regresión logística
modelo_LogisticRegression = LogisticRegression()
modelo_LogisticRegression.fit(X_train_scaled, y_train)

# Realizar predicciones
y_pred_LogisticRegression = modelo_LogisticRegression.predict(X_test_scaled)
y_pred_LogisticRegression_proba = modelo_LogisticRegression.predict_proba(X_test_scaled)[:, 1]

"""### Evaluación"""

# Evaluar el modelo
accuracy = accuracy_score(y_test, y_pred_LogisticRegression)
report = classification_report(y_test, y_pred_LogisticRegression)

print("Accuracy:", accuracy)
print("Classification Report:\n", report)

# Calcular la matriz de confusión
confusion_matrix_LogisticRegression = confusion_matrix(y_test, y_pred_LogisticRegression)

# Graficar la matriz de confusión
plt.figure(figsize=(8, 6))
sns.heatmap(confusion_matrix_LogisticRegression,
            annot=True, fmt='d',
            cmap='Blues',
            xticklabels=['Sad', 'Happy'],
            yticklabels=['Sad', 'Happy'],
            annot_kws={"size": 16})
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.title('Regression Confusion Matrix')
plt.show()

TN = confusion_matrix_LogisticRegression[0][0]
FP = confusion_matrix_LogisticRegression[0][1] #tipo I
FN = confusion_matrix_LogisticRegression[1][0] #tipo II
TP = confusion_matrix_LogisticRegression[1][1]
print(TN, FP, FN, TP)

# Calcular la Curva de Precisión y Recall
precision, recall, thresholds = precision_recall_curve(y_test, y_pred_LogisticRegression_proba)

# Calcular el área bajo la curva (AUC)
pr_auc = auc(recall, precision)

# Graficar la Curva de Precisión y Recall
plt.figure(figsize=(8, 6))
plt.plot(recall, precision, marker='.', label=f'Logistic (AUC = {pr_auc:.2f})')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.legend(loc='best')
plt.show()

"""## Árbol de Decisiones

### Modelo
"""

# Importar el modelo
from sklearn.ensemble import RandomForestClassifier

# Entrenar el modelo
modelo_RandomForest = RandomForestClassifier()
modelo_RandomForest.fit(X_train,y_train)

# Predecir usando los datos de test
y_pred_RandomForest       = modelo_RandomForest.predict(X_test)
y_pred_RandomForest_proba = modelo_RandomForest.predict_proba(X_test)

"""### Evaluación"""

# Evaluar el modelo
accuracy = accuracy_score(y_test, y_pred_RandomForest)
report = classification_report(y_test, y_pred_RandomForest)

print("Accuracy:", accuracy)
print("Classification Report:\n", report)

# Calcular la matriz de confusión
confusion_matrix_RandomForest = confusion_matrix(y_test, y_pred_RandomForest)

# Graficar la matriz de confusión
plt.figure(figsize=(8, 6))
sns.heatmap(confusion_matrix_RandomForest, annot=True,xticklabels=['Sad','Happy'],
            yticklabels=['Sad','Happy'], cmap = 'Greens',annot_kws={"size": 16});
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.title('Tree Confusion Matrix')
plt.show()

TN = confusion_matrix_RandomForest[0][0]
FP = confusion_matrix_RandomForest[0][1] #tipo I
FN = confusion_matrix_RandomForest[1][0] #tipo II
TP = confusion_matrix_RandomForest[1][1]
print(TN, FP, FN, TP)

# Calcular la Curva de Precisión y Recall
precision, recall, thresholds = precision_recall_curve(y_test, y_pred_RandomForest)

# Calcular el área bajo la curva (AUC)
pr_auc = auc(recall, precision)

# Graficar la Curva de Precisión y Recall
plt.figure(figsize=(8, 6))
plt.plot(recall, precision, marker='.', label=f'Logistic (AUC = {pr_auc:.2f})', color='green')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.legend(loc='best')
plt.show()

"""### Visualización"""

#Arbol en indice 5
estimator = modelo_RandomForest.estimators_[5]

from sklearn import tree

fig = plt.figure(figsize=(40,20))
_ = tree.plot_tree(estimator,
                   feature_names=X.columns,
                   class_names=['Sad','Happy'],
                   node_ids=True,
                   filled=True)

"""# Optimización"""

# Importar las bibliotecas
from sklearn.model_selection import GridSearchCV

# Ignorar advertencias
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

"""## Regresión Logística"""

'''
# Inicializar el modelo de regresión logística
best_model_LogisticRegression = LogisticRegression(C=10, class_weight={0: 1.0, 1: 2.0})

# Entrenar el mejor modelo
best_model_LogisticRegression.fit(X_train, y_train)

# Predecir con el mejor modelo
best_y_pred_LogisticRegression = best_model_LogisticRegression.predict(X_test_scaled)
best_y_pred_LogisticRegression_proba = best_model_LogisticRegression.predict_proba(X_test_scaled)[:, 1]

# Evaluar el rendimiento del mejor modelo
best_accuracy = accuracy_score(y_test, best_y_pred_LogisticRegression)
best_report = classification_report(y_test, best_y_pred_LogisticRegression)

print("Accuracy:", best_accuracy)
print("Classification Report:\n", best_report)

# Calcular la matriz de confusión
confusion_matrix_LogisticRegression = confusion_matrix(y_test, y_pred_LogisticRegression)

# Graficar la matriz de confusión
plt.figure(figsize=(8, 6))
sns.heatmap(confusion_matrix_LogisticRegression,
            annot=True, fmt='d',
            cmap='Blues',
            xticklabels=['Sad', 'Happy'],
            yticklabels=['Sad', 'Happy'],
            annot_kws={"size": 16})
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.title('BEST Regression Confusion Matrix')
plt.show()

# Calcular la Curva de Precisión y Recall
precision, recall, thresholds = precision_recall_curve(y_test, best_y_pred_LogisticRegression_proba)

# Calcular el área bajo la curva (AUC)
pr_auc = auc(recall, precision)

# Graficar la Curva de Precisión y Recall
plt.figure(figsize=(8, 6))
plt.plot(recall, precision, marker='.', label=f'Logistic (AUC = {pr_auc:.2f})')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('BEST Precision-Recall Curve')
plt.legend(loc='best')
plt.show()
'''

"""## Árbol de Decisiones"""

'''
# Inicializar el modelo de árbol de decisiones
best_model_RandomForest = RandomForestClassifier()

# Definir los hiperparámetros a ajustar
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [3, 5, 7, 10, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'max_features': ['auto', 'sqrt', 'log2', None],
    'max_samples': [0.5, 0.7, 0.9, None],
    'bootstrap': [True, False],
    'oob_score': [True, False],
    'min_weight_fraction_leaf': [0.0, 0.1, 0.2]
}

# Crear el objeto de búsqueda de hiperparámetros
grid_search = GridSearchCV(estimator=best_model_RandomForest,
                           param_grid=param_grid,
                           cv=5,
                           scoring='accuracy',
                           )

# Realizar la búsqueda en la cuadrícula
grid_search.fit(X_train, y_train)

# Obtener los mejores hiperparámetros
best_params = grid_search.best_params_

# Crear el modelo con los mejores hiperparámetros
best_model_RandomForest = RandomForestClassifier(**best_params)

# Entrenar el modelo con los mejores hiperparámetros
best_model_RandomForest.fit(X_train, y_train)

# Realizar predicciones con el mejor modelo
best_y_pred_RandomForest = best_model_RandomForest.predict(X_test_scaled)
best_y_pred_RandomForest_proba = best_model_RandomForest.predict_proba(X_test_scaled)[:, 1]

# Evaluar el rendimiento del mejor modelo
best_accuracy = accuracy_score(y_test, best_y_pred_RandomForest)
best_report = classification_report(y_test, best_y_pred_RandomForest)

print("Accuracy:", best_accuracy)
print("Classification Report:\n", best_report)

# Calcular la matriz de confusión
best_confusion_matrix_RandomForest = confusion_matrix(y_test, best_y_pred_RandomForest)

# Graficar la matriz de confusión
plt.figure(figsize=(8, 6))
sns.heatmap(best_confusion_matrix_RandomForest, annot=True,xticklabels=['Sad','Happy'],
            yticklabels=['Sad','Happy'], cmap = 'Greens',annot_kws={"size": 16});
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.title('BEST Tree Confusion Matrix')
plt.show()

# Calcular la Curva de Precisión y Recall
precision, recall, thresholds = precision_recall_curve(y_test, best_y_pred_RandomForest)

# Calcular el área bajo la curva (AUC)
pr_auc = auc(recall, precision)

# Graficar la Curva de Precisión y Recall
plt.figure(figsize=(8, 6))
plt.plot(recall, precision, marker='.', label=f'Logistic (AUC = {pr_auc:.2f})', color='green')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('BEST Precision-Recall Curve')
plt.legend(loc='best')
plt.show()
'''

"""# Sistema de Recomendación"""

from ipywidgets import interact, widgets, Layout
from IPython.display import display, clear_output
import time

# Una función para obtener recomendaciones basadas en contenido según las características de la música
def content_based_recommendations(input_song_name, music_df, num_recommendations=5):
    # Normalize the music features using Min-Max scaling
    scaler = MinMaxScaler()
    music_features = music_df[['Danceability', 'Energy', 'Key',
                            'Loudness', 'Mode', 'Speechiness', 'Acousticness',
                            'Instrumentalness', 'Liveness', 'Valence', 'Tempo']].values
    music_features_scaled = scaler.fit_transform(music_features)

    if input_song_name not in music_df['Track Name'].values:
        print(f"'{input_song_name}' not found in the dataset. Please enter a valid song name.")
        return

    # Obtener el índice de la canción de entrada en el DataFrame de música
    input_song_index = music_df[music_df['Track Name'] == input_song_name].index[0]

    # Calcular los puntajes de similitud basados ​​en las características musicales (similitud de coseno)
    similarity_scores = cosine_similarity([music_features_scaled[input_song_index]], music_features_scaled)

    # Obtener los índices de las canciones más similares
    similar_song_indices = similarity_scores.argsort()[0][::-1][1:num_recommendations + 1]

    # Obtener los nombres de las canciones más similares según el filtrado basado en contenido
    content_based_recommendations = music_df.iloc[similar_song_indices][['Track Name', 'Artists', 'Album Name', 'Release Date', 'Popularity']]

    return content_based_recommendations

# GUI setup
url_text = widgets.Text(description="Playlist URL:", layout=Layout(width='50%'))
song_text = widgets.Text(description="Song Name:", layout=Layout(width='50%'))
process_button = widgets.Button(description="Process", layout=Layout(width='50%'))
loading_indicator = widgets.Label()

output_label = widgets.Output()

loading_indicator = widgets.Label()
loading_spinner = widgets.HTML(value='''<div class="spinner-border text-primary" role="status">
  <span class="visually-hidden">Loading...</span>
</div>''')

def process_spotify_data():
    playlist_url = url_text.value.strip()
    song = song_text.value.strip()

    # Extraer ID de playlist
    playlist_id = playlist_url.split('/')[-1]

    # Llamar función para obtener la data de la playlist
    music_df = get_trending_playlist_data(playlist_id, access_token)

    # Renombrar las columnas del dataframe
    music_df.rename(columns={
        'track_name': 'Track Name',
        'artists': 'Artists',
        'album_name': 'Album Name',
        'album_id': 'Album ID',
        'track_id': 'Track ID',
        'popularity': 'Popularity',
        'release_date': 'Release Date',
        'audio_features': 'Duration (ms)'
    }, inplace=True)

    print(content_based_recommendations(song, music_df))

    return music_df

def on_process_button_clicked(b):
    display(loading_spinner)
    process_button.disabled = True
    # ----- Toma tiempo -----
    process_spotify_data()
    # ----- Toma tiempo -----
    loading_spinner.close()
    process_button.disabled = False

process_button.on_click(on_process_button_clicked)

display(widgets.VBox([url_text, song_text, process_button, output_label]))
