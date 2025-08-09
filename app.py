import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

#Configuração da página, com título, ícone e layout
st.set_page_config(
    page_title="Análise de salários na área de dados",
    page_icon=":bar_chart:",
    layout="wide",
    )

#Carregamento dos dados
df= pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")


#--- Filtros ---

#Barra de filtros
st.sidebar.header("Filtros")

#Filtro de modadalidade de trabalho
contratos_disponiveis = sorted(df['remoto'].unique()) #Lista as modalidades
contratos_selecionados = st.sidebar.selectbox("Modalidade de Trabalho", contratos_disponiveis)

#Filtro de ano
anos_disponiveis = sorted(df['ano'].unique()) #Lista os anos
ano_selecionado = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

#Filtro de senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique()) #Lista as senioridades
senioridade_selecionada = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

#Filtro de tamanho da empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique()) #Lista os tamanhos
tamanho_selecionado = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)


#--- Filtragem do DF ---

df_filtrado = df[
    (df['ano'].isin(ano_selecionado)) &
    (df['senioridade'].isin(senioridade_selecionada)) &
    (df['tamanho_empresa'].isin(tamanho_selecionado)) &
    (df['remoto']==(contratos_selecionados))
]

#--- Conteúdo principal ---
st.title("Análise Global de Salários na Área de Dados")
st.markdown("Explore as informações salariais de profissionais da área de dados ao redor do mundo.\n\nUtilize os filtros à esquerda para personalizar a visualização dos dados.")

#--- Métricas principais ---
st.subheader('**Métricas gerais (salários anuais e dolarizados)**')

#Se o df_filtrado não estiver vazio, calcula as métricas; caso contrário, define todas as métricas como zero ou "N/A"
#Feito com int e sem int
if not df_filtrado.empty:
    salario_medio = int(df_filtrado['usd'].mean())
    salario_mediano = int(df_filtrado['usd'].median())
    salario_maximo = df_filtrado['usd'].max()
    salario_minimo = df_filtrado['usd'].min()
    total_registros = df_filtrado.shape[0]
    cargo_mais_popular = df_filtrado['cargo'].mode()[0]
    local_mais_popular = df_filtrado['residencia_iso3'].mode()[0]
    paises_unicos = df_filtrado['residencia_iso3'].nunique()
    salarios_analisados = df_filtrado['usd'].count()
else:
    salario_medio, salario_mediano, salario_maximo, salario_minimo, total_registros, cargo_mais_popular = 0, 0, 0, 0, 0, "N/A", "N/A", 0, 0

#Define a quantidade de colunas na página e define seus valores
#Forma padrão de largura das colunas = set.columns(8)
#Forma de editar a largura individualmente = st.columns((1, 1, 1, 1, 2, 2, 1, 1))
col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(([1, 1, 1, 1, 1.5, 1, 1, 1]))
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário mediano", f"${salario_mediano:,.0f}")
col3.metric("Salário máximo", f"${salario_maximo:,.0f}")
col4.metric("Salário mínimo", f"${salario_minimo:,.0f}")
col5.metric("Cargo mais popular", cargo_mais_popular)
col6.metric("Local mais popular", local_mais_popular)
col7.metric("Países analisados", f"{paises_unicos:,}")
col8.metric("Salários analisados", f"{salarios_analisados:,}")

#Adiciona quebra de linha
st.markdown("---")

#--- Gráficos ---

#Definição das colunas
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        #Organiza por decrescente e pega os 5 maiores salários médios por cargo
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(5).sort_values(ascending=True).reset_index()
        #Puxa o gráfico de barras
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual', 'cargo': ''}
        )
        grafico_cargos.update_traces(marker_color='rgb(227, 32, 51)', marker_line_color='rgb(240,240,240)', marker_line_width=1, opacity=0.75)
        grafico_cargos.update_layout(title_x=0.5, yaxis={'categoryorder':'total ascending'})
        #Comando para exibir o gráfico
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins= 80,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        #---Configurações do gráfico---
        #Define o título do gráfico. 1= direita, 0.5 = centro, 0 = esquerda
        grafico_hist.update_layout(title_x=0.5)
        grafico_hist.update_traces(marker_color='rgb(227, 32, 51)', marker_line_color='rgb(240,240,240)', marker_line_width=1, opacity=0.75)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3 = st.columns(1)

with col_graf3[0]:
    if not df_filtrado.empty:
        
        #Pega a média do salário por país
        media_ds_pais = df_filtrado.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='reds',
            title='Salário médio por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.5)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

#--- Tabela de dados abertos---
st.subheader("**Dados detalhados**")
st.dataframe(df_filtrado)
    


