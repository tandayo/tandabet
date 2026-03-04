import streamlit as st
import requests
import pandas as pd
from scipy.stats import poisson
import math

st.set_page_config(page_title="TandaBet Global API", layout="wide")
st.title("🌍 Poisson Football Analyzer – Multi‑Ligas")

API_KEY = "test85g57"  # coloque sua API Key
# Coloque os IDs que obteve no painel FootyStats aqui:
liga_ids = {
    "Premier League": 39,
    "La Liga": 140,
    "Serie A": 135,
    "Bundesliga": 78,
    "Ligue 1": 61,
    "Brasileirão": 71,
    "Primeira Liga": 94,
    "Eredivisie": 88,
    "MLS": 253,
    "Liga MX": 262,
    "Argentina Primera": 128,
    "J1 League": 102,
    "Chinese Super League": 243,
    "Saudi Pro League": 315,
    "Süper Lig": 203,
    "Belgian Pro League": 88,
    "Allsvenskan": 278,
    "Russian Premier": 63,
    "Scottish Premiership": 261,
    "A-Ligue (Aus)": 235
}

seasons = {"2025": "2025", "2026": "2026"}  # se quiser opções de temporada

liga_selecionada = st.selectbox("Escolha a liga", list(liga_ids.keys()))
season_selected = st.selectbox("Escolha a temporada", list(seasons.keys()))

liga_id = liga_ids[liga_selecionada]

# ⚽ Buscar jogos da liga selecionada
@st.cache_data(ttl=600)
def buscar_jogos_footystats(api_key, league_id, season):
    url = f"https://footystats.org/api/fixtures?key={api_key}&league={league_id}&season={season}"
    res = requests.get(url)
    if res.status_code != 200:
        st.error("Erro ao buscar jogos")
        return []
    return res.json().get("fixtures", [])

jogos = buscar_jogos_footystats(API_KEY, liga_id, season_selected)

if len(jogos) == 0:
    st.write("Nenhum jogo encontrado para essa liga/temporada")
else:
    jogo_choices = [f"{j['home_team']} x {j['away_team']}" for j in jogos]
    escolhido = st.selectbox("Selecione o jogo", jogo_choices)
   jogo_obj = next(j for j in jogos if f"{j['home_team']} x {j['away_team']}" == escolhido)
    # ⚽ Buscar estatísticas de cada time
    def stats_time(id, api_key):
        url = f\"https://footystats.org/api/team?key={api_key}&team_id={id}&season={season_selected}\"
        r = requests.get(url)
        return r.json().get("team", {})

    home_stats = stats_time(jogo_obj["home_id"], API_KEY)
    away_stats = stats_time(jogo_obj["away_id"], API_KEY)

    # Exemplo de métricas para Poisson
    ataque_casa = home_stats.get("attack_home_avg", 1.5)
    defesa_casa = home_stats.get("defense_home_avg", 1.2)
    ataque_fora = away_stats.get("attack_away_avg", 1.4)
    defesa_fora = away_stats.get("defense_away_avg", 1.3)

    media_liga = 2.6
    lambda_c = (ataque_casa * defesa_fora)/media_liga
    lambda_f = (ataque_fora * defesa_casa)/media_liga

    over25 = 1 - sum(poisson.pmf(i, lambda_c+lambda_f) for i in range(3))
    ambas = 1 - poisson.pmf(0, lambda_c) - poisson.pmf(0, lambda_f) + poisson.pmf(0, lambda_c)*poisson.pmf(0, lambda_f)
    over05_ht = 1 - poisson.pmf(0, (lambda_c+lambda_f)*0.45)

    st.markdown("## Probabilidade bons mercados")
    st.write(f"Over 2.5: {over25*100:.2f}%")
    st.write(f"Both Teams to Score: {ambas*100:.2f}%")
    st.write(f"Over 0.5 HT: {over05_ht*100:.2f}%")
