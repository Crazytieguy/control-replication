import json
import random
from itertools import chain
from pathlib import Path

import typer


def main():
    """Select 1500 interview difficulty problems from APPS dataset and save them in APPS_filtered directory."""
    out_dir = Path("APPS_filtered")
    out_dir.mkdir(exist_ok=True)
    interview_level_problem_dirs = []
    for problem_dir in chain(Path("APPS/train").iterdir(), Path("APPS/test").iterdir()):
        if valid_problem(problem_dir):
            interview_level_problem_dirs.append(problem_dir)
    existing_problems = [d for d in out_dir.iterdir() if d.is_dir()]
    existing_problem_names = {d.name for d in existing_problems}
    for problem_dir in existing_problems:
        if not valid_problem(problem_dir):
            print(f"Removing {problem_dir}")
            for file in problem_dir.iterdir():
                file.unlink()
            problem_dir.rmdir()
            existing_problem_names.remove(problem_dir.name)
    interview_level_problem_dirs = [
        d
        for d in interview_level_problem_dirs
        if format_dir_name(d) not in existing_problem_names
    ]
    sample = random.sample(
        list(interview_level_problem_dirs), 1500 - len(existing_problem_names)
    )
    for problem_dir in sample:
        target = out_dir / format_dir_name(problem_dir)
        target.mkdir(exist_ok=True)
        for file in problem_dir.iterdir():
            (target / file.name).write_text(file.read_text())


def valid_problem(problem_dir: Path) -> bool:
    metadata = json.loads((problem_dir / "metadata.json").read_text())
    if metadata["difficulty"] != "interview":
        return False
    if (problem_dir / "starter_code.py").exists():
        return False
    input_output_file = problem_dir / "input_output.json"
    if not input_output_file.exists():
        return False
    input_output = json.loads(input_output_file.read_text())
    if not input_output["inputs"] or not input_output["outputs"]:
        return False
    return True


def format_dir_name(d: Path):
    return f"{d.parent.name}-{d.name}"


if __name__ == "__main__":
    typer.run(main)
