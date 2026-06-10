#!/usr/bin/env python3
"""
gc_montar_v9.py — Montagem do vídeo final UGC v9
Video Anchor | MANUOS IA

Melhorias v9 (feedback Marcos + análise estratégica):
- Hook confessional: "Minha pele tava me envergonhando" (não estatística)
- Tom emocional, não informativo
- Headlines GRANDES no TOPO do frame — expõem a dor antes da fala
  (funciona com e sem som, para o scroll visualmente)
- CTA com preço específico e urgência real
- Persona: Usuária Comum (relatable, casual, não especialista)
"""

import subprocess
import sys
import shutil
from pathlib import Path

REPO = Path("/home/ubuntu/video-anchor")
TAKES_DIR = REPO / "gc_assets" / "takes_v9"
OUTPUT_DIR = REPO / "gc_output"
TRILHA = REPO / "assets" / "trilha_anchor.mp3"
TEMP = Path("/tmp/ugc_v9")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP.mkdir(parents=True, exist_ok=True)

# Headlines GRANDES no topo — expõem a dor visualmente antes da fala
TAKES = [
    {
        "video": TAKES_DIR / "take1_problema.mp4",
        "headline": "Minha pele tava me envergonhando",
        "headline_pos": "top",   # headline no topo, grande, impacto visual imediato
    },
    {
        "video": TAKES_DIR / "take2_solucao.mp4",
        "headline": "Em 2 semanas minha pele ficou outra",
        "headline_pos": "top",
    },
    {
        "video": TAKES_DIR / "take3_cta.mp4",
        "headline": "R$89,90 — Esgotando rapido",
        "headline_pos": "bottom",  # CTA no fundo, próximo ao dedo apontando
    },
]

OUTPUT_FILE = OUTPUT_DIR / "creme_facial_UGC_v9_FINAL.mp4"


def run(cmd, desc=""):
    print(f"  → {desc}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [ERRO] {result.stderr[-500:]}")
        sys.exit(1)


def montar():
    print("=" * 60)
    print("  MONTAGEM UGC v9 — Hook Confessional + Headlines de Dor")
    print("=" * 60)

    takes_prontos = []

    for i, take in enumerate(TAKES, 1):
        headline = take["headline"]
        pos = take["headline_pos"]
        print(f"\n  [TAKE {i}] Headline: '{headline}' ({pos})")

        # Normalizar para 720x1280, 24fps, preservando áudio
        norm_path = TEMP / f"take{i}_norm.mp4"
        run([
            "ffmpeg", "-y",
            "-i", str(take["video"]),
            "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,"
                   "pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            str(norm_path)
        ], f"Normalizar take {i}")

        # Headline grande estilo TikTok
        headline_safe = headline.replace("'", "\\\\'").replace(":", "\\:")
        hl_path = TEMP / f"take{i}_hl.mp4"

        if pos == "top":
            # Headline no topo: fundo preto semitransparente + texto branco grande
            vf = (
                f"drawbox=x=0:y=0:w=iw:h=130:color=black@0.65:t=fill,"
                f"drawtext=text='{headline_safe}':fontsize=36:fontcolor=white"
                f":x=(w-text_w)/2:y=45:font=Arial"
            )
        else:
            # CTA no fundo: fundo vermelho vibrante + texto branco
            vf = (
                f"drawbox=x=0:y=ih-130:w=iw:h=130:color=0xFF0050@0.92:t=fill,"
                f"drawtext=text='{headline_safe}':fontsize=38:fontcolor=white"
                f":x=(w-text_w)/2:y=h-85:font=Arial"
            )

        run([
            "ffmpeg", "-y",
            "-i", str(norm_path),
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "copy",
            str(hl_path)
        ], f"Headline take {i}")

        takes_prontos.append(hl_path)
        print(f"  [TAKE {i}] ✓")

    # Concatenar
    print(f"\n  [CONCAT] Concatenando 3 takes...")
    concat_list = TEMP / "concat_list.txt"
    with open(concat_list, "w") as f:
        for p in takes_prontos:
            f.write(f"file '{p}'\n")

    concat_path = TEMP / "concat_raw.mp4"
    run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(concat_path)
    ], "Concatenar takes")

    # Trilha de fundo
    if TRILHA.exists():
        print(f"\n  [TRILHA] Mixando trilha (vol 0.06)...")
        run([
            "ffmpeg", "-y",
            "-i", str(concat_path),
            "-i", str(TRILHA),
            "-filter_complex",
            "[0:a]volume=1.0[voz];[1:a]volume=0.06[trilha];"
            "[voz][trilha]amix=inputs=2:duration=first[audio_final]",
            "-map", "0:v",
            "-map", "[audio_final]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            str(OUTPUT_FILE)
        ], "Mixar voz + trilha")
    else:
        shutil.copy(str(concat_path), str(OUTPUT_FILE))

    # Resultado
    result = subprocess.run([
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration,size",
        "-of", "csv=p=0", str(OUTPUT_FILE)
    ], capture_output=True, text=True)
    dur, tam = result.stdout.strip().split(",")
    print(f"\n{'=' * 60}")
    print(f"  ✓ VÍDEO FINAL v9 GERADO!")
    print(f"  Arquivo  : {OUTPUT_FILE.name}")
    print(f"  Duração  : {float(dur):.2f}s")
    print(f"  Tamanho  : {int(tam)//1024//1024:.1f} MB")
    print(f"  Resolução: 720x1280 (9:16 TikTok)")
    print(f"  Hook     : Confessional — 'Minha pele tava me envergonhando'")
    print(f"  Headlines: Grandes no topo (takes 1-2) + CTA vermelho (take 3)")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    montar()
