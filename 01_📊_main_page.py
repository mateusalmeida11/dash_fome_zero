# bibliotecas: 

import streamlit as st
import pandas as pd
import numpy as np 
import plotly.express as px
from pathlib import Path
import inflection as inflection
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
from PIL import Image
# funções para o dataframe 

## função para descobrir quais são as colunas que tem valores iguais 

def coluna_values_unicos (df): 

    #extraindo as colunas do dataframe
    colunas = list(df.columns)

    colunas_unicas = [coluna_unica for coluna_unica in colunas if len(df[coluna_unica].unique()) == 1]

    return colunas_unicas

## função para preencher os países: 

COUNTRIES = {
   1: "India",
   14: "Australia",
   30: "Brazil",
   37: "Canada",
   94: "Indonesia",
   148: "New Zeland",
   162: "Philippines",
   166: "Qatar",
   184: "Singapure",
   189: "South Africa",
   191: "Sri Lanka",
   208: "Turkey",
   214: "United Arab Emirates",
   215: "England",
   216: "United States of America",
}
def country_name(country_id): return COUNTRIES[country_id]

## função para criação do nome das cores 

COLORS = {
   "3F7E00": "darkgreen",
   "5BA829": "green",
   "9ACD32": "lightgreen",
   "CDD614": "orange",
   "FFBA00": "red",
   "CBCBC8": "darkred",
   "FF7800": "darkred",
}
def color_name(color_code): return COLORS[color_code]

## função para renomear os nomes dos dataframes: 

def rename_columns(dataframe):
   df = dataframe.copy()
   title = lambda x: inflection.titleize(x) 
   snakecase = lambda x: inflection.underscore(x) 
   spaces = lambda x: x.replace(" ", "")
   cols_old = list(df.columns)
   cols_old = list(map(title, cols_old)) 
   cols_old = list(map(spaces, cols_old)) 
   cols_new = list(map(snakecase, cols_old)) 
   df.columns = cols_new
   return df

## função para categorizar a comida 

def create_price_tye(price_range):
   if price_range == 1: 
      return "cheap"
   elif price_range == 2: 
      return "normal"
   elif price_range == 3: 
      return "expensive"
   else:
      return "gourmet" 
   
# abrindo o arquivo para gerar o dataframe

## caminho do arquivo: 

arquivo = Path.cwd()/'dataset'/'zomato.csv'

## criando um dataframe

df = pd.read_csv(arquivo)

# limpeza de dados 

## pelo método info conseguimos identificar que tem 15 linhas na coluna 'Cusines' que são nulas. Desse modo vamos remover essas linhas 

df = df.dropna().reset_index(drop=True)

## removendo colunas com todos os valores iguais 

df = df.drop(coluna_values_unicos(df),axis=1)

## colocando o nome dos países pela função e criando uma nova coluna

df['Country Name'] = df['Country Code'].apply(country_name)

## criando uma coluna com o nome das cores

df['Color Name'] = df['Rating color'].apply(color_name)

## removendo linhas duplicadas

df = df.drop_duplicates().reset_index(drop=True)

## renomeando o nome das colunas 

df = rename_columns(df)

## categoriazando as cozinhas por apenas um tipo 

df["cuisines"] = df.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])

## usando a função de categorização para comida

df['price_range_name'] = df['price_range'].apply(create_price_tye)

#============================================== Layout Streamlit ========================================================================

st.set_page_config(page_title='📊 Main Page',layout='wide')

#====================================================Sidebar==================================================================================

# abrindo a imagem do logo

image = Image.open('logo.png')

st.sidebar.image(image,width=120,use_column_width=True)

# criando divisão entre as partes do sidebar

st.sidebar.markdown("""---------------------------------------------------------------------------------------------""")

# criação dos filtros 

st.sidebar.markdown('# Filtros')
st.sidebar.caption(':white[Escolha os países que deseja visualizar os restaurantes]')

## criação do multiselect filtro país

restaurant_option = st.sidebar.multiselect('Escolha os Países que Deseja visualizar os Restaurantes',
                                           df['country_name'].unique(),
                                           default=['Brazil','England','Qatar','South Africa','Canada','Australia'])

## atribuição do filtro de país

df = df.loc[df['country_name'].isin(restaurant_option),:]


## criação da copy da página Main Page

st.markdown('# Fome Zero!')
st.markdown('## O Melhor lugar para encontrar seu mais novo restaurante favorito')
st.markdown('#### Temos as seguintes marcas dentro da nossa plataforma:')

# indicadores 

with st.container(): 

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1: 

        restaurantes_unicos = len(df['restaurant_id'].unique())
        col1.metric('Restaurantes\n Cadastrados',restaurantes_unicos)
        
    with col2: 
       
       paises_unicos = len(df['country_name'].unique())

       col2.metric('Países \ncadastrados',paises_unicos)
    
    with col3: 
       
       cidades_unicas = len(df['city'].unique())

       col3.metric('Cidades Cadastradas',cidades_unicas)
    
    with col4: 
       
        total_avaliacoes = df['votes'].sum()
        col4.metric('Avaliações Feitas',total_avaliacoes)
    
    with col5: 
       
       tipos_culinarias = df['cuisines'].nunique()
       col5.metric('Tipos de Culinárias',tipos_culinarias)

with st.container(): 
   
   mapa = folium.Map()
   marker_cluster = MarkerCluster().add_to(mapa)
   
   for index,info_location in df.iterrows(): 

        pop_up_text = (f"<strong>{info_location['restaurant_name']}</strong>"
                    f"<br><br>Price: {info_location['average_cost_for_two']} ({info_location['currency']}) para dois"
                    f"<br>Type: {info_location['cuisines']}<br>Aggregate Rating: {info_location['aggregate_rating']}/5.0")
    
        cor_restaurante = info_location['color_name']

        folium.Marker([info_location['latitude'],info_location['longitude']],
                  popup=folium.Popup(pop_up_text,max_width=4500),
                  icon=folium.Icon(color=cor_restaurante,icon='home')).add_to(marker_cluster)
   
   folium_static(mapa,width=897,height=600)