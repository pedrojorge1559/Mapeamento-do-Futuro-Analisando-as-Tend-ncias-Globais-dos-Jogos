import streamlit as st
import pandas as pd
import altair as alt

def tabela_cruzada(df, linha, coluna):
    tabela_cruzada = pd.crosstab(df[linha], df[coluna])
    return tabela_cruzada

st.title("Mapeamento do Futuro Analisando as Tendências Globais dos Jogos")

# Carregando o arquivo CSV
df = pd.read_csv('vgsales_com_clusters.csv')
st.write(f"Arquivo: {df.name} carregado com sucesso!")  # Mensagem de sucesso
st.write(df.head())

colunas = df.columns.tolist()

# Tabela Cruzada
coluna1 = st.selectbox("Selecione a coluna para a tabela cruzada (linha)", options=colunas)
coluna2 = st.selectbox("Selecione a coluna para a tabela cruzada (coluna)", options=colunas)
if st.button("Executar Tabela Cruzada"):
    st.table(tabela_cruzada(df, coluna1, coluna2))

# Gráfico de Série Histórica
if 'Year' in df.columns:
    ano_inicial, ano_final = st.select_slider("Selecione o período de anos", options=df['Year'].unique(), value=(df['Year'].min(), df['Year'].max()))
    df_filtrado = df[(df['Year'] >= ano_inicial) & (df['Year'] <= ano_final)]
    if st.button("Executar Gráfico de Série Histórica"):
        st.line_chart(df_filtrado.set_index('Year')[colunas[0]])  

# Gráfico de Dispersão
colunas_numericas = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
if len(colunas_numericas) >= 2:
    coluna_x = st.selectbox("Selecione a coluna para o gráfico de dispersão (eixo X)", options=colunas_numericas)
    coluna_y = st.selectbox("Selecione a coluna para o gráfico de dispersão (eixo Y)", options=colunas_numericas)
    if st.button("Executar Gráfico de Dispersão"):
        if 'Cluster' in df.columns:
            chart = alt.Chart(df).mark_circle(size=60).encode(
                x=coluna_x,
                y=coluna_y,
                color=alt.condition(
                    alt.datum.Cluster == 0,
                    alt.value('red'),
                    alt.value('blue')
                ),
                tooltip=[coluna_x, coluna_y, 'Cluster']
            ).interactive()
            st.altair_chart(chart, use_container_width=True)
        else:
            st.error("A coluna 'Cluster' não foi encontrada no DataFrame.") # Mensagem de erro