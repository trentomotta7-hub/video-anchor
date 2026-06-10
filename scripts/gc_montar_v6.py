#!/usr/bin/env python3
"""
gc_montar_v6.py — Montagem do vídeo final UGC v6
Video Anchor | MANUOS IA

Monta o vídeo final de 24s a partir dos 3 takes gerados por IA:
- Normaliza cada take para 720x1280, 24fps
- Adiciona áudio TTS sincronizado (estendendo ou cortando o vídeo conforme necessário)
- Adiciona banners estilo TikTok com texto branco em fundo semitransparente
- Concatena os 3 takes com corte direto
- Adiciona trilha de fundo em volume baixo (0.06)
"""

import subprocess
import sys
from pathlib import Path

# ─── Caminhos ─────────────────────────────────────────────────────────────────
REPO = Path("/home/ubuntu/video-anchor")
TAKES_DIR = REPO / "gc_assets" / "takes_v6"
AUDIO_DIR = REPO / "gc_assets"
OUTPUT_DIR = REPO / "gc_output"
TRILHA = REPO / "assets" / "trilha_anchor.mp3"
TEMP = Path("/tmp/ugc_v6")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP.mkdir(parents=True, exist_ok=True)

# ─── Configurações ─────────────────────────────────────────────────────────────
TAKES = [
    {
        "video": TAKES_DIR / "take1_problema.mp4",
        "audio": AUDIO_DIR / "take1_audio.wav",
        "banner": "Rugas incomodando você?",
        "duracao_audio": 9.12,
    },
    {
        "video": TAKES_DIR / "take2_solucao.mp4",
        "audio": AUDIO_DIR / "take2_audio.wav",
        "banner": "Colágeno que transforma",
        "duracao_audio": 9.16,
    },
    {
        "video": TAKES_DIR / "take3_cta.mp4",
        "audio": AUDIO_DIR / "take3_audio.wav",
        "banner": "Clica para ver o preço",
        "duracao_audio": 6.12,
    },
]

OUTPUT_FILE = OUTPUT_DIR / "creme_facial_UGC_v6_FINAL.mp4"

def run(cmd, desc=""):
    """Executa um comando ffmpeg e verifica erros."""
    print(f"  → {desc}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [ERRO] {result.stderr[-300:]}")
        sys.exit(1)

def montar():
    print("=" * 55)
    print("  MONTAGEM UGC v6 — Creme Facial Anti-Idade")
    print("=" * 55)

    takes_prontos = []

    for i, take in enumerate(TAKES, 1):
        dur_audio = take["duracao_audio"]
        # Usar a duração do áudio como duração do take (máx 10s)
        dur_take = min(dur_audio + 0.3, 10.0)
        banner = take["banner"]

        print(f"\n  [TAKE {i}] Processando... (duração: {dur_take:.2f}s)")

        # Passo 1: Normalizar vídeo para 720x1280, 24fps, duração = dur_take
        norm_path = TEMP / f"take{i}_norm.mp4"
        run([
            "ffmpeg", "-y",
            "-i", str(take["video"]),
            "-vf", f"scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24",
            "-t", str(dur_take),
            "-an",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            str(norm_path)
        ], f"Normalizar take {i}")

        # Passo 2: Adicionar banner estilo TikTok (fundo branco semitransparente, texto preto)
        banner_path = TEMP / f"take{i}_banner.mp4"
        # Banner na parte inferior: retângulo branco semitransparente + texto
        # Escapar apóstrofes e caracteres especiais no banner
        banner_safe = banner.replace("'", "\\\\'").replace(":", "\\:")
        drawtext = (
            f"drawbox=x=0:y=ih-120:w=iw:h=120:color=white@0.88:t=fill,"
            f"drawtext=text='{banner_safe}':fontsize=40:fontcolor=black:x=(w-text_w)/2:y=h-78:font=Arial"
        )
        run([
            "ffmpeg", "-y",
            "-i", str(norm_path),
            "-vf", drawtext,
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-an",
            str(banner_path)
        ], f"Adicionar banner take {i}: '{banner}'")

        # Passo 3: Combinar vídeo com áudio TTS
        combined_path = TEMP / f"take{i}_combined.mp4"
        run([
            "ffmpeg", "-y",
            "-i", str(banner_path),
            "-i", str(take["audio"]),
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "128k",
            "-t", str(dur_take),
            "-shortest",
            str(combined_path)
        ], f"Combinar vídeo + áudio take {i}")

        takes_prontos.append(combined_path)
        print(f"  [TAKE {i}] ✓ Pronto")

    # Passo 4: Concatenar os 3 takes
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

    # Passo 5: Adicionar trilha de fundo (se existir)
    if TRILHA.exists():
        print(f"\n  [TRILHA] Adicionando trilha de fundo...")
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
        ], "Mixar voz + trilha")
    else:
        # Sem trilha — apenas renomear
        import shutil
        shutil.copy(str(concat_path), str(OUTPUT_FILE))
        print(f"\n  [TRILHA] Trilha não encontrada — usando apenas voz")

    # Verificar resultado
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
    print(f"{'=' * 55}")

if __name__ == "__main__":
    montar()
