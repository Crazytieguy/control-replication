from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import typer
from tqdm import tqdm

from control_replication.openai_queries import honest_gpt4_solution


def main(concurrency: int = 32):
    """Generate honest solutions for all of the problems in APPS_filtered directory."""
    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = [
            ex.submit(generate_honest_solution, d)
            for d in Path("APPS_filtered").iterdir()
            if d.is_dir()
        ]
        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Generating honest solutions",
        ):
            future.result()


def generate_honest_solution(problem_directory: Path):
    out_file = problem_directory / "honest-solution.cpp"
    if out_file.exists():
        return
    problem_text = (problem_directory / "question.txt").read_text()
    solution = honest_gpt4_solution(problem_text)
    out_file.write_text(solution)


if __name__ == "__main__":
    typer.run(main)
