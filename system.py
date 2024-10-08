import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV

# Carregando o arquivo CSV
df = pd.read_csv('Arquivos Gerados/vgsales_com_clusters.csv')

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

st.subheader("Métricas da Empresa")

# 1) Seleção da empresa
st.subheader("Seleção da Empresa")
empresas = df['Publisher'].unique()
empresa_simulada = st.selectbox("Selecione a empresa", options=empresas)

# 2) Seleção do gênero
st.subheader("Seleção do Gênero")
generos = df['Genre'].unique()
genero_simulado = st.selectbox("Selecione o gênero", options=generos)

# 3) Gráfico de barras da quantidade de jogos por gênero da empresa selecionada
st.subheader("Gráfico de Barras da Quantidade de Jogos por Gênero da Empresa Selecionada")
df_empresa = df[df['Publisher'] == empresa_simulada]
jogos_por_genero = df_empresa['Genre'].value_counts().reset_index()
jogos_por_genero.columns = ['Gênero', 'Quantidade']

bar_chart_jogos = alt.Chart(jogos_por_genero).mark_bar().encode(
    x=alt.X('Gênero', sort='-y'),
    y='Quantidade',
    color='Gênero'
).properties(title='Quantidade de Jogos por Gênero da Empresa')
st.altair_chart(bar_chart_jogos, use_container_width=True)

# 4) Gráfico de vendas regionais por gênero (agora puxando do dataframe inteiro)
st.subheader("Gráfico de Vendas Regionais por Gênero")
vendas_regionais = df.groupby('Genre')[['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']].sum().reset_index()
vendas_regionais = vendas_regionais[vendas_regionais['Genre'] == genero_simulado]

if not vendas_regionais.empty:
    vendas_regionais_melted = vendas_regionais.melt(id_vars='Genre', var_name='Região', value_name='Total de Vendas')
    bar_chart_vendas_regionais = alt.Chart(vendas_regionais_melted).mark_bar().encode(
        x='Região',
        y='Total de Vendas',
        color='Região'
    ).properties(title=f'Total de Vendas Regionais para o Gênero "{genero_simulado}"')
    st.altair_chart(bar_chart_vendas_regionais, use_container_width=True)
else:
    st.warning(f"Nenhum jogo encontrado no gênero '{genero_simulado}' no mercado.")

# 5) Gráfico de vendas globais por gênero
vendas_globais = df.groupby('Genre')['Global_Sales'].sum().reset_index()
vendas_globais = vendas_globais[vendas_globais['Genre'] == genero_simulado]

if not vendas_globais.empty:
    bar_chart_vendas_globais = alt.Chart(vendas_globais).mark_bar().encode(
        x='Genre',
        y='Global_Sales',
        color='Genre'
    ).properties(title=f'Total de Vendas Globais para o Gênero "{genero_simulado}"')
    st.altair_chart(bar_chart_vendas_globais, use_container_width=True)
else:
    st.warning(f"Nenhum jogo encontrado no gênero '{genero_simulado}' no mercado.")

# 6) Algoritmo de RNA e Árvore de Decisão para a empresa simulada
st.subheader("Algoritmo de RNA e Árvore de Decisão para a Empresa Simulada")
if not df_empresa[df_empresa['Genre'] == genero_simulado].empty:
    df_genero_empresa = df_empresa[df_empresa['Genre'] == genero_simulado]
    X = df_genero_empresa[['Year', 'NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']]
    y = df_genero_empresa['Global_Sales']

    if len(X) > 1:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Normalizando os dados
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Hiperparâmetros para RNA
        param_grid_rna = {
            'hidden_layer_sizes': [(100,), (100, 50), (50, 50)],
            'max_iter': [500, 1000],
        }
        grid_search_rna = GridSearchCV(MLPRegressor(random_state=42), param_grid_rna, cv=5)
        grid_search_rna.fit(X_train_scaled, y_train)
        rna = grid_search_rna.best_estimator_

        # Hiperparâmetros para Árvore de Decisão
        param_grid_tree = {
            'max_depth': [None, 10, 20, 30],
            'min_samples_split': [2, 5, 10],
        }
        grid_search_tree = GridSearchCV(DecisionTreeRegressor(random_state=42), param_grid_tree, cv=5)
        grid_search_tree.fit(X_train, y_train)
        arvore = grid_search_tree.best_estimator_

        # Fazendo previsões
        previsoes_rna = rna.predict(X_test_scaled)
        previsoes_arvore = arvore.predict(X_test)

        # Gráfico de vendas reais
        plt.figure(figsize=(10, 5))
        plt.plot(y_test.values, label='Vendas Reais', color='blue')
        plt.plot(previsoes_rna, label='Previsões RNA', color='orange')
        plt.plot(previsoes_arvore, label='Previsões Árvore de Decisão', color='green')
        plt.legend()
        plt.title('Comparação de Vendas Reais e Previsões')
        plt.xlabel('Amostras do Conjunto de Teste')
        plt.ylabel('Vendas')
        st.pyplot(plt)

        # Identificando o melhor mercado com base nas previsões
        mercados = ['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']
        vendas_previstas_rna = {mercado: np.sum(previsoes_rna) for mercado in mercados}
        vendas_previstas_arvore = {mercado: np.sum(previsoes_arvore) for mercado in mercados}

        melhor_mercado_rna = max(vendas_previstas_rna, key=vendas_previstas_rna.get)
        melhor_mercado_arvore = max(vendas_previstas_arvore, key=vendas_previstas_arvore.get)

        st.write(f"Melhor mercado com base nas previsões RNA: {melhor_mercado_rna} com vendas previstas de {vendas_previstas_rna[melhor_mercado_rna]:.2f}")
        st.write(f"Melhor mercado com base nas previsões Árvore de Decisão: {melhor_mercado_arvore} com vendas previstas de {vendas_previstas_arvore[melhor_mercado_arvore]:.2f}")
    else:
        st.error("Não há dados suficientes para realizar a simulação interna.")
else:
    st.warning(f"A empresa '{empresa_simulada}' nunca lançou jogos no gênero '{genero_simulado}'. Análise interna não pode ser realizada.")

# 7) Algoritmo de RNA e Árvore de Decisão para o mercado geral
st.subheader("Algoritmo de RNA e Árvore de Decisão para o Mercado Geral")
df_genero_mercado = df[df['Genre'] == genero_simulado]
if not df_genero_mercado.empty:
    X_mercado = df_genero_mercado[['Year', 'NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']]
    y_mercado = df_genero_mercado['Global_Sales']

    if len(X_mercado) > 1:
        X_train_mercado, X_test_mercado, y_train_mercado, y_test_mercado = train_test_split(X_mercado, y_mercado, test_size=0.2, random_state=42)

        # Normalizando os dados
        scaler_mercado = StandardScaler()
        X_train_scaled_mercado = scaler_mercado.fit_transform(X_train_mercado)
        X_test_scaled_mercado = scaler_mercado.transform(X_test_mercado)

        # Hiperparâmetros para RNA
        param_grid_rna = {
            'hidden_layer_sizes': [(100,), (100, 50), (50, 50)],
            'max_iter': [500, 1000],
        }
        grid_search_rna_mercado = GridSearchCV(MLPRegressor(random_state=42), param_grid_rna, cv=5)
        grid_search_rna_mercado.fit(X_train_scaled_mercado, y_train_mercado)
        rna_mercado = grid_search_rna_mercado.best_estimator_

        # Hiperparâmetros para Árvore de Decisão
        param_grid_tree = {
            'max_depth': [None, 10, 20, 30],
            'min_samples_split': [2, 5, 10],
        }
        grid_search_tree_mercado = GridSearchCV(DecisionTreeRegressor(random_state=42), param_grid_tree, cv=5)
        grid_search_tree_mercado.fit(X_train_mercado, y_train_mercado)
        arvore_mercado = grid_search_tree_mercado.best_estimator_

        # Fazendo previsões
        previsoes_rna_mercado = rna_mercado.predict(X_test_scaled_mercado)
        previsoes_arvore_mercado = arvore_mercado.predict(X_test_mercado)

        # Gráfico de vendas reais
        plt.figure(figsize=(10, 5))
        plt.plot(y_test_mercado.values, label='Vendas Reais', color='blue')
        plt.plot(previsoes_rna_mercado, label='Previsões RNA', color='orange')
        plt.plot(previsoes_arvore_mercado, label='Previsões Árvore de Decisão', color='green')
        plt.legend()
        plt.title('Comparação de Vendas Reais e Previsões (Mercado Geral)')
        plt.xlabel('Amostras do Conjunto de Teste')
        plt.ylabel('Vendas')
        
        # Exibindo o gráfico no Streamlit
        st.pyplot(plt)

        # Identificando o melhor mercado com base nas previsões
        mercados = ['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']
        vendas_previstas_rna_mercado = {mercado: np.sum(previsoes_rna_mercado) for mercado in mercados}
        vendas_previstas_arvore_mercado = {mercado: np.sum(previsoes_arvore_mercado) for mercado in mercados}

        melhor_mercado_rna_mercado = max(vendas_previstas_rna_mercado, key=vendas_previstas_rna_mercado.get)
        melhor_mercado_arvore_mercado = max(vendas_previstas_arvore_mercado, key=vendas_previstas_arvore_mercado.get)

        st.write(f"Melhor mercado com base nas previsões RNA (Mercado Geral): {melhor_mercado_rna_mercado} com vendas previstas de {vendas_previstas_rna_mercado[melhor_mercado_rna_mercado]:.2f}")
        st.write(f"Melhor mercado com base nas previsões Árvore de Decisão (Mercado Geral): {melhor_mercado_arvore_mercado} com vendas previstas de {vendas_previstas_arvore_mercado[melhor_mercado_arvore_mercado]:.2f}")
    else:
        st.error("Não há dados suficientes para realizar a simulação no mercado geral.")
else:
    st.warning(f"Nenhum jogo encontrado no gênero '{genero_simulado}' no mercado geral.")