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

    # REFINO_GAME_INSIGHTS_2026: traduzir resultados estatisticos para o basquete.
    valido_cv = recorte.dropna(subset=['cv'])
    valido_iqr = recorte.dropna(subset=['iqr'])
    destaques = []
    time_atual = recorte[recorte['time'] == time_selecionado]

    if not time_atual.empty:
        atual = time_atual.iloc[0]
        destaques.append(
            f'Nos jogos do {time_selecionado}, a media de {variaveis[variavel].lower()} '
            f'foi {atual["media"]:.2f} por partida e a mediana foi {atual["mediana"]:.2f}. '
            'A media resume todos os jogos; a mediana indica o valor central, '
            'sem ser tao influenciada por partidas muito diferentes do habitual.'
        )

    if not valido_cv.empty:
        mais_regular = valido_cv.loc[valido_cv['cv'].idxmin()]
        menos_regular = valido_cv.loc[valido_cv['cv'].idxmax()]
        destaques.append(
            f'Na estatistica de {variaveis[variavel].lower()}, '
            f'{mais_regular["time"]} teve a menor oscilacao relativa entre partidas '
            f'(CV de {mais_regular["cv"]:.2f}%). '
            f'{menos_regular["time"]} oscilou mais (CV de {menos_regular["cv"]:.2f}%). '
            'Isso fala de regularidade, nao de quem teve o melhor desempenho medio.'
        )

    if not time_atual.empty:
        atual = time_atual.iloc[0]
        destaques.append(
            f'No {time_selecionado}, metade dos jogos ficou aproximadamente entre '
            f'{atual["q1"]:.2f} e {atual["q3"]:.2f} '
            f'em {variaveis[variavel].lower()}. Essa faixa tem largura de '
            f'{atual["iqr"]:.2f} (IQR). Quanto mais estreita, mais proximos '
            'ficaram os resultados centrais das partidas.'
        )

    if not valido_iqr.empty:
        mais_concentrado = valido_iqr.loc[valido_iqr['iqr'].idxmin()]
        mais_espalhado = valido_iqr.loc[valido_iqr['iqr'].idxmax()]
        destaques.append(
            f'Comparando as equipes nessa mesma estatistica, a metade central '
            f'dos jogos foi mais concentrada em {mais_concentrado["time"]} '
            f'(IQR {mais_concentrado["iqr"]:.2f}) e mais espalhada em '
            f'{mais_espalhado["time"]} (IQR {mais_espalhado["iqr"]:.2f}). '
            'O IQR observa os resultados centrais e sofre menos influencia de jogos extremos.'
        )

    if not time_atual.empty:
        atual = time_atual.iloc[0]
        if pd.notna(atual['skew']):
            g = atual['skew']
            if abs(g) < 0.5:
                forma = 'os resultados ficaram aproximadamente equilibrados em torno da faixa central'
            elif g > 0:
                forma = 'algumas partidas com valores mais altos alongaram a cauda da distribuicao para a direita'
            else:
                forma = 'algumas partidas com valores mais baixos alongaram a cauda da distribuicao para a esquerda'
            destaques.append(
                f'A assimetria do {time_selecionado} em {variaveis[variavel].lower()} '
                f'foi {g:.3f}: {forma}. O histograma e o Boxplot ajudam a conferir '
                'esse comportamento; o coeficiente sozinho nao conta toda a historia.'
            )
        if atual['media'] > 0 and atual['media'] < 1:
            destaques.append(
                'Como a media desta estatistica e muito pequena, uma pequena mudanca '
                'entre jogos pode produzir CV elevado. Por isso, a interpretacao exige cautela.'
            )
        if atual['iqr'] > 0 and atual['amplitude'] > 3 * atual['iqr']:
            destaques.append(
                f'A diferenca entre o maior e o menor resultado do {time_selecionado} '
                'e bem maior do que a faixa central dos jogos. Isso sugere que vale '
                'olhar as partidas extremas no Boxplot, sem concluir que haja erro nos dados.'
            )

    # Comparacao das sete estatisticas dentro da equipe, sempre pelo CV (percentual).
    dados_equipe = tabela[tabela['time'] == time_selecionado].dropna(subset=['cv'])
    dados_equipe = dados_equipe[dados_equipe['media'] > 0]
    if len(dados_equipe) > 1:
        menor = dados_equipe.loc[dados_equipe['cv'].idxmin()]
        maior = dados_equipe.loc[dados_equipe['cv'].idxmax()]
        destaques.append(
            f'Entre as sete estatisticas do {time_selecionado}, '
            f'{menor["variavel"].lower()} teve a menor variacao proporcional '
            f'(CV {menor["cv"]:.2f}%), enquanto {maior["variavel"].lower()} '
            f'teve a maior (CV {maior["cv"]:.2f}%). '
            'Essa comparacao usa porcentagens porque pontos, assistencias e bloqueios '
            'possuem escalas diferentes. Medias muito pequenas exigem cuidado.'
        )

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
