import libtorrent as lt
import sys, time

TORRENT = sys.argv[1]
SAVE_PATH = sys.argv[2] if len(sys.argv) > 2 else "seed"
PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 6881

ses = lt.session({
    "listen_interfaces": f"0.0.0.0:{PORT}",
    "enable_dht": False,
    "enable_lsd": False,
    "enable_upnp": False,
    "enable_natpmp": False,
})

info = lt.torrent_info(TORRENT)
h = ses.add_torrent({"ti": info, "save_path": SAVE_PATH})
h.force_recheck()

print("seeder: aguardando verificação...", flush=True)
while not h.status().is_seeding:
    time.sleep(0.5)
print("seeder: SEEDING", flush=True)

try:
    while True:
        s = h.status()
        print(f"seeder: state={s.state} peers={s.num_peers} "
              f"seeds={s.num_seeds} upload={s.upload_rate/1024:.1f} KB/s",
              flush=True)
        time.sleep(2)
except KeyboardInterrupt:
    pass