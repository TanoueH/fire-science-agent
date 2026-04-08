import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from custom_tool import (
    LoadCSVTool,
    NormalizeSensorsTool,
    PredictFireTool,
    CompileReportTool,
)

app = FastAPI(title="Fire Science Agent", version="1.0")


@dataclass(frozen=True)
class Settings:
    project_root: Path
    tasks_file: Path
    output_dir: Path
    input_csv: str
    report_file: str
    alpha: float
    seed: int
    run_id: str

    @staticmethod
    def from_env() -> "Settings":
        project_root = Path(os.getenv("PROJECT_ROOT", "/app")).resolve()
        tasks_file = Path(
            os.getenv("TASKS_FILE", str(project_root / "tasks.yaml"))
        ).resolve()
        output_dir = Path(
            os.getenv("OUTPUT_DIR", str(project_root / "output"))
        ).resolve()

        input_csv = os.getenv("INPUT_CSV", str(project_root / "data" / "samples" / "scenario_S1_sample.csv"))
        report_file = os.getenv("REPORT_FILE", str(output_dir / "report.md"))
        alpha = float(os.getenv("ALPHA", "0.5"))
        seed = int(os.getenv("SEED", "42"))
        run_id = os.getenv("RUN_ID", "paper-run")

        return Settings(
            project_root=project_root,
            tasks_file=tasks_file,
            output_dir=output_dir,
            input_csv=input_csv,
            report_file=report_file,
            alpha=alpha,
            seed=seed,
            run_id=run_id,
        )


SETTINGS = Settings.from_env()

TOOLS = {
    "LoadCSVTool": LoadCSVTool(),
    "NormalizeSensorsTool": NormalizeSensorsTool(),
    "PredictFireTool": PredictFireTool(),
    "CompileReportTool": CompileReportTool(),
}


def _substitute_vars(obj: Any, variables: Dict[str, str]) -> Any:
    if isinstance(obj, str):
        out = obj
        for k, v in variables.items():
            out = out.replace("${" + k + "}", v)
        return out
    if isinstance(obj, dict):
        return {k: _substitute_vars(v, variables) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_substitute_vars(v, variables) for v in obj]
    return obj


def _load_tasks() -> Dict[str, Any]:
    if not SETTINGS.tasks_file.exists():
        raise FileNotFoundError(f"Tasks file not found: {SETTINGS.tasks_file}")

    with SETTINGS.tasks_file.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    variables = {
        "INPUT_CSV": SETTINGS.input_csv,
        "REPORT_FILE": SETTINGS.report_file,
        "ALPHA": str(SETTINGS.alpha),
        "SEED": str(SETTINGS.seed),
        "RUN_ID": SETTINGS.run_id,
        "OUTPUT_DIR": str(SETTINGS.output_dir),
    }
    return _substitute_vars(cfg, variables)


def _resolve_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return (SETTINGS.project_root / path).resolve()


def _read_output(path: Path) -> Any:
    if path.suffix.lower() == ".json":
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return path.read_text(encoding="utf-8")


def _write_output(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".json":
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    else:
        with path.open("w", encoding="utf-8") as f:
            f.write(str(data))


def _resolve_input(input_spec: Any, results: Dict[str, Any]) -> Optional[Any]:
    if input_spec is None:
        return None

    if isinstance(input_spec, str):
        if input_spec in results:
            return results[input_spec]
        path = _resolve_path(input_spec)
        if path.exists():
            return _read_output(path)
        return None

    if isinstance(input_spec, list):
        assembled: List[Any] = []
        for item in input_spec:
            if isinstance(item, str) and item in results:
                assembled.append(results[item])
                continue
            path = _resolve_path(str(item))
            if path.exists():
                assembled.append(_read_output(path))
        return assembled

    return input_spec


def run_pipeline() -> Dict[str, Any]:
    cfg = _load_tasks()
    tasks = cfg.get("tasks", [])
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("No tasks found in tasks.yaml")

    SETTINGS.output_dir.mkdir(parents=True, exist_ok=True)

    results: Dict[str, Any] = {}

    for task in tasks:
        task_id = task.get("id", "<no-id>")
        tool_name = task.get("tool")
        if tool_name not in TOOLS:
            raise ValueError(f"Tool not found: {tool_name} (task: {task_id})")

        tool = TOOLS[tool_name]
        input_data = _resolve_input(task.get("input"), results)
        params = task.get("params", {}) or {}

        params.setdefault("seed", SETTINGS.seed)
        params.setdefault("run_id", SETTINGS.run_id)

        output_data = tool.run(input_data, **params)

        out = task.get("output", str(SETTINGS.output_dir / f"{task_id}.json"))
        out_path = _resolve_path(out)
        _write_output(out_path, output_data)

        results[task_id] = output_data

    return results


class RunResponse(BaseModel):
    run_id: str
    output_dir: str
    report_file: str
    tasks_executed: int


@app.get("/")
async def root():
    return {"message": "Fire Science Agent active"}


@app.get("/health")
async def health():
    ok = True
    details: Dict[str, Any] = {
        "tasks_file_exists": SETTINGS.tasks_file.exists(),
    }

    if not SETTINGS.tasks_file.exists():
        ok = False

    try:
        SETTINGS.output_dir.mkdir(parents=True, exist_ok=True)
        details["output_dir_writable"] = True
    except Exception:
        ok = False
        details["output_dir_writable"] = False

    return {"ok": ok, "details": details}


@app.post("/run", response_model=RunResponse)
async def run():
    try:
        results = run_pipeline()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return RunResponse(
        run_id=SETTINGS.run_id,
        output_dir=str(SETTINGS.output_dir),
        report_file=SETTINGS.report_file,
        tasks_executed=len(results),
    )


if __name__ == "__main__":
    run_pipeline()