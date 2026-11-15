
from pathlib import Path

from flask import Flask, render_template, request
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ==========================================
# 1. CONFIGURAÇÕES INICIAIS
# ==========================================

app = Flask(__name__)

# Diretório principal do projeto
BASE_DIR = Path(__file__).resolve().parent

# Caminhos dos arquivos
CAMINHO_DADOS = (
    BASE_DIR
    / "data"
    / "original"
    / "stats_times_regular_final.csv"
)

CAMINHO_PROCESSADOS = BASE_DIR / "data" / "processed"
CAMINHO_STATIC = BASE_DIR / "static"

CAMINHO_STATIC.mkdir(exist_ok=True)


# ==========================================
# 2. CARREGAMENTO DA BASE
# ==========================================

df = pd.read_csv(
    CAMINHO_DADOS,
    dtype={
        "Game_ID": "string",
        "Team_ID": "string"
    }
)

# Conversão de datas
df["GAME_DATE"] = pd.to_datetime(
    df["GAME_DATE"],
    errors="coerce"
)


# ==========================================
# 3. VARIÁVEIS ANALISADAS
# ==========================================

variaveis = {
    "PTS": "Pontos",
    "REB": "Rebotes totais",
    "AST": "Assistências",
    "STL": "Roubos de bola",
    "BLK": "Bloqueios",
    "PF": "Faltas pessoais",
    "FG3M": "Cestas de 3 convertidas"
}

# Correspondência de nomes da base tratada
nomes_variaveis_tratadas = {
    "pontos": "Pontos",
    "rebotes_totais": "Rebotes totais",
    "assistencias": "Assistências",
    "roubos_bola": "Roubos de bola",
    "bloqueios": "Bloqueios",
    "faltas_pessoais": "Faltas pessoais",
    "cestas_3_convertidas": "Cestas de 3 convertidas"
}


# ==========================================
# 4. CARREGAMENTO DOS OUTLIERS
# ==========================================

arquivos_outliers = {
    "IQR": "outliers_iqr.csv",
    "Z-score": "outliers_zscore.csv",
    "Grubbs": "outliers_grubbs.csv",
    "ECOD": "outliers_ecod.csv",
    "K-NN": "outliers_knn.csv",
    "DBSCAN": "outliers_dbscan.csv"
}

resultados_outliers = {}

for metodo, arquivo in arquivos_outliers.items():

    caminho = CAMINHO_PROCESSADOS / arquivo

    resultados_outliers[metodo] = pd.read_csv(
        caminho,
        dtype={"id_partida": "string"}
    )


# ==========================================
# 5. ROTA PRINCIPAL
# ==========================================

@app.route("/")
def inicio():

    # --------------------------------------
    # FILTROS
    # --------------------------------------

    times = sorted(
        df["TEAM_NAME"].dropna().unique()
    )

    time_selecionado = request.args.get(
        "time", times[0]
    )

    if time_selecionado not in times:
        time_selecionado = times[0]

    variavel = request.args.get(
        "variavel", "PTS"
    )

    if variavel not in variaveis:
        variavel = "PTS"

    nome_variavel = variaveis[variavel]

    # Base filtrada pela equipe
    dados_time = df[
        df["TEAM_NAME"] == time_selecionado
    ].copy()
    
    # ======================================
    # 6. VISÃO GERAL DO DATASET
    # ======================================

    total_registros = len(df)
    total_colunas = len(df.columns)
    total_times = df["TEAM_NAME"].nunique()

    # Partidas únicas da base
    total_partidas_base = df["Game_ID"].nunique()

    # Registros da equipe selecionada
    total_jogos_time = len(dados_time)

    # Qualidade dos dados
    total_ausentes = int(
        df.isna().sum().sum()
    )

    total_duplicados = int(
        df.duplicated().sum()
    )

    # Período analisado
    data_inicial = df["GAME_DATE"].min()
    data_final = df["GAME_DATE"].max()

    periodo = "Não informado"

    if (
        pd.notna(data_inicial)
        and pd.notna(data_final)
    ):
        periodo = (
            f"{data_inicial:%d/%m/%Y} "
            f"até {data_final:%d/%m/%Y}"
        )


    # ======================================
    # 7. ESTATÍSTICAS DESCRITIVAS
    # ======================================

    estatisticas = []

    for codigo, nome in variaveis.items():

        valores = dados_time[codigo].dropna()

        if valores.empty:
            continue

        # Moda
        modas = valores.mode()

        moda = (
            float(modas.iloc[0])
            if not modas.empty
            else None
        )

        # Quartis
        q1 = valores.quantile(0.25)
        q3 = valores.quantile(0.75)

        # Intervalo interquartil
        iqr = q3 - q1

        # Amplitude
        amplitude = valores.max() - valores.min()

        # Estatísticas
        estatisticas.append({
            "nome": nome,
            "media": valores.mean(),
            "mediana": valores.median(),
            "moda": moda,
            "desvio": valores.std(ddof=1),
            "variancia": valores.var(ddof=1),
            "minimo": valores.min(),
            "maximo": valores.max(),
            "amplitude": amplitude,
            "q1": q1,
            "q3": q3,
            "iqr": iqr
        })


    # ======================================
    # INTERPRETAÇÃO DOS RESULTADOS
    # ======================================

    # Seleciona os valores da variável escolhida
    valores_analise = dados_time[variavel].dropna()

    media = valores_analise.mean()
    mediana = valores_analise.median()

    desvio = valores_analise.std(ddof=1)

    q1 = valores_analise.quantile(0.25)
    q3 = valores_analise.quantile(0.75)

    iqr = q3 - q1

    # Coeficiente de variação
    cv = (
        (desvio / media) * 100
        if media > 0
        else None
    )

    # Limites para identificação de outliers
    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr

    outliers_variavel = valores_analise[
        (valores_analise < limite_inferior)
        | (valores_analise > limite_superior)
    ]

    quantidade_outliers = len(outliers_variavel)

    # Interpretação da tendência central
    if media > mediana:
        interpretacao_central = (
            f"A média de {nome_variavel.lower()} "
            f"({media:.2f}) é superior à mediana "
            f"({mediana:.2f}). Isso indica que valores "
            f"elevados podem estar influenciando a média."
        )

    elif media < mediana:
        interpretacao_central = (
            f"A média de {nome_variavel.lower()} "
            f"({media:.2f}) é inferior à mediana "
            f"({mediana:.2f}). Valores baixos podem "
            f"estar influenciando o resultado médio."
        )

    else:
        interpretacao_central = (
            f"A média e a mediana de "
            f"{nome_variavel.lower()} são iguais "
            f"({media:.2f}), indicando coincidência "
            f"entre essas duas medidas centrais."
        )

    # Interpretação da dispersão
    if cv is not None:

        interpretacao_dispersao = (
            f"O coeficiente de variação é de "
            f"{cv:.2f}%, indicando a dispersão "
            f"relativa dos valores em relação à média."
        )

        if media < 1:
            interpretacao_dispersao += (
                " Como a média é muito pequena, "
                "o CV deve ser interpretado com cautela."
            )

    else:
        interpretacao_dispersao = (
            "O coeficiente de variação não foi "
            "calculado porque a média não é positiva."
        )

    # Interpretação do intervalo interquartil
    interpretacao_iqr = (
        f"Metade central dos registros de "
        f"{nome_variavel.lower()} está aproximadamente "
        f"entre {q1:.2f} e {q3:.2f}, "
        f"com intervalo interquartil de {iqr:.2f}."
    )

    # Interpretação dos outliers
    interpretacao_outliers = (
        f"Foram identificadas {quantidade_outliers} "
        f"observações fora dos limites de "
        f"{limite_inferior:.2f} e "
        f"{limite_superior:.2f}, utilizando "
        f"a regra de 1,5 × IQR."
    )

    interpretacoes = [
        interpretacao_central,
        interpretacao_dispersao,
        interpretacao_iqr,
        interpretacao_outliers
    ]

    # ======================================
    # 8. HISTOGRAMA
    # ======================================

    plt.figure(figsize=(9, 5))

    plt.hist(
        dados_time[variavel].dropna(),
        bins=10,
        color="#4285D4",
        edgecolor="white",
        linewidth=1.2
    )

    plt.title(
        f"Distribuição de {nome_variavel}"
        f" - {time_selecionado}",
        fontsize=14
    )

    plt.xlabel(nome_variavel)
    plt.ylabel("Frequência de partidas")

    plt.grid(
        axis="y",
        alpha=0.2
    )

    plt.tight_layout()

    caminho_grafico = (
        CAMINHO_STATIC / "histograma.png"
    )

    plt.savefig(
        caminho_grafico,
        dpi=120
    )

    plt.close()


    # ======================================
    # 9. RESUMO DOS MÉTODOS DE OUTLIERS
    # ======================================

    resumo_metodos = []
    outliers = []

    for metodo, dados_metodo in resultados_outliers.items():

        dados_equipe = dados_metodo[
            dados_metodo["time"] == time_selecionado
        ]

        quantidade_partidas = (
            dados_equipe["id_partida"].nunique()
        )

        resumo_metodos.append({
            "metodo": metodo,
            "quantidade": int(quantidade_partidas)
        })


        # ==================================
        # 10. DETALHAMENTO DOS OUTLIERS
        # ==================================

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

                registro["variavel"] = (
                    nomes_variaveis_tratadas.get(
                        linha["variavel"],
                        linha["variavel"]
                    )
                )

                registro["valor"] = linha["valor"]

                registro["detalhe"] = (
                    f"{linha['tipo']} | "
                    f"Limites: "
                    f"{linha['limite_inferior']:.2f} "
                    f"a {linha['limite_superior']:.2f}"
                )

            elif metodo == "Z-score":

                registro["variavel"] = (
                    nomes_variaveis_tratadas.get(
                        linha["variavel"],
                        linha["variavel"]
                    )
                )

                registro["valor"] = linha["valor"]

                registro["detalhe"] = (
                    f"Z-score: "
                    f"{linha['z_score']:.2f}"
                )

            elif metodo == "Grubbs":

                registro["variavel"] = (
                    nomes_variaveis_tratadas.get(
                        linha["variavel"],
                        linha["variavel"]
                    )
                )

                registro["valor"] = linha["valor"]

                registro["detalhe"] = (
                    f"G: {linha['G']:.2f} | "
                    f"G crítico: "
                    f"{linha['G_critico']:.2f}"
                )

            elif metodo in ["ECOD", "K-NN"]:

                registro["valor"] = round(
                    linha["pontuacao_anomalia"], 2
                )

                registro["detalhe"] = (
                    "Pontuação de anomalia"
                )

            elif metodo == "DBSCAN":

                registro["valor"] = linha["rotulo"]

                registro["detalhe"] = (
                    "Observação classificada como ruído"
                )

            outliers.append(registro)


    # Ordenação por data
    outliers.sort(
        key=lambda registro: str(registro["data"]),
        reverse=True
    )


    # ======================================
    # 11. ENVIO DOS DADOS AO HTML
    # ======================================

    return render_template(
        "index.html",

        # Filtros
        times=times,
        time=time_selecionado,
        variaveis=variaveis,
        variavel=variavel,
        nome_variavel=nome_variavel,

        # Estatísticas
        estatisticas=estatisticas,
        total_jogos_time=total_jogos_time,
        interpretacoes=interpretacoes,

        # Dataset
        total_registros=total_registros,
        total_colunas=total_colunas,
        total_times=total_times,
        total_partidas_base=total_partidas_base,

        # Compatibilidade com versões antigas
        total_partidas=total_partidas_base,

        # Qualidade
        total_ausentes=total_ausentes,
        total_duplicados=total_duplicados,
        periodo=periodo,

        # Outliers
        resumo_metodos=resumo_metodos,
        outliers=outliers
    )



# ==========================================
# 12. EXECUÇÃO DA APLICAÇÃO
# ==========================================
if __name__ == "__main__":
    app.run(debug=True)
