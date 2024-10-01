import streamlit as st
import pandas as pd
from back import tabela_cruzada
df = pd.read_csv('vgsales_com_clusters.csv')

st.title("Tabela Cruzada")
st.write(tabela_cruzada(df, 'Platform', 'Genre'))