import pandas as pd
from pyod.models.ecod import ECOD
from pyod.models.knn import KNN
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

print("Base carregada:", dados.shape)

# Lista que armazenará os resultados
resultados_iqr = []

# Lista que armazenará as observações identificadas
outliers_iqr = []

# Analisando cada equipe separadamente
for nome_time, grupo in dados.groupby("nome_time"):
    # Analisando cada variável
    for variavel in variaveis:
        # calculando os quartis
        q1 = grupo[variavel].quantile(0.25)
        q3 = grupo[variavel].quantile(0.75)

        #Calculando o intervalor interquartil 
        iqr = q3 - q1
        
        # calculando os limites
        limite_inferior = q1 - (1.5 * iqr)
        limite_superior = q3 + (1.5 * iqr)
        
        # Identificando os valores fora dos limites
        mascara = (
            (grupo[variavel] < limite_inferior) |
            (grupo[variavel] > limite_superior)
        )

        identificados = grupo[mascara]

        # Registrando o resumo de análise
        resultados_iqr.append({
            "time": nome_time,
            "variavel": variavel,
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "limite_inferior": limite_inferior,
            "limite_superior": limite_superior,
            "quantidade_outliers": len(identificados),
            "percentual_outliers": (
                len(identificados) / len(grupo)
            ) * 100
        })

        # Registrando cada observação identificada
        for _, linha in identificados.iterrows():

            valor = linha[variavel]

            outliers_iqr.append({
                "time": nome_time,
                "id_partida": linha["id_partida"],
                "data_partida": linha["data_partida"],
                "variavel": variavel,
                "valor": valor,
                "limite_inferior": limite_inferior,
                "limite_superior": limite_superior,
                "tipo": (
                    "Inferior"
                    if valor < limite_inferior
                    else "Superior"
                )
            })

# Transformando os resultados em DataFrames
df_resultados = pd.DataFrame(resultados_iqr)
df_outliers = pd.DataFrame(outliers_iqr)

# Salvando os relatórios
df_resultados.to_csv(
    "data/processed/resumo_outliers_iqr.csv",
    index=False
)

df_outliers.to_csv(
    "data/processed/outliers_iqr.csv",
    index=False
)

print("\n--- RESUMO IQR ---")
print(df_resultados.head(15).to_string(index=False))

print("\nQuantidade total de observações sinalizadas:")
print(len(df_outliers))

print("\nRelatórios salvos com sucesso!")

# quantidade de outliers por variavel
print("\n--- OUTLIERS POR VARIÁVEL ---")

print(
    df_outliers.groupby("variavel")
    .size()
    .sort_values(ascending=False)
)

# Quantidade de outliers por equipe
print("\n ---OUTLIERS POR EQUIPE ---")

print(
    df_outliers.groupby("time")
    .size()
    .sort_values(ascending=False)
)

# Quantidade de partidas distintas sinalizadas
observacoes_sinalizadas = df_outliers[
    ["time", "id_partida"]
].drop_duplicates()

print(
    "\nObservações distintas (equipe-partida):",
    len(observacoes_sinalizadas)
)

# Quantidade de equipes afetadas
print(
    "Partidas únicas sinalizadas:",
    df_outliers["id_partida"].nunique()
)


resultados_zscore = []
outliers_zscore = []

for nome_time, grupo in dados.groupby("nome_time"):

    for variavel in variaveis:

        # Estatísticas da equipe atual
        media = grupo[variavel].mean()
        desvio = grupo[variavel].std()

        if desvio == 0:
            continue

        # Cálculo do Z-score
        z_score = (grupo[variavel] - media) / desvio

        # Identificação dos valores com Z-score maior que 3
        mascara = z_score.abs() > 3

        identificados = grupo[mascara]

        resultados_zscore.append({
            "time": nome_time,
            "variavel": variavel,
            "media": media,
            "desvio_padrao": desvio,
            "quantidade_outliers": len(identificados),
            "percentual_outliers": (
                len(identificados) / len(grupo)
            ) * 100
        })

        for indice, linha in identificados.iterrows():

            outliers_zscore.append({
                "time": nome_time,
                "id_partida": linha["id_partida"],
                "data_partida": linha["data_partida"],
                "variavel": variavel,
                "valor": linha[variavel],
                "z_score": z_score.loc[indice]
            })

df_resultados_zscore = pd.DataFrame(resultados_zscore)
df_outliers_zscore = pd.DataFrame(outliers_zscore)

df_resultados_zscore.to_csv(
    "data/processed/resumo_outliers_zscore.csv",
    index=False
)

df_outliers_zscore.to_csv(
    "data/processed/outliers_zscore.csv",
    index=False
)

print("\n--- RESUMO Z-SCORE ---")
print(df_resultados_zscore.head(15).to_string(index=False))

print("\nTotal de ocorrências sinalizadas:", len(df_outliers_zscore))

print(
    "Partidas únicas sinalizadas:",
    df_outliers_zscore["id_partida"].nunique()
)

print("\nRelatórios Z-score salvos!")


# contar as partidas unicas sinalizadas com IQR ou ZSCORE
print(
    "Partidas únicas sinalizadas pelo IQR:",
    df_outliers["id_partida"].nunique()
)

print(
    "Partidas únicas sinalizadas pelo Z-score:",
    df_outliers_zscore["id_partida"].nunique()
)

print("\n--- COMPARAÇÃO POR VARIÁVEL ---")

comparacao = pd.merge(
    df_resultados.groupby("variavel")["quantidade_outliers"]
    .sum()
    .reset_index()
    .rename(columns={"quantidade_outliers": "IQR"}),

    df_resultados_zscore.groupby("variavel")["quantidade_outliers"]
    .sum()
    .reset_index()
    .rename(columns={"quantidade_outliers": "Z-score"}),

    on="variavel"
)

print(comparacao.to_string(index=False))


from scipy.stats import t
import numpy as np

resultados_grubbs = []
outliers_grubbs = []

nivel_significancia = 0.05

for nome_time, grupo in dados.groupby("nome_time"):

    for variavel in variaveis:

        valores = grupo[variavel].dropna()
        n = len(valores)

        if n < 3:
            continue

        media = valores.mean()
        desvio = valores.std(ddof=1)

        if desvio == 0:
            continue

        # Identifica a observação mais distante da média
        desvios = (valores - media).abs()
        indice_extremo = desvios.idxmax()

        valor_extremo = valores.loc[indice_extremo]

        # Estatística de Grubbs
        G = desvios.loc[indice_extremo] / desvio

        # Cálculo do valor crítico
        t_critico = t.ppf(
            1 - nivel_significancia / (2 * n),
            n - 2
        )

        G_critico = (
            (n - 1) / np.sqrt(n)
        ) * np.sqrt(
            t_critico**2 /
            (n - 2 + t_critico**2)
        )

        identificado = G > G_critico

        resultados_grubbs.append({
            "time": nome_time,
            "variavel": variavel,
            "media": media,
            "desvio_padrao": desvio,
            "valor_extremo": valor_extremo,
            "G": G,
            "G_critico": G_critico,
            "outlier_identificado": identificado
        })

        if identificado:

            linha = grupo.loc[indice_extremo]

            outliers_grubbs.append({
                "time": nome_time,
                "id_partida": linha["id_partida"],
                "data_partida": linha["data_partida"],
                "variavel": variavel,
                "valor": valor_extremo,
                "G": G,
                "G_critico": G_critico
            })


df_resultados_grubbs = pd.DataFrame(resultados_grubbs)
df_outliers_grubbs = pd.DataFrame(outliers_grubbs)

df_resultados_grubbs.to_csv(
    "data/processed/resumo_outliers_grubbs.csv",
    index=False
)

df_outliers_grubbs.to_csv(
    "data/processed/outliers_grubbs.csv",
    index=False
)

print("\n--- RESUMO GRUBBS ---")

print(
    df_resultados_grubbs.head(15).to_string(index=False)
)

print(
    "\nTotal de ocorrências identificadas:",
    len(df_outliers_grubbs)
)

print(
    "Partidas únicas sinalizadas:",
    df_outliers_grubbs["id_partida"].nunique()
)

print("\nRelatórios Grubbs salvos!")


print("\n--- GRUBBS POR VARIÁVEL ---")

print(
    df_outliers_grubbs.groupby("variavel")
    .size()
    .sort_values(ascending=False)
)

print("\n--- REGISTROS IDENTIFICADOS PELO GRUBBS ---")

print(
    df_outliers_grubbs[
        [
            "time",
            "id_partida",
            "variavel",
            "valor",
            "G",
            "G_critico"
        ]
    ].to_string(index=False)
)

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

# detecção de anomalias - K-NN
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
    
    # obtendo previsoes e pontuações
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


print("\nTotal de observações sinalizadas:")
print(len(df_outliers_knn))

print("\nPartidas distintas sinalizadas:")
print(df_outliers_knn["id_partida"].nunique())

print("\nRelatórios K-NN salvos com sucesso!")

# DBSCAN - análise das distâncias para escolha do eps

min_samples = 5

# Selecionar um time para analisar
grupo = dados[dados["nome_time"] == "Boston Celtics"]

# Selecionar e padronizar as variáveis
X = grupo[variaveis].copy()

scaler = StandardScaler()
X_padronizado = scaler.fit_transform(X)

# Calcular as distâncias dos 5 vizinhos mais próximos
vizinhos = NearestNeighbors(n_neighbors=min_samples)
vizinhos.fit(X_padronizado)

distancias, indices = vizinhos.kneighbors(X_padronizado)

# Pegar a distância até o 5º vizinho
distancias_ordenadas = sorted(distancias[:, -1])

# Gerar gráfico
plt.figure(figsize=(10, 5))
plt.plot(distancias_ordenadas)
plt.xlabel("Observações ordenadas")
plt.ylabel("Distância até o 5º vizinho")
plt.title("Gráfico K-distance - Boston Celtics")
plt.grid()
plt.savefig("data/processed/grafico_k_distance.png")
plt.show()

# DETECÇÃO DE ANOMALIAS - DBSCAN

resultados_dbscan = []
outliers_dbscan = []
resumo_dbscan = []

eps = 2.7
min_samples = 5

for nome_time, grupo in dados.groupby("nome_time"):

    # Selecionando as variáveis
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

    # Quantidade de grupos e ruídos
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

# Salvando os relatórios
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

print("\nTotal de observações sinalizadas:")
print(len(df_outliers_dbscan))

print("\nPartidas únicas sinalizadas:")
print(df_outliers_dbscan["id_partida"].nunique())

print("\nRelatórios DBSCAN salvos com sucesso!")

# COMPARAÇÃO ENTRE OS MÉTODOS

metodos = {
    "IQR": df_outliers[["time", "id_partida"]],
    "Z-score": df_outliers_zscore[["time", "id_partida"]],
    "Grubbs": df_outliers_grubbs[["time", "id_partida"]],
    "ECOD": df_outliers_ecod[["time", "id_partida"]],
    "K-NN": df_outliers_knn[["time", "id_partida"]],
    "DBSCAN": df_outliers_dbscan[["time", "id_partida"]]
}

# Criar uma tabela com as partidas identificadas
comparacao_metodos = None

for nome, resultado in metodos.items():

    partidas = resultado.drop_duplicates().copy()

    partidas[nome] = 1

    if comparacao_metodos is None:
        comparacao_metodos = partidas
    else:
        comparacao_metodos = pd.merge(
            comparacao_metodos,
            partidas,
            on=["time", "id_partida"],
            how="outer"
        )

# Substituir valores ausentes por zero
comparacao_metodos = comparacao_metodos.fillna(0)

# Calcular quantos métodos identificaram cada partida
colunas_metodos = list(metodos.keys())

comparacao_metodos["quantidade_metodos"] = (
    comparacao_metodos[colunas_metodos].sum(axis=1)
)

# Exibir as partidas identificadas por mais de um método
print("\n--- PARTIDAS IDENTIFICADAS POR MAIS DE UM MÉTODO ---")

print(
    comparacao_metodos[
        comparacao_metodos["quantidade_metodos"] >= 2
    ].sort_values(
        "quantidade_metodos",
        ascending=False
    ).to_string(index=False)
)

# Salvar comparação
comparacao_metodos.to_csv(
    "data/processed/comparacao_metodos.csv",
    index=False
)

# Ranking das partidas identificadas por mais métodos

ranking_anomalias = comparacao_metodos.sort_values(
    by="quantidade_metodos",
    ascending=False
)

# Selecionar partidas identificadas por pelo menos 3 métodos
ranking_anomalias = ranking_anomalias[
    ranking_anomalias["quantidade_metodos"] >= 3
]

print("\n--- RANKING DE PARTIDAS SUSPEITAS ---")

print(
    ranking_anomalias[
        ["time", "id_partida", "quantidade_metodos"]
    ].to_string(index=False)
)

# Salvar relatório
ranking_anomalias.to_csv(
    "data/processed/ranking_anomalias.csv",
    index=False
)

# investigar partidas identificadas pelos seis métodos

partidas_prioritarias = comparacao_metodos[
    comparacao_metodos["quantidade_metodos"] == 6
]

dados_investigacao = dados.merge(
    partidas_prioritarias[["time", "id_partida"]],
    left_on=["nome_time", "id_partida"],
    right_on=["time", "id_partida"],
    how="inner"
)

colunas_investigacao = [
    "nome_time",
    "id_partida",
    "data_partida",
    "pontos",
    "rebotes_totais",
    "assistencias",
    "roubos_bola",
    "bloqueios",
    "faltas_pessoais",
    "cestas_3_convertidas"
]

print("\n--- INVESTIGAÇÃO DAS PARTIDAS PRIORITÁRIAS ---")

print(
    dados_investigacao[colunas_investigacao]
    .sort_values(["id_partida", "nome_time"])
    .to_string(index=False)
)