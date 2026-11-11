# ------ aplicação flask ------
# importação de bibliotecas
from flask import Flask, render_template, request
import pandas as pd
import matplotlib

import matplotlib.pyplot as plt
import os

# criação da aplicação --> inicialização do flask
app = Flask(__name__)

# Carregando a base
df = pd.read_csv("data/stats_times_regular_final.csv")

# Variaveis principais
variaveis = ["PTS","REB","AST","STL","BLK","PF", "FG3M"]

os.makedirs("static", exist_ok=True)


# criação de uma rota -> uma rota define o endereço que o usuário pode acessar
@app.route("/")

def inicio():

    times = sorted(df["TEAM_NAME"].unique())

    # recebimento do filtro -> o flask recebe o time selecionado pelo usuario através da URL
    time_selecionado = request.args.get("time", times[0])

    if time_selecionado not in times:
        time_selecionado = times[0]

    variavel = request.args.get("variavel", "PTS")

    if variavel not in variaveis:
        variavel = "PTS"

    # Filtragem de dados -> seleciona apenas os registros daquele time
    dados_time = df [
        df["TEAM_NAME"] == time_selecionado
    ]

    # calculo das estatisticas
    estatisticas = (
        dados_time[variaveis]
        .describe()
        .round(2)
        .to_dict()
    )

    # Gerando histograma
    plt.figure(figsize=(8, 5))

    plt.hist(
        dados_time[variavel].dropna(),
        bins=10,
        edgecolor="black"
    )

    plt.title(f"Distribuição de {variavel} - {time_selecionado}")
    plt.xlabel(variavel)
    plt.ylabel("Frequência")
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig("static/histograma.png")
    plt.close()

    return render_template(
        "index.html",
        times=times,
        time=time_selecionado,
        estatisticas=estatisticas,
        total_partidas=len(dados_time)
    )

if __name__ == "__main__":
    app.run(debug=True)