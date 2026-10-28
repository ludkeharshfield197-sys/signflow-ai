import csv
from pathlib import Path
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
OUT_FILE = Path(__file__).parent / "图4_CSL_ASL_mAP05_柱状图.png"


def parse_table(section_title: str):
    lines = DATA_FILE.read_text(encoding="utf-8").splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == section_title:
            start = i + 1
            break
    if start is None:
        raise ValueError(f"找不到: {section_title}")
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


def get_map05(table_rows, model_name: str):
    for row in table_rows:
        if row[0].strip() == model_name:
            return float(row[1])
    raise ValueError(f"找不到模型: {model_name}")


def main():
    set_academic_style()
    _, csl_rows = parse_table("表1 CSL 测试集性能对比")
    _, asl_rows = parse_table("表2 ASL 测试集性能对比")

    models = ["YOLOv8", "YOLOv8-DA"]
    csl_map = [get_map05(csl_rows, m) * 100 for m in models]
    asl_map = [get_map05(asl_rows, m) * 100 for m in models]

    x = range(len(models))
    width = 0.35
    colors = ["#1f4e79", "#851c1c"]

    fig, ax = plt.subplots(figsize=(3.5, 2.8))
    bars_csl = ax.bar(
        [i - width / 2 for i in x],
        csl_map,
        width,
        label="CSL",
        color=colors[0],
        hatch="//",
        alpha=0.7,
        edgecolor="black",
        linewidth=0.5,
    )
    bars_asl = ax.bar(
        [i + width / 2 for i in x],
        asl_map,
        width,
        label="ASL",
        color=colors[1],
        hatch="\\\\",
        alpha=0.7,
        edgecolor="black",
        linewidth=0.5,
    )

    ax.set_ylabel("mAP@0.5 (%)")
    ax.set_xticks(list(x))
    ax.set_xticklabels(models)
    ax.set_ylim(95, 100)
    ax.legend(frameon=False)

    ax.grid(axis="y", linestyle="--", alpha=0.3, color="#B0B0B0")
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(direction="in", which="both")

    ax.bar_label(bars_csl, fmt="%.2f", padding=2, fontsize=8)
    ax.bar_label(bars_asl, fmt="%.2f", padding=2, fontsize=8)

    out_pdf = OUT_FILE.with_suffix(".pdf")
    out_png = OUT_FILE
    try:
        fig.savefig(out_pdf, bbox_inches="tight")
        print(f"已保存: {out_pdf}")
    except PermissionError:
        fig.savefig(out_png, bbox_inches="tight", dpi=600)
        print(f"PDF被占用，已保存PNG: {out_png}")


if __name__ == "__main__":
    main()
