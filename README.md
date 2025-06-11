# 🧠 Processando CSVs - Análise de Metas do Poder Judiciário
Trabalho final da disciplina Programação Concorrente e Paralela
📚 Universidade Católica de Brasília 

# 🎯 Objetivo
Desenvolver um sistema em Python para calcular o desempenho dos tribunais brasileiros no cumprimento das metas definidas pelo Conselho Nacional de Justiça (CNJ), aplicando o processo ETL (Extract, Transform, Load) e comparando o desempenho entre uma versão sequencial e uma paralela do código.

# 📂 Estrutura do Projeto
base_dados/: Arquivos CSV originais (não devem ser modificados)

Versao_NP.py: Código não paralelo

Versao_P.py: Código com paralelização

Consolidado.csv: Concatenação de todos os dados

ResumoMetas.csv: Resultado com o desempenho de cada tribunal

grafico_comparativo.png: Gráfico comparativo entre as versões

README.md: Este documento

# 🚀 Como Executar
Instale as dependências necessárias (caso ainda não tenha):

pip install pandas matplotlib
Execute a versão sequencial:

python Versao_NP.py
Execute a versão paralela:

python Versao_P.py
🔄 Processo ETL Aplicado
Extract (Extração): Leitura dos arquivos CSV com dados do sistema judiciário.

Transform (Transformação): Cálculo das metas conforme fórmulas fornecidas no enunciado do trabalho.

Load (Carga): Geração dos arquivos ResumoMetas.csv, Consolidado.csv e do gráfico grafico_comparativo.png.

# 📊 Comparação de Desempenho
Um gráfico é gerado automaticamente comparando o tempo de execução da versão sequencial e paralela, demonstrando o ganho de performance (speedup) obtido com paralelização.

# 📌 Observações
Valores ausentes foram substituídos por NA no ResumoMetas.csv.

Nenhum arquivo original da base de dados foi alterado.

As fórmulas e metas foram aplicadas conforme o PDF da atividade.

Cada versão (NP e P) está implementada em um único arquivo, conforme solicitado.
