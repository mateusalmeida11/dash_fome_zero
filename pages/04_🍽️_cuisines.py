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

## função para definir os tipos de culinária

def tipos_de_culinarias(df,cozinha,classification=True): 

    df1 = (df.loc[(df['cuisines']==cozinha),['restaurant_id','restaurant_name','aggregate_rating']]
                         .sort_values(['aggregate_rating','restaurant_id'],ascending=[classification,True]))
    restaurant_name = df1.iloc[0,1]

    id_rest = df1.index[0]

    aggregate_rating = df.loc[(df.index==id_rest),['aggregate_rating']].iloc[0,0]

    pais = df.loc[(df.index==id_rest),['country_name']].iloc[0,0]

    average_cost_for_two = df.loc[(df.index==id_rest),['average_cost_for_two']].iloc[0,0]

    currency = df.loc[(df.index==id_rest),['currency']].iloc[0,0]

    city = df.loc[(df.index==id_rest),['city']].iloc[0,0]

    return restaurant_name, aggregate_rating, pais, average_cost_for_two, currency,city
   
# abrindo o arquivo para gerar o dataframe

## caminho do arquivo: 

arquivo = Path.cwd()/'dataset'/'zomato.csv'

print(arquivo)

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

st.set_page_config(page_title='🍽️ Visão Tipos de Cozinhas',layout='wide')

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

## criação do slider para definir a quantidade de restaurantes que o usuário deseja visualizar 

qtd_restaurantes = st.sidebar.slider('Selecione a quantidade de Restaurantes que Deseja Visualizar',0,20,10)

## filtro para selecionar os tiposd e culinária 

cuisines_options = st.sidebar.multiselect('Escolha o Tipo de Culinária',
                                          ((df.loc[:,'cuisines'].unique().tolist())),
                                          default=['Home-made','BBQ','Japanese','Brazilian','Arabian','American','Italian']
                                          )

df1 = df.loc[df['cuisines'].isin(cuisines_options),:]

## atribuição do filtro de país

df1 = df.loc[df['country_name'].isin(restaurant_option),:]

## atribuição do filtro quantidade de restaurantes ao dataframe: 

df1 = df.head(qtd_restaurantes)

#====================================================Parte Central================================================================================

## criação da copy da página central das cozinhas:

st.markdown('# 🍽️ Visão Tipos de Cozinhas')
st.markdown('## Melhores Restaurantes dos Principais Tipos Culinários')

with st.container(): 

    col1,col2,col3,col4,col5 = st.columns(5)

    with col1: 

        restaurant_name = tipos_de_culinarias(df,'Italian',False)[0]
        aggregate_rating = tipos_de_culinarias(df,'Italian',False)[1]
        pais = tipos_de_culinarias(df,'Italian',False)[2]
        average_cost_for_two = tipos_de_culinarias(df,'Italian',False)[3]
        curency = tipos_de_culinarias(df,'Italian',False)[4]
        city = tipos_de_culinarias(df,'Italian',False)[5]

        st.metric(label=f'Italian: {restaurant_name}',value=f'{aggregate_rating}/5.0',
                  help=(f'País: {pais}\n\nCidade: {city}\n\nMédia prato para dois: {average_cost_for_two} ({curency})'))
        
    with col2: 

        restaurant_name = tipos_de_culinarias(df,'American',False)[0]
        aggregate_rating = tipos_de_culinarias(df,'American',False)[1]
        pais = tipos_de_culinarias(df,'American',False)[2]
        average_cost_for_two = tipos_de_culinarias(df,'Italian',False)[3]
        curency = tipos_de_culinarias(df,'American',False)[4]
        city = tipos_de_culinarias(df,'American',False)[5]

        st.metric(label=f'American: {restaurant_name}',value=f'{aggregate_rating}/5.0',
                  help=(f'País: {pais}\n\nCidade: {city}\n\nMédia prato para dois: {average_cost_for_two} ({curency})'))

    with col3: 

        restaurant_name = tipos_de_culinarias(df,'Arabian',False)[0]
        aggregate_rating = tipos_de_culinarias(df,'Arabian',False)[1]
        pais = tipos_de_culinarias(df,'Arabian',False)[2]
        average_cost_for_two = tipos_de_culinarias(df,'Arabian',False)[3]
        curency = tipos_de_culinarias(df,'Arabian',False)[4]
        city = tipos_de_culinarias(df,'Arabian',False)[5]

        st.metric(label=f'Arabian: {restaurant_name}',value=f'{aggregate_rating}/5.0',
                  help=(f'País: {pais}\n\nCidade: {city}\n\nMédia prato para dois: {average_cost_for_two} ({curency})'))
        
    with col4: 

        restaurant_name = tipos_de_culinarias(df,'Japanese',False)[0]
        aggregate_rating = tipos_de_culinarias(df,'Japanese',False)[1]
        pais = tipos_de_culinarias(df,'Japanese',False)[2]
        average_cost_for_two = tipos_de_culinarias(df,'Japanese',False)[3]
        curency = tipos_de_culinarias(df,'Japanese',False)[4]
        city = tipos_de_culinarias(df,'Japanese',False)[5]

        st.metric(label=f'Japanese: {restaurant_name}',value=f'{aggregate_rating}/5.0',
                  help=(f'País: {pais}\n\nCidade: {city}\n\nMédia prato para dois: {average_cost_for_two} ({curency})'))
        
    with col5: 

        restaurant_name = tipos_de_culinarias(df,'Brazilian',False)[0]
        aggregate_rating = tipos_de_culinarias(df,'Brazilian',False)[1]
        pais = tipos_de_culinarias(df,'Brazilian',False)[2]
        average_cost_for_two = tipos_de_culinarias(df,'Brazilian',False)[3]
        curency = tipos_de_culinarias(df,'Brazilian',False)[4]
        city = tipos_de_culinarias(df,'Brazilian',False)[5]

        st.metric(label=f'Brazilian: {restaurant_name}',value=f'{aggregate_rating}/5.0',
                  help=(f'País: {pais}\n\nCidade: {city}\n\nMédia prato para dois: {average_cost_for_two} ({curency})'))
        
with st.container(): 

    st.title(f'Top {qtd_restaurantes} Restaurantes')

    top_restaurants = (df.loc[(df['country_name'].isin(restaurant_option) & (df['cuisines'].isin(cuisines_options))),['restaurant_id','restaurant_name','country_name','city','cuisines','average_cost_for_two','aggregate_rating','votes']]
                         .sort_values(['aggregate_rating','restaurant_id'],ascending=[False,True])
                         .head(qtd_restaurantes))
    
    st.dataframe(top_restaurants)

with st.container():

    col1, col2 = st.columns(2)

    with col1: 

        df_aux = (df.loc[(df['country_name'].isin(restaurant_option)),['cuisines','aggregate_rating']]
                    .groupby('cuisines')
                    .mean()
                    .sort_values('aggregate_rating',ascending=False)
                    .reset_index()
                    .head(qtd_restaurantes))

        df_aux = df_aux.round(2)

        fig = px.bar(df_aux,x='cuisines',y='aggregate_rating',labels={'cuisines':'Tipos de Culinária','aggregate_rating':'Média da Avaliação Média'})

        fig.update_traces(text=df_aux['aggregate_rating'],textposition='inside')

        fig.update_layout(title=f'Top {qtd_restaurantes} melhores tipos de culinária',
                      title_x=0.27
                      ,paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                      font={'color':'white'})
        
        st.plotly_chart(fig,use_container_width=True)

    with col2: 

        df_aux = (df.loc[(df['country_name'].isin(restaurant_option)),['cuisines','aggregate_rating']]
                    .groupby('cuisines')
                    .mean()
                    .sort_values('aggregate_rating',ascending=True)
                    .reset_index().head(qtd_restaurantes))
        
        df_aux = df_aux.round(2)

        fig = px.bar(df_aux,x='cuisines',y='aggregate_rating',labels={'cuisines':'Tipos de Culinária','aggregate_rating':'Média da Avaliação Média'})

        fig.update_traces(text=df_aux['aggregate_rating'],textposition='inside')

        fig.update_layout(title=f'Top {qtd_restaurantes} piores tipos de culinária',
                      title_x=0.27,paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                      font={'color':'white'})
        
        st.plotly_chart(fig,use_container_width=True)