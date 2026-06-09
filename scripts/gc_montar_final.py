"""
gc_montar_final.py — Montagem Final do Vídeo GC de 25s
Video Anchor | MANUOS IA

Monta o vídeo final a partir de:
- 3 imagens ultra-realistas (9:16)
- Narração TTS (WAV)
- Roteiro JSON (para legendas)

Estrutura:
  Take 1 (0-9.3s):  Imagem 1 + Ken Burns zoom-in
  Take 2 (9.3-18.6s): Imagem 2 + Ken Burns pan
  Take 3 (18.6-27.9s): Imagem 3 + Ken Burns zoom-out
  Crossfade de 0.5s entre takes
  Legendas TikTok-style queimadas
  Narração + trilha de fundo

Uso:
  python gc_montar_final.py --prefixo creme_facial_test
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_DIR = Path(__file__).parent.parent
ASSETS_DIR = REPO_DIR / "gc_assets"
IMAGES_DIR = ASSETS_DIR / "images"
AUDIO_DIR = ASSETS_DIR / "audio"
TEMP_DIR = ASSETS_DIR / "temp"
OUTPUT_DIR = REPO_DIR / "gc_output"
TRILHA_PATH = REPO_DIR / "assets" / "trilha_anchor.mp3"

TEMP_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WIDTH = 1080
HEIGHT = 1920
FPS = 30
CROSSFADE = 0.5
MUSIC_VOL = 0.12

# Estilo legendas TikTok
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
        print(f"  [FFMPEG] ✗ Erro em '{label}':")
        print(f"  {result.stderr[-600:]}")
        raise RuntimeError(f"FFmpeg falhou: {label}")
    return result


def obter_duracao(path):
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    return float(data.get("format", {}).get("duration", 9.0))


def sec_to_srt(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    ms = int((s % 1) * 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def gerar_srt(roteiro, duracao_total, prefixo):
    """Gera SRT com 3 blocos de legenda baseados no roteiro."""
    srt_path = TEMP_DIR / f"{prefixo}.srt"
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

            # Divide em 2 linhas para melhor leitura
            palavras = texto.split()
            meio = len(palavras) // 2 + 1
            linha1 = " ".join(palavras[:meio])
            linha2 = " ".join(palavras[meio:])

            meio_take = t_start + dur_take * 0.5

            # Primeira metade
            f.write(f"{idx}\n{sec_to_srt(t_start)} --> {sec_to_srt(meio_take - 0.1)}\n{linha1}\n\n")
            idx += 1

            # Segunda metade
            f.write(f"{idx}\n{sec_to_srt(meio_take)} --> {sec_to_srt(t_end)}\n{linha2}\n\n")
            idx += 1

    print(f"  [SRT] ✓ Legendas geradas: {srt_path.name}")
    return srt_path


def criar_take(img_path, take_id, duracao, prefixo):
    """Cria um take de vídeo com efeito Ken Burns a partir de uma imagem."""
    output = TEMP_DIR / f"{prefixo}_take{take_id}.mp4"
    n_frames = int(duracao * FPS)
    fade_dur = 0.3

    # Movimentos Ken Burns por take
    if take_id == 1:
        # Zoom in suave
        zoompan = f"zoompan=z='min(zoom+0.0012,1.25)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n_frames}:s={WIDTH}x{HEIGHT}"
    elif take_id == 2:
        # Pan da esquerda para direita
        zoompan = f"zoompan=z='1.15':x='if(gte(on,1),x+1.2,iw*0.05)':y='ih/2-(ih/zoom/2)':d={n_frames}:s={WIDTH}x{HEIGHT}"
    else:
        # Zoom out (revela)
        zoompan = f"zoompan=z='if(lte(zoom,1.0),1.25,max(1.0,zoom-0.0012))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n_frames}:s={WIDTH}x{HEIGHT}"

    # Etapa 1: escala + crop + zoompan
    vf_zoom = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},"
        f"{zoompan}"
    )

    zoom_tmp = TEMP_DIR / f"{prefixo}_take{take_id}_zoom.mp4"
    run([
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(img_path),
        "-t", str(duracao),
        "-vf", vf_zoom,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-r", str(FPS), "-pix_fmt", "yuv420p", "-an",
        str(zoom_tmp)
    ], f"take {take_id} zoom")

    # Etapa 2: fade in/out
    run([
        "ffmpeg", "-y",
        "-i", str(zoom_tmp),
        "-vf", f"fade=t=in:st=0:d={fade_dur},fade=t=out:st={duracao - fade_dur}:d={fade_dur}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-r", str(FPS), "-pix_fmt", "yuv420p", "-an",
        str(output)
    ], f"take {take_id} fade")

    print(f"  [VIDEO] ✓ Take {take_id}: {output.name}")
    return output


def concatenar_xfade(takes, duracao_take, prefixo):
    """Concatena 3 takes com crossfade xfade."""
    output = TEMP_DIR / f"{prefixo}_video_base.mp4"

    offset1 = duracao_take - CROSSFADE
    offset2 = duracao_take * 2 - CROSSFADE * 2

    run([
        "ffmpeg", "-y",
        "-i", str(takes[0]),
        "-i", str(takes[1]),
        "-i", str(takes[2]),
        "-filter_complex",
        f"[0:v][1:v]xfade=transition=fade:duration={CROSSFADE}:offset={offset1}[v01];"
        f"[v01][2:v]xfade=transition=fade:duration={CROSSFADE}:offset={offset2}[v]",
        "-map", "[v]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-r", str(FPS), "-pix_fmt", "yuv420p",
        str(output)
    ], "xfade concatenação")

    print(f"  [VIDEO] ✓ Takes concatenados: {output.name}")
    return output


def adicionar_legendas(video_path, srt_path, prefixo):
    """Queima legendas no vídeo."""
    output = TEMP_DIR / f"{prefixo}_legendado.mp4"
    srt_str = str(srt_path).replace("\\", "/")

    run([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", f"subtitles='{srt_str}':force_style='{SUBTITLE_STYLE}'",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-r", str(FPS), "-pix_fmt", "yuv420p", "-an",
        str(output)
    ], "legendas")

    print(f"  [VIDEO] ✓ Legendas adicionadas: {output.name}")
    return output


def mixar_audio_final(video_path, audio_path, duracao_total, prefixo):
    """Mixa narração + trilha de fundo e gera o vídeo final."""
    output = OUTPUT_DIR / f"{prefixo}_FINAL.mp4"
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
            f"afade=t=in:st=0:d=1,afade=t=out:st={duracao_total - 1}:d=1[trilha];"
            f"[naracao][trilha]amix=inputs=2:duration=first:dropout_transition=2[audio]",
            "-map", "0:v", "-map", "[audio]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-t", str(duracao_total), "-movflags", "+faststart",
            str(output)
        ], "mixagem com trilha")
    else:
        run([
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-t", str(duracao_total), "-movflags", "+faststart",
            str(output)
        ], "mixagem sem trilha")

    size = output.stat().st_size / (1024 * 1024)
    print(f"  [VIDEO] ✓ VÍDEO FINAL: {output.name} ({size:.1f} MB)")
    return output


def montar_video_gc(prefixo, imagens, audio_path, roteiro, duracao_audio):
    """Pipeline completo de montagem."""
    print(f"\n{'='*55}")
    print(f"MONTAGEM GC: {prefixo}")
    print(f"{'='*55}")

    # Duração por take baseada no áudio real
    duracao_take = duracao_audio / 3

    print(f"\n  Duração total: {duracao_audio:.1f}s | Take: {duracao_take:.1f}s")

    # 1. Criar takes com Ken Burns
    print("\n  [1/4] Criando takes com Ken Burns...")
    takes = []
    for i, img in enumerate(imagens, 1):
        take = criar_take(img, i, duracao_take, prefixo)
        takes.append(take)

    # 2. Concatenar com crossfade
    print("\n  [2/4] Concatenando takes com crossfade...")
    video_base = concatenar_xfade(takes, duracao_take, prefixo)

    # 3. Adicionar legendas
    print("\n  [3/4] Adicionando legendas...")
    srt = gerar_srt(roteiro, duracao_audio, prefixo)
    video_legendado = adicionar_legendas(video_base, srt, prefixo)

    # 4. Mixar áudio
    print("\n  [4/4] Mixando áudio...")
    video_final = mixar_audio_final(video_legendado, audio_path, duracao_audio, prefixo)

    print(f"\n{'='*55}")
    print(f"✓ VÍDEO FINAL PRONTO!")
    print(f"  Arquivo: {video_final}")
    print(f"  Duração: {duracao_audio:.1f}s | Formato: {WIDTH}x{HEIGHT} | {FPS}fps")
    print(f"{'='*55}")

    return video_final


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monta o vídeo GC final de 25s")
    parser.add_argument("--prefixo", type=str, required=True, help="Prefixo dos arquivos")
    args = parser.parse_args()

    prefixo = args.prefixo

    # Carregar imagens
    imagens = [
        IMAGES_DIR / f"{prefixo}_angulo1_desejo.png",
        IMAGES_DIR / f"{prefixo}_angulo2_contexto.png",
        IMAGES_DIR / f"{prefixo}_angulo3_resultado.png",
    ]

    # Verificar imagens
    for img in imagens:
        if not img.exists():
            print(f"ERRO: Imagem não encontrada: {img}")
            sys.exit(1)

    # Carregar áudio
    audio_path = AUDIO_DIR / f"{prefixo}_naracao_completa.wav"
    if not audio_path.exists():
        print(f"ERRO: Áudio não encontrado: {audio_path}")
        sys.exit(1)

    # Carregar roteiro
    roteiro_path = ASSETS_DIR / "inputs" / f"{prefixo}_roteiro.json"
    if roteiro_path.exists():
        with open(roteiro_path, encoding="utf-8") as f:
            dados = json.load(f)
        roteiro = dados.get("roteiro", {})
    else:
        roteiro = {
            "take_1_vontade": "Pele lisinha e hidratada todo dia",
            "take_2_urgencia_dor": "Cada dia sem cuidado é difícil de recuperar",
            "take_3_solucao_cta": "Vitamina C e colágeno. Clica no link agora!"
        }

    # Obter duração do áudio
    duracao = obter_duracao(str(audio_path))

    # Montar vídeo
    video = montar_video_gc(prefixo, imagens, audio_path, roteiro, duracao)
    print(f"\nVídeo gerado: {video}")
