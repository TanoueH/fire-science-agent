import csv
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def _as_bool(v: Union[str, bool, None], default: bool = True) -> bool:
    if v is None:
        return default
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ("1", "true", "yes", "y", "on")


# =========================================================
# Tool: LoadCSVTool
# =========================================================
class LoadCSVTool:
    def run(self, input_data=None, path: str = None, **kwargs) -> List[Dict[str, Any]]:
        if not path:
            raise FileNotFoundError("CSV path not provided.")
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"CSV not found: {path}")

        rows: List[Dict[str, Any]] = []
        with p.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                rows.append(row)

        print(f"Loaded {len(rows)} rows from {p}")
        return rows


# =========================================================
# Tool: NormalizeSensorsTool
# =========================================================
class NormalizeSensorsTool:
    def run(self, input_data: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        if not input_data:
            return []

        normalized: List[Dict[str, Any]] = []
        for row in input_data:
            try:
                norm_row = {
                    "id": row.get("identifier") or row.get("id"),
                    "temperature_C": float(row.get("temperature_C", 0) or 0),
                    "co_ppm": float(row.get("co_ppm", 0) or 0),
                    "visibility_m": float(row.get("visibility_m", 0) or 0),
                    "air_velocity_ms": float(row.get("air_velocity_ms", 0) or 0),
                }
                normalized.append(norm_row)
            except Exception as e:
                # Avoid noisy prints per row in production; count errors instead if needed
                print(f"Normalization warning: failed to parse row: {e}")

        print(f"Normalization completed: {len(normalized)} records")
        return normalized


# =========================================================
# Tool: FetchLiteratureTool (guarded)
# =========================================================
class FetchLiteratureTool:
    """
    Paper-ready rule:
    - Never generate fabricated references.
    - In OFFLINE mode, return an explicit 'skipped' payload.
    - In ONLINE mode, this tool should query real sources (to be implemented).
    """

    def run(self, input_data, offline: Optional[Union[str, bool]] = None, **kwargs) -> Dict[str, Any]:
        offline_mode = _as_bool(offline, default=True)

        if offline_mode:
            print("FetchLiteratureTool skipped (OFFLINE_MODE=true).")
            return {"skipped": True, "items": [], "reason": "offline_mode"}

        # IMPORTANT: Avoid placeholders that look like real citations.
        # If not implemented, fail explicitly rather than returning fictional data.
        raise NotImplementedError(
            "FetchLiteratureTool online mode is not implemented. "
            "Provide a curated dataset or implement real retrieval."
        )


# =========================================================
# Tool: WebScraperTool (guarded)
# =========================================================
class WebScraperTool:
    """
    Paper-ready rule:
    - In OFFLINE mode, return 'skipped'.
    - In ONLINE mode, scrape only allowed/public sources and store raw evidence.
    """

    def run(self, input_data, offline: Optional[Union[str, bool]] = None, **kwargs) -> Dict[str, Any]:
        offline_mode = _as_bool(offline, default=True)

        if offline_mode:
            print("WebScraperTool skipped (OFFLINE_MODE=true).")
            return {"skipped": True, "items": [], "reason": "offline_mode"}

        raise NotImplementedError(
            "WebScraperTool online mode is not implemented. "
            "Provide a curated abstracts cache or implement compliant scraping."
        )


# =========================================================
# Tool: PredictFireTool (deterministic scoring)
# =========================================================
class PredictFireTool:
    def run(self, input_data: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        if not input_data:
            return {"risk_score": 0.0, "level": "LOW", "n_samples": 0, "message": "No data provided."}

        total_score = 0.0
        n = len(input_data)

        for row in input_data:
            try:
                temp = float(row.get("temperature_C", 0) or 0)
                co = float(row.get("co_ppm", 0) or 0)
                vis = float(row.get("visibility_m", 100) or 100)
                air = float(row.get("air_velocity_ms", 0) or 0)

                temp_factor = min(temp / 100.0, 1.0)
                co_factor = min(co / 2000.0, 1.0)
                vis_factor = max(0.0, min((50.0 - vis) / 50.0, 1.0))
                air_factor = max(0.0, 1.0 - (air / 10.0))  # higher velocity -> lower risk

                row_score = (0.4 * temp_factor +
                             0.3 * co_factor +
                             0.2 * vis_factor -
                             0.1 * air_factor)

                total_score += max(row_score, 0.0)

            except Exception as e:
                print(f"Prediction warning: failed row: {e}")

        risk_score = round(min(total_score / max(n, 1), 1.0), 2)

        if risk_score >= 0.75:
            level = "HIGH"
            message = "Critical alert: elevated fire risk."
        elif risk_score >= 0.4:
            level = "MEDIUM"
            message = "Warning: conditions may favor ignition."
        else:
            level = "LOW"
            message = "Normal conditions."

        result = {"risk_score": risk_score, "level": level, "n_samples": n, "message": message}
        print(f"Prediction completed: score={risk_score}, level={level}, n_samples={n}")
        return result


# =========================================================
# Tool: CompileReportTool (returns Markdown content)
# =========================================================
class CompileReportTool:
    """
    Contract:
    - input_data: can be dict/list assembled by pipeline runner
    - returns: Markdown string content
    - If output_path is provided, writes the file and returns the same Markdown string (not the path).
    """

    def run(self, input_data, output_path: str = "./output/report.md", **kwargs) -> str:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        md = []
        md.append("# FireScience Report\n")
        md.append("## Summary of Results\n")
        md.append("```json")
        md.append(json.dumps(input_data, indent=2, ensure_ascii=False))
        md.append("```")
        md.append("")

        content = "\n".join(md)

        output_file.write_text(content, encoding="utf-8")
        print(f"Report written to {output_file}")
        return content
