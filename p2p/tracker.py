from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, unquote_to_bytes
import re
import bencode
import time

PEERS = {}  # info_hash (bytes) -> {peer_id (bytes): (ip, port, last_seen)}

def extrair(query, chave):
    """Extrai o valor de ?chave=... como bytes, sem decodificar como UTF-8."""
    m = re.search(rf"(?:^|&){chave}=([^&]*)", query)
    if not m:
        return None
    return unquote_to_bytes(m.group(1))

class Tracker(BaseHTTPRequestHandler):
    def do_GET(self):
        u = urlparse(self.path)
        if u.path != "/announce":
            self.send_response(404); self.end_headers(); return

        info_hash = extrair(u.query, "info_hash")
        peer_id   = extrair(u.query, "peer_id")
        port_str  = extrair(u.query, "port")
        port      = int(port_str.decode()) if port_str else 0
        ip        = self.client_address[0]

        if info_hash is None or peer_id is None or port == 0:
            self.send_response(400); self.end_headers(); return

        now = time.time()
        peers = PEERS.setdefault(info_hash, {})
        peers[peer_id] = (ip, port, now)

        for pid in list(peers):
            if now - peers[pid][2] > 120:
                del peers[pid]

        # compact peer list: 4 bytes IP + 2 bytes port por peer
        peer_bytes = b""
        for pid, (pip, pport, _) in peers.items():
            if pid == peer_id:
                continue
            peer_bytes += bytes(int(x) for x in pip.split(".")) + pport.to_bytes(2, "big")

        resp = bencode.bencode({
            b"interval": 5,
            b"peers": peer_bytes,
        })

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(resp)))
        self.end_headers()
        self.wfile.write(resp)

        print(f"announce: info_hash={info_hash.hex()[:8]} "
              f"peer={peer_id.hex()[:8]} port={port} "
              f"-> {len(peer_bytes)//6} peers  (total no dict: {len(peers)})",
              flush=True)

    def log_message(self, *a):
        pass

if __name__ == "__main__":
    print("Tracker ouvindo em 0.0.0.0:6969", flush=True)
    HTTPServer(("0.0.0.0", 6969), Tracker).serve_forever()