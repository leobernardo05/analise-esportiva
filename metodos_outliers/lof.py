"""Executa LOF em cada equipe e exporta CSV de anomalias.

Execução: python metodos_outliers/lof.py
Não altera dados originais. Contaminação = 5%; até 20 vizinhos.
"""
from pathlib import Path
import pandas as pd
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler

BASE = Path(__file__).resolve().parents[1]
CAMINHO_DADOS = BASE / 'data' / 'processed' / 'dados_tratados.csv'
CAMINHO_SAIDA = BASE / 'data' / 'processed' / 'outliers_lof.csv'
COLUNAS = ['pontos','rebotes_totais','assistencias','roubos_bola','bloqueios','faltas_pessoais','cestas_3_convertidas']

dados = pd.read_csv(CAMINHO_DADOS, dtype={'id_partida': 'string'})
resultados = []

for time, grupo in dados.groupby('nome_time'):
    X = grupo[COLUNAS].apply(pd.to_numeric, errors='coerce')
    X = X.fillna(X.median()).fillna(0)  # Apenas para o modelo; não altera o CSV.
    if len(X) < 4:
        continue
    X = StandardScaler().fit_transform(X)
    vizinhos = min(20, len(X) - 1)
    modelo = LocalOutlierFactor(n_neighbors=vizinhos, contamination=0.05)
    rotulos = modelo.fit_predict(X)
    pontuacoes = -modelo.negative_outlier_factor_
    for i, (_, linha) in enumerate(grupo.iterrows()):
        if rotulos[i] == -1:
            resultados.append({
                'time': time,
                'id_partida': linha['id_partida'],
                'data_partida': linha['data_partida'],
                'pontuacao_anomalia': float(pontuacoes[i]),
                'anomalia': 1,
            })

pd.DataFrame(resultados, columns=['time','id_partida','data_partida','pontuacao_anomalia','anomalia']).to_csv(CAMINHO_SAIDA, index=False)
print(f'LOF concluído: {len(resultados)} observações exportadas em {CAMINHO_SAIDA}')
