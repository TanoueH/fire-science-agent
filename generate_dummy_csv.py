import os
import csv
from datetime import datetime, timedelta
import random

# Caminho padrão do CSV
DATA_DIR = "data"
CSV_PATH = os.path.join(DATA_DIR, "sensores.csv")

# Garante que a pasta 'data/' exista
os.makedirs(DATA_DIR, exist_ok=True)

# Configuração dos sensores simulados
sensores = [1, 2, 3]
num_registros = 12  # 12 linhas de amostra (~1 hora de dados)
inicio = datetime(2025, 11, 9, 10, 0, 0)

# Geração de dados aleatórios simulados
linhas = []
for i in range(num_registros):
    timestamp = (inicio + timedelta(minutes=5 * i)).isoformat() + "Z"
    for sensor_id in sensores:
        temperatura = round(random.uniform(24.5, 27.0), 1)
        co = round(random.uniform(7.5, 8.5), 2)
        velocidade_ar = round(random.uniform(1.0, 1.5), 2)
        umidade = round(random.uniform(65.0, 70.0), 1)
        linhas.append([timestamp, sensor_id, temperatura, co, velocidade_ar, umidade])

# Escreve o CSV
with open(CSV_PATH, mode="w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "sensor_id", "temperatura", "co", "velocidade_ar", "umidade"])
    writer.writerows(linhas)

# Mostra resultado
print(f"✅ CSV de teste gerado com sucesso: {os.path.abspath(CSV_PATH)}")
print("Prévia das 5 primeiras linhas:")
with open(CSV_PATH, "r") as f:
    for i, linha in enumerate(f.readlines()[:6]):
        print(linha.strip())
