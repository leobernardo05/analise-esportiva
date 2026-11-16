
# 🏀 NBA Analytics — Game Insights


Aplicação web desenvolvida em **Python e Flask** para realizar análises estatísticas de partidas da NBA, comparar o desempenho das equipes e apresentar os resultados por meio de gráficos, tabelas e interpretações em linguagem acessível.

O sistema funciona como um relatório interativo de análise exploratória de dados, permitindo selecionar equipes e variáveis e acompanhar os resultados correspondentes.

---

## 1. Objetivo

O objetivo deste projeto é investigar o comportamento das principais estatísticas das equipes da NBA ao longo das partidas, identificando padrões, variações, assimetrias e observações atípicas.

O projeto analisa sete variáveis:

| Código | Variável | Unidade |
|---|---|---|
| PTS | Pontos | Pontos por partida |
| REB | Rebotes totais | Rebotes por partida |
| AST | Assistências | Assistências por partida |
| STL | Roubos de bola | Roubos por partida |
| BLK | Bloqueios | Bloqueios por partida |
| PF | Faltas pessoais | Faltas por partida |
| FG3M | Cestas de três pontos convertidas | Cestas por partida |

O conjunto de dados possui registros por equipe-partida. Um jogo pode gerar dois registros, um para cada equipe, portanto a quantidade de linhas não corresponde necessariamente ao número de partidas distintas.

## 2. Tecnologias utilizadas

| Tecnologia | Finalidade |
|---|---|
| Python | Linguagem principal |
| Flask | Desenvolvimento da aplicação web |
| pandas | Manipulação e análise dos dados |
| NumPy | Operações numéricas |
| SciPy | Testes estatísticos e KDE |
| Matplotlib | Criação dos gráficos |
| scikit-learn | Algoritmos de detecção de anomalias |
| PyOD | Métodos especializados de detecção de outliers |
| Jinja2 | Integração dos resultados Python com HTML |
| HTML5 | Estrutura da interface |
| CSS3 | Estilização e responsividade |
| JavaScript | Interações visuais da interface |

As dependências utilizadas estão declaradas no arquivo `requirements.txt`.

## 3. Instalação e execução local

### Requisitos

- Python instalado;
- pip disponível;
- acesso ao terminal;
- navegador web.

### Windows — PowerShell

Clone o repositório:

```powershell
git clone https://github.com/leobernardo05/analise-esportiva.git
cd analise-esportiva
```

Crie e ative o ambiente virtual:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

Inicie a aplicação:

```powershell
python app.py
```

Acesse:

**http://127.0.0.1:5000**

### Linux e macOS

```bash
git clone https://github.com/leobernardo05/analise-esportiva.git
cd analise-esportiva

python3 -m venv venv
source venv/bin/activate

python -m pip install -r requirements.txt
python app.py
```

O repositório já contém o dataset e os resultados processados necessários para a visualização inicial. Não é necessário executar novamente todos os algoritmos para acessar o dashboard.

O modo `debug=True` é utilizado somente no desenvolvimento local.

---

## 4. Estrutura do projeto

```text
analise-esportiva/
│
├── app.py
├── analise_complementar.py
├── explorar.py
├── qualidade.py
│
├── metodos_outliers/
│   ├── __init__.py
│   ├── iqr.py
│   ├── zscore.py
│   ├── grubbs.py
│   ├── ecod.py
│   ├── knn.py
│   ├── dbscan.py
│   └── lof.py
│
├── data/
│   ├── original/
│   │   └── stats_times_regular_final.csv
│   │
│   └── processed/
│       ├── dados_tratados.csv
│       ├── relatorio_qualidade.csv
│       ├── outliers_iqr.csv
│       ├── outliers_zscore.csv
│       ├── outliers_grubbs.csv
│       ├── outliers_ecod.csv
│       ├── outliers_knn.csv
│       ├── outliers_dbscan.csv
│       ├── outliers_lof.csv
│       └── outros relatórios auxiliares
│
├── templates/
│   ├── base.html
│   └── index.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── histograma.png
│   ├── boxplot.png
│   └── barras.png
│
├── requirements.txt
├── .gitignore
└── README.md
```

### Responsabilidade dos arquivos

**`app.py`**

Arquivo principal da aplicação. Inicializa o Flask, carrega os dados, recebe os filtros, calcula medidas estatísticas, gera gráficos e envia os resultados ao template HTML.

**`analise_complementar.py`**

Responsável pelas matrizes de CV, IQR e assimetria, pelo dicionário de dados e pelas interpretações comparativas.

**`explorar.py`**

Realiza a exploração inicial, a padronização dos nomes das colunas e o tratamento dos tipos de dados, especialmente datas e identificadores.

**`qualidade.py`**

Executa verificações de integridade, incluindo valores ausentes, duplicidades, valores negativos e inconsistências entre estatísticas.

**`metodos_outliers/`**

Contém os sete métodos utilizados para identificar observações estatisticamente atípicas.

**`templates/`**

Contém o layout principal e o conteúdo das análises utilizando Jinja2.

**`static/css/style.css`**

Define a identidade visual Game Insights, a sidebar, os cards, as tabelas e o comportamento responsivo.

---

## 5. Fluxo de processamento

O projeto segue as seguintes etapas:

1. **Carregamento:** leitura do dataset original.
2. **Exploração:** identificação das colunas, tipos de dados e características da base.
3. **Tratamento:** padronização de nomes e conversão dos campos necessários.
4. **Qualidade:** verificação de valores ausentes, duplicados e inconsistências.
5. **Outliers:** execução dos métodos estatísticos e algoritmos de detecção.
6. **Análise descritiva:** cálculo das medidas por equipe e variável.
7. **Visualização:** geração de gráficos, tabelas e matrizes comparativas.
8. **Interpretação:** elaboração de comentários com base nos resultados calculados.

O Flask utiliza a base original para as estatísticas descritivas e os CSVs previamente processados para apresentar os resultados de detecção de outliers.

---

## 6. Funcionalidades do dashboard

O sistema está organizado em dez seções.

### 6.1. Visão geral

Apresenta:

- Quantidade de registros;
- Número de colunas;
- Total de equipes;
- Quantidade de partidas distintas;
- Período analisado.

### 6.2. Qualidade dos dados

Apresenta indicadores de valores ausentes e duplicados.

Os scripts de qualidade também verificam valores negativos, percentuais inválidos e inconsistências entre estatísticas relacionadas.

### 6.3. Dicionário de dados

Apresenta os nomes originais e tratados das colunas, seus tipos e significados no contexto das partidas da NBA.

### 6.4. Estatísticas descritivas

Para as sete variáveis, o sistema calcula:

- Média;
- Mediana;
- Moda;
- Mínimo e máximo;
- Amplitude;
- Desvio padrão;
- Variância;
- Primeiro quartil (Q1);
- Terceiro quartil (Q3);
- Intervalo interquartil (IQR);
- Coeficiente de assimetria.

### 6.5. Distribuição

Apresenta:

- Histograma;
- Curva de densidade KDE;
- Boxplot;
- Quadro-resumo das medidas de distribuição.

### 6.6. Comparação entre equipes

Exibe um gráfico de barras horizontais com a média da variável selecionada para as equipes da base.

A equipe escolhida no filtro recebe destaque visual.

### 6.7. Matrizes comparativas

Apresenta matrizes de:

- Coeficiente de variação;
- Intervalo interquartil;
- Assimetria;
- Quartis e medidas de dispersão.

### 6.8. Detecção de outliers

Apresenta a quantidade de partidas identificadas por cada método e uma tabela com os registros sinalizados.

### 6.9. Destaques da análise

Resume automaticamente três indicadores da equipe selecionada:

- Regularidade relativa (CV);
- Faixa central dos resultados (Q1–Q3);
- Assimetria da distribuição.

### 6.10. Síntese dos resultados

Apresenta interpretações em linguagem acessível, relacionando os cálculos estatísticos ao desempenho esportivo das equipes.

Os textos são atualizados conforme a equipe e a variável escolhidas.

---

## 7. Metodologia estatística

### 7.1. Medidas descritivas

O projeto utiliza as funções do pandas para calcular as medidas de tendência central e dispersão.

O desvio padrão e a variância seguem a convenção amostral, com `ddof=1`.

Os quartis são calculados com interpolação linear:

```python
q1 = valores.quantile(0.25)
q3 = valores.quantile(0.75)

iqr = q3 - q1
```

A moda apresentada corresponde ao primeiro valor retornado por `pandas.Series.mode()` quando existem múltiplas modas.

### 7.2. Coeficiente de variação (CV)

O coeficiente de variação mede a dispersão relativa dos resultados.

**Fórmula:**

\[
CV(\%) = \frac{s}{\bar{x}} \times 100
\]

Onde:

- \(s\): desvio padrão amostral;
- \(\bar{x}\): média da variável.

**Interpretação:**

Um CV menor indica que os resultados de uma equipe foram relativamente mais regulares entre as partidas.

Um CV maior indica maior oscilação relativa.

O CV permite comparar a variabilidade entre estatísticas de diferentes escalas, mas exige cautela quando a média está próxima de zero.

### 7.3. Intervalo interquartil (IQR)

O IQR mede a largura da faixa central da distribuição.

**Fórmula:**

\[
IQR = Q3 - Q1
\]

O intervalo entre Q1 e Q3 contém aproximadamente 50% das observações.

Quanto menor o IQR, maior a concentração dos resultados centrais.

Quanto maior o IQR, mais espalhados estão esses resultados.

Para identificar outliers, utiliza-se a regra:

\[
LI = Q1 - 1{,}5 \times IQR
\]

\[
LS = Q3 + 1{,}5 \times IQR
\]

Observações abaixo do limite inferior ou acima do limite superior são sinalizadas como possíveis outliers.

### 7.4. Assimetria (Skewness)

O projeto utiliza o coeficiente amostral ajustado de **Fisher-Pearson**, implementado por:

```python
valores.skew()
```

**Classificação adotada:**

| Valor absoluto | Classificação |
|---|---|
| Menor que 0,5 | Aproximadamente simétrica |
| De 0,5 até menos que 1 | Moderada |
| Maior ou igual a 1 | Forte |

Um coeficiente positivo indica uma cauda mais longa à direita.

Um coeficiente negativo indica uma cauda mais longa à esquerda.

O coeficiente é interpretado juntamente com o histograma, a curva KDE e o Boxplot.

### 7.5. Histograma e KDE

O histograma representa a frequência dos valores observados.

A curva **Kernel Density Estimation (KDE)** fornece uma estimativa suavizada da distribuição.

Sua implementação utiliza:

```python
from scipy.stats import gaussian_kde

kde = gaussian_kde(valores, bw_method="scott")
```

A curva é ajustada à escala de frequência do histograma para facilitar a comparação visual.

---

## 8. Métodos de detecção de outliers

O projeto implementa sete métodos.

| Método | Funcionamento |
|---|---|
| IQR | Detecta valores fora dos limites calculados com os quartis |
| Z-score | Avalia o afastamento de um valor em relação à média, medido em desvios padrão |
| Grubbs | Testa uma observação extrema considerando a distribuição dos dados |
| ECOD | Analisa observações incomuns por meio das distribuições empíricas |
| K-NN | Utiliza distâncias entre observações vizinhas |
| DBSCAN | Identifica observações classificadas como ruído em agrupamentos por densidade |
| LOF | Compara a densidade local de uma observação com a densidade de seus vizinhos |

### Local Outlier Factor (LOF)

O LOF é executado por equipe e considera simultaneamente as sete estatísticas esportivas.

O algoritmo utiliza:

- `StandardScaler` para padronização;
- Até 20 vizinhos;
- `contamination=0.05`;
- Distância euclidiana.

O preenchimento de valores ausentes, quando necessário, ocorre apenas na matriz utilizada pelo algoritmo, sem modificar a base original.

### Diferenças entre métodos

Os algoritmos não utilizam necessariamente os mesmos critérios.

Alguns analisam uma variável individualmente, enquanto outros avaliam múltiplas características ao mesmo tempo.

Por isso, uma partida pode ser considerada atípica por um método e normal por outro.

As contagens de outliers não devem ser somadas como se representassem partidas distintas.

---

## 9. Tratamento e qualidade dos dados

O projeto contempla:

- Identificação de valores ausentes;
- Verificação de linhas duplicadas;
- Verificação de duplicatas de equipe e partida;
- Conversão de datas;
- Identificação de valores negativos;
- Verificação de percentuais fora do intervalo esperado;
- Conferência de arremessos convertidos e tentados;
- Validação da soma dos rebotes;
- Validação da pontuação total;
- Verificação da estrutura das partidas.

### Mecanismos de ausência

Os mecanismos clássicos de ausência são:

**MCAR — Missing Completely At Random**

A ausência dos dados é independente dos valores observados e não observados.

**MAR — Missing At Random**

A ausência pode ser explicada por outras informações observadas.

**MNAR — Missing Not At Random**

A ausência depende de informações não observadas, inclusive do próprio valor ausente.

Testes como Little, Jamshidian–Jalal, Listing–Schlitgen e abordagens baseadas em regressão logística de Fairclough podem auxiliar na investigação desses mecanismos.

**Esses testes específicos são discutidos metodologicamente, mas não foram executados no projeto.**

---

## 10. Interpretação dos resultados

Além dos cálculos, o sistema apresenta explicações relacionadas ao comportamento das equipes.

A interpretação considera:

**Desempenho médio:** o resultado médio da equipe em determinada estatística.

**Regularidade:** o quanto uma equipe mantém resultados relativamente próximos de seu padrão entre partidas.

**Dispersão central:** como se distribuem os 50% centrais dos jogos.

**Assimetria:** a existência de uma cauda mais longa em direção a resultados altos ou baixos.

**Outliers:** partidas com resultados estatisticamente incomuns.

Uma equipe com maior pontuação média não necessariamente apresenta maior regularidade. Da mesma forma, uma partida considerada outlier não representa obrigatoriamente um erro no dataset.

As análises realizadas são descritivas e não estabelecem relações causais nem previsões de desempenho futuro.

---

## 11. Limitações do projeto

As principais limitações identificadas são:

1. O sistema analisa as equipes presentes no CSV, não necessariamente apenas um subconjunto designado ao grupo.

2. Os métodos de outliers possuem critérios distintos, de modo que suas contagens não são diretamente equivalentes.

3. A implementação do Grubbs analisa o candidato mais extremo, sem realizar uma detecção iterativa completa.

4. Os testes específicos sobre mecanismos MCAR, MAR e MNAR não foram executados.

5. Os gráficos são atualmente gravados como PNGs na pasta `static/`, solução apropriada à execução local, mas que precisa de adaptação para ambientes serverless.

6. Os escudos das equipes dependem da disponibilidade de imagens hospedadas externamente.

7. Os resultados descrevem apenas as partidas presentes no conjunto de dados utilizado.

---

## 12. Atualização dos dados e resultados

Quando o CSV original for atualizado, a exploração e o tratamento podem ser executados novamente:

```powershell
python explorar.py
python qualidade.py
```

Os algoritmos de outliers podem ser executados individualmente.

Exemplo:

```powershell
python metodos_outliers/lof.py
```

Após atualizar os resultados processados, reinicie a aplicação:

```powershell
python app.py
```

Os arquivos produzidos ficam armazenados em `data/processed/`.

---

## 13. Publicação

O sistema funciona localmente por meio do Flask.

A publicação em ambiente público será realizada em etapa posterior, com os ajustes necessários para execução em ambiente serverless.

**Repositório:**

https://github.com/leobernardo05/analise-esportiva

**Execução local:**

```powershell
python app.py
```

**Endereço público da aplicação:** a definir após o deploy.

---

**NBA Analytics — Game Insights**

Projeto acadêmico desenvolvido para aplicar técnicas de exploração, tratamento, visualização e interpretação estatística de dados esportivos.
