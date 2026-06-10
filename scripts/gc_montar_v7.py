#!/usr/bin/env python3
"""
gc_montar_v7.py — Montagem do vídeo final UGC v7
Video Anchor | MANUOS IA

Diferença v7 vs v6:
- Takes gerados com áudio nativo (generate_audio=true) — lip-sync real
- Preserva o áudio original de cada take (não substitui por TTS externo)
- Adiciona banners estilo TikTok em cada take
- Concatena os 3 takes com corte direto
- Mixar trilha de fundo em volume baixo (0.06) sobre o áudio nativo
"""

import subprocess
import sys
from pathlib import Path

# ─── Caminhos ─────────────────────────────────────────────────────────────────
REPO = Path("/home/ubuntu/video-anchor")
TAKES_DIR = REPO / "gc_assets" / "takes_v7"
OUTPUT_DIR = REPO / "gc_output"
TRILHA = REPO / "assets" / "trilha_anchor.mp3"
TEMP = Path("/tmp/ugc_v7")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP.mkdir(parents=True, exist_ok=True)

# ─── Configurações ─────────────────────────────────────────────────────────────
TAKES = [
    {
        "video": TAKES_DIR / "take1_problema.mp4",
        "banner": "Rugas incomodando você?",
    },
    {
        "video": TAKES_DIR / "take2_solucao.mp4",
        "banner": "Colágeno que transforma",
    },
    {
        "video": TAKES_DIR / "take3_cta.mp4",
        "banner": "Clica para ver o preço",
    },
]

OUTPUT_FILE = OUTPUT_DIR / "creme_facial_UGC_v7_FINAL.mp4"


def run(cmd, desc=""):
    print(f"  → {desc}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [ERRO] {result.stderr[-400:]}")
        sys.exit(1)


def montar():
    print("=" * 55)
    print("  MONTAGEM UGC v7 — Creme Facial Anti-Idade")
    print("  Áudio nativo com lip-sync real")
    print("=" * 55)

    takes_prontos = []

    for i, take in enumerate(TAKES, 1):
        banner = take["banner"]
        print(f"\n  [TAKE {i}] Adicionando banner: '{banner}'")

        # Normalizar vídeo para 720x1280, 24fps — preservando áudio original
        norm_path = TEMP / f"take{i}_norm.mp4"
        run([
            "ffmpeg", "-y",
            "-i", str(take["video"]),
            "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            str(norm_path)
        ], f"Normalizar take {i} (preservando áudio)")

        # Adicionar banner estilo TikTok
        banner_safe = banner.replace("'", "\\\\'").replace(":", "\\:")
        banner_path = TEMP / f"take{i}_banner.mp4"
        drawtext = (
            f"drawbox=x=0:y=ih-120:w=iw:h=120:color=white@0.88:t=fill,"
            f"drawtext=text='{banner_safe}':fontsize=40:fontcolor=black"
            f":x=(w-text_w)/2:y=h-78:font=Arial"
        )
        run([
            "ffmpeg", "-y",
            "-i", str(norm_path),
            "-vf", drawtext,
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "copy",
            str(banner_path)
        ], f"Banner take {i}")

        takes_prontos.append(banner_path)
        print(f"  [TAKE {i}] ✓ Pronto")

    # Concatenar os 3 takes
    print(f"\n  [CONCAT] Concatenando 3 takes com áudio nativo...")
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

    # Adicionar trilha de fundo (se existir)
    if TRILHA.exists():
        print(f"\n  [TRILHA] Mixando trilha de fundo (vol 0.06)...")
        run([
            "ffmpeg", "-y",
            "-i", str(concat_path),
            "-i", str(TRILHA),
            "-filter_complex",
            "[0:a]volume=1.0[voz];[1:a]volume=0.06[trilha];[voz][trilha]amix=inputs=2:duration=first[audio_final]",
            "-map", "0:v",
            "-map", "[audio_final]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            str(OUTPUT_FILE)
        ], "Mixar voz nativa + trilha")
    else:
        import shutil
        shutil.copy(str(concat_path), str(OUTPUT_FILE))
        print(f"\n  [TRILHA] Sem trilha — usando apenas áudio nativo")

    # Resultado
    result = subprocess.run([
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration,size",
        "-of", "csv=p=0",
        str(OUTPUT_FILE)
    ], capture_output=True, text=True)

    dur_total, tamanho = result.stdout.strip().split(",")
    print(f"\n{'=' * 55}")
    print(f"  ✓ VÍDEO FINAL GERADO!")
    print(f"  Arquivo: {OUTPUT_FILE.name}")
    print(f"  Duração: {float(dur_total):.2f}s")
    print(f"  Tamanho: {int(tamanho) // 1024 // 1024:.1f} MB")
    print(f"  Resolução: 720x1280 (9:16 TikTok)")
    print(f"  Áudio: nativo com lip-sync real")
    print(f"{'=' * 55}")


if __name__ == "__main__":
    montar()
