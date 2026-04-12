import sqlite3
import yaml
import os
import tweepy
import random
from datetime import datetime

# 1. Rutas
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'data', 'sentimientos.db')
config_path = os.path.join(base_dir, 'src', 'config.yaml')

# 2. Leer Configuración y Token
bearer_token = os.getenv('X_BEARER_TOKEN')

with open(config_path, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

# --- CAMBIO AQUÍ: Apuntamos a la nueva estructura del YAML ---
tema = config['analisis_masivo']['query'] 
max_res = config['analisis_masivo'].get('max_results', 10) # Usa 10 por defecto si no existe

# 3. Conectar a Base de Datos (Agregamos columna 'texto' por si acaso)
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

# 4. Ingesta desde la API de X
print(f"Buscando posts reales sobre: {tema}...")
try:
    client = tweepy.Client(bearer_token=bearer_token)
    query_busqueda = f"{tema} -is:retweet lang:es"
    
    # Usamos max_res desde el config
    tweets = client.search_recent_tweets(query=query_busqueda, max_results=max_res, tweet_fields=['created_at', 'text'])

    if tweets.data:
        sentimientos_lista = ['Positivo', 'Neutral', 'Negativo']
        for tweet in tweets.data:
            fecha = tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')
            # Simulamos análisis de sentimiento
            sent_simulado = random.choices(sentimientos_lista, weights=[0.3, 0.4, 0.3])[0]
            
            # Guardamos incluyendo el texto del tweet
            cursor.execute("INSERT INTO tweets (tema, date, sentimiento, texto) VALUES (?, ?, ?, ?)", 
                           (tema, fecha, sent_simulado, tweet.text))
            
        print(f"✅ Se ingestaron {len(tweets.data)} posts de X.")
    else:
        print("No se encontraron resultados recientes.")

except Exception as e:
    print(f"❌ Error API: {e}")

conn.commit()
conn.close()