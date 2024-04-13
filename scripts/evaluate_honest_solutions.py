import logging
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import typer
from tqdm import tqdm

from control_replication.evaluate_solution import evaluate_solution

logging.basicConfig(level=logging.WARN)


def main(concurrency: int = 8):
    """Evaluate honest solutions for all of the problems in APPS_filtered directory."""
    counter = Counter()
    problems = [d for d in Path("APPS_filtered").iterdir() if d.is_dir()]
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = [
            ex.submit(evaluate_solution, d, d / "honest-solution.cpp") for d in problems
        ]
        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Evaluating honest solutions",
        ):
            passed = future.result()
            counter[passed] += 1
    print(counter)


if __name__ == "__main__":
    typer.run(main)
