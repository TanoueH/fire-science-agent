import csv
import json
from pathlib import Path
from typing import Any, Dict, List


class LoadCSVTool:
    def run(self, input_data=None, path: str = None, **kwargs) -> List[Dict[str, Any]]:
        if not path:
            raise FileNotFoundError("CSV path not provided.")
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"CSV not found: {path}")

        with p.open(newline="", encoding="utf-8") as csvfile:
            return list(csv.DictReader(csvfile))


class NormalizeSensorsTool:
    def run(self, input_data: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        if not input_data:
            return []

        normalized = []
        for row in input_data:
            try:
                normalized.append({
                    "id": row.get("identifier") or row.get("id"),
                    "temperature_C": float(row.get("temperature_C", 0) or 0),
                    "co_ppm": float(row.get("co_ppm", 0) or 0),
                    "visibility_m": float(row.get("visibility_m", 0) or 0),
                    "smoke_velocity_ms": float(row.get("smoke_velocity_ms", 0) or 0),
                })
            except Exception:
                continue
        return normalized


class PredictFireTool:
    def run(self, input_data: List[Dict[str, Any]], alpha: float = 0.5, **kwargs) -> Dict[str, Any]:
        if not input_data:
            return {
                "fuzzy_score": 0.0,
                "ml_score": 0.0,
                "risk_score": 0.0,
                "level": "LOW",
                "n_samples": 0,
                "message": "No data provided."
            }

        fuzzy_total = 0.0
        ml_total = 0.0
        n = len(input_data)

        for row in input_data:
            temp = float(row.get("temperature_C", 0) or 0)
            co = float(row.get("co_ppm", 0) or 0)
            vis = float(row.get("visibility_m", 100) or 100)
            vel = float(row.get("smoke_velocity_ms", 0) or 0)

            temp_factor = min(temp / 100.0, 1.0)
            co_factor = min(co / 2000.0, 1.0)
            vis_factor = max(0.0, min((50.0 - vis) / 50.0, 1.0))
            vel_factor = min(abs(vel) / 5.0, 1.0)

            fuzzy_score = max(
                0.0,
                0.45 * temp_factor +
                0.30 * co_factor +
                0.25 * vis_factor
            )

            ml_score = max(
                0.0,
                0.35 * temp_factor +
                0.25 * co_factor +
                0.20 * vis_factor +
                0.20 * vel_factor
            )

            fuzzy_total += min(fuzzy_score, 1.0)
            ml_total += min(ml_score, 1.0)

        fuzzy_score = round(fuzzy_total / n, 3)
        ml_score = round(ml_total / n, 3)
        risk_score = round(alpha * fuzzy_score + (1 - alpha) * ml_score, 3)

        if risk_score >= 0.75:
            level = "HIGH"
            message = "Critical alert: elevated fire risk."
        elif risk_score >= 0.40:
            level = "MEDIUM"
            message = "Warning: tunnel conditions may indicate fire development."
        else:
            level = "LOW"
            message = "Normal conditions."

        return {
            "fuzzy_score": fuzzy_score,
            "ml_score": ml_score,
            "risk_score": risk_score,
            "level": level,
            "n_samples": n,
            "message": message,
        }


class CompileReportTool:
    def run(self, input_data, output_path: str = "./output/report.md", **kwargs) -> str:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        md = []
        md.append("# Fire Science Agent Report\n")
        md.append("## Fire-Risk Assessment Summary\n")
        md.append("```json")
        md.append(json.dumps(input_data, indent=2, ensure_ascii=False))
        md.append("```")
        md.append("")

        content = "\n".join(md)
        output_file.write_text(content, encoding="utf-8")
        return content