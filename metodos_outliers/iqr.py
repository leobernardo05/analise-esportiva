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

print("Base carregada:", dados.shape)

# Lista que armazenará os resultados
resultados_iqr = []

# Lista que armazenarÃ¡ as observacoes identificadas
outliers_iqr = []

# Analisando cada equipe separadamente
for nome_time, grupo in dados.groupby("nome_time"):
    # Analisando cada variavel
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

        # Registrando o resumo de analise
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

        # Registrando cada observacao identificada
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

# Salvando os relatorios
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

print("\nQuantidade total de observacoes sinalizadas:")
print(len(df_outliers))

print("\nRelatorios salvos com sucesso!")

# quantidade de outliers por variavel
print("\n--- OUTLIERS POR VARIAVEL ---")

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
    "\nObservaçoes distintas (equipe-partida):",
    len(observacoes_sinalizadas)
)

# Quantidade de equipes afetadas
print(
    "Partidas unicas sinalizadas:",
    df_outliers["id_partida"].nunique()
)


