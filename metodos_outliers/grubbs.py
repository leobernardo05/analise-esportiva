from scipy.stats import t
import numpy as np
import pandas as pd

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

# inicialização arrays grubs
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

        # Identifica a observaÃ§Ã£o mais distante da mÃ©dia
        desvios = (valores - media).abs()
        indice_extremo = desvios.idxmax()

        valor_extremo = valores.loc[indice_extremo]

        # EstatÃ­stica de Grubbs
        G = desvios.loc[indice_extremo] / desvio

        # CÃ¡lculo do valor crÃ­tico
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
    "\nTotal de ocorrÃªncias identificadas:",
    len(df_outliers_grubbs)
)

print(
    "Partidas Ãºnicas sinalizadas:",
    df_outliers_grubbs["id_partida"].nunique()
)

print("\nRelatÃ³rios Grubbs salvos!")


print("\n--- GRUBBS POR VARIÃVEL ---")

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
