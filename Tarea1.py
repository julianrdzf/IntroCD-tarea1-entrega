# -*- coding: utf-8 -*-
"""
Created on Tue May 16 18:04:17 2023

@author: Agustín Porley & Julián Rodríguez
"""
#%%
from time import time
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

import numpy as np

#%%
# Creamos el directorio Tarea_1/data/shakespeare
data_dir = Path("data") / "shakespeare"
data_dir.mkdir(parents=True, exist_ok=True)


def load_table(table_name, engine):
    """
    Leer la tabla con SQL y guardarla como CSV,
    o cargarla desde el CSV si ya existe
    """
    path_table = data_dir / f"{table_name}.csv"
    if not path_table.exists():
        print(f"Consultando tabla con SQL: {table_name}")
        t0 = time()
        df_table = pd.read_sql(f"SELECT * FROM {table_name}", engine)
        t1 = time()
        print(f"Tiempo: {t1 - t0:.1f} segundos")

        print(f"Guardando: {path_table}\n")
        df_table.to_csv(path_table)
    else:
        print(f"Cargando tabla desde CSV: {path_table}")
        df_table = pd.read_csv(path_table, index_col=[0])
    return df_table


print("Conectando a la base...")
conn_str = "mysql+pymysql://guest:relational@relational.fit.cvut.cz:3306/Shakespeare"
engine = create_engine(conn_str)

# DataFrame con todas las obras:
df_works = load_table("works", engine)

# Todos los párrafos de todas las obras
df_paragraphs = load_table("paragraphs", engine)

# TODO: cargar el resto de las tablas
df_characters = load_table("characters", engine)
df_chapters = load_table("chapters", engine)

#%%
#Funcion para el calculo de espacios vacios para datos cargados desde el .csv

def Contar_Vacio(df_name, dataframe_name):
    for column_name in df_name.columns:
        cantidad = df_name[column_name].isna().sum()
        total_datos = df_name.shape[0]
        print(f"La columna {column_name} correspondiente a la tabla {dataframe_name} tiene {cantidad} espacios vacíos de {total_datos}")


Vacio_Char=Contar_Vacio(df_characters,"Characters") 
Vacio_Chap=Contar_Vacio(df_chapters, "Chapters") 
Vacio_Para=Contar_Vacio(df_paragraphs, "Paragraphs") 
Vacio_works=Contar_Vacio(df_works, "Works") 

#%%

# Veamos las obras incluídas:
df_works

#%%

df_paragraphs["PlainText"]

#%%
#Parte 1.a.
df_parrafos = pd.merge(df_paragraphs, df_characters[["id", "CharName"]], left_on="character_id", right_on="id")
parrafos_personajes = df_parrafos.groupby("CharName")["PlainText"].count().sort_values(ascending=False)


#%%
#Parte 1.b.

#Genero bines
min_anho = df_works["Date"].min()
max_anho = df_works["Date"].max()
bin_edges = np.arange(df_works['Date'].min(), df_works['Date'].max() + 3, 2)


#Grafico
plt.hist(df_works['Date'], bins=bin_edges, density=False, rwidth=0.7, color='red')
plt.xlabel("Año")
plt.ylabel("Cantidad de obras")
plt.title('Histograma de obras por períodos')
plt.xticks(bin_edges, rotation = 45)
plt.ylim(ymin=0, ymax = 7.5)
plt.show()



generos = df_works.groupby("GenreType")["Date"].count().sort_values(ascending=False)


#%%
generos_cat = ["Comedy","History","Tragedy","Poem","Sonnet"]

bin_edges = np.arange(df_works['Date'].min(), df_works['Date'].max() + 3, 2)

a=df_works[df_works["GenreType"]==generos_cat[0]]['Date']
b=df_works[df_works["GenreType"]==generos_cat[1]]['Date']
c=df_works[df_works["GenreType"]==generos_cat[2]]['Date']
d=df_works[df_works["GenreType"]==generos_cat[3]]['Date']
e=df_works[df_works["GenreType"]==generos_cat[4]]['Date']

colors = ['#dcd392', '#295264', '#bd2f28', '#fab4b6', '#89abb4']


plt.hist([a,b,c,d,e], bins=bin_edges, color = colors, label = generos_cat, density=False, rwidth=0.7, stacked=True)

plt.legend(prop={'size': 8})

plt.xlabel("Año")
plt.ylabel("Cantidad de obras")
plt.title('Histograma de obras por períodos apilados por género')
plt.xticks(bin_edges, rotation = 45)
plt.ylim(ymin=0, ymax = 7.5)
plt.show()


#%%

def clean_text(df, column_name):
    # Convertir todo a minúsculas
    result = df[column_name].str.lower()

    # Quitar signos de puntuación y cambiarlos por espacios (" ")
    # TODO: completar signos de puntuación faltantes
    for punc in ["[", "\n", ",", ";", "]", ".", ":", "!", "¡", "?", "¿", "-", " '", "' "]:
        result = result.str.replace(punc, " ")
    return result

# Creamos una nueva columna CleanText a partir de PlainText
df_paragraphs["CleanText"] = clean_text(df_paragraphs, "PlainText")

# Veamos la diferencia
df_paragraphs[["PlainText", "CleanText"]]




#%%

# Convierte párrafos en listas "palabra1 palabra2 palabra3" -> ["palabra1", "palabra2", "palabra3"]
df_paragraphs["WordList"] = df_paragraphs["CleanText"].str.split()

# Veamos la nueva columna creada
# Notar que a la derecha tenemos una lista: [palabra1, palabra2, palabra3]
df_paragraphs[["CleanText", "WordList"]]

#%%

# Nuevo dataframe: cada fila ya no es un párrafo, sino una sóla palabra
df_words = df_paragraphs.explode("WordList")

# Quitamos estas columnas redundantes
df_words.drop(columns=["CleanText", "PlainText"], inplace=True)

# Renombramos la columna WordList -> word
df_words.rename(columns={"WordList": "word"}, inplace=True)

# Verificar que el número de filas es mucho mayor
df_words

#%%
# Agregamos el nombre de los personajes
# TODO: des-comentar luego de cargar df_characters
df_words = pd.merge(df_words, df_characters[["id", "CharName"]], left_on="character_id", right_on="id")

#%%
# TODO:
# - des-comentar luego de hacer el merge
# - Encuentra algún problema en los resultados?

words_per_character = df_words.groupby("CharName")["word"].count().sort_values(ascending=False)
words_per_character

#%%
#Se prueba agrupando por id
words_per_character_2 = df_words.groupby("character_id")["word"].count().sort_values(ascending=False)
words_per_character_2

#%%
#Gráfico de barras de cantidad de palabras
count_words = df_words.groupby("word")["word"].count().sort_values(ascending=False)

plt.bar(count_words.index[:10],np.array(count_words[:10]), color = 'red')

plt.ylabel("Cantidad de ocurrencias")
plt.title('Ocurrencia de palabras')
plt.xticks(count_words.index[:10])
plt.show()



#%%
# Ejemplo: 10 personajes con más palabras
char_show = words_per_character[:10]
plt.bar(char_show.index, char_show.values, color = 'red')
_ = plt.xticks(rotation=90)
