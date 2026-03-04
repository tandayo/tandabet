import streamlit as st
import pandas as pd
from scipy.stats import poisson
import math
import streamlit as st
import requests
import pandas as pd
from scipy.stats import poisson
import math

# =============================
# Configuração da página
# =============================
st.set_page_config(
    page_title="TandaBet Global - FootyStats",
    page_icon="⚽",
    layout="wide"
)
st.title("⚽ Poisson Football Analyzer – FootyStats")

# =============================
# Configuração API
# =============================
API_KEY = "SUA_CHAVE_API"  # substitua aqui
LEAGUE_ID = "INSIRA_AQUI_O_ID_DA_LIGA"  # FootyStats liga específica

# =============================
# Função para buscar jogos do dia
# =============================
@st.cache_data(ttl=600)
def buscar_jogos(api_key, league_id):
    url = f"https://footystats.org/api/fixtures?key={api_key}&league={league_id}"
    res = requests.get(url)
    if res.status_code != 200:
        st.error("Erro ao buscar dados da API.")
        return []
    return res.json().get("fixtures", [])

# =============================
# Função para buscar estatísticas do time
# =============================
@st.cache_data(ttl=600)
def buscar_estatisticas_time(team_id, api_key):
    url = f"https://footystats.org/api/team?key={api_key}&team_id={team_id}"
    res = requests.get(url)
    if res.status_code != 200:
        return {}
    return res.json().get("team", {})

# =============================
# Seleção de jogos
# =============================
st.markdown("### Jogos do dia")
jogos = buscar_jogos(API_KEY, LEAGUE_ID)

if len(jogos) == 0:
    st.write("Nenhum jogo encontrado.")
else:
    jogo_selecionado = st.selectbox(
        "Escolha um jogo",
        [f"{j['home_team']} x {j['away_team']}" for j in jogos]
    )
    jogo_obj = next(j for j in jogos if f"{j['home_team']} x {j['away_team']}" == jogo_selecionado)

    # =============================
    # Buscar estatísticas
    # =============================
    home_stats = buscar_estatisticas_time(jogo_obj["home_id"], API_KEY)
    away_stats = buscar_estatisticas_time(jogo_obj["away_id"], API_KEY)

    # Valores aproximados para Poisson
    ataque_casa = home_stats.get("attack_home_avg", 1.5)
    defesa_casa = home_stats.get("defense_home_avg", 1.2)
    ataque_fora = away_stats.get("attack_away_avg", 1.4)
    defesa_fora = away_stats.get("defense_away_avg", 1.3)

    media_liga = 2.6

    # =============================
    # Calcular λ
    # =============================
    lambda_casa = (ataque_casa * defesa_fora) / media_liga
    lambda_fora = (ataque_fora * defesa_casa) / media_liga
    lambda_total = lambda_casa + lambda_fora
    lambda_ht = lambda_total * 0.45

    # =============================
    # Probabilidades de mercados
    # =============================
    over25 = 1 - sum(poisson.pmf(i, lambda_total) for i in range(3))
    ambas = 1 - poisson.pmf(0, lambda_casa) - poisson.pmf(0, lambda_fora) + poisson.pmf(0, lambda_casa)*poisson.pmf(0, lambda_fora)
    over05_ht = 1 - poisson.pmf(0, lambda_ht)

    # =============================
    # Intervalo de confiança
    # =============================
    ic_min = lambda_total - 1.96 * math.sqrt(lambda_total)
    ic_max = lambda_total + 1.96 * math.sqrt(lambda_total)

    # =============================
    # Valor Esperado (EV) - exemplo de odds
    # =============================
    odd_over25 = 1.9
    odd_ambas = 1.85
    odd_over05ht = 1.35

    ev_over25 = (over25 * odd_over25) - 1
    ev_ambas = (ambas * odd_ambas) - 1
    ev_ht = (over05_ht * odd_over05ht) - 1

    # =============================
    # Placar exato
    # =============================
    max_gols = 5
    placares = []
    for i in range(max_gols + 1):
        for j in range(max_gols + 1):
            prob = poisson.pmf(i, lambda_casa) * poisson.pmf(j, lambda_fora)
            placares.append((f"{i}x{j}", prob))
    df = pd.DataFrame(placares, columns=["Placar", "Probabilidade"]).sort_values(by="Probabilidade", ascending=False)

    # =============================
    # Exibição
    # =============================
    col1, col2, col3 = st.columns(3)
    col1.metric("λ Casa", round(lambda_casa,2))
    col2.metric("λ Fora", round(lambda_fora,2))
    col3.metric("λ Total", round(lambda_total,2))

    st.markdown("### Intervalo de Confiança (95%)")
    st.write(f"{round(ic_min,2)} a {round(ic_max,2)} gols esperados")

    st.markdown("## Probabilidades dos Mercados")
    col4, col5, col6 = st.columns(3)
    col4.metric("Over 2.5", f"{round(over25*100,2)}%")
    col5.metric("Ambas Marcam", f"{round(ambas*100,2)}%")
    col6.metric("Over 0.5 HT", f"{round(over05_ht*100,2)}%")

    st.markdown("## Valor Esperado (EV)")
    col7, col8, col9 = st.columns(3)
    col7.metric("EV Over 2.5", round(ev_over25,3))
    col8.metric("EV Ambas", round(ev_ambas,3))
    col9.metric("EV Over 0.5 HT", round(ev_ht,3))

    st.markdown("## Top 10 Placar Exato")
    st.dataframe(df.head(10))

    st.markdown("---")
    st.caption("Modelo baseado na Distribuição de Poisson com dados reais da FootyStats API.")

API_KEY = "test85g57"  # aqui você coloca a chave que pegou no site
# =============================
# Configuração da página
# =============================
st.set_page_config(
    page_title="TandaBet Global",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("⚽ Poisson Football Analyzer – Global")

# =============================
# Dados dos clubes (simplificado)
# =============================
# Exemplo de clubes de várias ligas (Europa, América, Ásia e Austrália)
clubes = {
    # Europa
    "Manchester United": {"ataque_casa":1.8,"defesa_casa":0.9,"ataque_fora":1.5,"defesa_fora":1.2},
    "Liverpool": {"ataque_casa":2.0,"defesa_casa":0.8,"ataque_fora":1.7,"defesa_fora":1.1},
    "Real Madrid": {"ataque_casa":1.9,"defesa_casa":0.9,"ataque_fora":1.6,"defesa_fora":1.2},
    "Barcelona": {"ataque_casa":1.8,"defesa_casa":1.0,"ataque_fora":1.5,"defesa_fora":1.3},

    # América do Sul
    "Flamengo": {"ataque_casa":2.0,"defesa_casa":0.9,"ataque_fora":1.7,"defesa_fora":1.1},
    "Palmeiras": {"ataque_casa":2.0,"defesa_casa":0.9,"ataque_fora":1.7,"defesa_fora":1.1},
    "Corinthians": {"ataque_casa":1.8,"defesa_casa":1.0,"ataque_fora":1.2,"defesa_fora":1.3},

    # Ásia
    "Al Hilal": {"ataque_casa":1.6,"defesa_casa":1.0,"ataque_fora":1.3,"defesa_fora":1.2},
    "Urawa Reds": {"ataque_casa":1.5,"defesa_casa":1.1,"ataque_fora":1.2,"defesa_fora":1.3},

    # Austrália
    "Sydney FC": {"ataque_casa":1.7,"defesa_casa":1.1,"ataque_fora":1.5,"defesa_fora":1.3},
    "Melbourne City": {"ataque_casa":1.8,"defesa_casa":1.0,"ataque_fora":1.6,"defesa_fora":1.2}
}

# =============================
# Seleção do jogo
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
    # Calculo λ
    # =============================
    lambda_casa = (dados_casa["ataque_casa"] * dados_fora["defesa_fora"]) / media_liga
    lambda_fora = (dados_fora["ataque_fora"] * dados_casa["defesa_casa"]) / media_liga
    lambda_total = lambda_casa + lambda_fora
    lambda_ht = lambda_total * 0.45

    # =============================
    # Probabilidades de mercados
    # =============================
    over25 = 1 - sum(poisson.pmf(i, lambda_total) for i in range(3))
    ambas = 1 - poisson.pmf(0, lambda_casa) - poisson.pmf(0, lambda_fora) + poisson.pmf(0, lambda_casa)*poisson.pmf(0, lambda_fora)
    over05_ht = 1 - poisson.pmf(0, lambda_ht)

    # =============================
    # Intervalo de confiança
    # =============================
    ic_min = lambda_total - 1.96 * math.sqrt(lambda_total)
    ic_max = lambda_total + 1.96 * math.sqrt(lambda_total)

    # =============================
    # Valor Esperado (EV)
    # =============================
    odd_over25 = 1.9
    odd_ambas = 1.85
    odd_over05ht = 1.35

    ev_over25 = (over25 * odd_over25) - 1
    ev_ambas = (ambas * odd_ambas) - 1
    ev_ht = (over05_ht * odd_over05ht) - 1

    # =============================
    # Placar exato
    # =============================
    max_gols = 5
    placares = []
    for i in range(max_gols + 1):
        for j in range(max_gols + 1):
            prob = poisson.pmf(i, lambda_casa) * poisson.pmf(j, lambda_fora)
            placares.append((f"{i}x{j}", prob))
    df = pd.DataFrame(placares, columns=["Placar", "Probabilidade"]).sort_values(by="Probabilidade", ascending=False)

    # =============================
    # Exibição
    # =============================
    col1, col2, col3 = st.columns(3)
    col1.metric("λ Casa", round(lambda_casa,2))
    col2.metric("λ Fora", round(lambda_fora,2))
    col3.metric("λ Total", round(lambda_total,2))

    st.markdown("### Intervalo de Confiança (95%)")
    st.write(f"{round(ic_min,2)} a {round(ic_max,2)} gols esperados")

    st.markdown("## Probabilidades dos Mercados")
    col4, col5, col6 = st.columns(3)
    col4.metric("Over 2.5", f"{round(over25*100,2)}%")
    col5.metric("Ambas Marcam", f"{round(ambas*100,2)}%")
    col6.metric("Over 0.5 HT", f"{round(over05_ht*100,2)}%")

    st.markdown("## Valor Esperado (EV)")
    col7, col8, col9 = st.columns(3)
    col7.metric("EV Over 2.5", round(ev_over25,3))
    col8.metric("EV Ambas", round(ev_ambas,3))
    col9.metric("EV Over 0.5 HT", round(ev_ht,3))

    st.markdown("## Top 10 Placar Exato")
    st.dataframe(df.head(10))

    st.markdown("---")
    st.caption("Modelo baseado na Distribuição de Poisson para análise estatística de futebol.")
