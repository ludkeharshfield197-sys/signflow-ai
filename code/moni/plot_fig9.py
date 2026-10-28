from pathlib import Path
import csv
import matplotlib.pyplot as plt


def set_academic_style():
    plt.style.use("seaborn-v0_8-paper")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Microsoft YaHei", "SimHei", "Arial Unicode MS"],
        "font.serif": ["Times New Roman"],
        "axes.unicode_minus": False,
        "font.size": 10,
        "axes.labelsize": 10,
        "axes.titlesize": 10,
        "axes.titleweight": "normal",
        "legend.fontsize": 8,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "axes.linewidth": 1.0,
        "grid.linewidth": 0.5,
        "grid.alpha": 0.3,
        "grid.linestyle": "--",
        "savefig.dpi": 300,
        "figure.constrained_layout.use": True,
    })

DATA_FILE = Path(__file__).parent / "模拟数据.txt"
OUT_FILE = Path(__file__).parent / "图9_并发延迟折线图.png"


def parse_latency():
    lines = DATA_FILE.read_text(encoding="utf-8").splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == "任务四：并发延迟模拟数据（图9）":
            start = i + 1
            break
    if start is None:
        raise ValueError("找不到并发延迟数据标题")

    header = None
    rows = []
    for line in lines[start:]:
        if not line.strip():
            break
        if header is None:
            header = next(csv.reader([line]))
            continue
        rows.append(next(csv.reader([line])))
    return header, rows


def main():
    set_academic_style()
    _, rows = parse_latency()
    concurrency = [int(r[0]) for r in rows]
    latency = [float(r[1]) for r in rows]

    yerr = [2, 3, 4, 5]

    fig, ax = plt.subplots(figsize=(3.5, 2.8))
    ax.plot(
        concurrency,
        latency,
        color="#1f4e79",
        marker="o",
        markersize=5,
        markerfacecolor="white",
        markeredgewidth=1.2,
        linewidth=1.2,
    )
    ax.fill_between(
        concurrency,
        [v - e for v, e in zip(latency, yerr)],
        [v + e for v, e in zip(latency, yerr)],
        color="#1f4e79",
        alpha=0.15,
        linewidth=0,
    )
    for x, y in zip(concurrency, latency):
        ax.text(x, y + 1.2, f"{y:.0f}", ha="center", va="bottom", fontsize=8)
    ax.set_xlabel("并发数")
    ax.set_ylabel("平均延迟 (ms)")
    ax.set_xticks(concurrency)
    ax.grid(True, linestyle="--", alpha=0.3, color="#B0B0B0")
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(direction="in", which="both")

    fig.savefig(OUT_FILE, bbox_inches="tight", dpi=600)
    print(f"已保存: {OUT_FILE}")


if __name__ == "__main__":
    main()
