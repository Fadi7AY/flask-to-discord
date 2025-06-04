from flask import Flask , render_template , request, redirect , jsonify
from discord_webhook import DiscordWebhook
import sqlite3
from datetime import datetime ,timedelta
from dotenv import load_dotenv
import os

load_dotenv()  

WEBHOOK_URL = os.getenv("WEBHOOK_URL")


app = Flask(__name__)

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print(current_time)




def connect_to_db():
    
    conn = sqlite3.connect("messages.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS messages(
                   
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   content TEXT,
                   timestamp TEXT
                   )
    """)


    conn.commit()
    conn.close()

@app.route('/')
def home():
    print("Welcome")
    return redirect('/get_messages')

@app.route('/show_messages')
def show_messages():
    conn = connect_to_db()
    cursor = conn.cursor()
    thirty_min_ago = datetime.now() - timedelta(minutes=30)
    cursor.execute("SELECT * FROM messages WHERE timestamp >= ?", (thirty_min_ago.strftime('%Y-%m-%d %H:%M:%S'),))
    rows = cursor.fetchall()
    conn.close()
    return render_template('show_messages.html', messages=rows)


@app.route('/get_messages_json')
def get_messages_json():
    conn = connect_to_db()
    cursor = conn.cursor()
    thirty_min_ago = datetime.now() - timedelta(minutes=30)
    cursor.execute("SELECT * FROM messages WHERE timestamp >= ?", (thirty_min_ago.strftime('%Y-%m-%d %H:%M:%S'),))
    rows = cursor.fetchall()
    conn.close()

    messages = [
        {"id": row["id"], "content": row["content"], "timestamp": row["timestamp"]}
        for row in rows
    ]
    return jsonify(messages)

@app.route('/get_messages')
def get_messages():
    conn = connect_to_db()
    cursor = conn.cursor()
    thirty_min_ago = datetime.now() - timedelta(minutes=30)
    cursor.execute("SELECT * FROM messages WHERE timestamp >= ?", (thirty_min_ago.strftime('%Y-%m-%d %H:%M:%S'),))
    rows = cursor.fetchall()

    conn.close()


    
    return render_template('index.html',msg=rows)



@app.route('/input_text', methods=['GET', 'POST'])
def input_text():
    if request.method == 'POST':
        message = request.form['message']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO messages (content, timestamp) VALUES (?, ?)', (message, timestamp))
        conn.commit()
        conn.close()

        webhook = DiscordWebhook(url=WEBHOOK_URL, content=message)
        response = webhook.execute()

        return redirect('/get_messages')
    

    
    

if __name__ == '__main__':
    connect_to_db()
    init_db()
    app.run(debug=True , port=5000)