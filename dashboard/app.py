import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import joblib # Ensure joblib is imported for model loading

# --- IMPORTANT: st.set_page_config() MUST BE THE FIRST STREAMLIT COMMAND ---
st.set_page_config(layout="wide", page_title="Dashboard Sensorial de Irrigação")
# --- END IMPORTANT ---


# --- 0. Carregar o Modelo e o Scaler ---
# Certifique-se de que o caminho para a pasta 'models' esteja correto
# Se 'app.py' está em 'dashboard/' e 'models' está em 'ml/models', então '../ml/models' está correto.
diretorio_models = "../ml/models"
try:
    model = joblib.load(os.path.join(diretorio_models, "modelo_irrigacao_knn.pkl"))
    scaler = joblib.load(os.path.join(diretorio_models, "scaler_irrigacao.pkl"))
    st.sidebar.success("Modelo e Scaler carregados com sucesso!")
except FileNotFoundError:
    st.sidebar.error(f"Erro: Modelo ou Scaler não encontrados em '{diretorio_models}/'. "
                     "Certifique-se de ter salvo eles usando o script anterior.")
    st.stop() # Interrompe a execução se o modelo não puder ser carregado
except Exception as e:
    st.sidebar.error(f"Erro ao carregar o modelo/scaler: {e}")
    st.stop()


# --- 1. Leitura de Dados CSV ---
# Defina o caminho para o arquivo CSV
# Se 'app.py' está em 'dashboard/' e 'console_print.csv' está em 'ml/', então '../ml/console_print.csv' está correto.
caminho_arquivo_csv = "../ml/console_print.csv"

try:
    # Use pandas para ler o CSV
    df = pd.read_csv(caminho_arquivo_csv)

    # Adicionar uma coluna de tempo para os gráficos de linha (simulando a coleta ao longo do tempo)
    # Se seu CSV já tiver uma coluna de timestamp, use-a. Caso contrário, esta linha criará uma.
    if 'timestamp' not in df.columns:
        df['timestamp'] = pd.to_datetime(pd.Series(range(len(df))), unit='s', origin='2025-06-20 08:00:00')
    else:
        # Tenta converter a coluna existente para datetime, se não for
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        # Remove linhas com timestamp inválido se 'coerce' for usado
        df.dropna(subset=['timestamp'], inplace=True)

    st.sidebar.success(f"Dados carregados com sucesso de '{caminho_arquivo_csv}'")

except FileNotFoundError:
    st.error(f"Arquivo CSV '{caminho_arquivo_csv}' não encontrado. Verifique o caminho.")
    st.stop()
except pd.errors.EmptyDataError:
    st.error(f"O arquivo CSV '{caminho_arquivo_csv}' está vazio.")
    st.stop()
except Exception as e:
    st.error(f"Ocorreu um erro inesperado ao carregar os dados CSV: {e}")
    st.stop()

# Verificar se o DataFrame não está vazio após o carregamento
if df.empty:
    st.warning("O DataFrame está vazio, o que pode afetar a exibição do dashboard.")
    st.stop()

# Definir as features que o modelo espera (deve ser o mesmo do treinamento)
model_features = ['temperatura', 'umidade', 'leitura_ldr', 'ph', 'potassio', 'fosforo']

# --- Restante do seu código Streamlit permanece igual ---
st.title("🌱 Dashboard de Monitoramento de Irrigação")
st.markdown("""
Este dashboard exibe os dados em tempo real (simulado) dos sensores e fornece uma sugestão de irrigação
baseada no modelo preditivo.
""")

# --- 3. Status Atual do Sistema e Sugestão do Modelo ---
st.subheader("Status de Irrigação & Sugestão do Modelo")

col_status_real, col_status_modelo = st.columns(2)

# --- Status Atual (Real) ---
with col_status_real:
    st.write("#### Status Real (Dados Recebidos)")
    if not df.empty: # Verifique se o DataFrame não está vazio
        status_real = df['irrigacao'].iloc[-1]
        if status_real == 'ATIVA':
            st.markdown(
                f"<h3 style='text-align: center; color: green;'>✅ ATIVA</h3>",
                unsafe_allow_html=True
            )
        elif status_real == 'INATIVA':
            st.markdown(
                f"<h3 style='text-align: center; color: red;'>❌ INATIVA</h3>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<h3 style='text-align: center; color: gray;'>❓ DESCONHECIDO</h3>",
                unsafe_allow_html=True
            )
        st.write(f"Última leitura: {df['timestamp'].iloc[-1].strftime('%H:%M:%S')}")
    else:
        st.write("Nenhum dado real disponível.")


# --- Modelo Preditivo (Baseada nos últimos 5 dados) ---
with col_status_modelo:
    st.write("#### Modelo Preditivo")

    # Adicionei uma verificação para garantir que todas as model_features existam no DataFrame
    missing_features = [f for f in model_features if f not in df.columns]
    if missing_features:
        st.error(f"Erro: As seguintes colunas necessárias para o modelo não foram encontradas no CSV: {', '.join(missing_features)}")
        st.write("Por favor, verifique se seu arquivo CSV contém todas as features esperadas pelo modelo.")
        st.stop() # Parar a execução se features essenciais estiverem faltando

    if not df.empty and len(df) >= 5: # Precisa de pelo menos 5 dados para pegar os últimos 5
        # Pegar os últimos 5 dados para as features que o modelo espera
        dados_para_prever = df[model_features].tail(5).mean().to_frame().T

        # Escalonar os dados para previsão usando o scaler carregado
        dados_para_prever_scaled = scaler.transform(dados_para_prever)

        # Fazer a previsão
        previsao_num = model.predict(dados_para_prever_scaled)
        sugestao_modelo = 'ATIVA' if previsao_num[0] == 1 else 'INATIVA'

        # Obter a confiança (probabilidade)
        probabilidades = model.predict_proba(dados_para_prever_scaled)
        prob_inativa = probabilidades[0][0] * 100
        prob_ativa = probabilidades[0][1] * 100

        if sugestao_modelo == 'ATIVA':
            st.markdown(
                f"<h3 style='text-align: center; color: blue;'>💡 ATIVAR</h3>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<h3 style='text-align: center; color: orange;'>💡 MANTER INATIVA</h3>",
                unsafe_allow_html=True
            )
        st.write(f"Confiança (ATIVA/INATIVA): {prob_ativa:.2f}% / {prob_inativa:.2f}%")
    else:
        st.write("Dados insuficientes para a sugestão do modelo (mínimo 5 registros).")


# --- Lógica de Alerta/Sugestão Adicional ---
st.markdown("---")
st.subheader("Análise e Ação Recomendada")

if not df.empty and len(df) >= 5: # Garante que há dados para comparação
    # status_real e sugestao_modelo já foram definidos acima
    if status_real == 'ATIVA' and sugestao_modelo == 'INATIVA':
        st.warning(
            "⚠️ **ALERTA: Irrigação ATIVA, mas o modelo sugere INATIVAR.** "
            "Pode haver desperdício de água ou excesso de umidade. "
            "Considere verificar as condições e desligar a irrigação."
        )
    elif status_real == 'INATIVA' and sugestao_modelo == 'ATIVA':
        st.info(
            "💧 **SUGESTÃO: Irrigação INATIVA, mas o modelo sugere ATIVAR.** "
            "As condições indicam que a irrigação pode ser necessária para a saúde da planta. "
            "Monitore os dados e considere ativar a irrigação."
        )
    elif status_real == sugestao_modelo:
        st.success(
            "✅ **STATUS OK:** A irrigação atual está alinhada com a sugestão do modelo."
        )
else:
    st.write("Aguardando dados suficientes para análise de recomendação.")


# --- 4. Gráficos de Linha para Variáveis Contínuas ---
st.subheader("Tendências dos Dados dos Sensores")

line_chart_cols = ['temperatura', 'umidade', 'ph', 'leitura_ldr']
col_chart1, col_chart2 = st.columns(2)

if not df.empty:
    with col_chart1:
        st.write("#### Temperatura (°C)")
        fig_temp = px.line(df, x='timestamp', y='temperatura', title='Temperatura ao Longo do Tempo',
                           labels={'temperatura': 'Temperatura (°C)', 'timestamp': 'Hora'},
                           template='plotly_white')
        st.plotly_chart(fig_temp, use_container_width=True)

    with col_chart2:
        st.write("#### Umidade (%)")
        fig_umid = px.line(df, x='timestamp', y='umidade', title='Umidade ao Longo do Tempo',
                           labels={'umidade': 'Umidade (%)', 'timestamp': 'Hora'},
                           template='plotly_white')
        st.plotly_chart(fig_umid, use_container_width=True)

    col_chart3, col_chart4 = st.columns(2)

    with col_chart3:
        st.write("#### Nível de pH")
        fig_ph = px.line(df, x='timestamp', y='ph', title='Nível de pH ao Longo do Tempo',
                         labels={'ph': 'pH', 'timestamp': 'Hora'},
                         template='plotly_white')
        st.plotly_chart(fig_ph, use_container_width=True)

    with col_chart4:
        st.write("#### Luminosidade (Leitura LDR)")
        fig_ldr = px.line(df, x='timestamp', y='leitura_ldr', title='Luminosidade ao Longo do Tempo (LDR)',
                          labels={'leitura_ldr': 'Leitura LDR', 'timestamp': 'Hora'},
                          template='plotly_white')
        st.plotly_chart(fig_ldr, use_container_width=True)
else:
    st.info("Nenhum dado disponível para exibir gráficos de tendência.")


# --- 5. Histogramas para Nutrientes ---
st.subheader("Distribuição de Nutrientes no Solo")

hist_cols = ['potassio', 'fosforo']
col_hist1, col_hist2 = st.columns(2)

if not df.empty:
    with col_hist1:
        st.write("#### Fósforo")
        fig_fosforo = px.histogram(df, x='fosforo', nbins=10, title='Distribuição de Fósforo',
                                   labels={'fosforo': 'Fósforo (PPM)'},
                                   template='plotly_white')
        st.plotly_chart(fig_fosforo, use_container_width=True)

    with col_hist2:
        st.write("#### Potássio")
        fig_potassio = px.histogram(df, x='potassio', nbins=10, title='Distribuição de Potássio',
                                    labels={'potassio': 'Potássio (PPM)'},
                                    template='plotly_white')
        st.plotly_chart(fig_potassio, use_container_width=True)
else:
    st.info("Nenhum dado disponível para exibir histogramas.")


# --- 6. Visualização dos Dados Brutos (Opcional) ---
st.subheader("Dados Brutos do Sensor")
if not df.empty:
    st.dataframe(df)
else:
    st.info("Nenhum dado bruto disponível.")