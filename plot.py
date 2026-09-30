import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ARQ_LABEL = {
    "seq":    "CS sequencial",
    "thread": "CS thread/cliente",
    "pool":   "CS pool",
}

def carregar(caminhos):
    dfs = []
    for c in caminhos:
        df = pd.read_csv(c)
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

def grafico_por_arquitetura(df, size_mb, outdir):
    sub = df[df["tamanho_mb"] == size_mb]
    if sub.empty:
        print(f"  (sem dados para {size_mb} MB)")
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    for arq, g in sub.groupby("arquitetura"):
        g = g.sort_values("clientes")
        ax.errorbar(
            g["clientes"], g["med_s"],
            yerr=[g["med_s"] - g["min_s"], g["max_s"] - g["med_s"]],
            marker="o", capsize=4, label=ARQ_LABEL.get(arq, arq),
        )
    ax.set_xlabel("Nº de clientes")
    ax.set_ylabel("Tempo (s)")
    ax.set_title(f"Tempo de transferência — {size_mb} MB")
    ax.set_xticks(sorted(sub["clientes"].unique()))
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    saida = outdir / f"tempo_{size_mb}MB.png"
    fig.savefig(saida, dpi=150)
    plt.close(fig)
    print(f"  gerado: {saida}")

def grafico_por_tamanho(df, arq, n_clientes, outdir):
    """Para uma arquitetura e nº de clientes, mostra o tempo vs tamanho."""
    sub = df[(df["arquitetura"] == arq) & (df["clientes"] == n_clientes)]
    if sub.empty:
        return
    sub = sub.sort_values("tamanho_mb")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(
        sub["tamanho_mb"], sub["med_s"],
        yerr=[sub["med_s"] - sub["min_s"], sub["max_s"] - sub["med_s"]],
        marker="s", capsize=4,
    )
    ax.set_xlabel("Tamanho do arquivo (MB)")
    ax.set_ylabel("Tempo (s)")
    ax.set_title(f"{ARQ_LABEL.get(arq, arq)} — {n_clientes} cliente(s)")
    ax.set_xscale("log")
    ax.set_xticks(sub["tamanho_mb"])
    ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())
    ax.grid(True, alpha=0.3, which="both")
    fig.tight_layout()
    saida = outdir / f"{arq}_{n_clientes}cli.png"
    fig.savefig(saida, dpi=150)
    plt.close(fig)
    print(f"  gerado: {saida}")

def grafico_barras_min_med_max(df, size_mb, n_clientes, outdir):
    sub = df[(df["tamanho_mb"] == size_mb) & (df["clientes"] == n_clientes)]
    if sub.empty:
        return

    # agrega as repetições: pega o min dos mins, a média das médias,
    # o max dos maxes, para cada arquitetura
    agg = (
        sub.groupby("arquitetura")
           .agg(min_s=("min_s", "min"),
                med_s=("med_s", "mean"),
                max_s=("max_s", "max"))
    )

    # agora reindexa com segurança (índice único)
    agg = agg.reindex(["seq", "thread", "pool", "p2p"]).dropna(how="all")

    x = range(len(agg))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar([i - width for i in x], agg["min_s"], width, label="mínimo")
    ax.bar(list(x),                 agg["med_s"], width, label="médio")
    ax.bar([i + width for i in x], agg["max_s"], width, label="máximo")

    ax.set_xticks(list(x))
    ax.set_xticklabels([ARQ_LABEL.get(a, a) for a in agg.index])
    ax.set_ylabel("Tempo (s)")
    ax.set_title(f"Min/Méd/Máx — {size_mb} MB, {n_clientes} cliente(s)")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    saida = outdir / f"barras_{size_mb}MB_{n_clientes}cli.png"
    fig.savefig(saida, dpi=150)
    plt.close(fig)
    print(f"  gerado: {saida}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("csv", nargs="+", help="um ou mais CSVs de resultados")
    p.add_argument("--outdir", default="graficos")
    args = p.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(exist_ok=True)

    df = carregar(args.csv)
    print(f"Total de linhas: {len(df)}")
    print(df.head())

    tamanhos = sorted(df["tamanho_mb"].unique())
    arquiteturas = sorted(df["arquitetura"].unique())
    clientes_unicos = sorted(df["clientes"].unique())

    print("\nGerando gráficos por arquitetura (tempo x nº clientes)...")
    for s in tamanhos:
        grafico_por_arquitetura(df, s, outdir)

    print("\nGerando gráficos por tamanho (tempo x MB)...")
    for arq in arquiteturas:
        for n in clientes_unicos:
            grafico_por_tamanho(df, arq, n, outdir)

    print("\nGerando gráficos de barras (min/méd/máx)...")
    for s in tamanhos:
        for n in clientes_unicos:
            grafico_barras_min_med_max(df, s, n, outdir)

    print("\nPronto.")

if __name__ == "__main__":
    main()