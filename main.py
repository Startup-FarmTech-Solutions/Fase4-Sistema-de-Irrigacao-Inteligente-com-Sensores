# importando as bibliotecas necessárias
import os
from connection.connection_db import ConnectionDB
from controller.area_plantio_controller import AreaPlantioController
from controller.cultura_controller import CulturaController
from controller.leitura_sensor_controller import LeituraSensorController
from controller.sensor_controller import SensorController
from display.menu import Menu

"""
    Este arquivo é o ponto de entrada principal do sistema de irrigação inteligente.
    Ele realiza o carregamento das variáveis de ambiente e inicializa a conexão com o banco de dados Oracle.

    Arquitetura do sistema: Microserviços
    - Cada microserviço é responsável por uma funcionalidade específica do sistema.

    Principais componentes:
    1. Sensor Solo: Coleta dados dos sensores de umidade do solo e armazena no banco de dados.
    2. Dashboard: Exibe, em tempo real, os dados coletados pelos sensores em um painel web.
    3. API: Fornece endpoints para interação externa com o sistema (ex: cadastro de áreas, sensores, culturas).

    Observação: 
    - É necessário criar um ambiente virtual (.venv) em cada pasta de microserviço para instalar as dependências específicas de cada um.

    Para iniciar o sistema, execute este arquivo.
"""

if __name__ == "__main__":
    try:
        connection = ConnectionDB()
        connection.connect_to_oracle() # Conecte ao banco de dados
        menu = Menu() # Instancia a classe menu
        menu.display_menu()  # Exibe o menu principal
    except ConnectionResetError as cre:
        print("Conexão de rede foi encerrada pelo host remoto. Detalhes:", cre)
    except Exception as e:
        print(f"Erro ao iniciar o sistema: {e}")
