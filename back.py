import pandas as pd
import streamlit as st
df = pd.read_csv('d:/PROJETOS/PI A1/vgsales_com_clusters.csv')

def tabela_cruzada(df, linhas, colunas):
    tabela_cruzada = pd.crosstab(df[linhas], df[colunas])
    st.write(tabela_cruzada)
    return tabela_cruzada
