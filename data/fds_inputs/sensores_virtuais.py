#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path
import re
import pandas as pd
import matplotlib.pyplot as plt


# =========================================================
# CONFIGURAÇÃO DOS SENSORES (ALINHADA AO FDS FINAL)
# =========================================================

SENSOR_METADATA = {
    "S01": {"x": 15.0, "y": 6.80, "z": -3.0},
    "S02": {"x": 15.0, "y": 6.80, "z":  3.0},
    "S03": {"x": 20.0, "y": 6.80, "z": -3.0},
    "S04": {"x": 20.0, "y": 6.80, "z":  3.0},
    "S05": {"x": 25.0, "y": 6.80, "z": -3.0},
    "S06": {"x": 25.0, "y": 6.80, "z":  3.0},
    "S07": {"x": 30.0, "y": 6.80, "z": -3.0},
    "S08": {"x": 30.0, "y": 6.80, "z":  3.0},
    "S09": {"x": 35.0, "y": 6.80, "z": -3.0},
    "S10": {"x": 35.0, "y": 6.80, "z":  3.0},
}


# =========================================================
# FUNÇÕES UTILITÁRIAS
# =========================================================

def ensure_output_dir(base_dir: Path):
    base_dir.mkdir(parents=True, exist_ok=True)


def infer_chid_from_csv(csv_path: Path) -> str:
    name = csv_path.name
    if name.endswith("_devc.csv"):
        return name[:-9]
    return csv_path.stem


def infer_scenario_from_chid(chid: str) -> str:
    chid_upper = chid.upper()
    if "S1" in chid_upper:
        return "S1"
    if "S2" in chid_upper:
        return "S2"
    if "S3" in chid_upper:
        return "S3"
    return "UNKNOWN"


def sanitize_column_name(col: str) -> str:
    col = str(col).strip().replace('"', "")
    col = re.sub(r"\s+", " ", col)
    return col


def read_fds_devc_csv(csv_path: Path) -> pd.DataFrame:
    """
    Lê CSV do FDS quando a 1ª linha contém unidades e a 2ª linha contém
    os nomes reais das colunas.
    """
    df = pd.read_csv(csv_path, header=0, skiprows=1)
    df.columns = [sanitize_column_name(c) for c in df.columns]

    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    time_col = find_time_column(df)
    df = df.dropna(subset=[time_col]).reset_index(drop=True)

    return df


def find_time_column(df: pd.DataFrame) -> str:
    possible_names = [
        "time",
        "Time",
        "TIME",
        "Time(s)",
        "Time (s)",
        "FDS Time",
    ]

    for col in df.columns:
        clean = str(col).strip()
        if clean in possible_names:
            return col

    for col in df.columns:
        clean = str(col).strip().lower().replace(" ", "")
        if "time" in clean:
            return col

    raise ValueError(
        f"Coluna de tempo não encontrada. Colunas lidas: {list(df.columns)}"
    )


def collect_columns(df: pd.DataFrame, ids):
    missing = []
    cols = {}

    normalized_cols = {sanitize_column_name(c): c for c in df.columns}

    for dev_id in ids:
        if dev_id in normalized_cols:
            cols[dev_id] = df[normalized_cols[dev_id]]
        else:
            candidates = [
                real_col for clean_col, real_col in normalized_cols.items()
                if clean_col.startswith(dev_id)
            ]
            if candidates:
                cols[dev_id] = df[candidates[0]]
            else:
                missing.append(dev_id)

    return cols, missing


def plot_quantity(time_s, series_dict, title, ylabel, out_png):
    plt.figure(figsize=(10, 6))
    for dev_id, s in series_dict.items():
        plt.plot(time_s, s.values, label=dev_id)
    plt.xlabel("Tempo (s)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend(ncol=2, fontsize=8)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_png, dpi=150)
    plt.close()


def summarize_last_window(time_s, series_dict, window_s=60.0, agg="mean"):
    if len(time_s) == 0:
        return {}

    t_end = time_s.iloc[-1]
    t_start = max(t_end - window_s, time_s.iloc[0])
    mask = (time_s >= t_start) & (time_s <= t_end)

    summary = {}
    for dev_id, s in series_dict.items():
        data = s[mask].dropna()
        if data.empty:
            summary[dev_id] = None
        else:
            if agg == "min":
                val = data.min()
            elif agg == "max":
                val = data.max()
            else:
                val = data.mean()
            summary[dev_id] = float(val)

    return summary


def build_sensor_dataset(time_s, temp_cols, vis_cols, co_ppm_cols, u_cols, scenario, chid):
    rows = []

    for i in range(1, 11):
        sensor_id = f"S{i:02d}"
        meta = SENSOR_METADATA.get(sensor_id, {"x": None, "y": None, "z": None})

        t_key = f"T_{sensor_id}"
        vis_key = f"VIS_{sensor_id}"
        co_key = f"CO_{sensor_id}"
        u_key = f"U_{sensor_id}"

        n = len(time_s)

        rows.append(pd.DataFrame({
            "chid": [chid] * n,
            "scenario": [scenario] * n,
            "sensor_id": [sensor_id] * n,
            "time_s": time_s.values,
            "x": [meta["x"]] * n,
            "y": [meta["y"]] * n,
            "z": [meta["z"]] * n,
            "temperature_c": temp_cols.get(t_key, pd.Series([pd.NA] * n)).values,
            "visibility_m": vis_cols.get(vis_key, pd.Series([pd.NA] * n)).values,
            "co_ppm": co_ppm_cols.get(co_key, pd.Series([pd.NA] * n)).values,
            "smoke_velocity_ms": u_cols.get(u_key, pd.Series([pd.NA] * n)).values,
        }))

    return pd.concat(rows, ignore_index=True)


def main():
    parser = argparse.ArgumentParser(
        description="Processar sensores virtuais do FDS (DEVC): Temperatura, Visibilidade, CO (ppm) e U-Velocity."
    )
    parser.add_argument("--chid", type=str, default=None,
                        help="CHID do caso (procura <CHID>_devc.csv na pasta atual).")
    parser.add_argument("--csv", type=str, default=None,
                        help="Caminho para o arquivo *_devc.csv.")
    parser.add_argument("--window", type=float, default=60.0,
                        help="Janela final (s) para estatística resumida. Padrão: 60 s.")
    parser.add_argument("--outdir", type=str, default="outputs",
                        help="Diretório base de saída.")
    args = parser.parse_args()

    if args.csv is None and args.chid is None:
        raise SystemExit("Forneça --chid ou --csv.")

    if args.csv:
        csv_path = Path(args.csv)
        if not csv_path.exists():
            raise SystemExit(f"Arquivo não encontrado: {csv_path}")
        chid = args.chid or infer_chid_from_csv(csv_path)
    else:
        chid = args.chid
        csv_path = Path(f"{chid}_devc.csv")
        if not csv_path.exists():
            raise SystemExit(f"Arquivo não encontrado: {csv_path}")

    scenario = infer_scenario_from_chid(chid)

    out_dir = Path(args.outdir) / chid
    ensure_output_dir(out_dir)

    df = read_fds_devc_csv(csv_path)
    time_col = find_time_column(df)
    time_s = df[time_col]

    temp_ids = [f"T_S{i:02d}" for i in range(1, 11)]
    vis_ids  = [f"VIS_S{i:02d}" for i in range(1, 11)]
    co_ids   = [f"CO_S{i:02d}" for i in range(1, 11)]
    u_ids    = [f"U_S{i:02d}" for i in range(1, 11)]

    temp_cols, miss_t = collect_columns(df, temp_ids)
    vis_cols,  miss_v = collect_columns(df, vis_ids)
    co_cols,   miss_c = collect_columns(df, co_ids)
    u_cols,    miss_u = collect_columns(df, u_ids)

    missing_all = miss_t + miss_v + miss_c + miss_u
    if missing_all:
        print("[AVISO] Dispositivos ausentes no CSV:", ", ".join(missing_all))

    # CO: fração volumétrica -> ppm
    co_ppm_cols = {k: v * 1e6 for k, v in co_cols.items()}

    # -----------------------------------------------------
    # GRÁFICOS
    # -----------------------------------------------------
    if temp_cols:
        plot_quantity(
            time_s, temp_cols,
            "Temperatura nos sensores virtuais (y = 6,80 m)",
            "Temperatura",
            out_dir / "temperatura_vs_tempo.png"
        )

    if vis_cols:
        plot_quantity(
            time_s, vis_cols,
            "Visibilidade nos sensores virtuais (y = 6,80 m)",
            "Visibilidade (m)",
            out_dir / "visibilidade_vs_tempo.png"
        )

    if co_ppm_cols:
        plot_quantity(
            time_s, co_ppm_cols,
            "Monóxido de carbono nos sensores virtuais (y = 6,80 m)",
            "CO (ppm)",
            out_dir / "co_ppm_vs_tempo.png"
        )

    if u_cols:
        plot_quantity(
            time_s, u_cols,
            "Velocidade longitudinal da fumaça nos sensores (y = 6,80 m)",
            "U-Velocity (m/s)",
            out_dir / "u_velocity_vs_tempo.png"
        )

    # -----------------------------------------------------
    # SUMÁRIOS
    # -----------------------------------------------------
    summary_rows = []

    t_sum = summarize_last_window(time_s, temp_cols, window_s=args.window, agg="mean")
    for dev_id, val in t_sum.items():
        summary_rows.append({
            "sensor": dev_id,
            "grandeza": "Temperatura",
            "estatistica": f"media_{int(args.window)}s",
            "valor": val,
            "unidade": "temperatura_raw"
        })

    v_sum = summarize_last_window(time_s, vis_cols, window_s=args.window, agg="min")
    for dev_id, val in v_sum.items():
        summary_rows.append({
            "sensor": dev_id,
            "grandeza": "Visibilidade",
            "estatistica": f"minimo_{int(args.window)}s",
            "valor": val,
            "unidade": "m"
        })

    co_sum = summarize_last_window(time_s, co_ppm_cols, window_s=args.window, agg="max")
    for dev_id, val in co_sum.items():
        summary_rows.append({
            "sensor": dev_id,
            "grandeza": "CO",
            "estatistica": f"maximo_{int(args.window)}s",
            "valor": val,
            "unidade": "ppm"
        })

    u_sum = summarize_last_window(time_s, u_cols, window_s=args.window, agg="mean")
    for dev_id, val in u_sum.items():
        summary_rows.append({
            "sensor": dev_id,
            "grandeza": "U-Velocity",
            "estatistica": f"media_{int(args.window)}s",
            "valor": val,
            "unidade": "m/s"
        })

    if summary_rows:
        summary_df = pd.DataFrame(summary_rows)
        summary_df.to_csv(out_dir / "summary_last_window.csv", index=False)
        try:
            summary_df.to_excel(out_dir / "summary_last_window.xlsx", index=False, engine="openpyxl")
        except Exception as e:
            print("[AVISO] Não foi possível escrever XLSX:", e)

    # -----------------------------------------------------
    # DATASET LONGO (PRONTO PARA PIPELINE)
    # -----------------------------------------------------
    dataset_long = build_sensor_dataset(
        time_s=time_s,
        temp_cols=temp_cols,
        vis_cols=vis_cols,
        co_ppm_cols=co_ppm_cols,
        u_cols=u_cols,
        scenario=scenario,
        chid=chid
    )
    dataset_long.to_csv(out_dir / "dataset_sensors_long.csv", index=False)

    # -----------------------------------------------------
    # DATASET WIDE OPCIONAL
    # -----------------------------------------------------
    wide_df = df.copy()
    for co_id, series in co_ppm_cols.items():
        wide_df[f"{co_id}_PPM"] = series
    wide_df.to_csv(out_dir / "dataset_devc_wide.csv", index=False)

    print("Processamento concluído.")
    print("CHID:", chid)
    print("Scenario:", scenario)
    print("Saídas em:", out_dir)


if __name__ == "__main__":
    main()