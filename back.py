import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('vgsales_com_clusters.csv')

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

