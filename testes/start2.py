import argparse
import csv
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from statistics import mean

def wait_for_port(host, port, timeout=10.0):
    """Tenta conectar até conseguir ou estourar o timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.1)
    return False

def start_server(arch, size_bytes, port, max_workers):
    args = [sys.executable, "-u", "server.py", arch, str(size_bytes), str(port)]
    if arch == "pool":
        args.append(str(max_workers))

    kwargs = {}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["preexec_fn"] = os.setsid

    return subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        **kwargs,
    )


def wait_until_ready(proc, timeout=10.0):
    """Lê o stdout do servidor até ele anunciar que está ouvindo."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        line = proc.stdout.readline()
        if not line:
            if proc.poll() is not None:
                err = proc.stderr.read()
                raise RuntimeError(f"servidor morreu:\n{err}")
            continue
        if "ouvindo" in line.lower():
            return
    raise RuntimeError("timeout esperando o servidor ficar pronto")

def kill_tree(proc):
    """Mata o processo e todos os filhos (Windows e Linux)."""
    if proc.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    else:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()

def start_client(host, port, size_bytes):
    args = [sys.executable, "client.py", host, str(size_bytes), str(port)]
    return subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )

def run_once(arch, size_bytes, n_clients, port, max_workers):
    server = start_server(arch, size_bytes, port, max_workers)
    try:
        wait_until_ready(server)          # <— em vez de wait_for_port

        clients = [start_client("127.0.0.1", port, size_bytes)
                   for _ in range(n_clients)]

        times = []
        for c in clients:
            out, err = c.communicate()
            if c.returncode != 0:
                print(f"  cliente falhou: {err.strip()}", file=sys.stderr)
                continue
            try:
                times.append(float(out.strip().splitlines()[-1]))
            except (ValueError, IndexError):
                print(f"  saída inesperada: {out!r}", file=sys.stderr)
        return times
    finally:
        kill_tree(server)
        time.sleep(0.3)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--arch", required=True,
                   choices=["seq", "thread", "pool"])
    p.add_argument("--size", type=int, required=True, help="tamanho em MB")
    p.add_argument("--clients", type=int, required=True)
    p.add_argument("--reps", type=int, default=3)
    p.add_argument("--max-workers", type=int, default=2,
                   help="usado apenas no modo pool")
    p.add_argument("--port", type=int, default=5000)
    p.add_argument("--out", default="resultados.csv")
    args = p.parse_args()

    size_bytes = args.size * 1024 * 1024
    all_times = []

    for r in range(1, args.reps + 1):
        print(f"[{args.arch}] {args.size}MB | {args.clients} clientes "
              f"| rep {r}/{args.reps}", flush=True)
        try:
            times = run_once(args.arch, size_bytes, args.clients,
                             args.port, args.max_workers)
        except Exception as e:
            print(f"  erro: {e}")
            continue
        if times:
            all_times.extend(times)
            fmt = " ".join(f"{t:.3f}" for t in times)
            print(f"  tempos: {fmt}")

    if not all_times:
        print("Nenhum resultado coletado.")
        return

    tmin = min(all_times)
    tmed = mean(all_times)
    tmax = max(all_times)
    print(f"Resumo: min={tmin:.3f}s  med={tmed:.3f}s  max={tmax:.3f}s")

    out = Path(args.out)
    novo = not out.exists()
    with out.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if novo:
            w.writerow(["arquitetura", "tamanho_mb", "clientes",
                        "min_s", "med_s", "max_s"])
        w.writerow([args.arch, args.size, args.clients,
                    f"{tmin:.4f}", f"{tmed:.4f}", f"{tmax:.4f}"])

if __name__ == "__main__":
    main()