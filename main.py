from fastapi import FastAPI # Imporamos FastAPI
import pandas as pd
import numpy as np
from fastapi.responses import HTMLResponse # Importamos este modulo que nos permite hacer los returns como codigo HTML
from fastapi.responses import RedirectResponse # Esta clase se utiliza para crear una respuesta HTTP de redireccionamiento (redirección) en una aplicación FastAPI.
from ModeL import cosine_sim

app = FastAPI()

@app.get("/", include_in_schema=False) #nos redirecciona directamente a /docs
def index():
    return RedirectResponse("/docs", status_code=308)

expanded_df_reviews = pd.read_parquet('clean_reviews.parquet.gzip')
df_steam_games = pd.read_parquet('clean_games.parquet.gzip')
expanded_df_items = pd.read_parquet('clean_items.parquet.gzip')
games_model = pd.read_parquet('games_model.parquet.gzip')

@app.get('/userdata/{User_id}', response_class=HTMLResponse)
def userdata(User_id: str):
    user_games = expanded_df_items[expanded_df_items['user_id'] == User_id]['item_id']
    prices = df_steam_games[df_steam_games['id'].isin(user_games)]['price']
    money_spent_by_user = prices.sum()
    
    user_reviews = expanded_df_reviews[expanded_df_reviews['user_id'] == User_id]
    total_reviews = user_reviews.shape[0]
    recommended_reviews = user_reviews[user_reviews['recommend'] == True].shape[0]
    
    if total_reviews == 0:
        percentage = 0
    
    percentage = (recommended_reviews / total_reviews) * 100
    
    items_per_user = expanded_df_items[expanded_df_items['user_id'] == User_id]['item_id'].count()
    
    return f'<p>${round(money_spent_by_user,2)} , {round(percentage,2)}%, {items_per_user}</p>'

@app.get('/countreviews/{start_date},{end_date}', response_class=HTMLResponse)
def countreviews(start_date: str, end_date: str):
    filtered_reviews = expanded_df_reviews[(expanded_df_reviews['posted'] >= start_date) & (expanded_df_reviews['posted'] <= end_date)]
    unique_users= filtered_reviews['user_id'].nunique()
    
    recommended_reviews = filtered_reviews[filtered_reviews['recommend'] == True].shape[0]
    total_reviews = filtered_reviews.shape[0]
    
    if total_reviews == 0:
        recommendation_percentage = 0
    else:
        recommendation_percentage = (recommended_reviews / total_reviews) * 100
    #return unique_users, recommendation_percentage
    return f'<p>{unique_users} : {round(recommendation_percentage,2)*100}%</p>'

#Devuelve el puesto en el que se encuentra un género sobre el ranking de los mismos analizado bajo la columna PlayTimeForever.
@app.get('/genre/{genre_name}', response_class=HTMLResponse)
def genre(genre_name: str):
    df_game_time = expanded_df_items[['item_id','playtime_forever']] # Solo trae estas dos columnas que son las necesarias para el codigo.
    df_grouped = df_game_time.groupby('item_id')['playtime_forever'].sum() # agrupa por juego el total jugado.
    df_steam_games.drop_duplicates(subset='id', inplace=True) #se eliminan juegos repetidos
    df_merged = pd.merge(df_steam_games, df_grouped, left_on='id', right_on='item_id', how='left') #se unen los datos
    df_merged.dropna(subset=['playtime_forever'], inplace=True) # Hago un drop en la columna playtime_forever

    #expando y extraigo todos los generos distintos
    expanded_merged = df_merged.explode('genres')
    unik_genres = df_merged.explode('genres')['genres'].unique()
    
    #se realizará el ranking
    listacalc = []

    def tiempo_genero(lista):
        listacalc = []
        for elemento in lista:
            calculo = expanded_merged.loc[expanded_merged['genres'] == str(elemento), 'playtime_forever'].sum()
            listacalc.append(calculo)
        return listacalc
    a = tiempo_genero(unik_genres)

    datos = {
    'generos' : unik_genres,
    'tiempo_juego': a
    }
    
    df = pd.DataFrame(datos)
    df['ranking'] = df['tiempo_juego'].rank(ascending=False)

    #Se buscará el numero de
    lugar = df.loc[df['generos'] == genre_name, 'ranking'].values[0]

    return f'<p>Ranking: {lugar}</p>'

@app.get('/userforgenre/{gender_name}', response_class=HTMLResponse)
def userforgenre(gender_name: str ):
    expanded_steam_games = df_steam_games.explode('genres') #se trae el df expandido para buscar generos
    user_review_gender = expanded_df_items[expanded_df_items['item_name'].isin(expanded_steam_games[expanded_steam_games['genres'] == gender_name]['app_name'])]
    ##
    hpu = user_review_gender.groupby('user_id')['playtime_forever'].sum().reset_index()
    top = hpu.sort_values(by='playtime_forever', ascending=False).head(5)
    ##
    top['user_url'] = "http://steamcommunity.com/id/" + top['user_id']

    top = top[['user_id', 'user_url', 'playtime_forever']]
    return f'<p>{top}</p>'

@app.get('/developer/{desarrollador}', response_class=HTMLResponse)
def developer(desarrollador: str):
    # Filtrar los juegos del desarrollador
    juegos_del_desarrollador = df_steam_games[df_steam_games['publisher'] == desarrollador]
    
    # Extraer el año de lanzamiento de cada juego
    juegos_del_desarrollador['release_year'] = juegos_del_desarrollador['release_date'].str.extract(r'(\d{4})').astype(int)
    
    # Contar la cantidad de ítems por año utilizando .loc
    item_count_by_year = juegos_del_desarrollador.groupby('release_year').size().sort_index()

    # Calcular el porcentaje de contenido gratuito ("Free") por año
    free_items_by_year = juegos_del_desarrollador[juegos_del_desarrollador['price'] == 0]
    free_item_count_by_year = free_items_by_year.groupby('release_year').size().sort_index()
    total_item_count_by_year = item_count_by_year.reindex(free_item_count_by_year.index).fillna(0)
    percentage_free_by_year = (free_item_count_by_year / total_item_count_by_year) * 100
    
    return f'<p>{percentage_free_by_year} </p>'

@app.get('/sentiment_analysis/{year}', response_class=HTMLResponse)
def sentiment_analysis(year: int):
    # Extraer el año de lanzamiento de cada juego
    expanded_df_reviews['post_year'] = expanded_df_reviews['posted'].dt.year
    expanded_df_reviews['post_year'] = expanded_df_reviews['posted'].dt.year
    df_reviews_by_year = expanded_df_reviews[expanded_df_reviews['post_year'] == year]
    sentiment_counts = df_reviews_by_year['sentiment_analysis'].value_counts()
    # Crear un diccionario para almacenar los resultados
    result = sentiment_counts.to_dict()
    return f'<p>{result} </p>'

@app.get('/recomendacion_juego/{id_item}', response_class=HTMLResponse)
def recomendacion_juego(id_item: str):
    # Buscamos el índice del producto con un ID específico en nuestro DataFrame 'games_model'
    item_indice = games_model[games_model['id'] == id_item].index[0]
    # Calculamos la similitud de coseno entre el producto seleccionado y todos los demás productos
    items_similares = list(enumerate(cosine_sim[item_indice]))
    # Ordenamos los productos similares en orden descendente de similitud
    recommended_items = sorted(items_similares, key=lambda x: x[1], reverse=True)
    # Extraemos los índices de los juegos más recomendados (excluyendo el juego original)
    indices = [index for index, _ in recommended_items[1:10]]
    # Obtenemos los IDs (o app_names) de los juegos recomendados
    recommended_items = games_model.iloc[indices]['id'].tolist()
    # Creamos una cadena de texto con las recomendaciones
    recomedations = ""
    for i in recommended_items[:5]:
        # Agregamos los nombres de los juegos recomendados a la cadena
        recomedations += f'{games_model[games_model.id == i].app_name.tolist()[0]}'
    return recomedations

