import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
import matplotlib.pyplot as plt

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

# Selecionando a empresa
empresas = df['Publisher'].unique()
empresa_selecionada = st.selectbox("Selecione a empresa", options=empresas)

# Filtrando o DataFrame pela empresa selecionada
df_empresa = df[df['Publisher'] == empresa_selecionada]

# Selecionando o gênero (agora qualquer gênero)
generos = df['Genre'].unique()
genero_selecionado = st.selectbox("Selecione o gênero (pode ser novo)", options=generos)

if st.button("Executar Simulação"):
    if not df_empresa.empty:
        # Preparando os dados para o modelo
        df_genero_empresa = df_empresa[df_empresa['Genre'] == genero_selecionado]
        df_genero_mercado = df[df['Genre'] == genero_selecionado]

        # Se a empresa nunca lançou jogos nesse gênero
        if df_genero_empresa.empty:
            st.warning(f"A empresa '{empresa_selecionada}' nunca lançou jogos no gênero '{genero_selecionado}'.")
            # Usar apenas dados do mercado geral
            if not df_genero_mercado.empty:
                X = df_genero_mercado[['Year', 'NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']]
                y = df_genero_mercado['Global_Sales']
            else:
                st.error(f"Nenhum jogo encontrado no gênero '{genero_selecionado}' no mercado.")
            st.stop()
        else:
            X = df_genero_empresa[['Year', 'NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']]
            y = df_genero_empresa['Global_Sales']

        # Verificando se há dados suficientes para dividir
        if len(X) > 1:  # Deve haver pelo menos 2 amostras para dividir
            # Dividindo os dados em treino e teste
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

            # Calculando a média das previsões
            media_previsao_rna = np.mean(previsoes_rna)
            media_previsao_arvore = np.mean(previsoes_arvore)

            st.success(f"Probabilidade de sucesso para o gênero '{genero_selecionado}' com a empresa '{empresa_selecionada}':")
            st.write(f"RNA: {media_previsao_rna:.2f} vendas previstas")
            st.write(f"Árvore de Decisão: {media_previsao_arvore:.2f} vendas previstas")

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
            st.error("Não há dados suficientes para realizar a simulação.")
    else:
        st.error(f"A empresa '{empresa_selecionada}' não possui jogos registrados.")

st.subheader("Métricas da Empresa")

# Vendas regionais
vendas_regionais = df_empresa[['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']].sum().reset_index()
vendas_regionais.columns = ['Região', 'Total de Vendas']
bar_chart_regionais = alt.Chart(vendas_regionais).mark_bar().encode(
    x='Região',
    y='Total de Vendas',
    color='Região'
).properties(title='Total de Vendas por Região')
st.altair_chart(bar_chart_regionais, use_container_width=True)

# Gêneros mais vendidos
genero_vendas = df_empresa.groupby('Genre')['Global_Sales'].sum().reset_index()
genero_vendas = genero_vendas.sort_values(by='Global_Sales', ascending=False)
bar_chart_generos = alt.Chart(genero_vendas).mark_bar().encode(
    x=alt.X('Genre', sort='-y'),
    y='Global_Sales',
    color='Genre'
).properties(title='Total de Vendas por Gênero')
st.altair_chart(bar_chart_generos, use_container_width=True)