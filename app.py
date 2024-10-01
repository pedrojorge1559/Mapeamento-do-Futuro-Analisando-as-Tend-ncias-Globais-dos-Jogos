import streamlit as st
import pandas as pd
from back import tabela_cruzada
from back import heat_map
df = pd.read_csv('vgsales_com_clusters.csv')

st.title("Tabela Cruzada")
st.table(tabela_cruzada(df, 'Platform', 'Genre'))
st.heat_map(df, 'Platform', 'Genre')