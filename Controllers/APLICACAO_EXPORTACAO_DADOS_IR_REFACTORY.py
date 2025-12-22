print("PROCESSO EXPORTAÇÃO DADOS IR")

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                                            # IMPORTAÇÕES DAS BIBLIOTECAS
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
from datetime import datetime, timedelta
import os
import time
import pandas as pd
import pyodbc
import json
from google.cloud import bigquery

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                                            # CONFIGURAÇÕES PARA CONEXÃO COM BANCO DE DADOS E GCP
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/

# =====================================================================
                        # 1. CONEXÃO COM BDS
# =====================================================================
dados_conexao_sql = (
    'Driver={SQL Server};'
    'Server=Snepdb56c01;'
    'Database=BDS;'
    'Trusted_Connection=yes;'
)

user = os.path.basename(os.environ['USERPROFILE'])
print(f"Usuário identificado: {user}")

conexao = pyodbc.connect(dados_conexao_sql)
cursor = conexao.cursor()
print("Conectado com sucesso ao banco BDS")

# =====================================================================
                      # 2. CONEXÃO COM BIGQUERY
# =====================================================================
client = bigquery.Client(project="tim-sdbx-resjourney-3175")
print("Conexão com SandBox do Journey bem sucedida")


#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                                            # CONFIGURAÇÕES GERAIS
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/

horario_start = datetime.now()

caminho_saida_json = fr"C:\Users\{user}\OneDrive - TIM\Documents\Aplicação Exportação Dados IR\json"


#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                                            # VALIDAÇÃO DA BASE DO ULTRA TAB GCP
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/

while True:
    
    data_referencia = datetime.now().replace(minute=0, second=0, microsecond=0)

    data_max_ultratab = list(client.query(
        "SELECT MAX(DATA_OFERTA) AS DATA_MAXIMA "
        "FROM `tim-sdbx-resjourney-3175.dm_prod.TB_CRC_ULTRATAB`"
    ).result())[0]["DATA_MAXIMA"]

    conversao_data_maxima_datetime = pd.to_datetime(data_max_ultratab).tz_localize(None)

    print(f"Horário fechado vigente: {data_referencia}")
    print(f"Data Máxima ULTRATAB: {conversao_data_maxima_datetime}")

    if conversao_data_maxima_datetime >= data_referencia:
        print("Bases atualizadas até o horário fechado vigente. Prosseguindo...")
        break
    else:
        print("Bases ainda não estão no horário vigente. Aguardando...")
        time.sleep(300)


#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                            # CARREGAMENTO DA BASE, TRANSFORMAÇÃO E FILTRAGEM
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/

print("\nIniciando exportação dos dados do indicador IR")

def carregamento_base_dados_ir():
    caminho_entrada_query_sql = os.path.join("data", "Base_IR.sql")

    with open(caminho_entrada_query_sql, "r", encoding='utf-8') as arquivo_sql:
        query = arquivo_sql.read()
        data_frame_base_IR = client.query(query).to_dataframe()
        print(f"DataFrame criado com {data_frame_base_IR.shape[0]} linhas e {data_frame_base_IR.shape[1]} colunas.")
        return data_frame_base_IR


def filtro_dados_horario_atual(data_frame_base_IR):
    hora_fechada = datetime.now().strftime("%H:00")

    dados_horario_vigente = data_frame_base_IR[data_frame_base_IR["data_oferta_hora_max"].astype(str) >= hora_fechada]

    if dados_horario_vigente.empty:
        raise Exception("Nenhum dado encontrado para o horário vigente.")
    
    print(f"Dados filtrados para o horário vigente: {hora_fechada}")
    return dados_horario_vigente, hora_fechada


def transformacao_dados(dados_horario_vigente):
    linha_dados = dados_horario_vigente.iloc[0]
    dados_dicionario = linha_dados.to_dict()
    print("Transformação do Data Frame em dicionário foi bem sucedida.") 
    return dados_dicionario


#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                        # IMPORTAÇÃO, ESTRUTURAÇÃO E EXPORTAÇÃO DO ARQUIVO JSON MENSAGEM COMPLETA 
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/

def importacao_arquivo_json():
    nome_arquivo_json = "report_information_IR_card.json"
    caminho_entrada_json = os.path.join("views", nome_arquivo_json)

    with open(caminho_entrada_json, "r", encoding="utf-8") as arquivo_json:
        estrutura = json.load(arquivo_json)

    print(f"Arquivo JSON {nome_arquivo_json} importado com sucesso.")
    return estrutura


def estrutura_json(dados_dicionario, estrutura):
    preenchimento_str = json.dumps(estrutura)

    for chave, valor in dados_dicionario.items():
        placeholder = "{{" + chave + "}}"
        preenchimento_str = preenchimento_str.replace(placeholder, str(valor))

    return json.loads(preenchimento_str)


def exportacao_arquivo_json(estrutura, hora_fechada):
    nome_arquivo_saida_json = "Mensagem_Dados_IR.json"
    caminho_saida_json_completa = os.path.join(caminho_saida_json, nome_arquivo_saida_json)

    with open(caminho_saida_json_completa, "w", encoding="utf-8") as arquivo_saida_json:
        json.dump(estrutura, arquivo_saida_json, ensure_ascii=False, indent=4)

    print(f"Arquivo JSON exportado com sucesso para: {caminho_saida_json_completa}")

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                            # IMPORTAÇÃO, ESTRUTURAÇÃO E EXPORTAÇÃO DO ARQUIVO JSON MENSAGEM RESUMIDA
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/

def importacao_arquivo_json_resumido():
    nome_arquivo = "report_resumido_ir.json"
    caminho_entrada = os.path.join("views", nome_arquivo)

    with open(caminho_entrada, "r", encoding="utf-8") as arquivo_json:
        estruturacao_arquivo_resumido = json.load(arquivo_json)
    print(f"Arquivo JSON {nome_arquivo} importado com sucesso.")

    return estruturacao_arquivo_resumido


def estrutura_json_resumido(dados_dicionario, estruturacao_arquivo_resumido):
    preenchimento_str_resumo = json.dumps(estruturacao_arquivo_resumido)

    for chave, valor in dados_dicionario.items():
        placeholder = "{{" + chave + "}}"
        preenchimento_str_resumo = preenchimento_str_resumo.replace(placeholder, str(valor))

    return json.loads(preenchimento_str_resumo)


def exportacao_arquivo_json_resumido(estrutura_resumida):
    nome_arquivo_saida_resumido = "Mensagem_Dados_IR_Resumo.json"
    caminho_saida_json_resumido = os.path.join(caminho_saida_json, nome_arquivo_saida_resumido)

    with open(caminho_saida_json_resumido, "w", encoding="utf-8") as arquivo_saida_json:
        json.dump(estrutura_resumida, arquivo_saida_json, ensure_ascii=False, indent=4)

    print(f"Arquivo JSON exportado com sucesso para: {caminho_saida_json}")


#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                                        # CHAMADA DAS FUNÇÕES
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/

data_frame = carregamento_base_dados_ir()
data_frame_filtrado, hora = filtro_dados_horario_atual(data_frame)
dados_dict = transformacao_dados(data_frame_filtrado)

estrutura_base = importacao_arquivo_json()
estrutura_preenchida = estrutura_json(dados_dict, estrutura_base)

exportacao_arquivo_json(estrutura_preenchida, hora)

estrutura_resumida_base = importacao_arquivo_json_resumido()
estrutura_resumida_preenchida = estrutura_json_resumido(dados_dict, estrutura_resumida_base)
exportacao_arquivo_json_resumido(estrutura_resumida_preenchida)


#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                                      # INSERÇÃO DE LOG
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/

log_processo = """
INSERT INTO TB_PROCS_LOG
VALUES(
    'PY_EXPORTACAO_DADOS_IR',
    ?, 
    cast(getdate() as datetime),
    'OK',
    NULL)
"""

cursor.execute(log_processo, horario_start)
conexao.commit()
conexao.close()
print("Log inserido com sucesso e conexão encerrada.")
