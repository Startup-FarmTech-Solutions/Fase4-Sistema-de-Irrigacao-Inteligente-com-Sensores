# Classe modelo do Leitura do Sensor
from datetime import date as Date

class LeituraSensorModel:
    def __init__(
            self,
            id_leitura_sensor: int = None,
            id_sensor: int = None,
            id_area_plantio: int = None,
            data_hora: str = Date.today,
            temperatura: float = None,
            umidade: float = None,
            leitura_ldr: int = None,
            ph: float = None,
            potassio: int = None,  
            fosforo: int = None,  
            irrigacao: chr = None
    ):
        self.id_leitura_sensor = id_leitura_sensor
        self.id_sensor = id_sensor
        self.id_area_plantio = id_area_plantio
        self.data_hora = data_hora
        self.temperatura = temperatura
        self.umidade = umidade
        self.leitura_ldr = leitura_ldr
        self.ph = ph
        self.potassio = potassio
        self.fosforo = fosforo
        self.irrigacao = irrigacao

    # Getters e Setters
    def get_id_leitura_sensor(self) -> int:
        return self.id_leitura_sensor

    def set_id_leitura_sensor(self, id_leitura_sensor: int):
        self.id_leitura_sensor = id_leitura_sensor

    def get_id_sensor(self) -> int:
        return self.id_sensor

    def set_id_sensor(self, id_sensor: int):
        self.id_sensor = id_sensor

    def get_id_area_plantio(self) -> int:
        return self.id_area_plantio

    def set_id_area_plantio(self, id_area_plantio: int):
        self.id_area_plantio = id_area_plantio

    def get_data_hora(self) -> Date:
        return self.data_hora

    def set_data_hora(self, data_hora: Date):
        self.data_hora = data_hora

    def get_temperatura(self) -> float:
        return self.temperatura

    def set_temperatura(self, temperatura: float):
        self.temperatura = temperatura

    def get_umidade(self) -> float:
        return self.umidade

    def set_umidade(self, umidade: float):
        self.umidade = umidade

    def get_leitura_ldr(self) -> int:
        return self.leitura_ldr

    def set_leitura_ldr(self, leitura_ldr: int):
        self.leitura_ldr = leitura_ldr

    def get_ph(self) -> float:
        return self.ph

    def set_ph(self, ph: float):
        self.ph = ph

    def get_potassio(self) -> int: 
        return self.potassio

    def set_potassio(self, potassio: int):
        self.potassio = potassio

    def get_fosforo(self) -> int: 
        return self.fosforo

    def set_fosforo(self, fosforo: int):
        self.fosforo = fosforo

    def get_irrigacao(self) -> str:
        return self.irrigacao

    def set_irrigacao(self, irrigacao: str):
        self.irrigacao = irrigacao

    def __str__(self):
        return (f"LeituraSensorModel(id_leitura_sensor={self.id_leitura_sensor}, id_sensor={self.id_sensor}, "
                f"id_area_plantio={self.id_area_plantio}, data_hora={self.data_hora}, temperatura={self.temperatura}, "
                f"umidade={self.umidade}, leitura_ldr={self.leitura_ldr}, ph={self.ph}, potassio={self.potassio}, "
                f"fosforo={self.fosforo}, irrigacao={self.irrigacao})")