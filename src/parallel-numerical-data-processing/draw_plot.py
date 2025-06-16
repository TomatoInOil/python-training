import os

import matplotlib.pyplot as plt
import pandas as pd


def log_plot(df: pd.DataFrame) -> plt:
    plt.figure(figsize=(12, 8))
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Размер входных данных (n)", fontsize=12)
    plt.ylabel("Время выполнения (секунды)", fontsize=12)
    plt.title("Сравнение времени выполнения процессов", fontsize=14)

    for column in df.columns[1:]:
        plt.plot(df["n"], df[column], marker="o", label=column)

    plt.legend()
    plt.grid(True, which="both", linestyle="--", alpha=0.6)
    return plt


def small_plot(df: pd.DataFrame) -> plt:
    df_small = df[df["n"] <= 10**4]

    plt.figure(figsize=(10, 6))
    plt.xlabel("n (линейная шкала)", fontsize=12)
    plt.ylabel("Время (секунды)", fontsize=12)
    plt.title("Малые n (10–10 000)", fontsize=14)
    plt.grid(True, linestyle="--", alpha=0.6)

    plt.plot(df_small["n"], df_small["process_a"], marker="o", label="process_a")
    plt.plot(df_small["n"], df_small["process_b"], marker="s", label="process_b")
    plt.plot(df_small["n"], df_small["process_c"], marker="^", label="process_c")
    plt.plot(df_small["n"], df_small["process_d"], marker="d", label="process_d")

    plt.legend()
    return plt


def big_plot(df: pd.DataFrame) -> plt:
    df_large = df[df["n"] > 10**4]

    plt.figure(figsize=(10, 6))
    plt.xlabel("n (линейная шкала)", fontsize=12)
    plt.ylabel("Время (секунды)", fontsize=12)
    plt.title("Большие n (100 000–1 000 000)", fontsize=14)
    plt.grid(True, linestyle="--", alpha=0.6)

    plt.plot(df_large["n"], df_large["process_a"], marker="o", label="process_a")
    plt.plot(df_large["n"], df_large["process_b"], marker="s", label="process_b")
    plt.plot(df_large["n"], df_large["process_c"], marker="^", label="process_c")
    plt.plot(df_large["n"], df_large["process_d"], marker="d", label="process_d")

    plt.legend()
    return plt


def save_plot(plot: plt, title: str) -> None:
    """Сохраняет текущий график в папку ./results/ в формате PNG."""
    os.makedirs("./results", exist_ok=True)
    filename = title.replace(" ", "_") + ".png"
    path = os.path.join("./results", filename)
    plot.savefig(path, dpi=300)


if __name__ == "__main__":
    df = pd.read_csv("./results/benchmark_results.csv")

    plot = log_plot(df)
    save_plot(plot, "log_plot")
    small_plot(df)
    save_plot(plot, "small_plot")
    big_plot(df)
    save_plot(plot, "big_plot")
