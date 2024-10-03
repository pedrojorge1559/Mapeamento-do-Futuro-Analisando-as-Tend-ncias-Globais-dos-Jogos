import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV

# Carregando o arquivo CSV
df = pd.read_csv('vgsales_com_clusters.csv')

st.title("Análise de Vendas de Jogos")

st.subheader("Primeiras 5 linhas do DataFrame")
st.write(df.head())

st.subheader("Quantidade de Jogos por Gênero")
genero_counts = df['Genre'].value_counts().reset_index()
genero_counts.columns = ['Gênero', 'Quantidade']
bar_chart = alt.Chart(genero_counts).mark_bar().encode(
    x=alt.X('Gênero', sort='-y'),
    y='Quantidade',
    color='Gênero'
).properties(title='Quantidade de Jogos por Gênero')
st.altair_chart(bar_chart, use_container_width=True)

st.subheader("Gráfico de Dispersão")
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
                    alt.value('blue'),
                    alt.value('red')
                ),
                tooltip=[coluna_x, coluna_y, 'Cluster']
            ).interactive()
            st.altair_chart(chart, use_container_width=True)
        else:
            st.error("A coluna 'Cluster' não foi encontrada no DataFrame.")  # Mensagem de erro
else:
    st.error("O DataFrame deve conter pelo menos duas colunas numéricas para o gráfico de dispersão.")

st.subheader("Simulação Empresarial")

empresas = df['Publisher'].unique()
empresa_selecionada = st.selectbox("Selecione a empresa", options=empresas)

df_empresa = df[df['Publisher'] == empresa_selecionada]

generos = df['Genre'].unique()
genero_selecionado = st.selectbox("Selecione o gênero", options=generos)

if st.button("Executar Simulação"):
    if not df_empresa.empty:
        df_genero = df_empresa[df_empresa['Genre'] == genero_selecionado]
        
        if not df_genero.empty:
            X = df_genero[['Year', 'NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']]
            y = df_genero['Global_Sales']
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            param_grid_rna = {
                'hidden_layer_sizes': [(100,), (100, 50), (50, 50)],
                'max_iter': [500, 1000],
            }
            grid_search_rna = GridSearchCV(MLPRegressor(random_state=42), param_grid_rna, cv=5)
            grid_search_rna.fit(X_train_scaled, y_train)
            rna = grid_search_rna.best_estimator_

            param_grid_tree = {
                'max_depth': [None, 10, 20, 30],
                'min_samples_split': [2, 5, 10],
            }
            grid_search_tree = GridSearchCV(DecisionTreeRegressor(random_state=42), param_grid_tree, cv=5)
            grid_search_tree.fit(X_train, y_train)
            arvore = grid_search_tree.best_estimator_

            previsoes_rna = rna.predict(X_test_scaled)
            previsoes_arvore = arvore.predict(X_test)

            media_previsao_rna = np.mean(previsoes_rna)
            media_previsao_arvore = np.mean(previsoes_arvore)

            st.success(f"Probabilidade de sucesso para o gênero '{genero_selecionado}' com a empresa '{empresa_selecionada}':")
            st.write(f"RNA: {media_previsao_rna:.2f} vendas previstas")
            st.write(f"Árvore de Decisão: {media_previsao_arvore:.2f} vendas previstas")
        else:
            st.error(f"Nenhum jogo encontrado para o gênero '{genero_selecionado}' nesta empresa.")
    else:
        st.error(f"A empresa '{empresa_selecionada}' não possui jogos registrados.")

st.subheader("Métricas da Empresa")

vendas_regionais = df_empresa[['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']].sum().reset_index()
vendas_regionais.columns = ['Região', 'Total de Vendas']
bar_chart_regionais = alt.Chart(vendas_regionais).mark_bar().encode(
    x='Região',
    y='Total de Vendas',
    color='Região'
).properties(title='Total de Vendas por Região')
st.altair_chart(bar_chart_regionais, use_container_width=True)

genero_vendas = df_empresa.groupby('Genre')['Global_Sales'].sum().reset_index()
genero_vendas = genero_vendas.sort_values(by='Global_Sales', ascending=False)
bar_chart_generos = alt.Chart(genero_vendas).mark_bar().encode(
    x=alt.X('Genre', sort='-y'),
    y='Global_Sales',
    color='Genre'
).properties(title='Total de Vendas por Gênero')
st.altair_chart(bar_chart_generos, use_container_width=True)