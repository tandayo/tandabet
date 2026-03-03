import streamlit as st
import numpy as np
import pandas as pd
from scipy.stats import poisson
import math
import streamlit as st
import pandas as pd
from scipy.stats import poisson
import math

# =============================
# CONFIGURAÇÃO PÁGINA
# =============================
st.set_page_config(
    page_title="TandaBet Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("⚽ Poisson Football Analyzer")

# =============================
# DADOS PRONTOS DOS CLUBES
# =============================
# Aqui você já tem os números de ataque/defesa de cada time
clubes = {
    "Corinthians": {"ataque_casa": 1.8, "defesa_casa": 1.0, "ataque_fora": 1.2, "defesa_fora": 1.3},
    "São Paulo": {"ataque_casa": 1.6, "defesa_casa": 1.2, "ataque_fora": 1.3, "defesa_fora": 1.4},
    "Palmeiras": {"ataque_casa": 1.9, "defesa_casa": 0.9, "ataque_fora": 1.5, "defesa_fora": 1.2},
    "Flamengo": {"ataque_casa": 2.0, "defesa_casa": 1.1, "ataque_fora": 1.6, "defesa_fora": 1.3},
}

# =============================
# SELEÇÃO DO JOGO
# =============================
time_casa = st.selectbox("Time Casa", list(clubes.keys()))
time_fora = st.selectbox("Time Fora", list(clubes.keys()))

if time_casa == time_fora:
    st.warning("Escolha times diferentes!")
else:
    dados_casa = clubes[time_casa]
    dados_fora = clubes[time_fora]

    media_liga = 2.6

    # =============================
    # CÁLCULO LAMBDA
    # =============================
    lambda_casa = (dados_casa["ataque_casa"] * dados_fora["defesa_fora"]) / media_liga
    lambda_fora = (dados_fora["ataque_fora"] * dados_casa["defesa_casa"]) / media_liga
    lambda_total = lambda_casa + lambda_fora
    lambda_ht = lambda_total * 0.45

    # =============================
    # PROBABILIDADES
    # =============================
    over25 = 1 - sum(poisson.pmf(i, lambda_total) for i in range(3))
    ambas = 1 - poisson.pmf(0, lambda_casa) - poisson.pmf(0, lambda_fora) + poisson.pmf(0, lambda_casa)*poisson.pmf(0, lambda_fora)
    over05_ht = 1 - poisson.pmf(0, lambda_ht)

    # =============================
    # INTERVALO DE CONFIANÇA
    # =============================
    ic_min = lambda_total - 1.96 * math.sqrt(lambda_total)
    ic_max = lambda_total + 1.96 * math.sqrt(lambda_total)

    # =============================
    # VALOR ESPERADO
    # =============================
    odd_over25 = 1.9
    odd_ambas = 1.85
    odd_over05ht = 1.35

    ev_over25 = (over25 * odd_over25) - 1
    ev_ambas = (ambas * odd_ambas) - 1
    ev_ht = (over05_ht * odd_over05ht) - 1

    # =============================
    # PLACARES EXATOS
    # =============================
    max_gols = 5
    placares = []
    for i in range(max_gols + 1):
        for j in range(max_gols + 1):
            prob = poisson.pmf(i, lambda_casa) * poisson.pmf(j, lambda_fora)
            placares.append((f"{i}x{j}", prob))
    df = pd.DataFrame(placares, columns=["Placar", "Probabilidade"]).sort_values(by="Probabilidade", ascending=False)

    # =============================
    # EXIBIÇÃO
    # =============================
    col1, col2, col3 = st.columns(3)
    col1.metric("λ Casa", round(lambda_casa, 2))
    col2.metric("λ Fora", round(lambda_fora, 2))
    col3.metric("λ Total", round(lambda_total, 2))

    st.markdown("### 📈 Intervalo de Confiança (95%)")
    st.write(f"{round(ic_min,2)} a {round(ic_max,2)} gols esperados")

    st.markdown("## 🎯 Probabilidades dos Mercados")
    col4, col5, col6 = st.columns(3)
    col4.metric("Over 2.5", f"{round(over25*100,2)}%")
    col5.metric("Ambas Marcam", f"{round(ambas*100,2)}%")
    col6.metric("Over 0.5 HT", f"{round(over05_ht*100,2)}%")

    st.markdown("## 💰 Valor Esperado (EV)")
    col7, col8, col9 = st.columns(3)
    col7.metric("EV Over 2.5", round(ev_over25, 3))
    col8.metric("EV Ambas", round(ev_ambas, 3))
    col9.metric("EV Over 0.5 HT", round(ev_ht, 3))

    st.markdown("## 📊 Top 10 Placar Exato")
    st.dataframe(df.head(10))

    st.markdown("---")
    st.caption("Modelo baseado na Distribuição de Poisson para análise estatística de futebol.")

st.set_page_config(page_title="Poisson Football Pro", layout="wide")
st.title("⚽ Poisson Football Analyzer")

st.sidebar.header("📊 Dados do Jogo")

ataque_casa = st.sidebar.number_input("Média Gols Casa", min_value=0.0, value=1.8)
defesa_casa = st.sidebar.number_input("Média Sofridos Casa", min_value=0.0, value=1.1)

ataque_fora = st.sidebar.number_input("Média Gols Fora", min_value=0.0, value=1.4)
defesa_fora = st.sidebar.number_input("Média Sofridos Fora", min_value=0.0, value=1.6)

media_liga = st.sidebar.number_input("Média Gols Liga", min_value=0.1, value=2.6)

odd_over25 = st.sidebar.number_input("Odd Over 2.5", min_value=1.01, value=1.90)
odd_ambas = st.sidebar.number_input("Odd Ambas Marcam", min_value=1.01, value=1.85)
odd_over05ht = st.sidebar.number_input("Odd Over 0.5 HT", min_value=1.01, value=1.35)

lambda_casa = (ataque_casa * defesa_fora) / media_liga
lambda_fora = (ataque_fora * defesa_casa) / media_liga
lambda_total = lambda_casa + lambda_fora
lambda_ht = lambda_total * 0.45

over25 = 1 - sum(poisson.pmf(i, lambda_total) for i in range(3))

ambas = (
    1
    - poisson.pmf(0, lambda_casa)
    - poisson.pmf(0, lambda_fora)
    + poisson.pmf(0, lambda_casa) * poisson.pmf(0, lambda_fora)
)

over05_ht = 1 - poisson.pmf(0, lambda_ht)

ic_min = lambda_total - 1.96 * math.sqrt(lambda_total)
ic_max = lambda_total + 1.96 * math.sqrt(lambda_total)

ev_over25 = (over25 * odd_over25) - 1
ev_ambas = (ambas * odd_ambas) - 1
ev_ht = (over05_ht * odd_over05ht) - 1

max_gols = 5
placares = []

for i in range(max_gols + 1):
    for j in range(max_gols + 1):
        prob = poisson.pmf(i, lambda_casa) * poisson.pmf(j, lambda_fora)
        placares.append((f"{i}x{j}", prob))

df = pd.DataFrame(placares, columns=["Placar", "Probabilidade"])
df = df.sort_values(by="Probabilidade", ascending=False)

col1, col2, col3 = st.columns(3)
col1.metric("λ Casa", round(lambda_casa, 2))
col2.metric("λ Fora", round(lambda_fora, 2))
col3.metric("λ Total", round(lambda_total, 2))

st.markdown("### 📈 Intervalo de Confiança (95%)")
st.write(f"{round(ic_min,2)} a {round(ic_max,2)} gols esperados")

st.markdown("## 🎯 Probabilidades dos Mercados")

col4, col5, col6 = st.columns(3)
col4.metric("Over 2.5", f"{round(over25*100,2)}%")
col5.metric("Ambas Marcam", f"{round(ambas*100,2)}%")
col6.metric("Over 0.5 HT", f"{round(over05_ht*100,2)}%")

st.markdown("## 💰 Valor Esperado (EV)")

col7, col8, col9 = st.columns(3)
col7.metric("EV Over 2.5", round(ev_over25, 3))
col8.metric("EV Ambas", round(ev_ambas, 3))
col9.metric("EV Over 0.5 HT", round(ev_ht, 3))

st.markdown("## 📊 Top 10 Placar Exato")
st.dataframe(df.head(10))

st.markdown("---")
st.caption("Modelo baseado na Distribuição de Poisson para análise estatística de futebol.")
