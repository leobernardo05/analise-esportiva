import pandas as pd
from pyod.models.knn import KNN
from sklearn.preprocessing import StandardScaler


# carregando a base tratada
dados = pd.read_csv(
    "data/processed/dados_tratados.csv",
    dtype={
        "id_time": "string",
        "id_partida": "string"
    }
)

# Variáveis solicitadas no trabalho
variaveis = [
    "pontos",
    "rebotes_totais",
    "assistencias",
    "roubos_bola",
    "bloqueios",
    "faltas_pessoais",
    "cestas_3_convertidas"
]

# detecÃ§Ã£o de anomalias - K-NN
resultados_knn = []
outliers_knn = []

contaminacao = 0.05
k_vizinhos = 5

for nome_time, grupo in dados.groupby("nome_time"):
    # selecionando as variaveis
    X = grupo[variaveis].copy()
    
    # padronizando os dados
    scaler = StandardScaler()
    X_padronizado = scaler.fit_transform(X)
    
    # criando o modelo K-NN
    modelo = KNN(
        contamination=contaminacao,
        n_neighbors=k_vizinhos
    )
    
    # Treinando o modelo
    modelo.fit(X_padronizado)
    
    # obtendo previsoes e pontuaÃ§Ãµes
    previsoes = modelo.labels_
    pontuacoes = modelo.decision_scores_

    # Registrando os resultados
    for i, (indice, linha) in enumerate(grupo.iterrows()):
        registro ={
            "time": nome_time,
            "id_partida": linha["id_partida"],
            "data_partida": linha["data_partida"],
            "pontuacao_anomalia": pontuacoes[i],
            "anomalia": previsoes[i]
        }

        resultados_knn.append(registro)

        if previsoes[i] == 1:
            outliers_knn.append(registro)

# Transformando em DATAFRAMES
df_resultados_knn = pd.DataFrame(resultados_knn)
df_outliers_knn = pd.DataFrame(outliers_knn)

# Salvando os relatorios
df_resultados_knn.to_csv(
    "data/processed/resultados_knn.csv",
    index=False
)

df_outliers_knn.to_csv(
    "data/processed/outliers_knn.csv",
    index=False
)

# RESUMO POR EQUIPE

print("\n--- OUTLIERS POR EQUIPE - K-NN ---")

print(
    df_outliers_knn.groupby("time")
    .size()
    .sort_values(ascending=False)
)


print("\nTotal de observaÃ§Ãµes sinalizadas:")
print(len(df_outliers_knn))

print("\nPartidas distintas sinalizadas:")
print(df_outliers_knn["id_partida"].nunique())

print("\nRelatÃ³rios K-NN salvos com sucesso!")

