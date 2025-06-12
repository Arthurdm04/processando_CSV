# 🧠 Processando CSVs - Análise de Metas do Poder Judiciário

Este repositório apresenta o trabalho final da disciplina **Programação Concorrente e Paralela** da Universidade Católica de Brasília.

## 🎯 Objetivo

Desenvolver um sistema em Python para calcular o desempenho dos tribunais brasileiros no cumprimento das metas definidas pelo Conselho Nacional de Justiça (CNJ), aplicando o processo ETL (Extract, Transform, Load) e comparando o desempenho entre uma versão sequencial e uma paralela do código.

## 📂 Estrutura do Projeto

* `base_dados/`: Contém os arquivos CSV originais do sistema judiciário (não devem ser modificados).
* `Versao_NP.py`: Código da implementação sequencial (não paralela).
* `Versao_P.py`: Código com a implementação paralela.
* `Consolidado.csv`: Arquivo gerado com a concatenação de todos os dados processados.
* `ResumoMetas.csv`: Resultado final com o desempenho detalhado de cada tribunal no cumprimento das metas.
* `grafico_comparativo.png`: Gráfico gerado automaticamente, comparando os tempos de execução da versão sequencial e paralela.
* `README.md`: Este documento.

## 🚀 Como Executar

1.  **Instale as dependências necessárias:**
    ```bash
    pip install pandas matplotlib
    ```
    *(Recomenda-se o uso de um ambiente virtual para gerenciar as dependências.)*

2.  **Execute a versão sequencial:**
    ```bash
    python Versao_NP.py
    ```

3.  **Execute a versão paralela:**
    ```bash
    python Versao_P.py
    ```
    *Após a execução, os arquivos `Consolidado.csv`, `ResumoMetas.csv` e `grafico_comparativo.png` serão gerados na pasta raiz do projeto.*

## 🔄 Processo ETL Aplicado

* **Extract (Extração):** Leitura dos arquivos CSV contendo os dados brutos do sistema judiciário.
* **Transform (Transformação):** Cálculo das metas de desempenho conforme as fórmulas fornecidas no enunciado do trabalho.
* **Load (Carga):** Geração dos arquivos `ResumoMetas.csv`, `Consolidado.csv` e do gráfico `grafico_comparativo.png` com os resultados.

## 📊 Comparação de Desempenho

Um gráfico é gerado automaticamente, visualizando a diferença nos tempos de execução entre a versão sequencial e paralela, demonstrando o ganho de performance (aceleração) obtido com a paralelização.

## 📌 Observações

* Valores ausentes (NaN) foram substituídos por 'NA' no `ResumoMetas.csv` para clareza.
* Nenhum arquivo original presente na pasta `base_dados/` foi modificado.
* As fórmulas e metas foram aplicadas rigorosamente conforme as especificações do PDF da atividade.
* Cada versão (sequencial e paralela) está implementada em um único arquivo Python, conforme solicitado.
