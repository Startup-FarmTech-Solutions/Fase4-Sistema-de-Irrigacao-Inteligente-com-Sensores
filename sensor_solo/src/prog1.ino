#include <ArduinoJson.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include <FS.h>
#include <SPIFFS.h>
#include <CJSON.h>
#include <WiFi.h>         // Biblioteca WiFi ESP32
#include <PubSubClient.h> // Biblioteca MQTT
#include <WiFiClientSecure.h>

// Definições dos pinos
#define DHTPIN 13
#define DHTTYPE DHT22
#define PINO_POTASSIO 18
#define LIGHT_SENSOR_PIN 36
#define PINO_FOSFORO 22
#define RELE_PIN 4
#define IRRIGACAO_ATIVA HIGH
#define IRRIGACAO_INATIVA LOW
#define LED_PIN 17

// Variáveis globais
LiquidCrystal_I2C lcd(0x27, 20, 4);
DHT dht(DHTPIN, DHTTYPE);
int potassioPresente = 0;
int fosforoPresente = 0;
float pH = 0.0;
float temperature_display = 0.0;
float humidity_display = 0.0;
float humidity_variation = 0.0;
float temperature_variation = 0.0;
// float pH_variation = 0.0;
bool leituraRealizada = false;
unsigned long lastReadTime = 0;
const unsigned long readInterval = 2000;
bool irrigacao_inicial = false;

int potassioInicial = random(0, 120);
int fosforoInicial = random(0, 50);
float pH_display = random(4.5, 9.0);

int leituraLDR = analogRead(LIGHT_SENSOR_PIN);

// Calibração do sensor de pH (LDR) - Ajuste esses valores conforme seu LDR no Wokwi
const int ldrMin = 100; // Valor LDR em alta luminosidade (pH alto/baixo) - Ajuste!
const int ldrMax = 900; // Valor LDR em baixa luminosidade (pH baixo/alto) - Ajuste!

// Configurações da rede Wi-Fi
const char *ssid = "Wokwi-GUEST";
const char *password = "";

const char *mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;

// Tópicos MQTT para publicação
const char *topic_temp = "solo/temperatura";
const char *topic_umid = "solo/umidade";
const char *topic_ph = "solo/ph";
const char *topic_ph_cat = "solo/ph/categoria";
const char *topic_potassio = "solo/nutrientes/potassio";
const char *topic_fosforo = "solo/nutrientes/fosforo";
const char *topic_irrigacao = "solo/irrigacao/status";

const char *server_ip = "192.168.1.48"; // Adicione o IP do seu computador
const uint16_t server_port = 12345;

WiFiClient espClient;
PubSubClient client(espClient);

typedef struct DadosSensor
{
  float temperatura;
  float umidade;
  int leitura;
  float ph;
  int potassio;
  int fosforo;
  char irrigacao;
} DadosSensor;

DadosSensor dadosSensor;

// Funções auxiliares
float mapearPH(int ldrValue)
{
  return 0.0 + (14.0 - 0.0) * (ldrValue - ldrMax) / float(ldrMin - ldrMax);
}

String categorizarPH(float phValue)
{
  if (phValue < 6.0)
  {
    return "Acido";
  }
  else if (phValue >= 6.1 && phValue <= 7.3)
  {
    return "Neutro";
  }
  else
  {
    return "Alcalino";
  }
}

void setup_wifi()
{
  delay(10);
  Serial.println("Conectando ao WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado!");
  Serial.println(WiFi.localIP());
}

void callback(char *topic, byte *payload, unsigned int length)
{
  Serial.print("Mensagem recebida em ");
  Serial.print(topic);
  Serial.print(": ");
  for (int i = 0; i < length; i++)
  {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

void reconnect()
{
  while (!client.connected())
  {
    Serial.print("Conectando no MQTT...");
    if (client.connect("ESP32Client"))
    {
      Serial.println("conectado!");
      if (client.connected())
      {
        char buffer[16];

        // Temperatura
        dtostrf(temperature_display, 4, 1, buffer);
        client.publish(topic_temp, buffer);

        // Umidade
        dtostrf(humidity_display, 4, 1, buffer);
        client.publish(topic_umid, buffer);

        // pH
        dtostrf(pH_display, 4, 1, buffer);
        client.publish(topic_ph, buffer);

        // Categoria do pH
        String categoriaPH = categorizarPH(pH_display);
        client.publish(topic_ph_cat, categoriaPH.c_str());

        // Potassio
        dtostrf(potassioInicial, 4, 1, buffer);
        client.publish(topic_potassio, buffer);

        // Fosforo
        dtostrf(fosforoInicial, 4, 1, buffer);
        client.publish(topic_fosforo, buffer);
      }
    }
    else
    {
      Serial.print("falhou, rc=");
      Serial.print(client.state());
      Serial.println(" tentando novamente em 5 segundos");
      delay(500);
    }
  }
}

void publicarDados()
{
  JsonDocument doc;
  doc["temperatura"] = temperature_display;
  doc["umidade"] = humidity_display;
  doc["pH"] = roundf(pH_display * 100) / 100.0;
  doc["potassio"] = potassioInicial;
  doc["fosforo"] = fosforoInicial;
  doc["irrigacao"] = digitalRead(RELE_PIN) == IRRIGACAO_ATIVA ? "ativa" : "inativa";

  char buffer[256];
  serializeJson(doc, buffer);

  if (client.connected())
  {
    client.publish("sensor/solo/dados", buffer);
  }
}

void enviarDadosPython(float temperatura, float umidade, int leitura_ldr, float ph, int potassio, int fosforo, String irrigacao)
{
  WiFiClient client;
  if (client.connect(server_ip, server_port))
  {
    String json = "{";
    json += "\"temperatura\":" + String(temperatura, 2) + ",";
    json += "\"umidade\":" + String(umidade, 2) + ",";
    json += "\"leitura_ldr\":" + String(leitura_ldr) + ",";
    json += "\"ph\":" + String(ph) + ",";
    json += "\"potassio\":" + String(potassio) + ",";
    json += "\"fosforo\":" + String(fosforo) + ",";
    json += "\"irrigacao\":\"" + irrigacao + "\"";
    json += "}";
    client.println(json);
    client.stop();
    Serial.println("Dados enviados ao Python!");
  }
  else
  {
    Serial.println("Falha ao conectar ao servidor Python.");
  }
}

void setup()
{
  pH = mapearPH(leituraLDR);

  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  // Inicializa o LCD
  dht.begin();
  lcd.init();
  lcd.backlight();
  lcd.setCursor(3, 1);
  lcd.print("HELLO EVERYONE!");
  delay(2000);
  lcd.clear();
  lcd.setCursor(0, 1);
  lcd.print("Medidor de");
  lcd.setCursor(0, 2);
  lcd.print("Parametros Solo");
  delay(2000);
  lcd.clear();

  // Inicializa o gerador de números aleatórios
  randomSeed(micros());

  // Configura os pinos dos botões e do relé
  pinMode(PINO_POTASSIO, INPUT_PULLUP);
  pinMode(PINO_FOSFORO, INPUT_PULLUP);
  pinMode(RELE_PIN, OUTPUT);
  digitalWrite(RELE_PIN, IRRIGACAO_INATIVA);

  lastReadTime = millis();

  // Lê os dados dos sensores
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  // Adiciona uma pequena variação aos valores das variáveis globais
  humidity_variation = random(-10, 10) / 10.0;
  temperature_variation = random(-5, 5) / 10.0;
  // pH_variation = random(-20, 20) / 10.0;

  temperature_display = temperature + temperature_variation;
  humidity_display = humidity + humidity_variation;
  // pH_display = constrain(pH + pH_variation, 0.0, 14.0);

  // Atualiza o estado dos nutrientes
  potassioPresente = (digitalRead(PINO_POTASSIO) == LOW) ? 1 : 0;
  fosforoPresente = (digitalRead(PINO_FOSFORO) == LOW) ? 1 : 0;

  String categoriaPH_inicial = categorizarPH(pH_display);

  // Apresentação dos resultados no monitor serial
  Serial.begin(115200);
  Serial.println("\n--- Leitura Inicial dos Sensores ---");
  Serial.print("Temperatura: ");
  Serial.print(temperature_display, 1);
  Serial.println(" C");
  Serial.print("Umidade: ");
  Serial.print(humidity_display, 1);
  Serial.println(" %");
  Serial.print("Leitura LDR: ");
  Serial.print(leituraLDR);
  Serial.print(" | pH: ");
  Serial.print(pH_display, 1);
  Serial.print(" (");
  Serial.print(categoriaPH_inicial);
  Serial.println(")");
  Serial.println("--------------------------");

  // Exibe os dados no LCD
  lcd.clear();
  lcd.setCursor(2, 0);
  lcd.print("Temperatura:");
  lcd.print(temperature_display);
  lcd.setCursor(2, 1);
  lcd.print("Umidade:");
  lcd.print(humidity_display);
  lcd.print("%");
  lcd.setCursor(2, 2);
  lcd.print("pH:");
  lcd.print(pH_display);
  lcd.setCursor(2, 3);
  lcd.print("Irrigacao:");
  lcd.print(irrigacao_inicial ? " ON" : " OFF"); // Indica o status da irrigação no LCD
  delay(3000);
  lcd.clear();

  pinMode(LED_PIN, OUTPUT);

  bool irrigar = " ";
  
  // Irriga se a umidade for baixa
  if (humidity_display < 40.0)
  {
    irrigar = true;
    digitalWrite(LED_PIN, HIGH);
  }
  // Interrompe a irrigação se a umidade estiver em uma faixa segura
  else
  {
    irrigar = false;
    digitalWrite(LED_PIN, LOW);
  }

  // Controla o relé e o LED
  digitalWrite(RELE_PIN, irrigar ? IRRIGACAO_ATIVA : IRRIGACAO_INATIVA);
  if (irrigar)
  {
    Serial.println("Irrigação Ativada!");
  }
  else
  {
    Serial.println("Irrigação Inativa!");
  }

  publicarDados();
}

void loop()
{
  // Lê o estado dos botões
  int leituraBotaoP = digitalRead(PINO_POTASSIO);
  int leituraBotaoF = digitalRead(PINO_FOSFORO);

  float humidity = temperature_display;
  float temperature = humidity_display;

  // Lógica de controle da irrigação
  bool irrigar = false;

  static bool botaoPPressionado = false;
  static bool botaoFPressionado = false;

  if (leituraBotaoP == LOW || leituraBotaoF == LOW)
  {
    leituraRealizada = true;

    // Potássio
    if (leituraBotaoP == LOW && !botaoPPressionado)
    {
      potassioPresente = 1;
      int potassioAdicionado = 0;
      if (potassioInicial < 40)
      {
      // Se está muito baixo, adiciona mais para tentar chegar na faixa adequada
      potassioAdicionado = random(10, 20); // valor aleatório entre 10 e 19
      }
      else if (potassioInicial >= 40 && potassioInicial <= 70)
      {
      // Se está baixo, adiciona um valor moderado
      potassioAdicionado = random(8, 15); // valor aleatório entre 8 e 14
      }
      else if (potassioInicial >= 71 && potassioInicial <= 120)
      {
      // Se está adequado, adiciona pouco
      potassioAdicionado = random(1, 5); // valor aleatório entre 1 e 4
      }
      else
      {
      // Se está alto, não adiciona
      potassioAdicionado = 0;
      }
      potassioInicial += potassioAdicionado;
      botaoPPressionado = true;
    }
    else if (leituraBotaoP == HIGH)
    {
      potassioPresente = 0;
      botaoPPressionado = false;
    }

    // Fósforo
    if (leituraBotaoF == LOW && !botaoFPressionado)
    {
      fosforoPresente = 1;
      int fosforoAdicionado = 0;
      if (fosforoInicial < 5)
      {
      // Muito baixo, adiciona mais
      fosforoAdicionado = random(4, 7); // valor aleatório entre 4 e 6
      }
      else if (fosforoInicial >= 5 && fosforoInicial <= 10)
      {
      // Baixo, adiciona moderado
      fosforoAdicionado = random(3, 5); // valor aleatório entre 3 e 4
      }
      else if (fosforoInicial >= 11 && fosforoInicial <= 20)
      {
      // Adequado, adiciona pouco
      fosforoAdicionado = random(1, 3); // valor aleatório entre 1 e 2
      }
      else
      {
      // Alto, não adiciona
      fosforoAdicionado = 0;
      }
      fosforoInicial += fosforoAdicionado;
      botaoFPressionado = true;
    }
    else if (leituraBotaoF == HIGH)
    {
      fosforoPresente = 0;
      botaoFPressionado = false;
    }

    Serial.println("\n--- Leitura dos Sensores ---");
    Serial.print("pH: ");
    Serial.print(pH_display, 1);
    Serial.print(" (");
    Serial.print(categorizarPH(pH_display));
    Serial.println(")");
    Serial.print("Potássio Detectado: ");
    Serial.println(potassioPresente ? "Sim" : "Não");
    Serial.print("Fósforo Detectado: ");
    Serial.println(fosforoPresente ? "Sim" : "Não");
    Serial.printf("Irrigacao: %s\n", irrigar ? "ATIVA" : "INATIVA");
    Serial.println("--------------------------");


    if (potassioInicial < 40 && potassioInicial <= 70){
      Serial.println("Nível de potássio baixo");
    }
    else if (potassioInicial >= 71 && potassioInicial <= 120)
    {
      Serial.println("Nível de potássio adequado");
    }
    else
    {
      Serial.println("Nível de potássio alto");
    }

    if (fosforoInicial < 5  && fosforoInicial <= 10){
      Serial.println("Nível de fósforo baixo");
    }
    else if (fosforoInicial >= 11 && fosforoInicial <= 20)
    {
      Serial.println("Nível de fósforo adequado");
    }
    else
    {
      Serial.println("Nível de fósforo alto");
    }

    // Exibe os dados no LCD
    lcd.clear();
    lcd.setCursor(3, 0);
    lcd.print("Potassio:");
    lcd.print(potassioInicial);
    lcd.setCursor(3, 1);
    lcd.print("Fosforo:");
    lcd.print(fosforoInicial);
    lcd.setCursor(3, 2);
    lcd.print("Irrigacao:");
    lcd.print(irrigar ? " ON" : " OFF"); // Indica o status da irrigação no LCD
    delay(900);
    lcd.clear();

    publicarDados();

    enviarDadosPython(
        temperature_display,
        humidity_display,
        leituraLDR,
        pH_display,
        potassioInicial,
        fosforoInicial,
        digitalRead(RELE_PIN) == IRRIGACAO_ATIVA ? "ATIVA" : "INATIVA");

    if (!client.connected())
    {
      reconnect();
    }
    client.loop();

    delay(100);
  }
  else if (leituraRealizada)
  {
    // Mantém a última leitura no LCD
    lcd.clear();
    lcd.setCursor(3, 0);
    lcd.print("Potassio:");
    lcd.print(potassioInicial);
    lcd.setCursor(3, 1);
    lcd.print("Fosforo:");
    lcd.print(fosforoInicial);
    lcd.setCursor(3, 2);
    lcd.print("Irrigacao:");
    lcd.print(irrigar ? " ON" : " OFF");
    delay(1000);
    lcd.clear();
  }
  else
  {
    lcd.setCursor(0, 2);
    lcd.print("Aguardando leitura.."); // Indica o status da irrigação no LCD
  }
  delay(200);
}
