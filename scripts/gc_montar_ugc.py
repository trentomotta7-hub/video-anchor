"""
gc_montar_ugc.py — Montagem Final do Vídeo GC com Takes UGC Reais
Video Anchor | MANUOS IA

Concatena 3 takes de vídeo reais gerados por IA (UGC-style),
adiciona narração, legendas e trilha de fundo.
Entrega um único vídeo final de ~25s para TikTok Shop.

Uso:
  python gc_montar_ugc.py --prefixo creme_facial_test
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_DIR = Path(__file__).parent.parent
ASSETS_DIR = REPO_DIR / "gc_assets"
TEMP_DIR = ASSETS_DIR / "temp"
AUDIO_DIR = ASSETS_DIR / "audio"
OUTPUT_DIR = REPO_DIR / "gc_output"
TRILHA_PATH = REPO_DIR / "assets" / "trilha_anchor.mp3"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WIDTH = 1080
HEIGHT = 1920
FPS = 30
MUSIC_VOL = 0.12

SUBTITLE_STYLE = (
    "FontName=Arial,"
    "FontSize=24,"
    "PrimaryColour=&H00FFFFFF,"
    "OutlineColour=&H00000000,"
    "BackColour=&H80000000,"
    "Bold=1,"
    "Outline=3,"
    "Shadow=1,"
    "Alignment=2,"
    "MarginV=100"
)


def run(cmd, label=""):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [FFMPEG] ✗ Erro em '{label}':\n  {result.stderr[-500:]}")
        raise RuntimeError(f"FFmpeg falhou: {label}")
    return result


def obter_duracao(path):
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def sec_to_srt(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    ms = int((s % 1) * 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def normalizar_take(input_path, output_path, duracao_alvo=None):
    """Normaliza um take para 720x1280, 30fps, sem áudio."""
    vf = f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT},setsar=1"
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-r", str(FPS), "-pix_fmt", "yuv420p", "-an",
    ]
    if duracao_alvo:
        cmd += ["-t", str(duracao_alvo)]
    cmd.append(str(output_path))
    run(cmd, f"normalizar {Path(input_path).name}")
    return output_path


def gerar_srt(roteiro, duracao_total, srt_path):
    """Gera SRT com 3 blocos de legenda."""
    dur_take = duracao_total / 3
    takes = [
        roteiro.get("take_1_vontade", ""),
        roteiro.get("take_2_urgencia_dor", ""),
        roteiro.get("take_3_solucao_cta", ""),
    ]
    with open(srt_path, "w", encoding="utf-8") as f:
        idx = 1
        for i, texto in enumerate(takes):
            if not texto:
                continue
            t_start = i * dur_take
            t_end = (i + 1) * dur_take - 0.3
            palavras = texto.split()
            meio = max(1, len(palavras) // 2)
            linha1 = " ".join(palavras[:meio])
            linha2 = " ".join(palavras[meio:])
            meio_take = t_start + dur_take * 0.5
            f.write(f"{idx}\n{sec_to_srt(t_start)} --> {sec_to_srt(meio_take - 0.1)}\n{linha1}\n\n")
            idx += 1
            f.write(f"{idx}\n{sec_to_srt(meio_take)} --> {sec_to_srt(t_end)}\n{linha2}\n\n")
            idx += 1
    print(f"  [SRT] ✓ Legendas: {Path(srt_path).name}")
    return srt_path


def montar_video_ugc(prefixo, takes_paths, audio_path, roteiro, duracao_audio):
    """
    Monta o vídeo final:
    1. Normaliza os 3 takes para o mesmo formato
    2. Concatena com crossfade
    3. Adiciona legendas
    4. Mixa narração + trilha
    """
    print(f"\n{'='*55}")
    print(f"MONTAGEM UGC: {prefixo}")
    print(f"{'='*55}")

    dur_take = duracao_audio / 3
    print(f"  Duração total: {duracao_audio:.1f}s | Take: {dur_take:.1f}s cada")

    # 1. Normalizar takes
    print("\n  [1/4] Normalizando takes...")
    norm_takes = []
    for i, tp in enumerate(takes_paths, 1):
        out = TEMP_DIR / f"{prefixo}_norm_take{i}.mp4"
        normalizar_take(tp, out, dur_take)
        norm_takes.append(out)
        print(f"  [VIDEO] ✓ Take {i} normalizado: {out.name}")

    # 2. Concatenar com crossfade
    print("\n  [2/4] Concatenando takes com crossfade...")
    CROSSFADE = 0.4
    offset1 = dur_take - CROSSFADE
    offset2 = dur_take * 2 - CROSSFADE * 2

    video_base = TEMP_DIR / f"{prefixo}_video_base.mp4"
    run([
        "ffmpeg", "-y",
        "-i", str(norm_takes[0]),
        "-i", str(norm_takes[1]),
        "-i", str(norm_takes[2]),
        "-filter_complex",
        f"[0:v][1:v]xfade=transition=fade:duration={CROSSFADE}:offset={offset1}[v01];"
        f"[v01][2:v]xfade=transition=fade:duration={CROSSFADE}:offset={offset2}[v]",
        "-map", "[v]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-r", str(FPS), "-pix_fmt", "yuv420p",
        str(video_base)
    ], "xfade concatenação")
    print(f"  [VIDEO] ✓ Takes concatenados: {video_base.name}")

    # 3. Legendas
    print("\n  [3/4] Adicionando legendas...")
    srt_path = TEMP_DIR / f"{prefixo}_legendas.srt"
    gerar_srt(roteiro, duracao_audio, srt_path)

    video_legendado = TEMP_DIR / f"{prefixo}_legendado.mp4"
    srt_str = str(srt_path).replace("\\", "/")
    run([
        "ffmpeg", "-y",
        "-i", str(video_base),
        "-vf", f"subtitles='{srt_str}':force_style='{SUBTITLE_STYLE}'",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-r", str(FPS), "-pix_fmt", "yuv420p", "-an",
        str(video_legendado)
    ], "legendas")
    print(f"  [VIDEO] ✓ Legendas adicionadas")

    # 4. Mixar áudio
    print("\n  [4/4] Mixando narração + trilha...")
    output = OUTPUT_DIR / f"{prefixo}_FINAL_UGC.mp4"
    usar_trilha = TRILHA_PATH.exists()

    if usar_trilha:
        run([
            "ffmpeg", "-y",
            "-i", str(video_legendado),
            "-i", str(audio_path),
            "-stream_loop", "-1", "-i", str(TRILHA_PATH),
            "-filter_complex",
            f"[1:a]volume=1.0[naracao];"
            f"[2:a]atrim=0:{duracao_audio},volume={MUSIC_VOL},"
            f"afade=t=in:st=0:d=1,afade=t=out:st={duracao_audio - 1}:d=1[trilha];"
            f"[naracao][trilha]amix=inputs=2:duration=first:dropout_transition=2[audio]",
            "-map", "0:v", "-map", "[audio]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-t", str(duracao_audio), "-movflags", "+faststart",
            str(output)
        ], "mixagem com trilha")
    else:
        run([
            "ffmpeg", "-y",
            "-i", str(video_legendado),
            "-i", str(audio_path),
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-t", str(duracao_audio), "-movflags", "+faststart",
            str(output)
        ], "mixagem sem trilha")

    size = output.stat().st_size / (1024 * 1024)
    print(f"\n{'='*55}")
    print(f"✓ VÍDEO FINAL PRONTO!")
    print(f"  {output}")
    print(f"  Duração: {duracao_audio:.1f}s | {WIDTH}x{HEIGHT} | {FPS}fps | {size:.1f}MB")
    print(f"{'='*55}")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefixo", required=True)
    args = parser.parse_args()
    prefixo = args.prefixo

    takes = [
        TEMP_DIR / "take1_vontade.mp4",
        TEMP_DIR / "take2_dor.mp4",
        TEMP_DIR / "take3_solucao.mp4",
    ]
    for t in takes:
        if not t.exists():
            print(f"ERRO: Take não encontrado: {t}")
            sys.exit(1)

    audio_path = AUDIO_DIR / f"{prefixo}_naracao_completa.wav"
    if not audio_path.exists():
        print(f"ERRO: Áudio não encontrado: {audio_path}")
        sys.exit(1)

    roteiro_path = ASSETS_DIR / "inputs" / f"{prefixo}_roteiro.json"
    if roteiro_path.exists():
        with open(roteiro_path, encoding="utf-8") as f:
            dados = json.load(f)
        roteiro = dados.get("roteiro", {})
    else:
        roteiro = {}

    duracao = obter_duracao(str(audio_path))
    video = montar_video_ugc(prefixo, takes, audio_path, roteiro, duracao)
    print(f"\nVídeo final: {video}")
