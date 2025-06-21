# FIAP - Faculdade de Informática e Administração Paulista 

<p align="center">
  <a href="https://www.fiap.com.br/">
    <img src="assets/logo-fiap.png" alt="FIAP" width="40%">
  </a>
</p>


<br>

# 🌱 FarmTech Solutions - Sistema de Irrigação Inteligente
## 👨‍🎓 Integrantes: 
- Vitor Eiji Fernandes Teruia
```
- RM: rm563683
- E-mail: vitorfer2018@gmail.com
- GitHub: [@Vitor985-hub](https://github.com/Vitor985-hub)
```
- Beatriz Pilecarte de Melo
```
 - RM: rm564952
 - E-mail: beatrizpilecartedemelo@gmail.com
 - GitHub: [@BPilecarte](https://github.com/BPilecarte)
```
- Francismar Alves Martins Junior
```
 - RM: m562869
 - E-mail: yggdrasil.git@gmail.com
 - GitHub: [@yggdrasilGit](https://github.com/yggdrasilGit
```
- Antônio Ancelmo Neto barros
```
 - RM: rm563683
 - E-mail: antonio.anbarros@gmail.com
 - GitHub: [@AntonioBarros19](https://github.com/AntonioBarros19)
```
- Matheus Soares Bento da Silva
```
 - RM: rm565540
 - E-mail: matheusbento044@gmail.com
 - GitHub: [matheusbento044](https://github.com/matheusbento04)
```

## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="https://www.linkedin.com/in/leonardoorabona/">Leonardo Ruiz Orabona</a>
### Coordenador(a)
- <a href="https://www.linkedin.com/company/inova-fusc">ANDRÉ GODOI CHIOVATO</a>


# 🌾 Sistema de Irrigação Inteligente com Sensores e ML

## 📜 Descrição

Este projeto desenvolve um sistema de irrigação inteligente, integrando simulações de hardware em **Wokwi** (com um microcontrolador **ESP32**) e um backend robusto em **Python**. O sistema coleta dados simulados de sensores de solo (umidade, pH, fósforo e potássio), utiliza um **modelo de Machine Learning (KNN)** para sugestões de irrigação, armazena os dados em um banco de dados **SQLite**, e fornece visualização através de um **dashboard Streamlit**. Além disso, incorpora dados climáticos reais via **API OpenWeather** para otimizar as decisões de irrigação.

## 🚀 Funcionalidades Principais

* **Coleta de Dados Simulada:** Sensores de solo (umidade, pH, fósforo, potássio) simulados no Wokwi com ESP32.
* **Controle de Irrigação Automatizado:** Relé simulado para acionamento da bomba de irrigação baseado em critérios de umidade, nutrientes, pH e condições climáticas.
* **Modelo Preditivo (Machine Learning):** Integração de um modelo KNN para fornecer sugestões inteligentes sobre o status da irrigação (Ativa/Inativa) com base nos dados dos sensores.
* **Persistência de Dados:** Armazenamento contínuo dos dados dos sensores em um banco de dados SQLite.
* **Visualização Interativa:** Dashboard interativo construído com Streamlit para monitoramento em tempo real dos dados do solo e do status da irrigação, incluindo a previsão do modelo.
* **Integração Climática:** Consulta à API do OpenWeather para obter dados climáticos (temperatura, chuva) e ajustar a lógica de irrigação.
* **Interface LCD:** Exibição dos dados dos sensores e status da irrigação diretamente no display LCD simulado.

---

## 🔧 Tecnologias Utilizadas

* **Hardware / Simulação:**
    * **ESP32:** Microcontrolador principal.
    * **Wokwi.com:** Plataforma de simulação online para o circuito do ESP32 e sensores.
    * **C/C++:** Linguagem de programação para o firmware do ESP32 (`main.ino`).
* **Backend / Análise:**
    * **Python 3:** Linguagem principal para scripts de backend, ML e dashboard.
    * **SQLite:** Banco de dados local para armazenamento de dados de sensores.
    * **Bibliotecas Python:**
        * `pyserial`: Comunicação serial com o ESP32 (simulada ou real).
        * `scikit-learn`: Para o desenvolvimento e uso do modelo KNN.
        * `streamlit`: Desenvolvimento do dashboard interativo.
        * `requests`: Para integração com a API climática.
        * Outras bibliotecas para manipulação de dados e conexão com DB.
    * **API Pública:** OpenWeather (https://openweathermap.org/api) para dados climáticos.

---

## 🧠 Lógica do Projeto

### Sensores e Atuadores Simulados (Wokwi)

| Sensor/Atuador | Componente Simulado | Tipo de Valor | Descrição |
| :------------- | :------------------ | :------------ | :------------------------------------------------ |
| Umidade        | DHT22               | Analógico     | Mede a umidade do solo e temperatura do ambiente. |
| Fósforo (P)    | Botão físico        | Booleano      | Simula a adição/presença de fósforo no solo.      |
| Potássio (K)   | Botão físico        | Booleano      | Simula a adição/presença de potássio no solo.     |
| pH             | LDR (sensor de luz) | Analógico     | Representa variação contínua do pH do solo.       |
| Bomba Irrigação| Relé + LED          | Booleano      | Atuador que simula o controle da bomba. O LED indica o status. |

### Fluxo de Dados e Processamento

1.  **Leitura do ESP32 (`main.ino`):** O firmware do ESP32 no Wokwi lê os dados dos sensores DHT22 (umidade/temperatura), LDR (pH), e os estados dos botões (fósforo/potássio).
2.  **Envio Serial:** Os dados são enviados do ESP32 para o computador (simulado) via comunicação serial.
3.  **Coleta Python (`main.py`):** Um script Python (`main.py`) lê esses dados da porta serial, processa-os e os salva no arquivo `console_print.csv`.
4.  **Integração Climática (`api_climatica.py`):** O script `api_climatica.py` consulta a API do OpenWeather para obter informações sobre a temperatura e precipitação em São Paulo.
    * **Lógica de Irrigação Inteligente:**
        * Se houver previsão de chuva ou chuva recente, a irrigação é evitada.
        * Se a temperatura ambiente estiver acima de 30°C e não houver previsão de chuva, a irrigação é mais provável.
        * Caso contrário, a irrigação ocorre conforme as outras regras de umidade/nutrientes.
5.  **Modelo de Machine Learning (`modelagem_ml.ipynb` e `ml/models/`):**
    * Um notebook Jupyter (`modelagem_ml.ipynb`) é usado para treinar um modelo de Classificação (KNN) com base em dados históricos de sensores e decisões de irrigação.
    * O modelo treinado (`modelo_irrigacao_knn.pkl`) e seu `scaler` (`scaler_irrigacao.pkl`) são salvos e carregados pelo dashboard.
6.  **Dashboard Streamlit (`dashboard/app.py`):**
    * Lê os dados mais recentes do `console_print.csv`.
    * Carrega o modelo de ML para fazer previsões em tempo real sobre a necessidade de irrigação.
    * Exibe gráficos e indicadores do status dos sensores, dos nutrientes, do pH e da previsão de irrigação do modelo.
    * Compara a sugestão do modelo com o status real da irrigação.

---

## 🧾 Critérios de Acionamento da Bomba (Lógica do Firmware e Backend)

A bomba de irrigação é controlada tanto pela lógica interna do ESP32 (baseada na umidade) quanto pela lógica mais avançada do script Python que considera múltiplos fatores:

* **Umidade:** A bomba é ligada se a umidade do solo estiver abaixo de um limite mínimo (ex: 40%).
* **Nutrientes (P e K):** A presença de nutrientes (simulada pelos botões) influencia a decisão.
* **pH:** O valor de pH (simulado via LDR) é considerado dentro de uma faixa ideal.
* **Condições Climáticas:** Dados da API OpenWeather são utilizados para sobrepor a decisão:
    * **Prioridade:** Se houver previsão de chuva ou chuva recente, a irrigação é geralmente *desativada*, independentemente das condições do solo.
    * **Reforço:** Se a temperatura estiver muito alta (>30°C) e não houver chuva, a irrigação pode ser incentivada.

---

## 🖼 Imagens dos Circuitos (Simulação Wokwi)

Aqui estão as visualizações dos circuitos individuais e do principal no simulador Wokwi.

### Sensor Solo
<img src="assets/imagens_dos_circuitos/sensor_solo.png" alt="Sensor solo" width="300">

#### Resultado serial plotter

![image](https://github.com/user-attachments/assets/c22a73a5-78c1-4ef1-97bf-b373c88f5104)

![image](https://github.com/user-attachments/assets/05dd1e59-aadb-4bf4-bec3-8e6d8e96effb)

![image](https://github.com/user-attachments/assets/5534d0d8-1ee8-4cc1-91af-d411cea5951e)

**Cores das Linhas**
- Roxa: pH
- Laranja: Leitura do LDR (simbolizando indiretamente o pH)
- Verde: Umidade
- Amarelo: Fósforo
- Branco: Temperatura

1. Leitura LDR (Laranja)
Padrão observado: Curva decrescente exponencial até se estabilizar próximo a zero.

**Interpretação:** Como o LDR simula o sensor de pH, essa queda brusca pode estar simulando uma redução de luminosidade — resultando num aumento de pH (que é o que a curva roxa mostra).

2. pH (Roxa)
Padrão observado: Estável, com leves oscilações, mas mantendo-se numa faixa entre aproximadamente 6.5 e 8.

**Interpretação:** Mesmo com a grande variação do LDR, o pH resultante (calculado com uma pequena variação aleatória + constrain) está suavizado. A estabilidade é desejável para evitar ruído no gráfico, e indica que o cálculo com constrain() + random está funcionando como esperado.

3. Umidade (Verde)
Padrão observado: Muito baixa, quase no chão (linha quase constante no valor mínimo).

**Interpretação:** A umidade lida pelo DHT22 está possivelmente retornando NaN ou um valor muito baixo.

4. Fósforo (Amarelo)
Padrão observado: Quase constante, próximo de zero.

**Interpretação:** O botão para aumentar fósforo (PINO_FOSFORO) possivelmente não foi pressionado. Como ele só aumenta no loop ao pressionar esse botão, o valor permanece estático.

5. Temperatura (Branca)
Padrão observado: Uma linha muito fina e reta próxima do eixo inferior, quase invisível.

##  Dashboard

![image](https://github.com/user-attachments/assets/ca1dac1e-603a-4830-b15f-0b0bfa18db39)

![image](https://github.com/user-attachments/assets/f1ea67f2-f315-42cd-ac4e-a5cb56b8c5e1)

![image](https://github.com/user-attachments/assets/f24df726-57c7-4297-b60e-8cef4d318b97)

![image](https://github.com/user-attachments/assets/8894cbf2-f37a-4d4e-9359-9338c1430303)

![image](https://github.com/user-attachments/assets/59dc8181-f631-452a-8203-296a47e30723)

---

## 📁 Estrutura de Pastas
``
FASE4-SISTEMA-DE-IRRIGACAO-INTELIGENTE-C
│
├── pycache/             # Cache de bytecode Python
├── .git/                    # Repositório Git
├── .venv/                   # Ambiente virtual Python (recomendado)
├── .vscode/                 # Configurações do VS Code
├── assets/                  # Ativos do projeto (imagens, logos)
│   └── imagens_dos_circuitos/ # Imagens dos circuitos Wokwi
│       ├── sensor_solo.png
│       ├── captura-umidade.png
│       ├── sensor_fosforo.png
│       ├── sensor_ph.png
│       └── sensor_potassio.png
│   └── logo-fiap.png
│
├── connection/              # Módulos para conexão com banco de dados
│   ├── pycache/
│   ├── init.py
│   └── connection_db.py     # Lógica de conexão com SQLite
│
├── controller/              # Lógica de controle e manipulação de dados
│   ├── pycache/
│   ├── init.py
│   ├── area_plantio_controller.py
│   ├── cultura_controller.py
│   └── sensor_controller.py # Controladores para interagir com os modelos e DB
│
├── dashboard/               # Aplicação de visualização (Streamlit)
│   ├── pycache/
│   ├── init.py
│   └── app.py               # Script principal do dashboard Streamlit
│
├── data/                    # Dados brutos ou temporários do sistema
│   └── console_print.json   # (Antigo: arquivo JSON dos dados do console)
│
├── ml/                      # Módulos e notebooks de Machine Learning
│   ├── .ipynb_checkpoints/  # Checkpoints de notebooks Jupyter
│   ├── models/              # Modelos ML treinados e scalers
│   │   ├── init.py
│   │   ├── modelo_irrigacao_knn.pkl
│   │   └── scaler_irrigacao.pkl
│   ├── console_print.csv    # (Novo: dados do console coletados em CSV)
│   └── modelagem_ml.ipynb   # Notebook Jupyter para treinamento do modelo ML
│
├── model/                   # Modelos de dados para o banco de dados
│   ├── pycache/
│   ├── init.py
│   ├── area_plantio_model.py
│   ├── correcao_model.py
│   ├── cultura_model.py
│   ├── leitura_sensor_model.py
│   └── sensor_model.py
│
├── sensor_solo/             # Código do firmware ESP32 e arquivos de simulação Wokwi
│   ├── .vscode/
│   ├── src/                 # Código-fonte principal do firmware
│   │   └── main.ino         # Firmware C/C++ para ESP32 (Wokwi)
│   ├── .gitignore
│   ├── diagram.json         # Configuração do circuito no Wokwi
│   ├── main.py              # Script Python para interagir com o Wokwi/ESP32 (Coleta de dados serial)
│   ├── platformio.ini       # Configuração do PlatformIO (se usado fora do Wokwi)
│   ├── python-installer.exe # Instalador Python (pode ser removido se desnecessário)
│   └── wokwi.toml           # Configurações do Wokwi
│
├── .env                     # Variáveis de ambiente
├── .env copy                # Cópia das variáveis de ambiente (remover se não usada)
├── .gitignore               # Arquivos/pastas a serem ignorados pelo Git
├── api_climatica.py         # Script para integração com a API climática
├── main.py                  # Script principal Python para rodar o sistema de backend (coleção, DB, etc.)
├── README.md                # Este arquivo de documentação
└── requirements.txt         # Dependências Python do projeto
``


## ▶️ Como Utilizar

### 💾 Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/Startup-FarmTech-Solutions/Sistema-de-Irrigacao-Inteligente-com-Sensores.git](https://github.com/Startup-FarmTech-Solutions/Sistema-de-Irrigacao-Inteligente-com-Sensores.git)
    cd Sistema-de-Irrigacao-Inteligente-com-Sensores
    ```
2.  **Crie e ative um ambiente virtual (altamente recomendado):**
    ```bash
    python -m venv .venv
    # No Windows:
    .venv\Scripts\activate
    # No Linux/macOS:
    source .venv/bin/activate
    ```
3.  **Instale as bibliotecas Python necessárias:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configuração de IPs (se necessário para comunicação local):**
    * **Firmware ESP32 (`sensor_solo/src/main.ino`):**
        * Localize a variável ou constante que define o IP do servidor Python (normalmente perto da linha 56, se a comunicação for via WiFi).
        * Insira o endereço IP da sua máquina host.
    * **Script Python (`sensor_solo/main.py`):**
        * Localize o método `def main()` (aproximadamente na linha 162).
        * Na variável `host` (ou similar, dependendo de como a conexão é estabelecida), insira o endereço IP da sua máquina host.
        * *Nota:* Se a comunicação for apenas serial simulada no Wokwi para o Python local, a configuração de IP pode não ser necessária neste script específico.

### 🔧 Como Executar o Código

1.  **📟 Simulação no Wokwi:**
    * Acesse o arquivo `diagram.json` localizado em `sensor_solo/`.
    * No Wokwi, clique em "Start Simulation".
    * Observe os dados dos sensores sendo exibidos no display LCD e no Serial Monitor/Plotter da simulação.

2.  **🐍 Execução do Backend Python (`main.py`):**
    * Certifique-se de que a simulação no Wokwi esteja rodando e enviando dados pela porta serial (ou via rede, dependendo da sua configuração).
    * Abra um terminal na raiz do projeto.
    * Execute o script principal Python:
        ```bash
        python main.py
        ```
    * Este script irá coletar os dados do Wokwi, processá-los, interagir com a API climática, salvar no banco de dados SQLite e no `console_print.csv`.

3.  **📊 Rodar o Dashboard (Streamlit):**
    * Abra um novo terminal (mantendo o `main.py` e a simulação Wokwi rodando).
    * Navegue até a pasta `dashboard`:
        ```bash
        cd dashboard
        ```
    * Execute o aplicativo Streamlit:
        ```bash
        streamlit run app.py
        ```
    * Uma nova aba no seu navegador será aberta, acessando o dashboard em `http://localhost:8501` (ou uma porta similar).

---

## 🗃 Histórico de Lançamentos

* **0.1.0 - 14/05/2025**
    * Inicialização do projeto base.
    * Simulação inicial de sensores (DHT22, LDR) e relé no Wokwi.
    * Configuração da comunicação serial.
* **0.2.0 - 19/05/2025**
    * Integração com botões para simulação de nutrientes (P, K).
    * Lógica inicial de controle de irrigação baseada em umidade e nutrientes.
    * Implementação básica de coleta de dados Python e armazenamento.
* **0.3.0 - [Data Atual]**
    * Adição da integração com API climática (OpenWeather) para lógica de irrigação avançada.
    * Migração do formato de dados coletados do console de `.json` para `.csv` (`ml/console_print.csv`).
    * Desenvolvimento e integração de modelo de Machine Learning (KNN) para sugestão de irrigação.
    * Criação do dashboard interativo com Streamlit para visualização e monitoramento de dados e previsões do ML.
    * Refatoração da estrutura de pastas para melhor modularidade (connection, controller, model, ml).

---

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/Startup-FarmTech-Solutions/Sistema-de-Irrigacao-Inteligente-com-Sensores.git">SISTEMA DE IRRIGAÇÃO INTELIGENTE</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sob <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
