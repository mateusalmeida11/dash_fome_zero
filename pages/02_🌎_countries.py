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
   
# função para plotar gráfico de barros por país: 

def bar_plotly_country(df,dimensao,operation): 

    # vamos fazer condicionais de acordo com cada operação que temos disponível

    if operation == 'quantidade' and dimensao != 'city':

        df_aux = df.loc[:,[dimensao,'country_name']].groupby('country_name').count().sort_values(dimensao,ascending=False).reset_index()

    elif operation == 'quantidade' and dimensao == 'city': 
    
        df_aux = df.loc[:,[dimensao,'country_name']].groupby('country_name').nunique().sort_values(dimensao,ascending=False).reset_index()

    else: 
        df_aux = df.loc[:,[dimensao,'country_name']].groupby('country_name').mean().sort_values(dimensao,ascending=False).reset_index()

    # definindo duas casas decimais para todo dataframe

    df_aux = df_aux.round(2)

    ## plotando o gráfico

    fig = px.bar(df_aux,x='country_name',y=dimensao)

    # trabalhando na estilização do design

    fig.update_traces(text=df_aux[dimensao],textposition='inside')

    fig.update_layout({'plot_bgcolor':'black','paper_bgcolor':'black','font':{'color':'white'}})

    return fig
   
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

st.set_page_config(page_title='🌎 Countries',layout='wide')

#====================================================Sidebar==================================================================================

# abrindo a imagem do logo

image = Image.open('logo.png')

st.sidebar.image(image,width=120,use_column_width=True)

# criando divisão entre as partes do sidebar

st.sidebar.markdown("""---------------------------------------------------------------------------------------------""")

# criação dos filtros 

st.sidebar.markdown('# Filtros')

## criação do multiselect filtro país

restaurant_option = st.sidebar.multiselect('Escolha os Países que Deseja visualizar os Restaurantes',
                                           df['country_name'].unique(),
                                           default=['Brazil','England','Qatar','South Africa','Canada','Australia'])

## atribuição do filtro de país

df = df.loc[df['country_name'].isin(restaurant_option),:]

#====================================================Parte Central================================================================================

## criação da copy da página central dos países: 

st.markdown('# 🌎 Visão Países')

## container do gráfico quantidade de restaurantes registrados por país 

with st.container(): 

    df_aux = df.loc[:,['restaurant_id','country_name']].groupby('country_name').count().sort_values('restaurant_id',ascending=False).reset_index()
   
    fig = px.bar(df_aux,x='country_name',y='restaurant_id',title='Quantidade de Restaurantes por Países',labels={'country_name':'Paises','restaurant_id':'Quantidade de restaurantes'})

    fig.update_traces(text=df_aux['restaurant_id'],textposition='inside')
    
    fig.update_layout({'font':{'color':'white'}},title_x=0.4)

    st.plotly_chart(fig,use_container_width=True)

 
## container do gráfico quantidade de cidades registradas por país
   
with st.container(): 
    
   # 1) Criando o gráfico: 

   fig = bar_plotly_country(df,'city','quantidade')

   # 2) Fazendo os updates necessários: 

   fig.update_layout({'title':'Quantidade de Cidades Registradas por País','title_x':0.4,'xaxis_title':'Paises',
                      'yaxis_title':'Quantidade de Cidades','font':{'color':'white'}},paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
   
   ## container dos dois gráficos de média, tanto de avaliações feitas por países como preço de um prato

   st.plotly_chart(fig,use_container_width=True)
   
with st. container(): 
   
   col1, col2 = st.columns(2)

   with col1: 

      fig = bar_plotly_country(df,'votes','media')

      fig.update_layout({'title':'Média de Avaliações Feitas por País','xaxis_title':'Paises',
                         'yaxis_title':'Quantidade de Avaliações','title_x':0.25,'width':400,
                         'font':{'color':'white'}},paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')

      col1.plotly_chart(fig,use_container_width=True)

   with col2: 

      fig = bar_plotly_country(df,'average_cost_for_two','media')

      fig.update_layout({'title':'Média de Preço de prato para duas pessoas por País','xaxis_title':'Paises',
                         'yaxis_title':'Preço de prato para duas Pessoas','width':400,
                         'font':{'color':'white'}},paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',title_x=0.15)

      col2.plotly_chart(fig,use_container_width=True)