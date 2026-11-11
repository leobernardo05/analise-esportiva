import pandas as pd

# isso é necessario para verificar integridade dos dados e utilização da tabela de forma efetiva, com um certo tratamento de dados
df = pd.read_csv("data/stats_times_regular_final.csv")

print("Dimensões da base:")
print(df.shape)

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