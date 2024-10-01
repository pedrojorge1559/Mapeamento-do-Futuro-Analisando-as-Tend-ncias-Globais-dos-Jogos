import streamlit as st

st.title("Minha Aplicação Streamlit")

st.write("Esta é uma aplicação simples usando Streamlit.")

nome = st.text_input("Digite seu nome:")

if st.button("Enviar"):
    st.write(f"Olá, {nome}!")