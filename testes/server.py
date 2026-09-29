import socket, threading, sys
from concurrent.futures import ThreadPoolExecutor
HOST = '0.0.0.0'
PORT = int(sys.argv[3])
CHUNK = 1024 * 1024  # 1 MB
def send_file(conn, size):
    try:
        remaining = size
        block = b'\0' * CHUNK
        while remaining > 0:
            n = min(CHUNK, remaining)
            conn.sendall(block[:n])
            remaining -= n
    finally:
        conn.close()

def main():
    mode = sys.argv[1]          # seq, thread, pool
    size = int(sys.argv[2])
    max_workers = int(sys.argv[3]) if mode == 'pool' else None

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(100)

    print(f"Servidor {mode} ouvindo...")

    if mode == 'seq':
        while True:
            conn, addr = s.accept()
            send_file(conn, size)

    elif mode == 'thread':
        while True:
            conn, addr = s.accept()
            threading.Thread(target=send_file, args=(conn, size), daemon=True).start()

    elif mode == 'pool':
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            while True:
                conn, addr = s.accept()
                pool.submit(send_file, conn, size)

if __name__ == '__main__':
    main()