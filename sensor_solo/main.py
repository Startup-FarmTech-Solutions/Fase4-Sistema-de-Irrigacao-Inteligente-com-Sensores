#importando as bibliotecas necessárias
import socket
import json
import random
import os
import sys
import csv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from connection.connection_db import ConnectionDB
from controller.leitura_sensor_controller import LeituraSensorController

# Banco de dados SQL simulado em Python (dicionário)1
database = {
    "leituras": []
}

# # Variáveis para armazenar os valores de potássio e fósforo
potassio_atual = 0.0  # Inicializado como zero para evitar erros de tipo
fosforo_atual = 0.0  # Inicializado como zero para evitar erros de tipo

# Função para adicionar uma leitura ao banco de dados simulado
def adicionar_leitura(leitura):
    """
    Adiciona uma nova leitura ao banco de dados.

    Parâmetros:
        leitura (dict): Um dicionário contendo os dados da leitura a ser adicionada.

    Efeitos colaterais:
        Adiciona a leitura à lista 'leituras' no banco de dados global e imprime uma mensagem de confirmação.
    """
    database["leituras"].append(leitura)

# Função para recuperar todas as leituras do banco de dados simulado
def obter_leituras():
    """
    Retrieve all soil sensor readings from the database.

    Returns:
        list: A list containing all readings stored in the 'leituras' key of the database.
    """
    return database["leituras"]

# Função para recuperar uma leitura específica por ID (simulado pelo índice)
def obter_leitura_por_id(id):
    """
    Retrieve a reading from the database by its ID.

    Args:
        id (int): The index of the reading to retrieve.

    Returns:
        dict or None: The reading at the specified index if it exists, otherwise None.
    """
    if 0 <= id < len(database["leituras"]):
        return database["leituras"][id]
    else:
        return None

# Função para atualizar uma leitura existente (simulado pelo índice)
def atualizar_leitura(id, nova_leitura):
    """
    Atualiza uma leitura existente no banco de dados pelo seu ID.

    Parâmetros:
        id (int): O índice da leitura a ser atualizada na lista de leituras.
        nova_leitura (any): O novo valor da leitura que substituirá o valor atual.

    Comportamento:
        - Se o ID fornecido estiver dentro do intervalo válido da lista de leituras, a leitura correspondente será atualizada com o novo valor.
        - Caso o ID seja inválido, uma mensagem de erro será exibida.
    """
    if 0 <= id < len(database["leituras"]):
        database["leituras"][id] = nova_leitura
    else:
        print("ID de leitura inválido.")

# Função para deletar uma leitura (simulado pelo índice)
def deletar_leitura(id):
    """
    Remove uma leitura do banco de dados pelo índice fornecido.

    Parâmetros:
        id (int): O índice da leitura a ser removida da lista 'leituras' no banco de dados.

    Comportamento:
        - Se o índice for válido (dentro do intervalo da lista), a leitura correspondente é removida.
        - Caso contrário, exibe uma mensagem indicando que o ID é inválido.
    """
    if 0 <= id < len(database["leituras"]):
        del database["leituras"][id]
    else:
        print("ID de leitura inválido.")

# Função para salvar os dados em um arquivo JSON (sobrescreve o arquivo, não gera lista)
def salvar_console_print_json(dados):
    """
    Salva os dados fornecidos em um arquivo JSON localizado em 'data/console_print.json', sobrescrevendo o conteúdo anterior.

    Parâmetros:
        dados (dict): Dicionário contendo as chaves:
            - "temperatura" (float): Valor da temperatura. Padrão 0.0 se ausente.
            - "umidade" (float): Valor da umidade. Padrão 0.0 se ausente.
            - "leitura_ldr" (int): Valor da leitura do sensor LDR. Padrão 0 se ausente.
            - "ph" (float): Valor do pH. Padrão 0.0 se ausente.
            - "potassio" (bool): Indica presença de potássio. Padrão False se ausente.
            - "fosforo" (bool): Indica presença de fósforo. Padrão False se ausente.
            - "irrigacao" (str): Estado da irrigação. Padrão string vazia se ausente.

    Exceções:
        Exibe mensagem de erro no console caso ocorra alguma exceção durante o salvamento.
    """
    try:
        os.makedirs("data", exist_ok=True)
        caminho = "data/console_print.json"
        # Salva apenas o último dado recebido, sobrescrevendo o arquivo
        estrutura = {
            "temperatura": dados.get("temperatura", 0.0),
            "umidade": dados.get("umidade", 0.0),
            "leitura_ldr": dados.get("leitura_ldr", 0),
            "ph": dados.get("ph", 0.0),
            "potassio": dados.get("potassio", 0),
            "fosforo": dados.get("fosforo", 0),
            "irrigacao": dados.get("irrigacao", "")
        }
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(estrutura, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar dados em JSON: {e}")

# Lista global para armazenar as leituras para o CSV
estrutura_csv = []

def salvar_console_print_csv(dados):
    """
    Salva dados em um arquivo CSV.
    Cria o diretório 'ml' se não existir.
    Adiciona o cabeçalho se o arquivo for novo ou estiver vazio.

    Args:
        dados (dict): Um dicionário contendo os dados a serem salvos,
                      com chaves como "temperatura", "umidade", etc.
    """
    try:
        # Define o diretório e o caminho completo do arquivo
        diretorio = "ml"
        caminho_arquivo = os.path.join(diretorio, "console_print.csv")

        # Cria o diretório se não existir
        os.makedirs(diretorio, exist_ok=True)

        # Cabeçalho esperado para o CSV
        cabecalho = [
            "temperatura",
            "umidade",
            "leitura_ldr",
            "ph",
            "potassio",
            "fosforo",
            "irrigacao"
        ]

        # Preparar o novo registro, garantindo que todos os campos do cabeçalho existam
        # e preenchendo com valores padrão se não estiverem nos 'dados'
        novo_registro = {
            "temperatura": dados.get("temperatura", 0.0),
            "umidade": dados.get("umidade", 0.0),
            "leitura_ldr": dados.get("leitura_ldr", 0),
            "ph": dados.get("ph", 0.0),
            "potassio": dados.get("potassio", 0),
            "fosforo": dados.get("fosforo", 0),
            "irrigacao": dados.get("irrigacao", "")
        }
        escrever_cabecalho = not os.path.exists(caminho_arquivo) or os.path.getsize(caminho_arquivo) == 0

        with open(caminho_arquivo, 'a', encoding='utf-8', newline='') as f:
            # Criar o escritor CSV baseado em dicionário, usando o cabeçalho definido
            csv_writer = csv.DictWriter(f, fieldnames=cabecalho)

            if escrever_cabecalho:
                csv_writer.writeheader()
                print(f"Cabeçalho adicionado ao arquivo '{caminho_arquivo}'.")

            # Escrever a nova linha de dados
            csv_writer.writerow(novo_registro)
            # print(f"Dados salvos com sucesso em '{caminho_arquivo}'.")

    except Exception as e:
        print(f"Erro ao salvar dados em CSV: {e}")

# Função principal para receber dados do ESP32 e processá-los
# Na variável host, coloque o IP do seu computador
def main(host = ' ', port = 12345):
    """
    Inicia um servidor TCP para receber leituras de sensores de um dispositivo ESP32, processar os dados recebidos,
    realizar operações CRUD em um banco de dados simulado, simular adição de potássio e fósforo, e responder ao cliente.
    Parâmetros:
        host (str): Endereço IP no qual o servidor irá escutar conexões. Padrão é '192.168.1.35'.
        port (int): Porta na qual o servidor irá escutar conexões. Padrão é 12345.
    Funcionalidades:
        - Inicializa conexão com banco de dados Oracle.
        - Cria um socket TCP para aguardar conexões do ESP32.
        - Recebe mensagens JSON contendo leituras de sensores.
        - Decodifica e processa os dados recebidos, adicionando-os ao banco de dados simulado.
        - Simula a adição de potássio e fósforo conforme comandos recebidos.
        - Realiza operações CRUD (criar, ler, atualizar, deletar) sobre as leituras armazenadas.
        - Salva os dados recebidos em um arquivo JSON.
        - Envia resposta de confirmação ou erro ao cliente.
        - Exibe logs detalhados das operações realizadas e dos dados recebidos.
        - Trata erros de decodificação JSON e outros erros inesperados, enviando mensagens apropriadas ao cliente.
    Observações:
        - O servidor aceita apenas uma conexão por vez.
        - O loop principal permanece ativo até que ocorra uma exceção não tratada.
        - Variáveis globais 'potassio_atual' e 'fosforo_atual' são utilizadas para simular o estoque atual desses nutrientes.
    """
    global potassio_atual, fosforo_atual

    connection = ConnectionDB()
    connection.connect_to_oracle()

    leitura_sensor = LeituraSensorController(connection)

    BUFFER_SIZE = 1024

    # Cria o socket do servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)  # Espera por apenas uma conexão

    print(f"Servidor aguardando conexão em {host}:{port}...")

    try:
        while True:
            # Aceita a conexão do ESP32
            client_socket, client_address = server_socket.accept()
            with client_socket:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    print("Conexão encerrada pelo cliente.")
                    continue

                mensagem = data.decode('utf-8').strip()

                try:
                    # Carrega os dados JSON
                    leitura = json.loads(mensagem)
                    adicionar_leitura(leitura)

                    if database["leituras"]:
                        primeira_leitura = obter_leitura_por_id(0)

                        leitura_sensor.processar_e_inserir_dados()
                        # print(leitura_sensor)

                        # Cria uma nova leitura para atualizar
                        nova_leitura = {
                            "temperatura": 28.5,
                            "umidade": 72.0,
                            "pH": 6.8,
                            "categoria_pH": "Neutro",
                            "potassio": 0,
                            "fosforo": 0,
                            "irrigacao": False
                        }
                        atualizar_leitura(0, nova_leitura)
                        # print("Leitura Atualizada:", obter_leitura_por_id(0))
                       
                        deletar_leitura(len(database["leituras"]) - 1)
                        # print("Leitura Deletada. Leituras Restantes:", obter_leituras())
                    else:
                        print("Banco de dados está vazio")

                    # Salva os dados em um arquivo JSON
                    salvar_console_print_json(leitura)
                    # Salva os dados em um arquivo CSV
                    salvar_console_print_csv(leitura)

                    # Envia uma resposta de volta para o cliente (ESP32)
                    client_socket.send("Dados recebidos com sucesso!".encode('utf-8'))

                except json.JSONDecodeError:
                    print(f"Erro ao decodificar JSON: {mensagem}")
                    client_socket.send("Erro ao decodificar JSON!".encode('utf-8'))
                except Exception as e:
                    print(f"Erro inesperado: {e}")
                    client_socket.send(f"Erro no servidor: {e}".encode('utf-8'))

    except Exception as e:
        print(f"Erro ao iniciar o servidor: {e}")

if __name__ == "__main__":
     main()