
from flask import Flask, render_template, request
import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Base original
df = pd.read_csv(
    "data/original/stats_times_regular_final.csv",
    dtype={"Game_ID": "string"}
)

# Códigos usados internamente e nomes exibidos na interface
nomes_variaveis = {
    "PTS": "Pontos",
    "REB": "Rebotes totais",
    "AST": "Assistências",
    "STL": "Roubos de bola",
    "BLK": "Bloqueios",
    "PF": "Faltas pessoais",
    "FG3M": "Cestas de 3 convertidas"
}

variaveis = list(nomes_variaveis.keys())

# Correspondência entre nomes dos métodos e arquivos
arquivos_outliers = {
    "IQR": "data/processed/outliers_iqr.csv",
    "Z-score": "data/processed/outliers_zscore.csv",
    "Grubbs": "data/processed/outliers_grubbs.csv",
    "ECOD": "data/processed/outliers_ecod.csv",
    "K-NN": "data/processed/outliers_knn.csv",
    "DBSCAN": "data/processed/outliers_dbscan.csv"
}

# Nomes das variáveis da base tratada
nomes_variaveis_tratadas = {
    "pontos": "Pontos",
    "rebotes_totais": "Rebotes totais",
    "assistencias": "Assistências",
    "roubos_bola": "Roubos de bola",
    "bloqueios": "Bloqueios",
    "faltas_pessoais": "Faltas pessoais",
    "cestas_3_convertidas": "Cestas de 3 convertidas"
}

# Carregamento dos resultados dos métodos
resultados_outliers = {}

for metodo, caminho in arquivos_outliers.items():
    resultados_outliers[metodo] = pd.read_csv(
        caminho,
        dtype={"id_partida": "string"}
    )

os.makedirs("static", exist_ok=True)


@app.route("/")
def inicio():

    times = sorted(df["TEAM_NAME"].unique())

    time_selecionado = request.args.get("time", times[0])

    if time_selecionado not in times:
        time_selecionado = times[0]

    variavel = request.args.get("variavel", "PTS")

    if variavel not in variaveis:
        variavel = "PTS"

    # Dados da equipe selecionada
    dados_time = df[df["TEAM_NAME"] == time_selecionado]

    # Estatísticas descritivas
    estatisticas = (
        dados_time[variaveis]
        .describe()
        .round(2)
        .to_dict()
    )

    # Histograma
    plt.figure(figsize=(9, 5))

    plt.hist(
        dados_time[variavel].dropna(),
        bins=10,
        edgecolor="white",
        linewidth=1.2
    )

    nome_variavel = nomes_variaveis[variavel]

    plt.title(f"Distribuição de {nome_variavel}", fontsize=14)
    plt.xlabel(nome_variavel)
    plt.ylabel("Frequência")
    plt.grid(axis="y", alpha=0.2)

    plt.tight_layout()
    plt.savefig("static/histograma.png", dpi=120)
    plt.close()

    # Resumo dos métodos
    resumo_metodos = []
    outliers = []

    for metodo, dados_metodo in resultados_outliers.items():

        dados_equipe = dados_metodo[
            dados_metodo["time"] == time_selecionado
        ]

        quantidade_partidas = dados_equipe["id_partida"].nunique()

        resumo_metodos.append({
            "metodo": metodo,
            "quantidade": quantidade_partidas
        })

        # Detalhamento dos registros identificados
        for _, linha in dados_equipe.iterrows():

            registro = {
                "metodo": metodo,
                "partida": linha["id_partida"],
                "data": linha["data_partida"],
                "variavel": "Análise multivariada",
                "valor": "—",
                "detalhe": "Anomalia identificada"
            }

            if metodo == "IQR":
                registro["variavel"] = nomes_variaveis_tratadas.get(
                    linha["variavel"], linha["variavel"]
                )
                registro["valor"] = linha["valor"]
                registro["detalhe"] = (
                    f"{linha['tipo']} | Limites: "
                    f"{linha['limite_inferior']} a "
                    f"{linha['limite_superior']}"
                )

            elif metodo == "Z-score":
                registro["variavel"] = nomes_variaveis_tratadas.get(
                    linha["variavel"], linha["variavel"]
                )
                registro["valor"] = linha["valor"]
                registro["detalhe"] = (
                    f"Z-score: {linha['z_score']:.2f}"
                )

            elif metodo == "Grubbs":
                registro["variavel"] = nomes_variaveis_tratadas.get(
                    linha["variavel"], linha["variavel"]
                )
                registro["valor"] = linha["valor"]
                registro["detalhe"] = (
                    f"G: {linha['G']:.2f} | "
                    f"G crítico: {linha['G_critico']:.2f}"
                )

            elif metodo == "ECOD":
                registro["valor"] = round(
                    linha["pontuacao_anomalia"], 2
                )
                registro["detalhe"] = "Pontuação de anomalia"

            elif metodo == "K-NN":
                registro["valor"] = round(
                    linha["pontuacao_anomalia"], 2
                )
                registro["detalhe"] = "Pontuação de anomalia"

            elif metodo == "DBSCAN":
                registro["valor"] = linha["rotulo"]
                registro["detalhe"] = (
                    "Observação classificada como ruído"
                )

            outliers.append(registro)

    outliers.sort(
        key=lambda registro: str(registro["data"]),
        reverse=True
    )

    return render_template(
        "index.html",
        times=times,
        time=time_selecionado,
        variaveis=variaveis,
        nomes_variaveis=nomes_variaveis,
        variavel=variavel,
        nome_variavel=nome_variavel,
        estatisticas=estatisticas,
        total_partidas=len(dados_time),
        resumo_metodos=resumo_metodos,
        outliers=outliers
    )


if __name__ == "__main__":
    app.run(debug=True)
