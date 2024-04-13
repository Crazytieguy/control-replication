import json
import logging
import subprocess
from pathlib import Path

import typer

TIMEOUT = 1


def evaluate_solution(
    problem_directory: Path,
    solution_file: Path,
) -> bool:
    """Evaluate the solution code against the test cases in the problem directory."""
    solution_binary = solution_file.with_suffix("")
    if not solution_file.exists():
        raise ValueError(f"Solution file {solution_file} does not exist")
    if not solution_binary.exists():
        compilation_result = subprocess.run(
            ["g++", "-std=c++17", "-O2", "-o", solution_binary, solution_file],
            capture_output=True,
        )
        if compilation_result.returncode != 0:
            solution_file.with_suffix(".stderr").write_bytes(compilation_result.stderr)
            logging.info(f"{solution_file} failed due to compilation error")
            return False
    assert solution_binary.exists()
    input_output_file = problem_directory / "input_output.json"
    input_output = json.loads(input_output_file.read_text())
    if isinstance(input_output["inputs"][0], list):
        input_output["inputs"] = ["\n".join(i) for i in input_output["inputs"]]
    if isinstance(input_output["outputs"][0], list):
        input_output["outputs"] = ["\n".join(o) for o in input_output["outputs"]]
    cases = dict(zip(input_output["inputs"], input_output["outputs"]))
    for case, expected_output in cases.items():
        try:
            result = subprocess.run(
                [solution_binary],
                input=case,
                capture_output=True,
                text=True,
                timeout=TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            logging.info(f"{solution_file} failed due to timeout")
            return False
        if result.returncode != 0:
            logging.info(f"{solution_file} failed due to runtime error")
            return False
        if result.stdout.strip() != expected_output.strip():
            logging.info(
                f"{solution_file} failed due to wrong output: {result.stdout.strip()} (expected {expected_output.strip()})"
            )
            return False
    return True


if __name__ == "__main__":
    # Just for testing
    typer.run(evaluate_solution)
