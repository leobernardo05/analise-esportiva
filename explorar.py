# isso é necessario para verificar integridade dos dados e utilização da tabela de forma efetiva, com um certo tratamento de dados
import pandas as pd
# carregando a base original
df = pd.read_csv("data/original/stats_times_regular_final.csv")

# criando uma copia para realizar os tratamentos
dados = df.copy() 

print("Dimensões da base original:", df.shape)
print("Dimensões da cópia: ", dados.shape)

#-----------  entendendo a tabela ------
print("\nPrimeiros registros:")
print(df.head())

print("\nInformações das colunas")
print(df.info())

print("\nValores ausentes")
print(df.isnull().sum())

print("\nTimes disponíveis:")
print(df["TEAM_NAME"].unique())

print("\nQuantidade de partidas por time:")
print(df["TEAM_NAME"].value_counts())

print("\nEstatísticas descritivas:")
print(df[["PTS", "REB", "AST", "STL", "BLK", "PF", "FG3M"]].describe())

print("\nRegistros duplicados:")
print(df.duplicated().sum())

print("\nDuplicatas de equipe e partida:")
print(df.duplicated(subset=["Team_ID", "Game_ID"]).sum())

print("\nQuantidade de registros por partida:")
print(df.groupby("Game_ID").size().value_counts())

print("\nValidação dos resultados:")
print(df.groupby("Game_ID")["WL"].sum().value_counts())

# padronização dos nomes das colunas na base de dados copiada

# Padronização dos nomes das colunas
novos_nomes = {
    "Team_ID": "id_time",
    "Game_ID": "id_partida",
    "GAME_DATE": "data_partida",
    "MATCHUP": "confronto",
    "WL": "resultado",
    "W": "vitorias_acumuladas",
    "L": "derrotas_acumuladas",
    "W_PCT": "percentual_vitorias",
    "MIN": "minutos",
    "FGM": "arremessos_convertidos",
    "FGA": "arremessos_tentados",
    "FG_PCT": "aproveitamento_arremessos",
    "FG3M": "cestas_3_convertidas",
    "FG3A": "tentativas_3",
    "FG3_PCT": "aproveitamento_3",
    "FTM": "lances_livres_convertidos",
    "FTA": "lances_livres_tentados",
    "FT_PCT": "aproveitamento_lances_livres",
    "OREB": "rebotes_ofensivos",
    "DREB": "rebotes_defensivos",
    "REB": "rebotes_totais",
    "AST": "assistencias",
    "STL": "roubos_bola",
    "BLK": "bloqueios",
    "TOV": "turnovers",
    "PF": "faltas_pessoais",
    "PTS": "pontos",
    "TEAM_NAME": "nome_time"
}

dados = dados.rename(columns=novos_nomes)

print("\nColunas após renomeação:")
print(dados.columns.tolist())


# Conversão da coluna de data
dados["data_partida"] = pd.to_datetime( #função responsavel pela conversão de datas
    dados["data_partida"],
    errors="coerce"
)

# Verificando datas inválidas
datas_invalidas = dados["data_partida"].isna().sum() #conta quantos valores estão ausentes

print("\nQuantidade de datas inválidas:")
print(datas_invalidas)

print("\nTipo da coluna de data:")
print(dados["data_partida"].dtype)


# Identificadores: não são variáveis quantitativas
dados["id_time"] = dados["id_time"].astype("string")
dados["id_partida"] = dados["id_partida"].astype("string")

# Campos textuais
dados["confronto"] = dados["confronto"].astype("string")
dados["nome_time"] = dados["nome_time"].astype("string")

print("\nTipos de dados após tratamento:")
print(dados.dtypes)


# Validação dos rebotes totais
rebotes_validos = (
    dados["rebotes_totais"]
    == dados["rebotes_ofensivos"] + dados["rebotes_defensivos"]
)

print("\nRegistros com rebotes inconsistentes:")
print((~rebotes_validos).sum())


# Validação da pontuação
pontos_validos = (
    dados["pontos"]
    == (
        2 * dados["arremessos_convertidos"]
        + dados["cestas_3_convertidas"]
        + dados["lances_livres_convertidos"]
    )
)

print("\nRegistros com pontuação inconsistente:")
print((~pontos_validos).sum())

# Criando a pasta de destino
import os

os.makedirs("data/processed", exist_ok=True)

# Salvando a base tratada
dados.to_csv(
    "data/processed/dados_tratados.csv",
    index=False,
    date_format="%Y-%m-%d"
)

print("\nBase tratada salva com sucesso!")

print("\nDimensões da base tratada:")
print(dados.shape)


