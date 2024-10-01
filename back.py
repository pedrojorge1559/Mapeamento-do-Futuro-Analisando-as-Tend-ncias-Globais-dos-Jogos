import pandas as pd
import streamlit as st
df = pd.read_csv('vgsales_com_clusters.csv')

def tabela_cruzada(df, linhas, colunas):
    tabela_cruzada = pd.crosstab(df[linhas], df[colunas])
    return tabela_cruzada
