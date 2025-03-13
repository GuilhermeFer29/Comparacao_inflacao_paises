# Importando as bibliotecas necessárias
import pandas   as pd
import openpyxl as xl
import numpy as np
import scipy.stats as sp
from itertools import combinations
import matplotlib.pyplot as plt
import re

# Importando o dataset
df = pd.read_csv('paises_europa/tabela_paises.csv')
df.head() # Mostrando as primeiras linhas do dataset

paises_eur = df.columns[1:].tolist() # Lista de países da Europa
comparacoes_por_mes = [] # Lista para armazenar as comparações

# Remover espaços em branco e caracteres especiais e repedição de caracteres
df['Mes/Ano'] = df['Mes/Ano'].apply(lambda x: re.match(r'([A-Za-z]+/\d{4})', x).group(1) if re.match(r'([A-Za-z]+/\d{4})', x) else x)

# Iterar sobre as linhas do DataFrame
for _, row in df.iterrows():
    mes_ano = str(row['Mes/Ano']).strip()  # Garante que é uma string limpa
    comparacoes = [] # Lista para armazenar as comparações para o mês atual
    
    # Comparar os valores de cada país da Europa
    for pais_eu1, pais_eu2 in combinations(paises_eur, 2):
        valor_eu1 = row[pais_eu1]
        valor_eu2 = row[pais_eu2]
        
        # Verificar se os valores são números e se são válidos
        if valor_eu1 > valor_eu2:
            msg = f"{pais_eu1} ({valor_eu1}) > {pais_eu2} ({valor_eu2})"
        elif valor_eu2 > valor_eu1:
            msg = f"{pais_eu2} ({valor_eu2}) > {pais_eu1} ({valor_eu1})"
        else:
            msg = f"{pais_eu1} = {pais_eu2} ({valor_eu1})"
        
        # Adicionar a mensagem à lista de comparações para o mês atual
        comparacoes.append(msg)  
    
    # Adicionar as comparações para o mês atual à lista geral
    comparacoes_por_mes.append({
        'Mes/Ano': mes_ano,
        'Comparações': comparacoes
    })

# Exibir resultados corretamente
for mes in comparacoes_por_mes[:48]:  
    print(f"\n--- {mes['Mes/Ano']} ---")  
    for comp in mes['Comparações']:
        print(comp)
        
# lista de paises
paises =['Alemanha', 'Estonia', 'Finlandia', 'Grecia', 'Suecia']

# criando um dicionário para armazenar as médias de inflação
medias_inflacao = {}

# calculando a média de inflação para cada país
for pais in paises:
    if pais in df.columns:
        medias_inflacao[pais]= np.mean(df[pais])
        print(f'A média de inflação do país {pais} é {medias_inflacao[pais]:.4f}')
    else:
        print(f'O país {pais} não está no dataframe')
        
        
# Extraindo od dados da coluna de países
extrato = df.columns[1:].tolist()

# Gerando todas as combinações possíveis de países
ger_pares = list(combinations(extrato, 2))

# Definindo o nível de confiança desejado
niv_confianca = float(input("Digite o nível de confiança desejado (ex: 0.95): "))


# Criando um dicionário para armazenar os resultados
for paises_eu1 , paises_eu2 in ger_pares :
        dados_paises_eu1 = df[paises_eu1]
        dados_paises_eu2 = df[paises_eu2]
    
        t_stat, p_valor = sp.stats.ttest_ind(dados_paises_eu1, dados_paises_eu2, equal_var=False)
    
        medias_eu1 = dados_paises_eu1.mean()
        medias_eu2 = dados_paises_eu2.mean()
    
    
        # Verificando se há diferença significativa entre as médias
        if p_valor < niv_confianca:
            diferenca_eu = "Diferença significativa entre as médias"
        else:
            diferenca_eu = "Não há diferença significativa entre as médias"
        
        print(f"País 1: {paises_eu1} | País 2: {paises_eu2}")
        print(f"Média dos País: {medias_eu1:.2f} vs {medias_eu2:.2f} ")
        print(f"Valor de P: {p_valor:.4f} ---> {diferenca_eu}\n")
                

# Gerando os graficos e ajustando o tamanho
fig, axs = plt.subplots(nrows=2, ncols=4, figsize=(15, 8))  

# Transformando axs em uma lista para iterar sobre os subplots
axs = axs.flatten()

# Iterando sobre os pares de paises

for i, (paises_eu1, paises_eu2) in enumerate(ger_pares):
    
    # Verifica se todos os graficos  foram criados
    if i >= len(axs):
        break

    ax = axs[i]
    dados_paises_eu1 = df[paises_eu1]
    dados_paises_eu2 = df[paises_eu2]

    t_stat, p_valor = sp.stats.ttest_ind(dados_paises_eu1, dados_paises_eu2, equal_var=False)

    medias_eu1 = dados_paises_eu1.mean()
    medias_eu2 = dados_paises_eu2.mean()

    diferenca_eu = "Diferença significativa" if p_valor < niv_confianca else "Sem diferença"

    ax.bar([paises_eu1, paises_eu2], [medias_eu1, medias_eu2], color=['blue', 'red'])
    ax.set_title(f"{paises_eu1} vs {paises_eu2}\n{diferenca_eu}")

plt.tight_layout()
plt.show()




# --- Criação do arquivo Excel com os resultados ---
with pd.ExcelWriter('resultados_inflacao.xlsx') as writer:
    # 1. Tabela de Comparações Mensais
    df_comparacoes = pd.DataFrame([
        {"Mes/Ano": mes['Mes/Ano'], "Comparação": comp} 
        for mes in comparacoes_por_mes 
        for comp in mes['Comparações']
    ])
    df_comparacoes.to_excel(writer, sheet_name='Comparações Mensais', index=False)

    # 2. Tabela de Médias de Inflação
    df_medias = pd.DataFrame(list(medias_inflacao.items()), columns=['País', 'Média Inflação'])
    df_medias.to_excel(writer, sheet_name='Médias por País', index=False)

    # 3. Tabela de Resultados Estatísticos
    resultados_estatisticos = []
    for paises_eu1, paises_eu2 in ger_pares:
        dados_paises_eu1 = df[paises_eu1]
        dados_paises_eu2 = df[paises_eu2]
        
        t_stat, p_valor = sp.stats.ttest_ind(dados_paises_eu1, dados_paises_eu2, equal_var=False)
        
        resultados_estatisticos.append({
            'País 1': paises_eu1,
            'País 2': paises_eu2,
            'Média 1': dados_paises_eu1.mean(),
            'Média 2': dados_paises_eu2.mean(),
            'Valor p': p_valor,
            'Conclusão': 'Diferença significativa' if p_valor < niv_confianca else 'Sem diferença'
        })
    
    df_estatistica = pd.DataFrame(resultados_estatisticos)
    df_estatistica.to_excel(writer, sheet_name='Testes Estatísticos', index=False)

print("Arquivo Excel 'resultados_inflacao.xlsx' gerado com sucesso!") 