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
float pH_display = 0.0;
float temperature_display = 0.0;
float humidity_display = 0.0;
float humidity_variation = 0.0;
float temperature_variation = 0.0;
float pH_variation = 0.0;
bool leituraRealizada = false;
unsigned long lastReadTime = 0;
const unsigned long readInterval = 2000;
bool irrigacao_inicial = false;

int leituraLDR_inicial = analogRead(LIGHT_SENSOR_PIN);

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

const char *server_ip = " "; // Adicione o IP do seu computador
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
  if (phValue < 6.5)
  {
    return "Acido";
  }
  else if (phValue > 7.5)
  {
    return "Alcalino";
  }
  else
  {
    return "Neutro";
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

        // Nutrientes
        client.publish(topic_potassio, potassioPresente ? "1" : "0");
        client.publish(topic_fosforo, fosforoPresente ? "1" : "0");
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
  doc["pH"] = roundf(pH_display * 100) / 100.0;;
  doc["potassio"] = potassioPresente;
  doc["fosforo"] = fosforoPresente;
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
    json += "\"ph\":" + String(ph, 2) + ",";
    json += "\"potassio\":" + String(potassio ? "true" : "false") + ",";
    json += "\"fosforo\":" + String(fosforo ? "true" : "false") + ",";
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
  pH = mapearPH(leituraLDR_inicial);

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
  pH_variation = random(-20, 20) / 10.0;

  temperature_display = temperature + temperature_variation;
  humidity_display = humidity + humidity_variation;
  pH_display = constrain(pH + pH_variation, 0.0, 14.0);

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
  Serial.print(leituraLDR_inicial);
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
  bool irrigar = " ";

  if (leituraBotaoP == LOW || leituraBotaoF == LOW)
  {
    leituraRealizada = true;

    potassioPresente = (leituraBotaoP == LOW) ? 1 : 0;
    fosforoPresente = (leituraBotaoF == LOW) ? 1 : 0;

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

    // Exibe os dados no LCD
    lcd.clear();
    lcd.setCursor(3, 0);
    lcd.print("Potassio:");
    lcd.print(potassioPresente ? "Sim" : "Não");
    lcd.setCursor(3, 1);
    lcd.print("Fosforo:");
    lcd.print(fosforoPresente ? "Sim" : "Não");
    lcd.setCursor(3, 2);
    lcd.print("Irrigacao:");
    lcd.print(irrigar ? " ON" : " OFF"); // Indica o status da irrigação no LCD
    delay(900);
    lcd.clear();

    publicarDados();

    enviarDadosPython(
        temperature_display,
        humidity_display,
        leituraLDR_inicial,
        pH_display,
        potassioPresente,
        fosforoPresente,
        digitalRead(RELE_PIN) == IRRIGACAO_ATIVA ? "ATIVA" : "INATIVA");

    if (!client.connected())
    {
      reconnect();
    }
    client.loop();

    if (client.connected())
    {
    }
    delay(100);
  }

  else if (leituraRealizada)
  {
    // Mantém a última leitura no LCD
    lcd.clear();
    lcd.setCursor(3, 0);
    lcd.print("Potassio:");
    lcd.print(potassioPresente ? "Sim" : "Nao");
    lcd.setCursor(3, 1);
    lcd.print("Fosforo:");
    lcd.print(fosforoPresente ? "Sim" : "Nao");
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
