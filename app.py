import streamlit as st
import pandas as pd
import altair as alt

def tabela_cruzada(df, linha, coluna):
    tabela_cruzada = pd.crosstab(df[linha], df[coluna])
    return tabela_cruzada

st.title("Mapeamento do Futuro Analisando as Tendências Globais dos Jogos")

uploaded_file = st.file_uploader("Selecione o arquivo CSV", type=["csv"])
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.write("Arquivo carregado com sucesso!")  # Mensagem de sucesso
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
                # Criar gráfico de dispersão usando Altair
                chart = alt.Chart(df).mark_circle(size=60).encode(
                    x=coluna_x,
                    y=coluna_y,
                    tooltip=[coluna_x, coluna_y]
                ).interactive()
                st.altair_chart(chart, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")  # Mensagem de erro