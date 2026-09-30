import subprocess, sys, time, re, shutil, threading, csv
from pathlib import Path
from statistics import mean

ARIA2 = "aria2c"
DONE = re.compile(r"The download was complete", re.IGNORECASE)
SEED = re.compile(r"seeder:\s*SEEDING", re.IGNORECASE)

def gravar_csv(caminho, arquitetura, tamanho_mb, clientes, tempos):
    if not tempos:
        return
    tmin = min(tempos)
    tmed = mean(tempos)
    tmax = max(tempos)

    arquivo = Path(caminho)
    novo = not arquivo.exists()
    with arquivo.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if novo:
            w.writerow(["arquitetura", "tamanho_mb", "clientes",
                        "min_s", "med_s", "max_s"])
        w.writerow([arquitetura, tamanho_mb, clientes,
                    f"{tmin:.4f}", f"{tmed:.4f}", f"{tmax:.4f}"])

    print(f"  -> CSV: p2p, {tamanho_mb}MB, {clientes} cli | "
          f"min={tmin:.3f}s med={tmed:.3f}s max={tmax:.3f}s")

def log(tag, msg):
    print(f"[{tag}] {msg}", flush=True)

def start_tracker():
    log("tracker", "subindo...")
    p = subprocess.Popen(
        [sys.executable, "-u", "tracker.py"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1,
    )
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < 10:
        line = p.stdout.readline()
        if not line:
            break
        log("tracker", line.rstrip())
        if "Tracker ouvindo" in line or "ouvindo" in line.lower():
            return p
    raise RuntimeError("tracker não subiu")

def start_seeder(torrent, seed_dir="seed", bt_port=6881):
    log("seeder", f"subindo (porta {bt_port})...")
    return subprocess.Popen(
        [sys.executable, "-u", "seeder.py", torrent, seed_dir, str(bt_port)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1,
    )

def esperar_seeder(seeder, timeout=60):
    log("seeder", f"esperando SEED (timeout {timeout}s)...")
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < timeout:
        line = seeder.stdout.readline()
        if not line:
            log("seeder", "stdout fechou")
            return False
        log("seeder", line.rstrip())
        if SEED.search(line):
            log("seeder", "pronto!")
            return True
    log("seeder", "TIMEOUT esperando SEED")
    return False

def start_leecher(i, torrent, leech_dir, bt_port):
    Path(leech_dir).mkdir(exist_ok=True)
    log(f"leech_{i}", f"subindo (porta {bt_port})...")
    return subprocess.Popen([
        ARIA2,
        "--enable-dht=false",
        f"--listen-port={bt_port}",
        f"--dir={leech_dir}",
        f"--torrent-file={torrent}",
        "--seed-time=600",
        "--console-log-level=info",
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

def limpar_leechers(n):
    for d in Path(".").glob("leech_*"):
        shutil.rmtree(d, ignore_errors=True)
    for i in range(1, n + 1):
        Path(f"leech_{i}").mkdir(exist_ok=True)

def matar_aria2():
    subprocess.run(["taskkill", "/F", "/IM", "aria2c.exe"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_once(n_leechers, torrent):
    limpar_leechers(n_leechers)
    matar_aria2()
    time.sleep(1)

    tracker = start_tracker()
    time.sleep(0.5)

    seeder = start_seeder(torrent)
    if not esperar_seeder(seeder, timeout=60):
        log("main", "abortando: seeder não ficou pronto")
        seeder.terminate(); tracker.terminate(); matar_aria2()
        return []

    log("main", "aguardando 3s para o primeiro announce...")
    time.sleep(3)

    procs = []
    for i in range(1, n_leechers + 1):
        procs.append(start_leecher(i, torrent, f"leech_{i}", 6900 + i))

    times = [None] * n_leechers

    def ler(proc, idx):
        t0 = time.perf_counter()
        for line in proc.stdout:
            log(f"leech_{idx+1}", line.rstrip())
            if DONE.search(line):
                times[idx] = time.perf_counter() - t0
                return

    threads = []
    for i, p in enumerate(procs):
        t = threading.Thread(target=ler, args=(p, i), daemon=True)
        t.start()
        threads.append(t)

    timeout = 300
    t0 = time.perf_counter()
    for t in threads:
        restante = timeout - (time.perf_counter() - t0)
        t.join(timeout=max(0, restante))

    log("main", f"tempos: {times}")

    for p in procs: p.terminate()
    seeder.terminate()
    tracker.terminate()
    time.sleep(0.5)
    matar_aria2()

    return [t for t in times if t is not None]

if __name__ == "__main__":
    # uso: python p2p.py <n_leechers> <torrent> <tamanho_mb> [reps] [csv]
    n         = int(sys.argv[1])
    torrent   = sys.argv[2]
    size_mb   = int(sys.argv[3])
    reps      = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    csv_saida = sys.argv[5] if len(sys.argv) > 5 else "resultados.csv"

    for r in range(reps):
        log("main", f"=== repetição {r+1}/{reps} ===")
        try:
            tempos = run_once(n, torrent)
        except Exception as e:
            log("main", f"erro: {e}")
            continue

        if tempos:
            gravar_csv(csv_saida, "p2p", size_mb, n, tempos)