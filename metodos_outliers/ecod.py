import pandas as pd
from pyod.models.ecod import ECOD

# carregando a base tratada
dados = pd.read_csv(
    "data/processed/dados_tratados.csv",
    dtype={
        "id_time": "string",
        "id_partida": "string"
    }
)

# Variaveis solicitadas no trabalho
variaveis = [
    "pontos",
    "rebotes_totais",
    "assistencias",
    "roubos_bola",
    "bloqueios",
    "faltas_pessoais",
    "cestas_3_convertidas"
]

# DETECCAO DE ANOMALIAS - ECOD
resultados_ecod = []
outliers_ecod = []

contaminacao = 0.05

for nome_time, grupo in dados.groupby("nome_time"):

    X = grupo[variaveis].copy()

    modelo = ECOD(contamination=contaminacao)

    modelo.fit(X)

    previsoes = modelo.labels_
    pontuacoes = modelo.decision_scores_
    for i, (indice, linha) in enumerate(grupo.iterrows()):
        registro = {
                "time": nome_time,
                "id_partida": linha["id_partida"],
                "data_partida": linha["data_partida"],
                "pontuacao_anomalia": pontuacoes[i],
                "anomalia": previsoes[i]
            }

        resultados_ecod.append(registro)

        if previsoes[i] == 1:
            outliers_ecod.append(registro)


# TRANSFORMAR EM DATAFRAMES
df_resultados_ecod = pd.DataFrame(resultados_ecod)
df_outliers_ecod = pd.DataFrame(outliers_ecod)

# SALVAR RELATORIOS
df_resultados_ecod.to_csv(
    "data/processed/resultados_ecod.csv",
    index=False
)

df_outliers_ecod.to_csv(
    "data/processed/outliers_ecod.csv",
    index=False
)

# RESUMO POR EQUIPE
print("\n--- OUTLIERS POR EQUIPE - ECOD ---")
print(
    df_outliers_ecod.groupby("time")
    .size()
    .sort_values(ascending=False)
)

print("\nTotal de observacoes sinalizadas:")
print(len(df_outliers_ecod))

print("\nPartidas distintas sinalizadas:")
print(df_outliers_ecod["id_partida"].nunique())

print("\nRelatorios ECOD salvos com sucesso!")

