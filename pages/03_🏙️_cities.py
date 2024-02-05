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

## função para plotar gráfico de barras por cidades: 

## precisamos definir o eixo_x, eixo_y, filtro_linha, operação de agregação, comparativo 

def bar_cities (df,eixo_x,eixo_y,limite_df,op_comp='nenhum',valor_comp='nenhum'):

    if op_comp == 'nenhum':

        df_aux = (df.loc[:,[eixo_x,eixo_y,'country_name']].groupby([eixo_x,'country_name'])
                    .count().sort_values([eixo_y,eixo_x],ascending=[False,True])
                    .reset_index().head(limite_df))
        
    elif op_comp == 'maior': 

        df_aux = (df.loc[(df['aggregate_rating'] >= valor_comp),[eixo_x,eixo_y,'country_name']].groupby([eixo_x,'country_name'])
                    .count().sort_values([eixo_y,eixo_x],ascending=[False,True])
                    .reset_index().head(limite_df))
        
    elif op_comp == 'menor': 

         df_aux = (df.loc[(df['aggregate_rating'] <= valor_comp),[eixo_x,eixo_y,'country_name']].groupby([eixo_x,'country_name'])
                    .count().sort_values([eixo_y,eixo_x],ascending=[False,True])
                    .reset_index().head(limite_df))       

    fig = px.bar(df_aux,x=eixo_x,y=eixo_y,color='country_name',text_auto=True,labels={eixo_x:'Cidade',eixo_y:'Restaurante','country_name':'País'})

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

st.set_page_config(page_title='🏙️ Visão Cidades',layout='wide')

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

#====================================================Parte Central================================================================================

## criação da copy da página central das cidades:

st.markdown('# 🏙️ Visão Cidades')

## container do gráfico quantidade de top 10 cidades com mais restaurantes no banco de dados 

with st.container(): 

    fig = bar_cities(df,'city','restaurant_id',10)

    fig.update_layout(title='Top 10 Cidades com mais Restaurantes na Base de Dados',title_x=0.25,paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font={'color':'white'})

    st.plotly_chart(fig,use_container_width=True)

## container responsável pelas avaliações e teremos duas colunas 
    
with st.container(): 

    col1, col2 = st.columns(2)

    with col1: 

        fig = bar_cities(df,'city','restaurant_id',7,op_comp='maior',valor_comp=4.0)

        fig.update_layout(title='Top 7 Cidades com média de avaliação acima de 4.0',title_x=0.1,paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font={'color':'white'})

        st.plotly_chart(fig,use_container_width=True) 

    with col2: 

        fig = bar_cities(df,'city','restaurant_id',7,op_comp='menor',valor_comp=2.5)

        fig.update_layout(title='Top 7 Cidades com média de avaliação abaixo de 2.5',title_x=0.1,paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font={'color':'white'})

        st.plotly_chart(fig,use_container_width=True)        

## container responsável pelas cidades com mais tipos de culinárias distintas 
        
with st.container(): 

    df_aux = (df.loc[:,['city','cuisines','country_name','restaurant_id']]
                .groupby(['city','country_name'])
                .nunique()
                .sort_values(['cuisines','restaurant_id'],ascending=[False,True]).reset_index().head(10))
    
    fig = px.bar(df_aux,x='city',y='cuisines',color='country_name',
                 text_auto=True,labels={'city':'Cidade','cuisines':'Tipos Culinários Únicos','country_name':'País'})

    fig.update_layout(title='Top 10 Cidades com mais restaurantes com tipos de culinários distintos',
                      title_x=0.1,paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                      font={'color':'white'})
    
    st.plotly_chart(fig,use_container_width=True)