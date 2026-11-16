# Análise Esportiva — Projeto 1 (UFAPE, 2026.2)

Aplicação web em Flask para análise exploratória de estatísticas de partidas da NBA.

## Executar

Na pasta do projeto, com Python e pip instalados:

```powershell
python -m pip install -r requirements.txt
python app.py
```

Acesse http://127.0.0.1:5000 .

## Estrutura preservada

- `explorar.py`: tratamento inicial e exportação para `data/processed/dados_tratados.csv`.
- `qualidade.py`: regras de consistência e relatório de qualidade.
- `outliers.py` e `metodos_outliers/`: análise e algoritmos de outliers.
- `metodos_outliers/lof.py`: LOF por equipe, com padronização e contaminação de 5%.
- `analise_complementar.py`: dicionário, matrizes de CV/IQR/assimetria e tabelas de qualidade.
- `app.py`: filtros Flask, estatística por equipe e gráficos; lê arquivos CSV de anomalias.
- `templates/index.html` e `static/css/style.css`: apresentação.

## Atualizar resultados do LOF

```powershell
python metodos_outliers/lof.py
```

Em caso de atualização da base, execute `explorar.py` antes dos métodos de outliers.

## Metodologia

- Fisher-Pearson ajustado (pandas `skew`), mínimo de três observações.
- Desvio padrão amostral (`ddof=1`). CV = 100 × desvio / média; não interpretar CV com média próxima de zero.
- Q1 e Q3 via interpolação linear do pandas; IQR = Q3 − Q1; limites de Tukey 1,5×IQR.
- Histograma com KDE gaussiana (`scipy.stats.gaussian_kde`, largura de banda Scott).
- LOF multivariado, distância euclidiana de dados padronizados (`StandardScaler`) e 5% de contaminação.

## Limitações

- Os mecanismos MCAR/MAR/MNAR são discutidos, mas os testes específicos não foram executados.
- O teste de Grubbs anterior avalia apenas o candidato mais extremo por equipe e variável.
- A comparação inclui as equipes disponíveis no arquivo; pode ser restringida às equipes do grupo se necessário.
- Os gráficos originais usam nomes estáticos; aplicação é prioritariamente para apresentação local.
- Resultados descritivos não demonstram causalidade nem predição.

## Entrega

O sistema é o relatório do projeto. Verifique as instruções atuais de submissão do Classroom.
