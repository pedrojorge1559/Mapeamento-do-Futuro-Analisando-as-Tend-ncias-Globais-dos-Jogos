import streamlit as st
import pandas as pd
from back import tabela_cruzada, heat_map, grafico_serie_historica, grafico_dispersao


st.title("Mapeamento do Futuro Analisando as Tendências Globais dos Jogos")

uploaded_file = st.file_uploader("Selecione o arquivo CSV", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    colunas = df.columns.tolist()
    coluna1, coluna2 = st.selectboxes("Selecione as colunas para a tabela cruzada", options=colunas, index=(0, 1))
    if st.button("Executar Tabela Cruzada"):
        st.table(tabela_cruzada(df, coluna1, coluna2))

    coluna1, coluna2 = st.selectboxes("Selecione as colunas para o heatmap", options=colunas, index=(0, 1))
    if st.button("Executar Heatmap"):
        st.pyplot(heat_map(df, coluna1, coluna2))

    if 'Year' in df.columns:
        ano_inicial, ano_final = st.select_slider("Selecione o período de anos", options=df['Year'].unique(), value=(df['Year'].min(), df['Year'].max()))
        if st.button("Executar Grafico de Serie Historica"):
            st.pyplot(grafico_serie_historica(df, 'Year', ano_inicial, ano_final))

    colunas_numericas = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    coluna_x, coluna_y = st.selectboxes("Selecione as colunas para o grafico de dispersão", options=colunas_numericas, index=(0, 1))
    if st.button("Executar Grafico de Dispersão"):
        st.pyplot(grafico_dispersao(df, coluna_x, coluna_y))