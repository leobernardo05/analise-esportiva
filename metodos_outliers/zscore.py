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

resultados_zscore = []
outliers_zscore = []

for nome_time, grupo in dados.groupby("nome_time"):

    for variavel in variaveis:

        # EstatÃ­sticas da equipe atual
        media = grupo[variavel].mean()
        desvio = grupo[variavel].std()

        if desvio == 0:
            continue

        # CÃ¡lculo do Z-score
        z_score = (grupo[variavel] - media) / desvio

        # IdentificaÃ§Ã£o dos valores com Z-score maior que 3
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

print("\nTotal de ocorrÃªncias sinalizadas:", len(df_outliers_zscore))

print(
    "Partidas Ãºnicas sinalizadas:",
    df_outliers_zscore["id_partida"].nunique()
)

print("\nRelatÃ³rios Z-score salvos!")
