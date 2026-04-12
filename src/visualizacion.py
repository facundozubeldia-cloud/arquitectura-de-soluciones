import sqlite3
import os
import tweepy
import yaml
import random

# Rutas
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'data', 'sentimientos.db')
config_path = os.path.join(base_dir, 'src', 'config.yaml')

bearer_token = os.getenv('X_BEARER_TOKEN')

# 1. URL del Tweet a analizar (Esto lo cambiás por el que pida el profe)
url_tweet = "https://x.com/madorni/status/1844715457313239401"
tweet_id = url_tweet.split('/')[-1]

# 2. Conectar y asegurar que la columna 'texto' exista
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tweets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tema TEXT,
        date TEXT,
        sentimiento TEXT,
        texto TEXT
    )
''')

try:
    client = tweepy.Client(bearer_token=bearer_token)
    response = client.get_tweet(id=tweet_id, tweet_fields=['created_at', 'text'])
    tweet = response.data

    if tweet:
        fecha = tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')
        # Aquí va el análisis (simulado o con pysentimiento)
        sent_simulado = random.choice(['Positivo', 'Neutral', 'Negativo'])
        
        cursor.execute("INSERT INTO tweets (tema, date, sentimiento, texto) VALUES (?, ?, ?, ?)", 
                       (f"Individual: {tweet_id}", fecha, sent_simulado, tweet.text))
        conn.commit()
        print(f"✅ Tweet analizado con éxito: {tweet.text[:50]}...")
    else:
        print("❌ No se encontró el tweet.")
finally:
    conn.close()