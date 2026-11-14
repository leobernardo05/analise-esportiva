import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt


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

# DBSCAN - anÃ¡lise das distÃ¢ncias para escolha do eps
min_samples = 5

# Selecionar um time para analisar
grupo = dados[dados["nome_time"] == "Boston Celtics"]

# Selecionar e padronizar as variÃ¡veis
X = grupo[variaveis].copy()

scaler = StandardScaler()
X_padronizado = scaler.fit_transform(X)

# Calcular as distÃ¢ncias dos 5 vizinhos mais prÃ³ximos
vizinhos = NearestNeighbors(n_neighbors=min_samples)
vizinhos.fit(X_padronizado)

distancias, indices = vizinhos.kneighbors(X_padronizado)

# Pegar a distÃ¢ncia atÃ© o 5Âº vizinho
distancias_ordenadas = sorted(distancias[:, -1])

# Gerar grÃ¡fico
plt.figure(figsize=(10, 5))
plt.plot(distancias_ordenadas)
plt.xlabel("ObservaÃ§Ãµes ordenadas")
plt.ylabel("DistÃ¢ncia atÃ© o 5Âº vizinho")
plt.title("GrÃ¡fico K-distance - Boston Celtics")
plt.grid()
plt.savefig("data/processed/grafico_k_distance.png")
plt.show()

# DETECÃ‡ÃƒO DE ANOMALIAS - DBSCAN

resultados_dbscan = []
outliers_dbscan = []
resumo_dbscan = []

eps = 2.7
min_samples = 5

for nome_time, grupo in dados.groupby("nome_time"):

    # Selecionando as variÃ¡veis
    X = grupo[variaveis].copy()

    # Padronizando os dados
    scaler = StandardScaler()
    X_padronizado = scaler.fit_transform(X)

    # Criando e executando o DBSCAN
    modelo = DBSCAN(
        eps=eps,
        min_samples=min_samples
    )

    rotulos = modelo.fit_predict(X_padronizado)

    # Quantidade de grupos e ruÃ­dos
    quantidade_grupos = len(set(rotulos)) - (1 if -1 in rotulos else 0)
    quantidade_ruidos = (rotulos == -1).sum()

    resumo_dbscan.append({
        "time": nome_time,
        "quantidade_grupos": quantidade_grupos,
        "quantidade_ruidos": quantidade_ruidos,
        "percentual_ruidos": (
            quantidade_ruidos / len(grupo)
        ) * 100
    })

    # Registrando os resultados
    for i, (_, linha) in enumerate(grupo.iterrows()):

        registro = {
            "time": nome_time,
            "id_partida": linha["id_partida"],
            "data_partida": linha["data_partida"],
            "rotulo": rotulos[i],
            "anomalia": rotulos[i] == -1
        }

        resultados_dbscan.append(registro)

        if rotulos[i] == -1:
            outliers_dbscan.append(registro)


# Transformando em DataFrames
df_resultados_dbscan = pd.DataFrame(resultados_dbscan)
df_outliers_dbscan = pd.DataFrame(outliers_dbscan)
df_resumo_dbscan = pd.DataFrame(resumo_dbscan)

# Salvando os relatÃ³rios
df_resultados_dbscan.to_csv(
    "data/processed/resultados_dbscan.csv",
    index=False
)

df_outliers_dbscan.to_csv(
    "data/processed/outliers_dbscan.csv",
    index=False
)

df_resumo_dbscan.to_csv(
    "data/processed/resumo_dbscan.csv",
    index=False
)

# Apresentando os resultados
print("\n--- DBSCAN POR EQUIPE ---")

print(df_resumo_dbscan.to_string(index=False))

print("\nTotal de observaÃ§Ãµes sinalizadas:")
print(len(df_outliers_dbscan))

print("\nPartidas Ãºnicas sinalizadas:")
print(df_outliers_dbscan["id_partida"].nunique())

print("\nRelatÃ³rios DBSCAN salvos com sucesso!")

