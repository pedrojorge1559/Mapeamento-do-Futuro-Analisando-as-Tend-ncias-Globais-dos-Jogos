# app.py

import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
from mlxtend.frequent_patterns import fpgrowth, association_rules
import altair as alt

# Carregar os dados
df = pd.read_csv('vgsales_com_clusters.csv')

# Função para treinar o modelo de Random Forest
def treinar_random_forest():
    df_encoded = pd.get_dummies(df[['Platform', 'Genre', 'Publisher', 'Global_Sales']], drop_first=True)
    X = df_encoded.drop('Global_Sales', axis=1)
    y = df_encoded['Global_Sales']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train_scaled, y_train)
    
    return rf, scaler, X

# Função para prever vendas globais
def prever_global_sales(rf, scaler, platform, genre, publisher):
    input_data = pd.DataFrame({'Platform': [platform], 'Genre': [genre], 'Publisher': [publisher]})
    input_data_encoded = pd.get_dummies(input_data, columns=['Platform', 'Genre', 'Publisher'], drop_first=True)
    input_data_encoded = input_data_encoded.reindex(columns=X.columns, fill_value=0)
    input_data_scaled = scaler.transform(input_data_encoded)
    predicted_sales = rf.predict(input_data_scaled)
    return predicted_sales[0]

# Função para aplicar FP-Growth
def aplicar_fp_growth():
    clusters = df['Cluster'].unique()
    todas_regras = pd.DataFrame()
    
    for cluster in clusters:
        limite_vendas = 1.0
        df_filtrado = df[(df['Global_Sales'] > limite_vendas) & (df['Cluster'] == cluster)]
        transacoes = df_filtrado.groupby(['Name', 'Genre'])['Platform'].apply(list).reset_index()
        transacoes['transacao'] = transacoes['Platform'].apply(lambda x: ', '.join(x))
        transacoes_df = transacoes['transacao'].str.get_dummies(sep=', ')
        
        frequent_itemsets = fpgrowth(transacoes_df, min_support=0.05, use_colnames=True)
        regras = association_rules(frequent_itemsets, metric="lift", min_threshold=1)
        todas_regras = pd.concat([todas_regras, regras], ignore_index=True)
    
    return todas_regras

# Interface do usuário
st.title("Sistema de Tomada de Decisão para Jogos")
st.header("Entrada de Dados")
platform = st.selectbox("Plataforma", df['Platform'].unique())
genre = st.selectbox("Gênero", df['Genre'].unique())
publisher = st.text_input("Distribuidora")

# Treinar o modelo de Random Forest
rf, scaler, X = treinar_random_forest()

# Botão para prever vendas
if st.button("Prever Vendas"):
    predicted_sales = prever_global_sales(rf, scaler, platform, genre, publisher)
    st.write(f"Vendas Previstas: {predicted_sales:.2f}")

    # Visualização das vendas previstas
    df_vendas = pd.DataFrame({
        'Plataforma': [platform],
        'Gênero': [genre],
        'Distribuidora': [publisher],
        'Vendas Previstas': [predicted_sales]
    })
    chart = alt.Chart(df_vendas).mark_bar().encode(
        x='Plataforma',
        y='Vendas Previstas',
        color='Gênero'
    ).properties(title='Vendas Previstas por Plataforma')
    st.altair_chart(chart)

# Aplicar FP-Growth
todas_regras = aplicar_fp_growth()

# Exibir regras de associação
st.header("Regras de Associação")
if st.button("Gerar Regras"):
    melhor_recomendacao = todas_regras.sort_values(by='lift', ascending=False).head(1)
    st.write(melhor_recomendacao)

# Visualização da distribuição de vendas por gênero e plataforma
st.header("Distribuição de Vendas por Gênero e Plataforma")
df_vendas_distribuicao = df.groupby(['Genre', 'Platform'])['Global_Sales'].sum().reset_index()
chart_distribuicao = alt.Chart(df_vendas_distribuicao).mark_bar().encode(
    x='Platform',
    y='Global_Sales',
    color='Genre',
    tooltip=['Genre', 'Global_Sales']
).properties(title='Distribuição de Vendas por Gênero e Plataforma')
st.altair_chart(chart_distribuicao)

# Exportar resultados
if st.button("Exportar Resultados"):
    todas_regras.to_csv('regras_associacao.csv', index=False)
    st.success("Resultados exportados com sucesso!")