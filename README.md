
# 🏀 NBA Analytics — Game Insights

### Análise Exploratória de Dados Esportivos | UFAPE — 2026.2

**NBA Analytics — Game Insights** é uma aplicação web desenvolvida em Python e Flask para análise exploratória das estatísticas de partidas da NBA.

A plataforma permite visualizar dados esportivos por equipe, comparar desempenhos, analisar distribuições estatísticas e identificar observações atípicas por meio de diferentes métodos de detecção de outliers.

O sistema funciona como um **relatório estatístico interativo**, reunindo resultados, gráficos, tabelas comparativas e interpretações em linguagem acessível.

## 🌐 Acesse a aplicação

**[🏀 Abrir NBA Analytics — Game Insights](https://analise-esportiva-eta.vercel.app)**

**Repositório:**  
https://github.com/leobernardo05/analise-esportiva

**Hospedagem:** Vercel  
**Framework:** Flask  
**Ambiente:** Produção  
**Status do deployment:** READY

---

## 1. Objetivo do projeto

O objetivo é investigar padrões de desempenho das equipes da NBA, utilizando ferramentas de Ciência de Dados e Estatística Descritiva.

A análise busca responder perguntas como:

- Quais equipes apresentam maiores médias em determinada estatística?
- Quais equipes possuem desempenho mais regular?
- Como os valores se distribuem entre as partidas?
- Existem resultados muito diferentes do comportamento habitual?
- Como os métodos de detecção de outliers se comparam?
- A média representa adequadamente o desempenho de uma equipe?
- Qual a influência da dispersão e da assimetria na interpretação dos resultados?

### Variáveis analisadas

| Código | Variável | Unidade |
|---|---|---|
| PTS | Pontos | Pontos por partida |
| REB | Rebotes totais | Rebotes por partida |
| AST | Assistências | Assistências por partida |
| STL | Roubos de bola | Roubos por partida |
| BLK | Bloqueios | Bloqueios por partida |
| PF | Faltas pessoais | Faltas por partida |
| FG3M | Cestas de três convertidas | Cestas por partida |

A unidade observacional da base é o registro de uma equipe em uma partida. Assim, uma partida pode apresentar dois registros, um para cada equipe participante.

---

## 2. Tecnologias utilizadas

O projeto utiliza as seguintes tecnologias:

| Tecnologia | Finalidade |
|---|---|
| Python 3.12 | Linguagem principal |
| Flask | Servidor e rotas da aplicação |
| pandas | Manipulação de dados e estatísticas |
| NumPy | Operações numéricas |
| SciPy | Análises estatísticas e KDE |
| Matplotlib | Geração dos gráficos |
| scikit-learn | Algoritmos de detecção de anomalias |
| PyOD | Métodos especializados de outliers |
| Jinja2 | Renderização dinâmica dos templates |
| HTML5 | Estrutura das páginas |
| CSS3 | Identidade visual e responsividade |
| JavaScript | Interações da interface |
| Git e GitHub | Versionamento |
| Vercel | Hospedagem da aplicação |

As bibliotecas usadas no processamento de outliers são mantidas separadamente das dependências necessárias para executar o dashboard em produção.

---

## 3. Funcionalidades da aplicação

A interface foi organizada em dez seções, acessíveis pela barra lateral.

### 3.1. Visão geral

Apresenta informações do conjunto de dados, incluindo:

- Número de registros;
- Quantidade de colunas;
- Número de equipes;
- Quantidade de partidas distintas;
- Período analisado.

### 3.2. Qualidade dos dados

Apresenta verificações relacionadas à integridade do dataset.

São analisados valores ausentes, duplicidades, zeros, valores negativos e inconsistências entre estatísticas relacionadas.

### 3.3. Dicionário de dados

Documenta as colunas do dataset, seus tipos, nomes tratados e significados no contexto esportivo.

### 3.4. Estatísticas por equipe

Permite selecionar uma equipe e uma variável para consultar:

- Média;
- Mediana;
- Moda;
- Valor mínimo;
- Valor máximo;
- Amplitude;
- Desvio padrão;
- Variância;
- Primeiro quartil (Q1);
- Terceiro quartil (Q3);
- Intervalo interquartil (IQR);
- Coeficiente de assimetria.

### 3.5. Distribuição

Disponibiliza:

- Histograma de frequências;
- Curva de densidade KDE;
- Boxplot;
- Indicação de medidas centrais e de dispersão;
- Interpretações estatísticas.

### 3.6. Comparação entre equipes

Apresenta um gráfico de barras horizontais com a média da variável analisada para as equipes presentes na base.

A equipe selecionada recebe destaque visual.

### 3.7. Matrizes estatísticas

Apresenta tabelas comparativas de:

- Coeficiente de variação (CV);
- Intervalo interquartil (IQR);
- Coeficiente de assimetria;
- Quartis e medidas associadas.

### 3.8. Detecção de outliers

Apresenta resultados obtidos por sete métodos distintos de identificação de observações atípicas.

São disponibilizadas contagens, comparações metodológicas e registros sinalizados.

### 3.9. Destaques da análise

Apresenta indicadores resumidos, calculados para a equipe e variável selecionadas:

- Regularidade relativa;
- Faixa central das observações;
- Assimetria da distribuição.

### 3.10. Síntese e interpretação

Reúne interpretações textuais dos resultados encontrados.

As explicações são atualizadas conforme os filtros selecionados e procuram traduzir conceitos estatísticos para situações compreensíveis no contexto do basquete.

---

## 4. Metodologia estatística

### 4.1. Estatística descritiva

A análise utiliza medidas de tendência central e dispersão.

O desvio padrão e a variância seguem a convenção amostral, com `ddof=1`.

Os quartis utilizam a interpolação linear implementada pelo pandas.

```python
q1 = valores.quantile(0.25)
q3 = valores.quantile(0.75)

iqr = q3 - q1
```

### 4.2. Coeficiente de variação (CV)

O coeficiente de variação permite comparar a dispersão relativa de diferentes estatísticas.

**Fórmula:**

\[
CV(\%) = \frac{s}{\bar{x}} \times 100
\]

Onde:

- \(s\) é o desvio padrão amostral;
- \(\bar{x}\) é a média da variável.

Um CV menor indica menor dispersão relativa entre partidas.

Um CV maior indica maior oscilação relativa.

A interpretação exige cautela quando a média está muito próxima de zero, especialmente em variáveis como bloqueios e roubos de bola.

### 4.3. Intervalo interquartil (IQR)

O IQR representa a largura da faixa que contém aproximadamente 50% das observações centrais.

\[
IQR = Q3 - Q1
\]

Um IQR pequeno indica maior concentração dos valores centrais.

Um IQR elevado indica maior dispersão dentro dessa faixa.

Para a detecção de outliers pela regra de Tukey, utilizam-se:

\[
LI = Q1 - 1{,}5 \times IQR
\]

\[
LS = Q3 + 1{,}5 \times IQR
\]

Valores fora desses limites são sinalizados como possíveis outliers.

### 4.4. Coeficiente de assimetria

A análise utiliza o coeficiente ajustado de Fisher-Pearson, calculado pelo pandas:

```python
valores.skew()
```

O coeficiente permite analisar a direção e a intensidade da assimetria.

| Valor absoluto | Classificação |
|---|---|
| Menor que 0,5 | Aproximadamente simétrica |
| De 0,5 até menos que 1 | Assimetria moderada |
| Maior ou igual a 1 | Assimetria forte |

Coeficientes positivos indicam cauda mais longa à direita.

Coeficientes negativos indicam cauda mais longa à esquerda.

Os resultados são analisados juntamente com o histograma e o Boxplot.

### 4.5. Histograma e KDE

O histograma mostra a frequência dos resultados registrados.

A curva KDE (*Kernel Density Estimation*) oferece uma estimativa suavizada da distribuição.

A implementação utiliza `scipy.stats.gaussian_kde`, com largura de banda de Scott.

```python
from scipy.stats import gaussian_kde

kde = gaussian_kde(valores, bw_method="scott")
```

A visualização permite observar concentração, dispersão e possíveis assimetrias na distribuição.

---

## 5. Métodos de detecção de outliers

O projeto implementa sete métodos distintos.

| Método | Descrição |
|---|---|
| IQR | Detecta observações fora dos limites interquartis |
| Z-score | Mede o afastamento de um valor em desvios padrão |
| Grubbs | Avalia uma observação extrema |
| ECOD | Identifica anomalias a partir de distribuições empíricas |
| K-NN | Analisa distâncias em relação aos vizinhos mais próximos |
| DBSCAN | Identifica ruídos em agrupamentos baseados em densidade |
| LOF | Detecta observações com densidade local atípica |

Os métodos foram implementados em scripts independentes, dentro de `metodos_outliers/`.

### Local Outlier Factor (LOF)

O LOF utiliza as sete estatísticas esportivas simultaneamente, com análise separada por equipe.

Características da implementação:

- Padronização com `StandardScaler`;
- Até 20 vizinhos;
- Contaminação de 5%;
- Distância euclidiana;
- Exportação dos resultados para CSV.

O tratamento de valores ausentes utilizado pelo algoritmo não modifica o arquivo original.

### Comparação entre métodos

Cada algoritmo utiliza um critério próprio.

Portanto, uma mesma partida pode ser sinalizada por um método e não por outro.

As contagens não são diretamente equivalentes e não devem ser somadas como se representassem observações distintas.

---

## 6. Qualidade e tratamento dos dados

O projeto realiza verificações relacionadas a:

- Valores ausentes;
- Valores negativos;
- Duplicidades;
- Valores fora de domínio;
- Consistência de percentuais;
- Relação entre arremessos tentados e convertidos;
- Soma de rebotes ofensivos e defensivos;
- Conferência da pontuação;
- Estrutura e identificadores das partidas;
- Conversão de datas e tipos de dados.

### Mecanismos de ausência

Os mecanismos clássicos de ausência são discutidos no sistema:

**MCAR — Missing Completely At Random**

Ausência independente dos valores observados e não observados.

**MAR — Missing At Random**

Ausência que pode ser explicada pelas informações observadas.

**MNAR — Missing Not At Random**

Ausência relacionada a informações não observadas ou ao próprio valor ausente.

São discutidas abordagens como os testes de Little, Jamshidian–Jalal, Listing–Schlitgen e regressão logística de Fairclough.

**Limitação:** esses testes específicos são apresentados metodologicamente, mas não foram executados no projeto.

---

## 7. Estrutura do repositório

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
│   └── imagens PNG de referência
│
├── public/
│   └── static/
│       └── css/
│           └── style.css
│
├── requirements.txt
├── requirements-analise.txt
├── .python-version
├── .gitignore
└── README.md
```

### Organização dos principais arquivos

**`app.py`**

Arquivo principal do Flask. Gerencia os filtros, os cálculos descritivos, os gráficos e a renderização da página.

**`analise_complementar.py`**

Produz o dicionário de dados, as matrizes estatísticas, as verificações complementares e as interpretações comparativas.

**`explorar.py`**

Responsável pela exploração, padronização e tratamento inicial dos dados.

**`qualidade.py`**

Responsável pelas verificações de integridade e consistência.

**`metodos_outliers/`**

Contém as implementações dos sete métodos de detecção de outliers.

**`templates/`**

Contém os templates HTML renderizados pelo Flask.

**`static/css/style.css`**

Define os estilos da interface Game Insights.

**`public/static/css/style.css`**

Disponibiliza a folha de estilos como arquivo estático no ambiente Vercel.

---

## 8. Execução local

### Requisitos

- Python 3.12;
- Git;
- pip;
- Navegador web.

### 8.1. Clonar o repositório

```powershell
git clone https://github.com/leobernardo05/analise-esportiva.git
cd analise-esportiva
```

### 8.2. Criar ambiente virtual

No Windows:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

No Linux ou macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 8.3. Instalar dependências do dashboard

```powershell
python -m pip install -r requirements.txt
```

Esse arquivo contém as dependências necessárias para executar a aplicação web:

```text
Flask==3.1.3
pandas==3.1.1
numpy==2.4.6
scipy==1.17.1
matplotlib==3.11.2
```

### 8.4. Executar a aplicação

```powershell
python app.py
```

Acesse:

http://127.0.0.1:5000

O repositório inclui os dados e os resultados processados necessários para executar o dashboard sem recalcular todos os métodos de outliers.

### 8.5. Instalar dependências completas para análise

Para executar novamente os algoritmos, instale as dependências completas:

```powershell
python -m pip install -r requirements-analise.txt
```

Esse arquivo inclui também `scikit-learn` e `pyod`.

### 8.6. Reprocessar dados

```powershell
python explorar.py
python qualidade.py
```

Os métodos de outliers podem ser executados individualmente.

Por exemplo:

```powershell
python metodos_outliers/lof.py
```

Os resultados são exportados para `data/processed/`.

---

## 9. Deploy na Vercel

A aplicação está publicada na Vercel, utilizando a integração com o repositório GitHub.

### Endereço da aplicação

**https://analise-esportiva-eta.vercel.app**

### Configuração

| Configuração | Valor |
|---|---|
| Plataforma | Vercel |
| Framework | Flask |
| Linguagem | Python |
| Versão do Python | 3.12 |
| Branch de produção | `main` |
| Diretório raiz | `./` |
| Arquivo principal | `app.py` |
| Dependências de produção | `requirements.txt` |

### Funcionamento em produção

O sistema utiliza a integração nativa da Vercel com aplicações Flask.

Os arquivos CSV são carregados a partir das pastas do repositório.

Os gráficos são produzidos com Matplotlib e convertidos para imagens PNG em memória, utilizando `BytesIO` e Base64.

Isso evita a necessidade de escrever arquivos na pasta `static/` durante as requisições, o que é importante para ambientes serverless.

Os resultados de outliers são previamente processados e armazenados em CSV, reduzindo as dependências necessárias na aplicação publicada.

### Separação das dependências

Foram criados dois arquivos:

- `requirements.txt`: bibliotecas necessárias ao dashboard em produção;
- `requirements-analise.txt`: bibliotecas completas para o processamento e a execução dos algoritmos de outliers.

Essa separação reduz o tamanho do pacote da função na Vercel sem eliminar os métodos do código-fonte.

### Atualizações

A aplicação está vinculada à branch `main` do GitHub.

Novos commits enviados à branch podem gerar automaticamente novos deployments de produção.

O ambiente local continua funcionando de forma independente da hospedagem.

---

## 10. Interpretação dos resultados

O dashboard não apresenta apenas números e gráficos.

A aplicação também interpreta as medidas calculadas, considerando o contexto esportivo.

**Desempenho médio:** representa o resultado médio da equipe em determinada estatística.

**Regularidade:** indica se o desempenho apresentou pouca ou muita oscilação relativa.

**Dispersão central:** descreve a amplitude dos 50% centrais das partidas.

**Assimetria:** permite identificar distribuições com caudas mais longas em uma direção.

**Outliers:** indicam partidas com resultados estatisticamente incomuns.

Uma equipe pode apresentar uma média elevada sem necessariamente ter resultados regulares.

Da mesma forma, uma partida atípica não representa obrigatoriamente um erro nos dados. Pode corresponder a um desempenho excepcional ou incomum.

O sistema procura distinguir essas situações e apresentar interpretações compatíveis com os cálculos realizados.

---

## 11. Limitações

Apesar de reunir diferentes técnicas estatísticas, o projeto possui limitações:

1. As conclusões se restringem ao conjunto de partidas disponível no dataset.

2. A análise é descritiva, não realizando previsões de partidas futuras.

3. Os métodos de outliers utilizam critérios diferentes e podem apresentar resultados distintos.

4. O teste de Grubbs implementado avalia o candidato mais extremo, sem detecção iterativa completa.

5. Os testes específicos sobre mecanismos de ausência não foram executados.

6. A interpretação do CV exige cautela para variáveis cuja média está próxima de zero.

7. A interface utiliza imagens externas para representar os escudos das equipes, sujeitas à disponibilidade do serviço de origem.

8. A atualização dos resultados de outliers depende da execução dos scripts de processamento; o dashboard publicado utiliza os CSVs gerados previamente.

---

## 12. Contexto acadêmico

**Instituição:** Universidade Federal do Agreste de Pernambuco (UFAPE)  
**Curso:** Bacharelado em Ciência da Computação   
**Professor:** Ryan Azevedo  
**Atividade:** Projeto 1 — Análise Exploratória de Dados

O projeto foi desenvolvido para apresentar, em uma aplicação web, os resultados e as interpretações de uma análise exploratória de dados esportivos.

---

## 13. Links

**Aplicação publicada:**  
https://analise-esportiva-eta.vercel.app

**Código-fonte:**  
https://github.com/leobernardo05/analise-esportiva

---

### 🏀 NBA Analytics — Game Insights

**Ciência de Dados aplicada ao basquete.**

*Análise estatística, visualização de dados e identificação de padrões de desempenho das equipes da NBA.*
