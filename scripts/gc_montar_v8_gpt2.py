#!/usr/bin/env python3
"""
gc_montar_v8_gpt2.py — Montagem do Creative 001 v8 (GPT Image 2 + TTS)
Video Anchor | MANUOS IA

Estratégia v8:
- 3 takes de 8s gerados a partir de imagens GPT Image 2 hiper-realistas
- Narração TTS em português brasileiro (Aoede voice)
- Concatenação dos 3 takes (24s total)
- Narração mixada sobre os vídeos
- Trilha de fundo em volume baixo
- Normalização para 1080x1920 (TikTok Shop)
"""
import subprocess
import sys
from pathlib import Path

# ─── Caminhos ─────────────────────────────────────────────────────────────────
REPO = Path("/home/ubuntu/video-anchor")
TAKES_DIR = REPO / "gc_assets" / "takes_v8_new"
OUTPUT_DIR = REPO / "gc_output" / "creative_001_v8"
TRILHA = REPO / "assets" / "trilha_anchor.mp3"
NARRACAO = TAKES_DIR / "narracao_bia_v8.wav"
TEMP = Path("/tmp/ugc_v8_gpt2")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP.mkdir(parents=True, exist_ok=True)

TAKES = [
    TAKES_DIR / "take1_hook_video_v8.mp4",
    TAKES_DIR / "take2_demo_video_v8.mp4",
    TAKES_DIR / "take3_cta_video_v8.mp4",
]

OUTPUT_RAW = OUTPUT_DIR / "creative_001_v8_24s_RAW.mp4"
OUTPUT_FINAL = OUTPUT_DIR / "creative_001_v8_24s_FINAL_1080x1920.mp4"


def run(cmd, desc=""):
    print(f"  → {desc}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [ERRO] {result.stderr[-600:]}")
        sys.exit(1)
    return result


def montar():
    print("=" * 60)
    print("  MONTAGEM UGC v8 — Creative 001 GPT Image 2 + TTS")
    print("  3 takes × 8s = 24s | 1080x1920 | Narração TTS pt-BR")
    print("=" * 60)

    # 1. Normalizar cada take para 720x1280, 24fps, sem áudio
    takes_norm = []
    for i, take in enumerate(TAKES, 1):
        norm = TEMP / f"take{i}_norm.mp4"
        run([
            "ffmpeg", "-y",
            "-i", str(take),
            "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,"
                   "pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-an",
            str(norm)
        ], f"Normalizar take {i} (720x1280, 24fps, sem áudio)")
        takes_norm.append(norm)
        print(f"  [TAKE {i}] ✓ Normalizado")

    # 2. Concatenar os 3 takes (vídeo puro, sem áudio)
    print("\n  [CONCAT] Concatenando 3 takes...")
    concat_list = TEMP / "concat_list.txt"
    with open(concat_list, "w") as f:
        for p in takes_norm:
            f.write(f"file '{p}'\n")

    concat_video = TEMP / "concat_video.mp4"
    run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(concat_video)
    ], "Concatenar 3 takes")

    # 3. Verificar duração da narração
    dur_result = subprocess.run([
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        str(NARRACAO)
    ], capture_output=True, text=True)
    dur_narracao = float(dur_result.stdout.strip())
    print(f"\n  [NARRAÇÃO] Duração: {dur_narracao:.2f}s")

    # 4. Ajustar duração do vídeo para cobrir a narração (se necessário)
    dur_video = 24.0
    if dur_narracao > dur_video:
        # Estender o último take para cobrir a narração
        extra = dur_narracao - dur_video
        print(f"  [NARRAÇÃO] Narração ({dur_narracao:.1f}s) > vídeo ({dur_video:.1f}s)")
        print(f"  [NARRAÇÃO] Estendendo último frame por {extra:.1f}s...")

        # Congelar último frame do take 3
        last_frame = TEMP / "last_frame.png"
        run([
            "ffmpeg", "-y",
            "-sseof", "-0.1",
            "-i", str(concat_video),
            "-vframes", "1",
            str(last_frame)
        ], "Extrair último frame")

        freeze_video = TEMP / "freeze_ext.mp4"
        run([
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(last_frame),
            "-t", str(extra + 0.5),
            "-vf", "scale=720:1280,fps=24",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-an",
            str(freeze_video)
        ], "Gerar extensão com frame congelado")

        ext_list = TEMP / "ext_list.txt"
        with open(ext_list, "w") as f:
            f.write(f"file '{concat_video}'\n")
            f.write(f"file '{freeze_video}'\n")

        concat_extended = TEMP / "concat_extended.mp4"
        run([
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(ext_list),
            "-c", "copy",
            str(concat_extended)
        ], "Concatenar vídeo + extensão")
        concat_video = concat_extended

    # 5. Mixar narração + trilha de fundo sobre o vídeo
    print("\n  [ÁUDIO] Mixando narração TTS + trilha de fundo...")
    if TRILHA.exists():
        run([
            "ffmpeg", "-y",
            "-i", str(concat_video),
            "-i", str(NARRACAO),
            "-i", str(TRILHA),
            "-filter_complex",
            "[1:a]volume=1.0[voz];"
            "[2:a]volume=0.05[trilha];"
            "[voz][trilha]amix=inputs=2:duration=first[audio_final]",
            "-map", "0:v",
            "-map", "[audio_final]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(OUTPUT_RAW)
        ], "Mixar narração + trilha")
    else:
        run([
            "ffmpeg", "-y",
            "-i", str(concat_video),
            "-i", str(NARRACAO),
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(OUTPUT_RAW)
        ], "Adicionar narração (sem trilha)")

    # 6. Upscale para 1080x1920 (TikTok Shop padrão)
    print("\n  [UPSCALE] Normalizando para 1080x1920...")
    run([
        "ffmpeg", "-y",
        "-i", str(OUTPUT_RAW),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,"
               "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,setsar=1",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        str(OUTPUT_FINAL)
    ], "Upscale para 1080x1920")

    # 7. Relatório final
    info = subprocess.run([
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration,size",
        "-of", "csv=p=0",
        str(OUTPUT_FINAL)
    ], capture_output=True, text=True)
    dur, size = info.stdout.strip().split(",")

    print(f"\n{'=' * 60}")
    print(f"  ✓ VÍDEO FINAL v8 GERADO COM SUCESSO!")
    print(f"  Arquivo  : {OUTPUT_FINAL.name}")
    print(f"  Duração  : {float(dur):.2f}s")
    print(f"  Tamanho  : {int(size) // 1024 // 1024:.1f} MB")
    print(f"  Resolução: 1080x1920 (TikTok Shop 9:16)")
    print(f"  Áudio    : Narração TTS pt-BR + trilha de fundo")
    print(f"  Modelo   : GPT Image 2 (hiper-realismo extremo)")
    print(f"{'=' * 60}")

    return OUTPUT_FINAL


if __name__ == "__main__":
    montar()
