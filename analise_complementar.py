"""Análises complementares do Projeto.

Recebe os dados do app.py e devolve tabelas e interpretações.
Não muda o fluxo do Flask nem os arquivos CSV já existentes.
"""
import pandas as pd

# Nome original -> (nome utilizado na base tratada, significado)
DICIONARIO = {
    'Team_ID': ('id_time', 'Identificador da equipe'),
    'Game_ID': ('id_partida', 'Identificador da partida'),
    'GAME_DATE': ('data_partida', 'Data em que a partida ocorreu'),
    'MATCHUP': ('confronto', 'Equipes envolvidas e mando de quadra'),
    'WL': ('resultado', 'Resultado: vitória = 1, derrota = 0'),
    'W': ('vitorias_acumuladas', 'Vitórias acumuladas até o registro'),
    'L': ('derrotas_acumuladas', 'Derrotas acumuladas até o registro'),
    'W_PCT': ('percentual_vitorias', 'Proporção de vitórias acumuladas'),
    'MIN': ('minutos', 'Minutos da equipe na partida'),
    'FGM': ('arremessos_convertidos', 'Arremessos de quadra convertidos'),
    'FGA': ('arremessos_tentados', 'Arremessos de quadra tentados'),
    'FG_PCT': ('aproveitamento_arremessos', 'Proporção de acerto em arremessos de quadra'),
    'FG3M': ('cestas_3_convertidas', 'Arremessos de três pontos convertidos'),
    'FG3A': ('tentativas_3', 'Arremessos de três pontos tentados'),
    'FG3_PCT': ('aproveitamento_3', 'Proporção de acerto de três pontos'),
    'FTM': ('lances_livres_convertidos', 'Lances livres convertidos'),
    'FTA': ('lances_livres_tentados', 'Lances livres tentados'),
    'FT_PCT': ('aproveitamento_lances_livres', 'Proporção de acerto de lances livres'),
    'OREB': ('rebotes_ofensivos', 'Rebotes ofensivos'),
    'DREB': ('rebotes_defensivos', 'Rebotes defensivos'),
    'REB': ('rebotes_totais', 'Soma de rebotes ofensivos e defensivos'),
    'AST': ('assistencias', 'Assistências'),
    'STL': ('roubos_bola', 'Roubos de bola'),
    'BLK': ('bloqueios', 'Bloqueios'),
    'TOV': ('turnovers', 'Perdas de posse de bola'),
    'PF': ('faltas_pessoais', 'Faltas pessoais'),
    'PTS': ('pontos', 'Pontuação da equipe na partida'),
    'TEAM_NAME': ('nome_time', 'Nome da equipe'),
}


METODOS = [
    ('IQR', 'Regra dos quartis: valores abaixo de Q1 - 1,5 IQR ou acima de Q3 + 1,5 IQR.'),
    ('Z-score', 'Distância padronizada à média, em desvios padrão; limiar |z| > 3.'),
    ('Grubbs', 'Teste estatístico para a observação mais distante da média; alfa = 0,05. O script atual testa um extremo por vez.'),
    ('ECOD', 'Identificação multivariada pela distribuição empírica das caudas; contaminação configurada no script.'),
    ('K-NN', 'Anomalia avaliada pela distância aos vizinhos no espaço padronizado.'),
    ('DBSCAN', 'Observações classificadas como ruído (rótulo -1) em agrupamento por densidade.'),
    ('LOF', 'Compara a densidade local de um registro com as densidades dos vizinhos; registros pouco densos são candidatos a anomalia.'),
]


def preparar_relatorio(df, variaveis, time_selecionado, variavel, pasta):
    """Monta tabelas (listas e matrizes) para o template Jinja2."""
    nomes = list(variaveis.keys())
    equipes = sorted(df['TEAM_NAME'].dropna().unique())

    # Cálculos por equipe e variável: todos feitos sobre a base original.
    linhas = []
    for time, grupo in df.groupby('TEAM_NAME'):
        for codigo, descricao in variaveis.items():
            v = pd.to_numeric(grupo[codigo], errors='coerce').dropna()
            if v.empty:
                continue
            media, mediana = v.mean(), v.median()
            desvio = v.std(ddof=1)
            q1 = v.quantile(.25, interpolation='linear')
            q3 = v.quantile(.75, interpolation='linear')
            iqr = q3-q1
            cv = 100 * desvio / media if media > 0 and pd.notna(desvio) else None
            skew = float(v.skew()) if len(v) >= 3 and desvio > 0 else None
            linhas.append({
                'time': time, 'codigo': codigo, 'variavel': descricao,
                'q1': float(q1), 'q3': float(q3), 'iqr': float(iqr),
                'cv': float(cv) if cv is not None else None,
                'skew': skew,
                'media': float(media), 'mediana': float(mediana),
                'desvio': float(desvio) if pd.notna(desvio) else None,
                'amplitude': float(v.max()-v.min()),
            })

    tabela = pd.DataFrame(linhas)
    ordem = [variaveis[c] for c in nomes]

    # pivot() muda apenas o formato da tabela: variáveis nas linhas, equipes nas colunas.
    def matriz(campo):
        m = tabela.pivot(index='variavel', columns='time', values=campo)
        m = m.reindex(index=ordem, columns=equipes)
        return [
            {'variavel': codigo, 'valores': [None if pd.isna(v) else float(v) for v in linha]}
            for codigo, linha in m.iterrows()
        ]

    recorte = tabela[tabela['codigo'] == variavel].sort_values('time')
    quartis = recorte[['time','q1','q3','iqr','amplitude','desvio']].to_dict('records')

    # Dicionário: nomes de explorar.py e tipos observados no CSV carregado.
    dicionario = []
    for coluna in df.columns:
        tratado, descricao = DICIONARIO.get(coluna, (coluna, 'Sem descrição cadastrada'))
        if coluna == 'GAME_DATE':
            tipo = 'Data'
        elif coluna in ('Team_ID', 'Game_ID'):
            tipo = 'Identificador'
        elif coluna == 'WL':
            tipo = 'Binária (0/1)'
        elif pd.api.types.is_numeric_dtype(df[coluna]):
            tipo = 'Numérica'
        else:
            tipo = 'Texto/categórica'
        dicionario.append({'original': coluna, 'tratado': tratado, 'tipo': tipo, 'descricao': descricao})

    # Ausentes por coluna, com percentual calculado sobre o total de linhas.
    ausentes = [
        {'coluna': c, 'quantidade': int(df[c].isna().sum()),
         'percentual': 100 * df[c].isna().sum()/len(df) if len(df) else 0}
        for c in df.columns
    ]

    # Verificações de qualidade reproduzem regras de qualidade.py.
    verificacoes = []
    def incluir(titulo, valor):
        verificacoes.append({'nome': titulo, 'quantidade': int(valor)})

    incluir('Linhas completamente duplicadas', df.duplicated().sum())
    incluir('Duplicatas de equipe-partida', df.duplicated(subset=['Team_ID','Game_ID']).sum())
    incluir('Datas inválidas/ausentes', df['GAME_DATE'].isna().sum())
    contagem = ['MIN','W','L','FGM','FGA','FG3M','FG3A','FTM','FTA','OREB','DREB','REB','AST','STL','BLK','TOV','PF','PTS']
    negativos = sum(int((df[c] < 0).sum()) for c in contagem)
    incluir('Valores negativos em campos de contagem', negativos)
    percentuais = ['W_PCT','FG_PCT','FG3_PCT','FT_PCT']
    incluir('Percentuais fora de 0 a 1', sum(int(((df[c] < 0)|(df[c] > 1)).sum()) for c in percentuais))
    incluir('FGM maior que FGA', (df['FGM']>df['FGA']).sum())
    incluir('FG3M maior que FG3A', (df['FG3M']>df['FG3A']).sum())
    incluir('FTM maior que FTA', (df['FTM']>df['FTA']).sum())
    incluir('REB diferente de OREB + DREB', (df['REB'] != df['OREB']+df['DREB']).sum())
    incluir('PTS diferente de 2×FGM + FG3M + FTM', (df['PTS'] != 2*df['FGM']+df['FG3M']+df['FTM']).sum())
    incluir('Partidas com número de registros diferente de 2', (df.groupby('Game_ID').size() != 2).sum())
    incluir('Partidas sem exatamente uma vitória', (df.groupby('Game_ID')['WL'].sum() != 1).sum())
    zeros = [{'coluna': c, 'quantidade': int((df[c] == 0).sum())} for c in contagem]

    # Destaques específicos para a variável escolhida, sem impor limiares arbitrários.
    valido_cv = recorte.dropna(subset=['cv'])
    valido_iqr = recorte.dropna(subset=['iqr'])
    destaques = []
    if not valido_cv.empty:
        maior_cv = valido_cv.loc[valido_cv['cv'].idxmax()]
        menor_cv = valido_cv.loc[valido_cv['cv'].idxmin()]
        destaques.append(
            f'Em {variaveis[variavel]}, {maior_cv["time"]} apresenta maior CV ({maior_cv["cv"]:.2f}%), '
            f'enquanto {menor_cv["time"]} apresenta menor CV ({menor_cv["cv"]:.2f}%). '
            'CV maior indica maior dispersão relativa, mas sua leitura exige cautela quando a média é baixa.'
        )
    if not valido_iqr.empty:
        maior_iqr = valido_iqr.loc[valido_iqr['iqr'].idxmax()]
        menor_iqr = valido_iqr.loc[valido_iqr['iqr'].idxmin()]
        destaques.append(
            f'Para {variaveis[variavel]}, a faixa dos 50% centrais é mais larga em '
            f'{maior_iqr["time"]} (IQR {maior_iqr["iqr"]:.2f}) e mais estreita em '
            f'{menor_iqr["time"]} (IQR {menor_iqr["iqr"]:.2f}).'
        )
    time_atual = recorte[recorte['time'] == time_selecionado]
    if not time_atual.empty:
        registro = time_atual.iloc[0]
        if pd.notna(registro['skew']):
            escolha = 'A mediana merece atenção por ser menos sensível a extremos.' if abs(registro['skew']) >= 1 else 'Média e mediana devem ser comparadas com o gráfico.'
            destaques.append(f'Assimetria de {time_selecionado} em {variaveis[variavel]}: {registro["skew"]:.3f}. {escolha}')
        if registro['media'] > 0 and registro['media'] < 1:
            destaques.append('A média está próxima de zero: o CV pode ficar artificialmente elevado.')
        if registro['iqr'] > 0 and registro['amplitude'] > 3*registro['iqr']:
            destaques.append('A amplitude é mais de três vezes o IQR; a distribuição merece inspeção dos extremos no Boxplot.')

    return {
        'equipes_comparacao': equipes,
        'matriz_cv': matriz('cv'),
        'matriz_iqr': matriz('iqr'),
        'matriz_assimetria': matriz('skew'),
        'quartis_comparativos': quartis,
        'dicionario_dados': dicionario,
        'ausentes_por_coluna': ausentes,
        'verificacoes_qualidade': verificacoes,
        'zeros_por_coluna': zeros,
        'metodos_explicacao': METODOS,
        'destaques_comparativos': destaques,
    }
