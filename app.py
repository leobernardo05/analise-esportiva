
from pathlib import Path

from flask import Flask, render_template, request
import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


# --------------------------------------------------
# CONFIGURAÇÕES INICIAIS
# --------------------------------------------------

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent

CAMINHO_DADOS = BASE_DIR / "data" / "original" / "stats_times_regular_final.csv"
CAMINHO_STATIC = BASE_DIR / "static"

CAMINHO_STATIC.mkdir(exist_ok=True)


# --------------------------------------------------
# CARREGAMENTO DA BASE
# --------------------------------------------------

df = pd.read_csv(CAMINHO_DADOS)

# Conversão da coluna de data
df["GAME_DATE"] = pd.to_datetime(
    df["GAME_DATE"],
    errors="coerce"
)


# --------------------------------------------------
# VARIÁVEIS E NOMES PARA EXIBIÇÃO
# --------------------------------------------------

variaveis = {
    "PTS": "Pontos",
    "REB": "Rebotes",
    "AST": "Assistências",
    "STL": "Roubos de bola",
    "BLK": "Bloqueios",
    "PF": "Faltas pessoais",
    "FG3M": "Cestas de três convertidas"
}


# --------------------------------------------------
# ROTA PRINCIPAL
# --------------------------------------------------

@app.route("/")
def inicio():

    # Lista de equipes
    times = sorted(df["TEAM_NAME"].dropna().unique())

    # Recebe os filtros enviados pelo formulário
    time_selecionado = request.args.get("time", times[0])
    variavel = request.args.get("variavel", "PTS")

    # Validação dos filtros
    if time_selecionado not in times:
        time_selecionado = times[0]

    if variavel not in variaveis:
        variavel = "PTS"

    # Filtra os dados da equipe
    dados_time = df[
        df["TEAM_NAME"] == time_selecionado
    ].copy()

    # --------------------------------------------------
    # ESTATÍSTICAS DESCRITIVAS
    # --------------------------------------------------

    estatisticas = []

    for codigo, nome in variaveis.items():

        valores = dados_time[codigo].describe()

        estatisticas.append({
            "nome": nome,
            "media": valores["mean"],
            "desvio": valores["std"],
            "mediana": valores["50%"],
            "minimo": valores["min"],
            "maximo": valores["max"]
        })

    # --------------------------------------------------
    # DADOS GERAIS DA BASE
    # --------------------------------------------------

    total_registros = len(df)
    total_colunas = len(df.columns)
    total_times = df["TEAM_NAME"].nunique()
    total_partidas = df["Game_ID"].nunique()

    total_jogos_time = len(dados_time)

    total_ausentes = int(df.isna().sum().sum())
    total_duplicados = int(df.duplicated().sum())

    data_inicial = df["GAME_DATE"].min()
    data_final = df["GAME_DATE"].max()

    periodo = "Não informado"

    if pd.notna(data_inicial) and pd.notna(data_final):
        periodo = (
            f"{data_inicial.strftime('%d/%m/%Y')} "
            f"até {data_final.strftime('%d/%m/%Y')}"
        )

    # --------------------------------------------------
    # HISTOGRAMA
    # --------------------------------------------------

    nome_variavel = variaveis[variavel]

    plt.figure(figsize=(9, 5))

    plt.hist(
        dados_time[variavel].dropna(),
        bins=10,
        edgecolor="black",
        alpha=0.8
    )

    plt.title(
        f"Distribuição de {nome_variavel} - {time_selecionado}"
    )

    plt.xlabel(nome_variavel)
    plt.ylabel("Frequência")

    plt.grid(
        axis="y",
        alpha=0.3
    )

    plt.tight_layout()

    caminho_grafico = CAMINHO_STATIC / "histograma.png"

    plt.savefig(caminho_grafico, dpi=120)
    plt.close()

    # --------------------------------------------------
    # ENVIO DOS DADOS PARA O HTML
    # --------------------------------------------------

    return render_template(
        "index.html",

        times=times,
        time=time_selecionado,

        variaveis=variaveis,
        variavel=variavel,
        nome_variavel=nome_variavel,

        estatisticas=estatisticas,

        total_registros=total_registros,
        total_colunas=total_colunas,
        total_times=total_times,
        total_partidas=total_partidas,

        total_jogos_time=total_jogos_time,

        total_ausentes=total_ausentes,
        total_duplicados=total_duplicados,

        periodo=periodo
    )


# --------------------------------------------------
# EXECUÇÃO
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
