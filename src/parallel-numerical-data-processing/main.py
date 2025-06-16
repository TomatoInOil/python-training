import os
import random
import timeit
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, Process, Queue

import pandas as pd


def process_a(data: list[int]) -> None:
    """Использование пула потоков с concurrent.futures."""
    with ThreadPoolExecutor(max_workers=4) as executor:
        _results = executor.map(_process_number, data)


def process_b(data: list[int]) -> None:
    """Использование multiprocessing.Pool с пулом процессов, равным количеству CPU."""
    with Pool(processes=4) as pool:
        pool.map(_process_number, data)


def process_c(data: list[int]) -> None:
    """
    Создание отдельных процессов с использованием multiprocessing.Process и
    очередей (multiprocessing.Queue) для передачи данных.
    """
    queue = Queue()

    p1 = Process(target=producer, args=(queue, data))
    p2 = Process(target=consumer, args=(queue,))
    p3 = Process(target=consumer, args=(queue,))
    p4 = Process(target=consumer, args=(queue,))

    list(map(lambda p: p.start(), [p1, p2, p3, p4]))

    p1.join()
    for _ in range(3):
        queue.put(None)
    list(map(lambda p: p.join(), [p2, p3, p4]))


def process_d(data: list[int]) -> None:
    """Однопоточный (однопроцессный) вариант."""
    for item in data:
        _process_number(item)


def consumer(queue: Queue) -> None:
    while True:
        item = queue.get()
        if item is None:
            break
        _process_number(item)


def producer(queue: Queue, data: list[int]) -> None:
    for item in data:
        queue.put(item)


def generate_data(n: int) -> list:
    return [random.randint(1, 1000) for _ in range(n)]


def _process_number(number: int) -> int:
    result = 1
    for item in range(2, number + 1):
        result *= item
    return result


def _generate_log_scale_range() -> list[int]:
    n_values = []
    current_n = 10
    while current_n <= 10**6:
        n_values.append(current_n)
        current_n *= 10
    return n_values


def _run_benchmark_processes(n_values: list[int], results: dict[str, list]) -> None:
    stm = "process_{}(input_data)"
    setup_stm = """
from __main__ import process_{}, generate_data

input_data = generate_data(n={})
"""
    for n in n_values:
        for letter in ["a", "b", "c", "d"]:
            result = timeit.timeit(
                stm.format(letter),
                setup=setup_stm.format(letter, n),
                number=1,
            )
            results[letter].append(result)


def _save_to_csv(n_values: list[int], results: dict[str, list[float]]) -> None:
    df = pd.DataFrame(results, index=n_values)
    df.index.name = "n"
    df.columns = [f"process_{letter}" for letter in ["a", "b", "c", "d"]]
    os.makedirs("./results", exist_ok=True)
    csv_path = "./results/benchmark_results.csv"
    df.to_csv(csv_path)


if __name__ == "__main__":
    n_values = _generate_log_scale_range()
    results = {letter: [] for letter in ["a", "b", "c", "d"]}
    _run_benchmark_processes(n_values, results)
    _save_to_csv(n_values, results)
