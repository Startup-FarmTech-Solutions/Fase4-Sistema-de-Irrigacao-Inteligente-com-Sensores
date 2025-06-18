from connection.connection_db import ConnectionDB
from model.sensor_model import SensorModel  # Importe o modelo SensorModel


class SensorController:
    def __init__(self):
        self.sensores = []  # Lista para armazenar objetos SensorModel, se necessário

    def menu_sensor(self):
        """
        Exibe o menu interativo para o usuário e executa as ações escolhidas.
        """
        while True:
            print("\n🚜Menu dos Sensores:")
            print("1️⃣ Cadastrar Sensor")
            print("2️⃣ Visualizar Sensores")
            print("3️⃣ Atualizar Sensor")
            print("4️⃣ Remover Sensor")
            print("0️⃣ Sair")
            
            opcao = input("Escolha uma opção (0-4): ").strip()
            if opcao == '1':
                self.create_sensor()
            elif opcao == '2':
                self.get_sensores()
            elif opcao == '3':
                self.update_sensor_by_id()
            elif opcao == '4':
                self.delete_sensor_by_id()
            elif opcao == '0':
                print("Saindo...")
                break
            else:
                print("Opção inválida! Por favor, escolha uma opção válida.")


    def create_sensor(self) -> SensorModel:
        """
        Cria um novo sensor no banco de dados e retorna um objeto SensorModel.
        """
        # Cria uma nova conexão com o banco que permite escrita
        connection = ConnectionDB(can_write=True)
        connection.connect_to_oracle()
        
        nome_sensor = input("Digite a descrição/nome do sensor: ")

            # Verifica se o sensor já existe
        if self.sensor_exist(connection, nome_sensor):
            # Solicita os dados do sensor ao usuário
            modelo = input("Digite o modelo do sensor: ")
            tipo_sensor = input("Digite o tipo do sensor: ")

            try:
                connection.write(f"""
                        INSERT INTO sensor ( modelo, tipo_sensor, nome_sensor) 
                        VALUES ('{modelo}', '{tipo_sensor}', '{nome_sensor}')
                        """)
                
                df_sensor = connection.fetch_dataframe(f"SELECT * FROM sensor WHERE nome_sensor = '{nome_sensor}'")

                # Verifica se o sensor foi inserido e no banco de dados corretamente
                if not df_sensor.empty:
                    # Cria e retorna um novo objeto SensorModel
                    novo_sensor = SensorModel(
                        df_sensor.id_sensor.values[0],
                        df_sensor.modelo.values[0],
                        df_sensor.nome_sensor.values[0],
                        df_sensor.tipo_sensor.values[0]
                    )
                    print("✅ Sensor criado e retornado com sucesso!")
                    return novo_sensor  # Retorna o novo sensor criado
                else:
                    print("⚠️ Erro: Sensor não encontrado no banco de dados após inserção.")
                    return None
                
            except Exception as e:
                print(f"❗️Erro ao inserir o sensor: {e}")
                return None
            finally:
                connection.close_all()  # Garante que a conexão seja fechada
        else:
            print(f"⚠️ Sensor {nome_sensor} já existe no banco de dados.")
            connection.close_all()
            return None

    def sensor_exist(self, connection: ConnectionDB, nome_sensor) -> bool:
        # Verifica se um sensor já existe no banco de dados com o nome fornecido.
        df_sensor = connection.fetch_dataframe(f"SELECT * FROM sensor WHERE nome_sensor = '{nome_sensor}'")
        return df_sensor.empty  # Retorna True se o sensor existir
    
    def get_sensores(self, connection: ConnectionDB = None) -> list:
        """
        Recupera todos os sensores do banco de dados e os exibe.
        """
        if connection is None:
            connection = ConnectionDB()
            connection.connect_to_oracle()

        try:
            df_sensores = connection.fetch_dataframe("SELECT * FROM sensor")
            if not df_sensores.empty:
                print("Sensores disponíveis:")
                for index, row in df_sensores.iterrows():
                    print(f"ID: {row['id_sensor']}, Nome: {row['nome_sensor']}, Modelo: {row['modelo']}, Tipo: {row['tipo_sensor']}")
            else:
                print("⚠️ Nenhum sensor encontrado.")
        finally:
            if connection is not None:
                connection.close_all()

    def update_sensor_by_id(self):
        """
        Atualiza os dados de um sensor existente no banco de dados.
        """
        connection = ConnectionDB(can_write=True)
        connection.connect_to_oracle()

        id_sensor = input("Digite o ID do sensor a ser atualizado: ")
        novo_nome_sensor = input("Digite o novo nome do sensor: ")
        novo_modelo = input("Digite o novo modelo do sensor: ")
        novo_tipo_sensor = input("Digite o novo tipo do sensor: ")

        try:
            connection.write(f"""
                UPDATE sensor 
                SET nome_sensor = '{novo_nome_sensor}', modelo = '{novo_modelo}', tipo_sensor = '{novo_tipo_sensor}'
                WHERE id_sensor = {id_sensor}
            """)
            connection.commit()
            print("✅ Sensor atualizado com sucesso!")
        except Exception as e:
            print(f"❗️Erro ao atualizar o sensor: {e}")
        finally:
            connection.close_all()

    def delete_sensor_by_id(self):
        """
        Remove um sensor do banco de dados pelo ID.
        """
        connection = ConnectionDB(can_write=True)
        connection.connect_to_oracle()

        id_sensor = input("Digite o ID do sensor a ser removido: ")

        try:
            connection.write(f"DELETE FROM sensor WHERE id_sensor = {id_sensor}")
            connection.commit()
            print("✅ Sensor removido com sucesso!")
        except Exception as e:
            print(f"❗️Erro ao remover o sensor: {e}")
        finally:
            connection.close_all()