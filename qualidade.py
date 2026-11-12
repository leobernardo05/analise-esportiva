# importação do pandas para verificação da base de dados
import pandas as pd

# Carregando a base tratada
dados = pd.read_csv(
    "data/processed/dados_tratados.csv",
    dtype={
        "id_time": "string",
        "id_partida": "string"
    }
)

print("Dimensões da base:", dados.shape)

# Quantidade de valores ausentos por coluna
ausentes = dados.isna().sum()

# Percentual de valores ausentes por coluna
percentual_ausentes = (
    dados.isna().mean()*100
).round(2)

relatorio_ausentes = pd.DataFrame({
    "Quantidade": ausentes,
    "Percentual": percentual_ausentes
})

print("\n--- VALORES AUSENTES ---")
print(relatorio_ausentes)
# -------- funções que é valido saber --------
# isna() identifica valores ausentes.
# sum() conta os valores identificados.
# mean() calcula a proporção de valores ausentes, porque os valores booleanos são interpretados como 0 e 1.
# DataFrame() permite reunir os resultados em uma tabela.


# Duplicações de linhas completas
duplicados = dados.duplicated().sum()

# Duplicações considerando time e partida
duplicados_time_partida = dados.duplicated(
    subset=["id_time", "id_partida"]
).sum()

print("\n--- DUPLICIDADES ---")
print("Linhas duplicadas:", duplicados)
print(
    "Duplicatas de time e partida:",
    duplicados_time_partida
)


# Variáveis quantitativas que não podem ser negativas
colunas_contagem = [
    "minutos",
    "vitorias_acumuladas",
    "derrotas_acumuladas",
    "arremessos_convertidos",
    "arremessos_tentados",
    "cestas_3_convertidas",
    "tentativas_3",
    "lances_livres_convertidos",
    "lances_livres_tentados",
    "rebotes_ofensivos",
    "rebotes_defensivos",
    "rebotes_totais",
    "assistencias",
    "roubos_bola",
    "bloqueios",
    "turnovers",
    "faltas_pessoais",
    "pontos"
]

print("\n--- VALORES NEGATIVOS ---")

for coluna in colunas_contagem:
    quantidade = (dados[coluna] < 0).sum()

    print(f"{coluna}: {quantidade}")


# Verificação dos percentuais
colunas_percentuais = [
    "percentual_vitorias",
    "aproveitamento_arremessos",
    "aproveitamento_3",
    "aproveitamento_lances_livres"
]

print("\n--- PERCENTUAIS FORA DO INTERVALO ---")

for coluna in colunas_percentuais:
    quantidade = (
        (dados[coluna] < 0) |
        (dados[coluna] > 1)
    ).sum()

    print(f"{coluna}: {quantidade}")


print("\n--- CONSISTÊNCIA DOS DADOS ---")

# Arremessos convertidos não podem superar os tentados
arremessos_invalidos = (
    dados["arremessos_convertidos"]
    > dados["arremessos_tentados"]
)

print(
    "Arremessos convertidos acima das tentativas:",
    arremessos_invalidos.sum()
)


# Cestas de três convertidas não podem superar as tentativas
tres_invalidos = (
    dados["cestas_3_convertidas"]
    > dados["tentativas_3"]
)

print(
    "Cestas de três acima das tentativas:",
    tres_invalidos.sum()
)


# Lances livres convertidos não podem superar os tentados
lances_invalidos = (
    dados["lances_livres_convertidos"]
    > dados["lances_livres_tentados"]
)

print(
    "Lances livres convertidos acima das tentativas:",
    lances_invalidos.sum()
)


# Cestas de três fazem parte dos arremessos convertidos
tres_maior_fgm = (
    dados["cestas_3_convertidas"]
    > dados["arremessos_convertidos"]
)

print(
    "Cestas de três acima dos arremessos convertidos:",
    tres_maior_fgm.sum()
)


# Rebotes totais
rebotes_invalidos = (
    dados["rebotes_totais"]
    != dados["rebotes_ofensivos"]
    + dados["rebotes_defensivos"]
)

print(
    "Rebotes inconsistentes:",
    rebotes_invalidos.sum()
)


# Pontuação total
pontos_invalidos = (
    dados["pontos"]
    != (
        2 * dados["arremessos_convertidos"]
        + dados["cestas_3_convertidas"]
        + dados["lances_livres_convertidos"]
    )
)

print(
    "Pontuações inconsistentes:",
    pontos_invalidos.sum()
)


# Quantidade de registros por partida
registros_por_partida = (
    dados.groupby("id_partida").size()
)

partidas_invalidas = (
    registros_por_partida != 2
).sum()

print("\n--- ESTRUTURA DAS PARTIDAS ---")

print(
    "Partidas com quantidade diferente de dois registros:",
    partidas_invalidas
)


# Conferindo resultados
resultados_por_partida = (
    dados.groupby("id_partida")["resultado"].sum()
)

resultados_invalidos = (
    resultados_por_partida != 1
).sum()

print(
    "Partidas sem exatamente uma vitória:",
    resultados_invalidos
)


# Organizando os resultados das verificações

relatorio = {
    "Verificação": [
        "Valores ausentes",
        "Linhas duplicadas",
        "Duplicatas de time e partida",
        "Valores negativos",
        "Percentuais fora do intervalo",
        "Arremessos inconsistentes",
        "Cestas de três inconsistentes",
        "Lances livres inconsistentes",
        "Rebotes inconsistentes",
        "Pontuações inconsistentes",
        "Partidas com quantidade incorreta de registros",
        "Partidas sem exatamente uma vitória"
    ],
    "Ocorrências": [
        dados.isna().sum().sum(),
        dados.duplicated().sum(),
        dados.duplicated(
            subset=["id_time", "id_partida"]
        ).sum(),
        sum(
            (dados[coluna] < 0).sum()
            for coluna in colunas_contagem
        ),
        sum(
            (
                (dados[coluna] < 0) |
                (dados[coluna] > 1)
            ).sum()
            for coluna in colunas_percentuais
        ),
        arremessos_invalidos.sum(),
        tres_invalidos.sum(),
        lances_invalidos.sum(),
        rebotes_invalidos.sum(),
        pontos_invalidos.sum(),
        partidas_invalidas,
        resultados_invalidos
    ]
}

df_relatorio = pd.DataFrame(relatorio)

df_relatorio.to_csv(
    "data/processed/relatorio_qualidade.csv",
    index=False
)

print("\n--- RELATÓRIO FINAL ---")
print(df_relatorio.to_string(index=False))

print("\nRelatório salvo com sucesso!")
