import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import seaborn as sns
import os
from datetime import datetime

# ==================================================
# 1. Mapeamento de meses em português
# ==================================================
meses_pt = {
    'Jan': 1, 'Fev': 2, 'Mar': 3, 'Abr': 4, 'Mai': 5, 'Jun': 6,
    'Jul': 7, 'Ago': 8, 'Set': 9, 'Out': 10, 'Nov': 11, 'Dez': 12
}

# ==================================================
# 2. Função para converter datas
# ==================================================
def converter_data(mes_ano_str):
    mes, ano = mes_ano_str.split('/')
    return datetime(int(ano), meses_pt[mes], 1)  # Dia fixo (1)

# ==================================================
# 3. Importar dados (com tratamento de datas)
# ==================================================
def importar_dados():
    df_comparacoes = pd.read_excel('resultados_inflacao.xlsx', sheet_name='Comparações Mensais')
    df_medias = pd.read_excel('resultados_inflacao.xlsx', sheet_name='Médias por País')
    df_testes = pd.read_excel('resultados_inflacao.xlsx', sheet_name='Testes Estatísticos')
    
    # Processar datas
    dados_mensais = []
    for _, row in df_comparacoes.iterrows():
        mes_ano = converter_data(row['Mes/Ano'])
        comparacoes = row['Comparação'].split('; ')
        
        for comp in comparacoes:
            if '=' in comp:
                partes = comp.split(' = ')
                valor = float(partes[1].split('(')[1].replace(')', ''))
                for pais in partes[0].split(' = '):
                    dados_mensais.append([mes_ano, pais.split(' ')[0], valor])
            else:
                partes = comp.split(' > ')
                valor = float(partes[0].split('(')[1].replace(')', ''))
                dados_mensais.append([mes_ano, partes[0].split(' ')[0], valor])

    df_mensal = pd.DataFrame(dados_mensais, columns=['Data', 'País', 'Inflação'])
    return df_mensal, df_medias, df_testes


# ==================================================
# 2. Gerar e salvar gráficos
# ==================================================
def gerar_graficos(df_mensal, df_medias, df_testes):
    # Criar pasta para os gráficos
    os.makedirs('graficos', exist_ok=True)

    # Gráfico 1: Comparações Mensais (Linhas)
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_mensal, x='Data', y='Inflação', hue='País', palette='tab10')
    plt.title('Inflação Mensal por País (2020-2023)')
    plt.gca().xaxis.set_major_formatter(DateFormatter('%b/%Y'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('graficos/inflacao_mensal.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Gráfico 2: Médias por País (Barras)
    plt.figure(figsize=(8, 5))
    sns.barplot(data=df_medias, x='País', y='Média Inflação', palette='viridis')
    plt.title('Média de Inflação por País')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('graficos/medias_pais.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Gráfico 3: Testes Estatísticos (Heatmap)
    plt.figure(figsize=(10, 6))
    matriz_p = df_testes.pivot(index='País 1', columns='País 2', values='Valor p')
    sns.heatmap(matriz_p, annot=True, cmap='YlGnBu', fmt=".3f", 
                cbar_kws={'label': 'Valor p'}, mask=matriz_p > 0.05)
    plt.title('Significância Estatística das Diferenças\n(máscara para p > 0.05)')
    plt.tight_layout()
    plt.savefig('graficos/heatmap_significancia.png', dpi=300, bbox_inches='tight')
    plt.close()

# ==================================================
# Execução principal
# ==================================================
if __name__ == "__main__":
    df_mensal, df_medias, df_testes = importar_dados()
    gerar_graficos(df_mensal, df_medias, df_testes)
    print("Gráficos salvos na pasta 'graficos'!")