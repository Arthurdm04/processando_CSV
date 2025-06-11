import pandas as pd
import matplotlib
# IMPORTANTE: Mude o backend do Matplotlib ANTES de importar o pyplot.
# O backend 'Agg' é não-interativo e seguro para scripts.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import glob
import os
import time
from typing import Dict, List, Optional, Callable, Tuple
import concurrent.futures
import threading
from tqdm import tqdm

# --- Configuração Inicial ---
DIRETORIO_DADOS_FONTE = "./Dados"
DIRETORIO_SAIDA = "./Saida"
NOME_ARQUIVO_CONSOLIDADO = "Consolidado.csv"
NOME_ARQUIVO_RESUMO_METAS = "ResumoMetas.csv"

# Nomes das colunas usadas nos cálculos
COLUNA_CASOS_JULGADOS_2025 = 'julgados_2025'
COLUNA_CASOS_NOVOS_2025 = 'casos_novos_2025'
COLUNA_CASOS_DESSOBRESTADOS_2025 = 'dessobrestados_2025'
COLUNA_CASOS_SUSPENSOS_2025 = 'suspensos_2025'

# Define o conjunto completo e a ordem das colunas de métricas para o arquivo de resumo final.
TODAS_COLUNAS_METRICAS = [
    'tribunal', 'ramo_justica', 'Meta1', 'Meta2A', 'Meta2B', 'Meta2C', 'Meta2ANT',
    'Meta4A', 'Meta4B', 'Meta6', 'Meta7A', 'Meta7B', 'Meta8A', 'Meta8B', 'Meta8',
    'Meta10A', 'Meta10B', 'Meta10'
]

# --- 1. Carregamento e Consolidação de Dados (Paralelizado com tqdm) ---

def _ler_csv(arquivo: str) -> Optional[pd.DataFrame]:
    """Função auxiliar para ler um único arquivo CSV em uma thread."""
    thread_id = threading.get_ident()
    try:
        df_temporario = pd.read_csv(arquivo, sep=',', encoding='utf-8')
        if 'sigla_tribunal' not in df_temporario.columns or 'ramo_justica' not in df_temporario.columns:
            print(f"THREAD ID: {thread_id} | 😬 Alerta! O arquivo '{os.path.basename(arquivo)}' não tem colunas essenciais.")
        return df_temporario
    except Exception as e:
        print(f"THREAD ID: {thread_id} | 🚨 Erro ao ler '{os.path.basename(arquivo)}': {e}")
        return None

def consolidar_arquivos_csv_paralelo(caminho_fonte: str, caminho_saida_arquivo: str) -> Optional[pd.DataFrame]:
    """
    Lê todos os arquivos CSV de forma paralela com barra de progresso,
    consolida-os e salva em um novo arquivo CSV.
    """
    tempo_inicio = time.time()
    print(f"🔎 Procurando arquivos de origem em '{caminho_fonte}'. Fica de olho!")
    arquivos_csv = glob.glob(os.path.join(caminho_fonte, "teste_*.csv"))

    if not arquivos_csv:
        print(f"🤔 Opa! Não achei nenhum arquivo CSV com o padrão 'teste_*.csv' em '{caminho_fonte}'.")
        return None

    lista_dataframes = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Usa tqdm para criar uma barra de progresso para a leitura dos arquivos
        resultados = list(tqdm(executor.map(_ler_csv, arquivos_csv),
                               total=len(arquivos_csv),
                               desc="Lendo arquivos CSV "))
        for df in resultados:
            if df is not None:
                lista_dataframes.append(df)

    if not lista_dataframes:
        print("❌ Deu ruim! Nenhum dataframe foi carregado. Não dá pra continuar a consolidação.")
        return None

    df_consolidado = pd.concat(lista_dataframes, ignore_index=True)
    try:
        df_consolidado.to_csv(caminho_saida_arquivo, index=False, sep=',', encoding='utf-8')
        print(f"🎉 É isso aí! Arquivo consolidado '{caminho_saida_arquivo}' criado com {len(df_consolidado)} linhas.")
    except Exception as e:
        print(f"💥 Falha crítica! Não consegui salvar o arquivo consolidado em '{caminho_saida_arquivo}': {e}")

    tempo_fim = time.time()
    print(f"⏱️ A consolidação dos CSVs levou {tempo_fim - tempo_inicio:.2f} segundos.")
    return df_consolidado

# --- 2. Funções Auxiliares para Cálculo de Métricas Genéricas ---
def calcular_metrica_tipo_1(df_tribunal: pd.DataFrame) -> float | str:
    """
    Calcula métricas usando a fórmula: (Σ julgados / (Σ casos_novos + Σ dessobrestados - Σ suspensos)) * 100
    Aplicável à Meta 1 para todos os tribunais.
    """
    total_julgados = df_tribunal[COLUNA_CASOS_JULGADOS_2025].sum()
    total_casos_novos = df_tribunal[COLUNA_CASOS_NOVOS_2025].sum()
    total_dessobrestados = df_tribunal[COLUNA_CASOS_DESSOBRESTADOS_2025].sum()
    total_suspensos = df_tribunal[COLUNA_CASOS_SUSPENSOS_2025].sum()

    denominador = total_casos_novos + total_dessobrestados - total_suspensos
    if denominador == 0:
        return "NA"
    return (total_julgados / denominador) * 100

def calcular_metrica_generica(df_tribunal: pd.DataFrame, multiplicador: float) -> float | str:
    """
    Calcula métricas usando a fórmula: (Σ julgados / (Σ distribuídos - Σ suspensos)) * multiplicador.
    'distribuídos' é representado pela coluna de casos novos.
    """
    total_julgados = df_tribunal[COLUNA_CASOS_JULGADOS_2025].sum()
    total_distribuidos = df_tribunal[COLUNA_CASOS_NOVOS_2025].sum()
    total_suspensos = df_tribunal[COLUNA_CASOS_SUSPENSOS_2025].sum()

    denominador = total_distribuidos - total_suspensos
    if denominador == 0:
        return "NA"
    return (total_julgados / denominador) * multiplicador

# --- 3. Funções de Cálculo de Métricas Específicas por Ramo da Justiça ---
def calcular_metricas_justica_estadual(df: pd.DataFrame) -> Dict[str, float | str]:
    """Calcula todas as métricas aplicáveis para os tribunais da Justiça Estadual."""
    return {
        'Meta1': calcular_metrica_tipo_1(df),
        'Meta2A': calcular_metrica_generica(df, multiplicador=(1000/8)),
        'Meta2B': calcular_metrica_generica(df, multiplicador=(1000/9)),
        'Meta2C': calcular_metrica_generica(df, multiplicador=(1000/9.5)),
        'Meta2ANT': calcular_metrica_generica(df, multiplicador=100),
        'Meta4A': calcular_metrica_generica(df, multiplicador=(1000/6.5)),
        'Meta4B': calcular_metrica_generica(df, multiplicador=100),
        'Meta6': calcular_metrica_generica(df, multiplicador=100),
        'Meta7A': calcular_metrica_generica(df, multiplicador=(1000/5)),
        'Meta7B': calcular_metrica_generica(df, multiplicador=(1000/5)),
        'Meta8A': calcular_metrica_generica(df, multiplicador=(1000/7.5)),
        'Meta8B': calcular_metrica_generica(df, multiplicador=(1000/9)),
        'Meta10A': calcular_metrica_generica(df, multiplicador=(1000/9)),
        'Meta10B': calcular_metrica_generica(df, multiplicador=(1000/10)),
    }

def calcular_metricas_justica_trabalho(df: pd.DataFrame) -> Dict[str, float | str]:
    """Calcula todas as métricas aplicáveis para os tribunais da Justiça do Trabalho."""
    return {
        'Meta1': calcular_metrica_tipo_1(df),
        'Meta2A': calcular_metrica_generica(df, multiplicador=(1000/9.4)),
        'Meta2ANT': calcular_metrica_generica(df, multiplicador=100),
        'Meta4A': calcular_metrica_generica(df, multiplicador=(1000/7)),
        'Meta4B': calcular_metrica_generica(df, multiplicador=100),
    }

def calcular_metricas_justica_federal(df: pd.DataFrame) -> Dict[str, float | str]:
    """Calcula todas as métricas aplicáveis para os tribunais da Justiça Federal."""
    return {
        'Meta1': calcular_metrica_tipo_1(df),
        'Meta2A': calcular_metrica_generica(df, multiplicador=(1000/8.5)),
        'Meta2B': calcular_metrica_generica(df, multiplicador=100),
        'Meta2ANT': calcular_metrica_generica(df, multiplicador=100),
        'Meta4A': calcular_metrica_generica(df, multiplicador=(1000/7)),
        'Meta4B': calcular_metrica_generica(df, multiplicador=100),
        'Meta6': calcular_metrica_generica(df, multiplicador=(1000/3.5)),
        'Meta7A': calcular_metrica_generica(df, multiplicador=(1000/3.5)),
        'Meta7B': calcular_metrica_generica(df, multiplicador=(1000/3.5)),
        'Meta8A': calcular_metrica_generica(df, multiplicador=(1000/7.5)),
        'Meta8B': calcular_metrica_generica(df, multiplicador=(1000/9)),
        'Meta10A': calcular_metrica_generica(df, multiplicador=100),
    }

def calcular_metricas_justica_militar_uniao(df: pd.DataFrame) -> Dict[str, float | str]:
    """Calcula todas as métricas aplicáveis para os tribunais da Justiça Militar da União."""
    return {
        'Meta1': calcular_metrica_tipo_1(df),
        'Meta2A': calcular_metrica_generica(df, multiplicador=(1000/9.5)),
        'Meta2B': calcular_metrica_generica(df, multiplicador=(1000/9.9)),
        'Meta2ANT': calcular_metrica_generica(df, multiplicador=100),
        'Meta4A': calcular_metrica_generica(df, multiplicador=(1000/9.5)),
        'Meta4B': calcular_metrica_generica(df, multiplicador=(1000/9.9)),
    }

def calcular_metricas_justica_militar_estadual(df: pd.DataFrame) -> Dict[str, float | str]:
    """Calcula todas as métricas aplicáveis para os tribunais da Justiça Militar Estadual."""
    return {
        'Meta1': calcular_metrica_tipo_1(df),
        'Meta2A': calcular_metrica_generica(df, multiplicador=(1000/9)),
        'Meta2B': calcular_metrica_generica(df, multiplicador=(1000/9.5)),
        'Meta2ANT': calcular_metrica_generica(df, multiplicador=100),
        'Meta4A': calcular_metrica_generica(df, multiplicador=(1000/9.5)),
        'Meta4B': calcular_metrica_generica(df, multiplicador=(1000/9.9)),
    }

def calcular_metricas_tribunal_superior_eleitoral(df: pd.DataFrame) -> Dict[str, float | str]:
    """Calcula todas as métricas aplicáveis para o Tribunal Superior Eleitoral."""
    return {
        'Meta1': calcular_metrica_tipo_1(df),
        'Meta2A': calcular_metrica_generica(df, multiplicador=(1000/7)),
        'Meta2B': calcular_metrica_generica(df, multiplicador=(1000/9.9)),
        'Meta2ANT': calcular_metrica_generica(df, multiplicador=100),
        'Meta4A': calcular_metrica_generica(df, multiplicador=(1000/9)),
        'Meta4B': calcular_metrica_generica(df, multiplicador=(1000/5)),
    }

def calcular_metricas_tribunal_superior_trabalho(df: pd.DataFrame) -> Dict[str, float | str]:
    """Calcula todas as métricas aplicáveis para o Tribunal Superior do Trabalho."""
    return {
        'Meta1': calcular_metrica_tipo_1(df),
        'Meta2A': calcular_metrica_generica(df, multiplicador=(1000/9.5)),
        'Meta2B': calcular_metrica_generica(df, multiplicador=(1000/9.9)),
        'Meta2ANT': calcular_metrica_generica(df, multiplicador=100),
        'Meta4A': calcular_metrica_generica(df, multiplicador=(1000/7)),
        'Meta4B': calcular_metrica_generica(df, multiplicador=100),
    }

def calcular_metricas_superior_tribunal_justica(df: pd.DataFrame) -> Dict[str, float | str]:
    """Calcula todas as métricas aplicáveis para o Superior Tribunal de Justiça."""
    return {
        'Meta1': calcular_metrica_tipo_1(df),
        'Meta2ANT': calcular_metrica_generica(df, multiplicador=100),
        'Meta4A': calcular_metrica_generica(df, multiplicador=(1000/9)),
        'Meta4B': calcular_metrica_generica(df, multiplicador=100),
        'Meta6': calcular_metrica_generica(df, multiplicador=(1000/7.5)),
        'Meta7A': calcular_metrica_generica(df, multiplicador=(1000/7.5)),
        'Meta7B': calcular_metrica_generica(df, multiplicador=(1000/7.5)),
        'Meta8': calcular_metrica_generica(df, multiplicador=(1000/10)),
        'Meta10': calcular_metrica_generica(df, multiplicador=(1000/10)),
    }

# --- 4. Processamento Principal dos Dados (Paralelizado com tqdm) ---
CALCULADORAS_METRICAS: Dict[str, Callable[[pd.DataFrame], Dict[str, float | str]]] = {
    "Justiça Estadual": calcular_metricas_justica_estadual,
    "Justiça do Trabalho": calcular_metricas_justica_trabalho,
    "Justiça Federal": calcular_metricas_justica_federal,
    "Justiça Militar da União": calcular_metricas_justica_militar_uniao,
    "Justiça Militar Estadual": calcular_metricas_justica_militar_estadual,
    "Tribunal Superior Eleitoral": calcular_metricas_tribunal_superior_eleitoral,
    "Tribunal Superior do Trabalho": calcular_metricas_tribunal_superior_trabalho,
    "Superior Tribunal de Justiça": calcular_metricas_superior_tribunal_justica,
}

def _processar_um_tribunal(args: Tuple[str, pd.DataFrame]) -> Dict[str, float | str]:
    """Função auxiliar para processar um único tribunal em uma thread."""
    sigla_tribunal, df_grupo_tribunal = args
    ramo_justica = df_grupo_tribunal['ramo_justica'].iloc[0]

    df_tribunal_copia = df_grupo_tribunal.copy()
    desempenho_tribunal = {'tribunal': sigla_tribunal, 'ramo_justica': ramo_justica}

    funcao_calculadora = CALCULADORAS_METRICAS.get(ramo_justica)

    metricas_calculadas = {}
    if funcao_calculadora:
        metricas_calculadas = funcao_calculadora(df_tribunal_copia)
    else:
        # Fallback para ramos não definidos
        metricas_calculadas['Meta1'] = calcular_metrica_tipo_1(df_tribunal_copia)

    desempenho_tribunal.update(metricas_calculadas)
    return desempenho_tribunal

def processar_dados_tribunais_paralelo(df_consolidado: Optional[pd.DataFrame], caminho_saida_arquivo: str) -> Optional[pd.DataFrame]:
    """
    Processa os dados de cada tribunal em paralelo com barra de progresso
    e salva o resultado em um arquivo CSV.
    """
    tempo_inicio = time.time()
    if df_consolidado is None or df_consolidado.empty:
        print("❌ Erro: O DataFrame consolidado está vazio. Não posso processar as métricas dos tribunais.")
        return None

    for coluna in ['sigla_tribunal', 'ramo_justica']:
        if coluna not in df_consolidado.columns:
            print(f"❌ Erro Crítico: A coluna essencial '{coluna}' não foi encontrada no DataFrame consolidado.")
            return None

    grupos_de_tribunais = list(df_consolidado.groupby('sigla_tribunal'))
    todos_resultados = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Usa tqdm para a barra de progresso do processamento dos tribunais
        resultados = list(tqdm(executor.map(_processar_um_tribunal, grupos_de_tribunais),
                               total=len(grupos_de_tribunais),
                               desc="Processando Tribunais"))
        todos_resultados = resultados

    df_resumo_metricas = pd.DataFrame(todos_resultados)
    df_resumo_metricas = df_resumo_metricas.reindex(columns=TODAS_COLUNAS_METRICAS).fillna("NA")

    try:
        df_resumo_metricas.to_csv(caminho_saida_arquivo, index=False, sep=',', encoding='utf-8')
        print(f"✅ Sucesso! O arquivo de resumo de métricas '{caminho_saida_arquivo}' foi gerado.")
    except Exception as e:
        print(f"💥 Erro: Não foi possível salvar o arquivo de resumo de métricas em '{caminho_saida_arquivo}': {e}")

    tempo_fim = time.time()
    print(f"⏱️ O processamento dos dados dos tribunais demorou {tempo_fim - tempo_inicio:.2f} segundos.")
    return df_resumo_metricas

# --- 5. Geração de Gráficos (Sequencial e Corrigido) ---

def gerar_graficos_resumo(df_resumo: Optional[pd.DataFrame], caminho_saida: str):
    """
    Gera e salva gráficos de barras de forma SEQUENCIAL para evitar erros de thread.
    """
    tempo_inicio = time.time()
    if df_resumo is None or df_resumo.empty:
        print("🤔 O DataFrame de resumo de métricas está vazio. Vou pular a geração de gráficos.")
        return

    if not os.path.exists(caminho_saida):
        try:
            os.makedirs(caminho_saida, exist_ok=True)
            print(f"📂 Diretório para os gráficos criado em '{caminho_saida}'.")
        except OSError as e:
            print(f"❌ Erro ao criar o diretório '{caminho_saida}': {e}. Os gráficos não serão salvos.")
            return

    metricas_para_plotar = ['Meta1', 'Meta2A', 'Meta2ANT', 'Meta4A', 'Meta6']
    top_n_tribunais = 15

    # A geração de gráficos agora é um loop sequencial simples
    for nome_metrica in tqdm(metricas_para_plotar, desc="Gerando Gráficos   "):
        if nome_metrica not in df_resumo.columns:
            print(f"😬 Ué? A métrica '{nome_metrica}' não foi encontrada nos dados de resumo.")
            continue

        df_plot = df_resumo[['tribunal', nome_metrica]].copy()
        df_plot[nome_metrica] = pd.to_numeric(df_plot[nome_metrica], errors='coerce')
        df_plot = df_plot.dropna(subset=[nome_metrica])
        df_plot = df_plot.sort_values(by=nome_metrica, ascending=False).head(top_n_tribunais)

        if df_plot.empty:
            print(f"🤷‍♂️ Nenhum dado válido disponível para a métrica '{nome_metrica}'.")
            continue

        plt.figure(figsize=(14, 8))
        barras = plt.bar(df_plot['tribunal'], df_plot[nome_metrica], color='#007ACC')

        plt.title(f'Comparativo de Performance - {nome_metrica} (Top {top_n_tribunais} Tribunais)', fontsize=16, pad=20)
        plt.ylabel(f'Valor da {nome_metrica}', fontsize=12)
        plt.xlabel('Tribunal', fontsize=12)
        plt.xticks(rotation=45, ha="right", fontsize=10)
        plt.yticks(fontsize=10)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)

        for barra in barras:
            yval = barra.get_height()
            plt.text(barra.get_x() + barra.get_width()/2.0, yval, f'{yval:.2f}', ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        caminho_grafico = os.path.join(caminho_saida, f"grafico_{nome_metrica}.png")
        try:
            plt.savefig(caminho_grafico, dpi=150)
        except Exception as e:
            print(f"💥 Erro ao salvar o gráfico '{caminho_grafico}': {e}")
        # É importante fechar a figura para liberar memória
        plt.close()

    tempo_fim = time.time()
    print(f"⏱️ A geração de gráficos levou {tempo_fim - tempo_inicio:.2f} segundos.")


# --- Bloco de Execução Principal ---
if __name__ == "__main__":
    tempo_inicio_total = time.time()
    print("--- 🚀 Começando o Pipeline de Processamento de Dados (Versão Corrigida)! ---")

    try:
        os.makedirs(DIRETORIO_SAIDA, exist_ok=True)
        print(f"📂 O diretório de saída '{DIRETORIO_SAIDA}' está pronto para uso.")
    except OSError as e:
        print(f"🚨 FATAL: Não foi possível criar o diretório de saída '{DIRETORIO_SAIDA}': {e}. Saindo.")
        exit()

    caminho_consolidado = os.path.join(DIRETORIO_SAIDA, NOME_ARQUIVO_CONSOLIDADO)
    caminho_resumo_metricas = os.path.join(DIRETORIO_SAIDA, NOME_ARQUIVO_RESUMO_METAS)

    # Passo 1: Consolidar dados dos CSVs de origem em paralelo
    dados_consolidados = consolidar_arquivos_csv_paralelo(DIRETORIO_DADOS_FONTE, caminho_consolidado)

    # Passo 2: Processar dados e calcular todas as métricas em paralelo
    dados_resumo_metricas = processar_dados_tribunais_paralelo(dados_consolidados, caminho_resumo_metricas)

    # Passo 3: Gerar gráficos visuais de forma sequencial para evitar erros
    if dados_resumo_metricas is not None:
        gerar_graficos_resumo(dados_resumo_metricas, DIRETORIO_SAIDA)
    else:
        print("🤔 O resumo de métricas não foi gerado, então não posso criar os gráficos.")

    tempo_fim_total = time.time()
    print("--- ✅ Pipeline de Processamento de Dados Finalizado! ---")
    print(f"🏁 Tempo total de execução: {tempo_fim_total - tempo_inicio_total:.2f} segundos.")