from datetime import datetime
import socket
import os
    
HOST = '127.0.0.1'
PORT = 8080
WEB_ROOT = './www'
MIME_TYPES = {
    ".html": "text/html",
    ".css": "text/css",
    ".webp": "image/webp"
}


def log_request(method, path, code):
    """Logging delle richieste HTTP"""
    print(f"[{datetime.now()}] {code} {method} {path}")

def handle_request(conn):
    """Gestione delle richieste HTTP"""
    try:
        request = conn.recv(1024).decode()
        if not request:
            return
        
        # Prendo il metodo (GET) e il percorso alla risorsa richiesta
        method = request.split()[0]
        path = request.split()[1]

        # Default a /index.html
        if path == "/":
            path = "/index.html"

        # Unisco il percorso della root del server con il percorso della risorsa richiesta
        # (utilizzo l'os.path.join per evitare problemi con sistemi operativi diversi)
        filepath = os.path.join(WEB_ROOT, path.lstrip("/"))
        if os.path.isfile(filepath):
            with open(filepath, 'rb') as f:
                content = f.read()

            # Determino il mime type in base all'estensione del file richiesto
            ext = os.path.splitext(filepath)[1]
            mime_type = MIME_TYPES.get(ext, "application/octet-stream")

            # Invio l'header di risposta insieme al contenuto del file
            conn.send("HTTP/1.1 200 OK\r\n".encode())
            conn.send(f"Content-Length: {len(content)}\r\n".encode())
            conn.send(f"Content-Type: {mime_type}\r\n\r\n".encode())
            conn.send(content)
            log_request(method, path, 200)
        else:
            # Se il file non esiste, invio una risposta 404 Not Found
            conn.send("HTTP/1.1 404 Not Found\r\n".encode())
            conn.send("Content-Type: text/html\r\n\r\n".encode())
            conn.send("<h1>404 Not Found</h1>".encode())
            conn.send("<a href='/'>Vai all'indice</a>".encode())
            log_request(method, path, 404)

    except Exception as e:
        print("Error:", e)
    finally:
        conn.close()

def run_server():
    """Avvio del server web"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Il server e' disponibile su {HOST}:{PORT}")
        while True:
            conn, _ = s.accept()
            handle_request(conn)

if __name__ == "__main__":
    run_server()
