import streamlit as st
import requests
import pandas as pd
from scipy.stats import poisson
import math

st.set_page_config(page_title="TandaBet Global API", layout="wide")
st.title("🌍 Poisson Football Analyzer – Multi‑Ligas")

API_KEY = "test85g57"  # coloque sua API Key da FootyStats

# IDs das 20 ligas principais
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
    "A-League": 235
}

seasons = {"2025": "2025", "2026": "2026"}

liga_selecionada = st.selectbox("Escolha a liga", list(liga_ids.keys()))
season_selected = st.selectbox("Escolha a temporada", list(seasons.keys()))
liga_id = liga_ids[liga_selecionada]

@st.cache_data(ttl=600)
def buscar_jogos(api_key, league_id, season):
    url = f"https://footystats.org/api/fixtures?key={api_key}&league={league_id}&season={season}"
    res = requests.get(url)
    if res.status_code != 200:
        st.error("Erro ao buscar jogos")
        return []
    return res.json().get("fixtures", [])

jogos = buscar_jogos(API_KEY, liga_id, season_selected)

if len(jogos) == 0:
    st.write("Nenhum jogo encontrado para essa liga/temporada")
else:
    jogo_choices = [f"{j['home_team']} x {j['away_team']}" for j in jogos]
    escolhido = st.selectbox("Selecione o jogo", jogo_choices)
    jogo_obj = next(j for j in jogos if f"{j['home_team']} x {j['away_team']}" == escolhido)

    def stats_time(team_id, api_key):
        url = f"https://footystats.org/api/team?key={api_key}&team_id={team_id}&season={season_selected}"
        res = requests.get(url)
        return res.json().get("team", {})

    home_stats = stats_time(jogo_obj["home_id"], API_KEY)
    away_stats = stats_time(jogo_obj["away_id"], API_KEY)

    ataque_casa = home_stats.get("attack_home_avg", 1.5)
    defesa_casa = home_stats.get("defense_home_avg", 1.2)
    ataque_fora = away_stats.get("attack_away_avg", 1.4)
    defesa_fora = away_stats.get("defense_away_avg", 1.3)

    media_liga = 2.6
    lambda_c = (ataque_casa * defesa_fora) / media_liga
    lambda_f = (ataque_fora * defesa_casa) / media_liga
    lambda_total = lambda_c + lambda_f
    lambda_ht = lambda_total * 0.45

    over25 = 1 - sum(poisson.pmf(i, lambda_total) for i in range(3))
    ambas = 1 - poisson.pmf(0, lambda_c) - poisson.pmf(0, lambda_f) + poisson.pmf(0, lambda_c)*poisson.pmf(0, lambda_f)
    over05_ht = 1 - poisson.pmf(0, lambda_ht)

    ic_min = lambda_total - 1.96 * math.sqrt(lambda_total)
    ic_max = lambda_total + 1.96 * math.sqrt(lambda_total)

    st.markdown("## Probabilidade dos Mercados")
    st.write(f"Over 2.5: {over25*100:.2f}%")
    st.write(f"Ambas Marcam: {ambas*100:.2f}%")
    st.write(f"Over 0.5 HT: {over05_ht*100:.2f}%")

    st.markdown("## Intervalo de Confiança (95%)")
    st.write(f"{ic_min:.2f} a {ic_max:.2f} gols esperados")

    max_gols = 5
    placares = []
    for i in range(max_gols+1):
        for j in range(max_gols+1):
            prob = poisson.pmf(i, lambda_c) * poisson.pmf(j, lambda_f)
            placares.append((f"{i}x{j}", prob))

    df = pd.DataFrame(placares, columns=["Placar", "Probabilidade"]).sort_values(by="Probabilidade", ascending=False)
    st.markdown("## Top 10 Placar Exato")
    st.dataframe(df.head(10))
