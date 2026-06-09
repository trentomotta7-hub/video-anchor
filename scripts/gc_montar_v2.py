"""
gc_montar_v2.py — Montagem Final UGC v2 com Textos Nativos TikTok
Video Anchor | MANUOS IA

Monta o vídeo final de 24s a partir de 3 takes UGC gerados por IA:
- Normaliza para 720x1280, 24fps
- Concatena os 3 takes com corte direto (sem crossfade — estilo UGC real)
- Queima textos nativos TikTok-style (banner branco com texto preto)
- Mixa narração + trilha de fundo
- Entrega 1 único arquivo MP4 final

Uso:
  python gc_montar_v2.py \
    --take1 path/take1.mp4 \
    --take2 path/take2.mp4 \
    --take3 path/take3.mp4 \
    --audio path/naracao.wav \
    --output path/final.mp4 \
    --texto1 "Texto do take 1" \
    --texto2 "Texto do take 2" \
    --texto3 "Clica para ver o preço"
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_DIR = Path(__file__).parent.parent
TEMP_DIR = REPO_DIR / "gc_assets" / "temp"
OUTPUT_DIR = REPO_DIR / "gc_output"
TRILHA_PATH = REPO_DIR / "assets" / "trilha_anchor.mp3"

TEMP_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WIDTH = 720
HEIGHT = 1280
FPS = 24
MUSIC_VOL = 0.10


def run(cmd, label=""):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [FFMPEG] ✗ Erro em '{label}':\n  {result.stderr[-600:]}")
        raise RuntimeError(f"FFmpeg falhou: {label}")
    return result


def obter_duracao(path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True
    )
    return float(r.stdout.strip())


def normalizar(input_path, output_path, dur=8.0):
    """Normaliza take para 720x1280, 24fps, sem áudio, 8s exatos."""
    run([
        "ffmpeg", "-y", "-i", str(input_path),
        "-vf", f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT},setsar=1",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-r", str(FPS), "-pix_fmt", "yuv420p", "-an",
        "-t", str(dur),
        str(output_path)
    ], f"normalizar {Path(input_path).name}")
    return output_path


def adicionar_texto_nativo(input_path, output_path, texto, t_start=4.0, t_end=7.5):
    """
    Queima um banner branco com texto preto no estilo TikTok/Instagram nativo.
    Aparece de t_start até t_end segundos.
    """
    # Banner branco arredondado com texto preto — estilo nativo TikTok
    # Usamos drawbox + drawtext do FFmpeg
    margem_h = 30
    banner_h = 70
    banner_y = HEIGHT - banner_h - margem_h
    banner_x = 40
    banner_w = WIDTH - 80

    # Texto centralizado no banner
    texto_y = banner_y + (banner_h // 2)

    vf = (
        # Banner branco arredondado (usando drawbox)
        f"drawbox=x={banner_x}:y={banner_y}:w={banner_w}:h={banner_h}"
        f":color=white@0.92:t=fill"
        f":enable='between(t,{t_start},{t_end})',"
        # Texto preto centralizado
        f"drawtext=text='{texto}'"
        f":fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        f":fontsize=28:fontcolor=black"
        f":x=(w-text_w)/2:y={texto_y}-(text_h/2)"
        f":enable='between(t,{t_start},{t_end})'"
    )

    run([
        "ffmpeg", "-y", "-i", str(input_path),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-r", str(FPS), "-pix_fmt", "yuv420p", "-an",
        str(output_path)
    ], f"texto nativo: {texto[:30]}")
    return output_path


def concatenar_direto(takes, output_path):
    """Concatena 3 takes com corte direto (sem crossfade — estilo UGC real)."""
    concat_list = TEMP_DIR / "concat_list.txt"
    with open(concat_list, "w") as f:
        for t in takes:
            f.write(f"file '{str(t)}'\n")

    run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-r", str(FPS), "-pix_fmt", "yuv420p", "-an",
        str(output_path)
    ], "concatenar takes")
    return output_path


def mixar_audio(video_path, audio_path, output_path, duracao_total):
    """Mixa narração + trilha de fundo."""
    usar_trilha = TRILHA_PATH.exists()

    if usar_trilha:
        run([
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-stream_loop", "-1", "-i", str(TRILHA_PATH),
            "-filter_complex",
            f"[1:a]volume=1.0[naracao];"
            f"[2:a]atrim=0:{duracao_total},volume={MUSIC_VOL},"
            f"afade=t=in:st=0:d=1,afade=t=out:st={duracao_total-1}:d=1[trilha];"
            f"[naracao][trilha]amix=inputs=2:duration=first:dropout_transition=2[audio]",
            "-map", "0:v", "-map", "[audio]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-t", str(duracao_total), "-movflags", "+faststart",
            str(output_path)
        ], "mixagem com trilha")
    else:
        run([
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-t", str(duracao_total), "-movflags", "+faststart",
            str(output_path)
        ], "mixagem sem trilha")
    return output_path


def montar(take1, take2, take3, audio_path, output_path,
           texto1, texto2, texto3, dur_take=8.0):

    print(f"\n{'='*55}")
    print(f"MONTAGEM UGC v2")
    print(f"{'='*55}")

    # 1. Normalizar takes
    print("\n  [1/4] Normalizando takes...")
    n1 = TEMP_DIR / "v2_norm1.mp4"
    n2 = TEMP_DIR / "v2_norm2.mp4"
    n3 = TEMP_DIR / "v2_norm3.mp4"
    normalizar(take1, n1, dur_take)
    normalizar(take2, n2, dur_take)
    normalizar(take3, n3, dur_take)
    print("  ✓ Takes normalizados")

    # 2. Adicionar textos nativos em cada take
    print("\n  [2/4] Adicionando textos nativos...")
    t1_txt = TEMP_DIR / "v2_t1_txt.mp4"
    t2_txt = TEMP_DIR / "v2_t2_txt.mp4"
    t3_txt = TEMP_DIR / "v2_t3_txt.mp4"

    # Take 1: texto aparece de 3s a 7s
    adicionar_texto_nativo(n1, t1_txt, texto1, t_start=3.0, t_end=7.5)
    # Take 2: texto aparece de 3s a 7s
    adicionar_texto_nativo(n2, t2_txt, texto2, t_start=3.0, t_end=7.5)
    # Take 3: texto CTA aparece de 2s a 7.5s
    adicionar_texto_nativo(n3, t3_txt, texto3, t_start=2.0, t_end=7.5)
    print("  ✓ Textos adicionados")

    # 3. Concatenar
    print("\n  [3/4] Concatenando takes...")
    video_base = TEMP_DIR / "v2_base.mp4"
    concatenar_direto([t1_txt, t2_txt, t3_txt], video_base)
    print("  ✓ Takes concatenados")

    # 4. Mixar áudio
    print("\n  [4/4] Mixando áudio...")
    duracao_audio = obter_duracao(str(audio_path))
    mixar_audio(video_base, audio_path, output_path, duracao_audio)

    size = Path(output_path).stat().st_size / (1024 * 1024)
    dur = obter_duracao(str(output_path))
    print(f"\n{'='*55}")
    print(f"✓ VÍDEO FINAL PRONTO!")
    print(f"  {output_path}")
    print(f"  Duração: {dur:.1f}s | {WIDTH}x{HEIGHT} | {FPS}fps | {size:.1f}MB")
    print(f"{'='*55}")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--take1", required=True)
    parser.add_argument("--take2", required=True)
    parser.add_argument("--take3", required=True)
    parser.add_argument("--audio", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--texto1", default="Eu não aguentava mais ver rugas no espelho")
    parser.add_argument("--texto2", default="Esse creme mudou minha pele em 30 dias")
    parser.add_argument("--texto3", default="Clica para ver o preço")
    parser.add_argument("--dur-take", type=float, default=8.0)
    args = parser.parse_args()

    for p in [args.take1, args.take2, args.take3, args.audio]:
        if not Path(p).exists():
            print(f"ERRO: Arquivo não encontrado: {p}")
            sys.exit(1)

    montar(
        take1=args.take1,
        take2=args.take2,
        take3=args.take3,
        audio_path=args.audio,
        output_path=args.output,
        texto1=args.texto1,
        texto2=args.texto2,
        texto3=args.texto3,
        dur_take=args.dur_take,
    )
