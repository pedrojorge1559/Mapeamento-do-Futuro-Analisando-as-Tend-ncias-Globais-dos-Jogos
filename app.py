import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def tabela_cruzada(df, linha, coluna):
    tabela_cruzada = pd.crosstab(df[linha], df[coluna])
    return tabela_cruzada

def heat_map(df, linha=None, coluna=None):
    if linha is not None and coluna is not None:
        df = df.pivot_table(index=linha, columns=coluna, aggfunc='size', fill_value=0)

    heatmap = sns.heatmap(df, annot=True, fmt='g', cmap='PuRd', annot_kws={'color': 'black'}, linewidths=1)
    plt.title(f'Mapa de calor: {linha} vs {coluna}')
    plt.xlabel(linha)
    plt.ylabel(coluna)
    return plt

def grafico_serie_historica(df, coluna, ano_inicial, ano_final):
    df_filtrado = df[(df['Year'] >= ano_inicial) & (df['Year'] <= ano_final)]
    plt.figure(figsize=(10, 5))
    plt.plot(df_filtrado['Year'], df_filtrado[coluna], marker='o')
    plt.title('Gráfico de Série Histórica')
    plt.xlabel('Ano')
    plt.ylabel(coluna)
    plt.grid()
    return plt

def grafico_dispersao(df, coluna_x, coluna_y):
    plt.figure(figsize=(10, 5))
    plt.scatter(df[coluna_x], df[coluna_y], alpha=0.7)
    plt.title('Gráfico de Dispersão')
    plt.xlabel(coluna_x)
    plt.ylabel(coluna_y)
    plt.grid()
    return plt

st.title("Mapeamento do Futuro Analisando as Tendências Globais dos Jogos")

uploaded_file = st.file_uploader("Selecione o arquivo CSV", type=["csv"])
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.write("Arquivo carregado com sucesso!")  # Mensagem de sucesso
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")  # Mensagem de erro

    colunas = df.columns.tolist()
    coluna1, coluna2 = st.selectbox("Selecione as colunas para a tabela cruzada", options=colunas, index=(0, 1))
    if st.button("Executar Tabela Cruzada"):
        st.table(tabela_cruzada(df, coluna1, coluna2))

    coluna1, coluna2 = st.selectbox("Selecione as colunas para o heatmap", options=colunas, index=(0, 1))
    if st.button("Executar Heatmap"):
        try:
            st.pyplot(heat_map(df, coluna1, coluna2))
        except Exception as e:
            st.error(f"Erro ao gerar o heatmap: {e}")

    if 'Year' in df.columns:
        ano_inicial, ano_final = st.select_slider("Selecione o período de anos", options=df['Year'].unique(), value=(df['Year'].min(), df['Year'].max()))
        if st.button("Executar Grafico de Serie Historica"):
            try:
                st.pyplot(grafico_serie_historica(df, 'Year', ano_inicial, ano_final))
            except Exception as e:
                st.error(f"Erro ao gerar o gráfico de série histórica: {e}")

    colunas_numericas = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    coluna_x, coluna_y = st.selectbox("Selecione as colunas para o grafico de dispersão", options=colunas_numericas, index=(0, 1))
    if st.button("Executar Grafico de Dispersão"):
        try:
            st.pyplot(grafico_dispersao(df, coluna_x, coluna_y))
        except Exception as e:
            st.error(f"Erro ao gerar o gráfico de dispersão: {e}")
