import tweepy, sqlite3, yaml, os, random, re
from datetime import datetime

# 1. Configuración de Rutas
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'data', 'sentimientos.db')
config_path = os.path.join(base_dir, 'src', 'config.yaml')

# 2. Carga de Credenciales y Config
bearer_token = os.getenv('X_BEARER_TOKEN')

with open(config_path, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

def obtener_detalles_y_respuestas(url):
    # Extraer ID con manejo de error por si la URL está mal
    match = re.search(r'status/(\d+)', url)
    if not match:
        return []
    
    tweet_id = match.group(1)
    client = tweepy.Client(bearer_token=bearer_token)
    
    # 1. Traer el Tweet Original
    t_res = client.get_tweet(id=tweet_id, tweet_fields=['text', 'created_at'])
    
    # 2. Traer Respuestas (Usando el conversation_id de la API v2)
    query = f"conversation_id:{tweet_id} -is:retweet lang:es"
    respuestas = client.search_recent_tweets(query=query, max_results=50, tweet_fields=['text', 'created_at'])
    
    data_to_save = []
    sentimientos_lista = ['Positivo', 'Neutral', 'Negativo']

    # Guardar original
    if t_res.data:
        fecha = t_res.data.created_at.strftime('%Y-%m-%d %H:%M:%S')
        data_to_save.append((f"Original:{tweet_id}", fecha, random.choice(sentimientos_lista), t_res.data.text))
    
    # Guardar respuestas
    if respuestas.data:
        for r in respuestas.data:
            fecha_r = r.created_at.strftime('%Y-%m-%d %H:%M:%S')
            data_to_save.append((f"Reply:{tweet_id}", fecha_r, random.choice(sentimientos_lista), r.text))
            
    return data_to_save

# --- Ejecución ---
if __name__ == "__main__":
    url_objetivo = config['analisis_unitario']['url_objetivo']
    print(f"🚀 Iniciando análisis de impacto para: {url_objetivo}")
    
    datos = obtener_detalles_y_respuestas(url_objetivo)

    if datos:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Crear tabla si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tweets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tema TEXT,
                date TEXT,
                sentimiento TEXT,
                texto TEXT
            )
        ''')
        
        cursor.executemany("INSERT INTO tweets (tema, date, sentimiento, texto) VALUES (?, ?, ?, ?)", datos)
        conn.commit()
        conn.close()
        print(f"✅ Proceso terminado. Se guardó el post y {len(datos)-1} respuestas.")
    else:
        print("❌ No se pudieron obtener datos. Verificá la URL o el Token.")