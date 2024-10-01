import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def tabela_cruzada(df, linha, coluna):
    tabela_cruzada = pd.crosstab(df[linha], df[coluna])
    return tabela_cruzada

def heat_map(df, linha=None, coluna=None):
    if linha is not None and coluna is not None:
        df = df.pivot_table(index=linha, columns=coluna, aggfunc='size', fill_value=0)

    heatmap = sns.heatmap(df, annot=True, fmt='g', cmap='PuRd', annot_kws={'color': 'black'}, linewidths=1)

    plt.title(f'Mapa de calor: {linha} vs {coluna}')
    plt.xlabel(linha)
    plt.ylabel(coluna)

    return heatmap

def grafico_serie_historica(df, coluna, ano_inicial, ano_final):
    df_filtrado = df[(df[coluna] >= ano_inicial) & (df[coluna] <= ano_final)]
    plt.figure(figsize=(10, 5))
    plt.plot(df_filtrado['Year'], df_filtrado[coluna], marker='o')
    plt.title('Gráfico de Série Histórica')
    plt.xlabel('Ano')
    plt.ylabel(coluna)
    plt.grid()
    return plt

def grafico_dispersao(df, coluna_x, coluna_y):
    plt.figure(figsize=(10, 5))
    plt.scatter(df[coluna_x], df[coluna_y], alpha=0.7)
    plt.title('Gráfico de Dispersão')
    plt.xlabel(coluna_x)
    plt.ylabel(coluna_y)
    plt.grid()
    return plt


