import numpy as np
import pandas as pd
from scipy.stats import poisson

# ===== ENTRADAS =====
ataque_casa = 1.8
defesa_casa = 1.1

ataque_fora = 1.4
defesa_fora = 1.6

media_liga = 2.6

# ===== CALCULO LAMBDA =====
lambda_casa = (ataque_casa * defesa_fora) / media_liga
lambda_fora = (ataque_fora * defesa_casa) / media_liga

lambda_total = lambda_casa + lambda_fora

lambda_casa_ht = lambda_casa * 0.45
lambda_fora_ht = lambda_fora * 0.45

# ===== MATRIZ DE PLACARES =====
max_gols = 5

placares = []

for i in range(max_gols+1):
    for j in range(max_gols+1):
        prob = poisson.pmf(i, lambda_casa) * poisson.pmf(j, lambda_fora)
        placares.append((f"{i}x{j}", prob))

df = pd.DataFrame(placares, columns=["Placar", "Probabilidade"])
df = df.sort_values(by="Probabilidade", ascending=False)

# ===== MERCADOS =====

# Over 2.5
over25 = 1 - sum(
    poisson.pmf(i, lambda_total)
    for i in range(3)
)

# Ambas Marcam
ambas = 1 - poisson.pmf(0, lambda_casa) - poisson.pmf(0, lambda_fora) + \
        poisson.pmf(0, lambda_casa)*poisson.pmf(0, lambda_fora)

# Over 0.5 HT
over05_ht = 1 - poisson.pmf(0, lambda_casa_ht + lambda_fora_ht)

print("Lambda Casa:", round(lambda_casa,2))
print("Lambda Fora:", round(lambda_fora,2))
print("Over 2.5:", round(over25*100,2), "%")
print("Ambas Marcam:", round(ambas*100,2), "%")
print("Over 0.5 HT:", round(over05_ht*100,2), "%")
print("\nTop 10 Placar Exato:")
print(df.head(10))
import math

ic_min = lambda_total - 1.96 * math.sqrt(lambda_total)
ic_max = lambda_total + 1.96 * math.sqrt(lambda_total)

print("Intervalo 95%:", round(ic_min,2), "a", round(ic_max,2))
{
  "lambda_casa": 1.65,
  "lambda_fora": 1.21,
  "over_2_5": 0.63,
  "ambas_marcam": 0.58,
  "over_0_5_ht": 0.72,
  "placar_mais_provavel": "1x1"
}
