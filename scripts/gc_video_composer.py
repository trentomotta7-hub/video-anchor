"""
gc_video_composer.py — Composição e Montagem Final do Vídeo GC
Video Anchor | MANUOS IA

Transforma 3 imagens + áudio + legendas em um vídeo final de 25s para TikTok Shop.
Estrutura: 3 takes de ~8s com efeito Ken Burns (zoom/pan), transições suaves e legendas.

Formato de saída: MP4, 1080x1920 (9:16 TikTok), 30fps, H.264

Uso:
  python gc_video_composer.py --meta gc_assets/images/produto_meta.json
  python gc_video_composer.py --json produto.json
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# ============================================================
# CONFIGURAÇÃO
# ============================================================
REPO_DIR = Path(__file__).parent.parent
ASSETS_DIR = REPO_DIR / "gc_assets"
TEMP_DIR = ASSETS_DIR / "temp"
OUTPUT_DIR = REPO_DIR / "gc_output"
TRILHA_PATH = REPO_DIR / "assets" / "trilha_anchor.mp3"

TEMP_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Especificações de vídeo
WIDTH = 1080
HEIGHT = 1920
FPS = 30
TAKE_DURATION = 8.0        # Duração de cada take em segundos
TOTAL_DURATION = 25.0      # Duração total do vídeo
CROSSFADE_DURATION = 0.5   # Duração da transição entre takes
MUSIC_VOLUME = 0.15        # Volume da trilha de fundo (0.0 a 1.0)

# Estilo das legendas (TikTok style)
SUBTITLE_STYLE = (
    "FontName=Montserrat Bold,"
    "FontSize=22,"
    "PrimaryColour=&H00FFFFFF,"
    "OutlineColour=&H00000000,"
    "BackColour=&H80000000,"
    "Bold=1,"
    "Outline=3,"
    "Shadow=1,"
    "Alignment=2,"
    "MarginV=120"
)

# ============================================================
# UTILITÁRIOS
# ============================================================

def run(cmd: list, label: str = "") -> subprocess.CompletedProcess:
    """Executa um comando FFmpeg e lança exceção em caso de erro."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [VIDEO] ✗ Erro em '{label}':")
        print(f"  {result.stderr[-500:]}")
        raise RuntimeError(f"FFmpeg falhou: {label}")
    return result


def obter_duracao(path: str) -> float:
    """Obtém duração de um arquivo de mídia via ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", path],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    return float(data.get("format", {}).get("duration", TAKE_DURATION))


# ============================================================
# CRIAÇÃO DOS TAKES (Ken Burns Effect)
# ============================================================

def criar_take_ken_burns(imagem_path: str, take_id: int, duracao: float, prefixo: str) -> Path:
    """
    Transforma uma imagem estática em um take de vídeo com efeito Ken Burns.
    Cada take tem um movimento diferente para variedade visual.
    """
    output_path = TEMP_DIR / f"{prefixo}_take{take_id}.mp4"

    # Movimentos Ken Burns diferentes para cada take
    movimentos = {
        1: {  # Take 1 (Vontade): Zoom in suave no centro
            "zoompan": f"z='min(zoom+0.0015,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(duracao*FPS)}:s={WIDTH}x{HEIGHT}:fps={FPS}"
        },
        2: {  # Take 2 (Dor/Urgência): Pan da esquerda para direita
            "zoompan": f"z='1.2':x='if(gte(on,1),x+1.5,0)':y='ih/2-(ih/zoom/2)':d={int(duracao*FPS)}:s={WIDTH}x{HEIGHT}:fps={FPS}"
        },
        3: {  # Take 3 (Solução): Zoom out suave (revela)
            "zoompan": f"z='if(lte(zoom,1.0),1.3,max(1.0,zoom-0.0015))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(duracao*FPS)}:s={WIDTH}x{HEIGHT}:fps={FPS}"
        }
    }

    movimento = movimentos.get(take_id, movimentos[1])
    zoompan_filter = movimento["zoompan"]

    # Filtro completo: escala, Ken Burns, fade in/out
    fade_dur = 0.4
    vf = (
        f"scale=iw*max({WIDTH}/iw\\,{HEIGHT}/ih):ih*max({WIDTH}/iw\\,{HEIGHT}/ih),"
        f"crop={WIDTH}:{HEIGHT},"
        f"{zoompan_filter},"
        f"fade=t=in:st=0:d={fade_dur},"
        f"fade=t=out:st={duracao - fade_dur}:d={fade_dur}"
    )

    run([
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(imagem_path),
        "-t", str(duracao),
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-r", str(FPS),
        "-pix_fmt", "yuv420p",
        "-an",
        str(output_path)
    ], f"take {take_id} Ken Burns")

    print(f"  [VIDEO] ✓ Take {take_id} criado: {output_path.name}")
    return output_path


# ============================================================
# CONCATENAÇÃO COM CROSSFADE
# ============================================================

def concatenar_takes_crossfade(takes: list, prefixo: str) -> Path:
    """
    Concatena os 3 takes com transição crossfade entre eles.
    Usa o filtro xfade do FFmpeg.
    """
    output_path = TEMP_DIR / f"{prefixo}_video_base.mp4"

    if len(takes) == 1:
        # Apenas 1 take, copia direto
        run(["ffmpeg", "-y", "-i", str(takes[0]), "-c", "copy", str(output_path)], "copy único take")
        return output_path

    if len(takes) == 2:
        # 2 takes com xfade
        dur1 = obter_duracao(str(takes[0]))
        offset = dur1 - CROSSFADE_DURATION
        run([
            "ffmpeg", "-y",
            "-i", str(takes[0]),
            "-i", str(takes[1]),
            "-filter_complex",
            f"[0:v][1:v]xfade=transition=fade:duration={CROSSFADE_DURATION}:offset={offset}[v]",
            "-map", "[v]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-r", str(FPS), "-pix_fmt", "yuv420p",
            str(output_path)
        ], "xfade 2 takes")
        return output_path

    # 3 takes com 2 xfades encadeados
    dur1 = obter_duracao(str(takes[0]))
    dur2 = obter_duracao(str(takes[1]))
    offset1 = dur1 - CROSSFADE_DURATION
    offset2 = dur1 + dur2 - CROSSFADE_DURATION * 2

    run([
        "ffmpeg", "-y",
        "-i", str(takes[0]),
        "-i", str(takes[1]),
        "-i", str(takes[2]),
        "-filter_complex",
        f"[0:v][1:v]xfade=transition=fade:duration={CROSSFADE_DURATION}:offset={offset1}[v01];"
        f"[v01][2:v]xfade=transition=fade:duration={CROSSFADE_DURATION}:offset={offset2}[v]",
        "-map", "[v]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-r", str(FPS), "-pix_fmt", "yuv420p",
        str(output_path)
    ], "xfade 3 takes")

    print(f"  [VIDEO] ✓ Takes concatenados com crossfade: {output_path.name}")
    return output_path


# ============================================================
# ADICIONAR LEGENDAS
# ============================================================

def adicionar_legendas(video_path: Path, srt_path: str, prefixo: str) -> Path:
    """Queima as legendas no vídeo usando o filtro subtitles do FFmpeg."""
    output_path = TEMP_DIR / f"{prefixo}_legendado.mp4"

    # Escapar o caminho do SRT para o filtro
    srt_escaped = str(srt_path).replace("\\", "/").replace(":", "\\:")

    run([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", f"subtitles='{srt_escaped}':force_style='{SUBTITLE_STYLE}'",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-r", str(FPS), "-pix_fmt", "yuv420p",
        "-an",
        str(output_path)
    ], "legendas")

    print(f"  [VIDEO] ✓ Legendas adicionadas: {output_path.name}")
    return output_path


# ============================================================
# MIXAGEM DE ÁUDIO
# ============================================================

def mixar_audio(video_path: Path, audio_naracao: str, duracao_total: float,
                prefixo: str, trilha_path: str = None) -> Path:
    """
    Adiciona a narração e a trilha de fundo ao vídeo.
    A narração tem prioridade; a trilha fica em segundo plano.
    """
    output_path = OUTPUT_DIR / f"{prefixo}_FINAL.mp4"

    # Verificar se a trilha existe
    usar_trilha = trilha_path and Path(trilha_path).exists()

    if usar_trilha:
        run([
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(audio_naracao),
            "-stream_loop", "-1", "-i", str(trilha_path),
            "-filter_complex",
            f"[1:a]volume=1.0[naracao];"
            f"[2:a]atrim=0:{duracao_total},volume={MUSIC_VOLUME},"
            f"afade=t=in:st=0:d=1,afade=t=out:st={duracao_total - 1}:d=1[trilha];"
            f"[naracao][trilha]amix=inputs=2:duration=first:dropout_transition=2[audio_out]",
            "-map", "0:v",
            "-map", "[audio_out]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(duracao_total),
            "-movflags", "+faststart",
            str(output_path)
        ], "mixagem áudio com trilha")
    else:
        run([
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(audio_naracao),
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(duracao_total),
            "-movflags", "+faststart",
            str(output_path)
        ], "mixagem áudio sem trilha")

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  [VIDEO] ✓ VÍDEO FINAL: {output_path.name} ({size_mb:.1f} MB)")
    return output_path


# ============================================================
# PIPELINE COMPLETO DE COMPOSIÇÃO
# ============================================================

def compor_video_final(imagens: dict, audio_meta: dict, prefixo: str = "produto") -> Path:
    """
    Pipeline completo de composição:
    1. Cria 3 takes com Ken Burns a partir das imagens
    2. Concatena com crossfade
    3. Adiciona legendas
    4. Mixa áudio (narração + trilha)
    5. Exporta vídeo final
    """
    print(f"\n{'='*50}")
    print(f"COMPOSIÇÃO DE VÍDEO: {prefixo}")
    print(f"{'='*50}")

    # Verificar imagens disponíveis
    imagens_ordenadas = []
    for angulo in ["angulo_1", "angulo_2", "angulo_3"]:
        path = imagens.get(angulo)
        if path and Path(path).exists():
            imagens_ordenadas.append(path)
        else:
            print(f"  [VIDEO] ⚠ Imagem ausente: {angulo}")

    if len(imagens_ordenadas) < 1:
        raise ValueError("Nenhuma imagem disponível para composição")

    # Ajustar duração por take baseado no número de imagens
    n_takes = len(imagens_ordenadas)
    duracao_por_take = TOTAL_DURATION / n_takes

    # Etapa 1: Criar takes com Ken Burns
    print(f"\n  [VIDEO] Criando {n_takes} takes...")
    takes = []
    for i, img_path in enumerate(imagens_ordenadas, 1):
        take_path = criar_take_ken_burns(img_path, i, duracao_por_take, prefixo)
        takes.append(take_path)

    # Etapa 2: Concatenar takes com crossfade
    print(f"\n  [VIDEO] Concatenando takes com crossfade...")
    video_base = concatenar_takes_crossfade(takes, prefixo)

    # Etapa 3: Adicionar legendas
    srt_path = audio_meta.get("srt", "")
    if srt_path and Path(srt_path).exists():
        print(f"\n  [VIDEO] Adicionando legendas...")
        video_legendado = adicionar_legendas(video_base, srt_path, prefixo)
    else:
        print(f"  [VIDEO] ⚠ SRT não encontrado, pulando legendas")
        video_legendado = video_base

    # Etapa 4: Mixar áudio
    print(f"\n  [VIDEO] Mixando áudio...")
    audio_naracao = audio_meta.get("audio_completo", "")
    duracao_total = audio_meta.get("duracao_total", TOTAL_DURATION)

    # Garantir duração mínima de 25s
    duracao_final = max(duracao_total, TOTAL_DURATION)

    trilha = str(TRILHA_PATH) if TRILHA_PATH.exists() else None
    video_final = mixar_audio(video_legendado, audio_naracao, duracao_final, prefixo, trilha)

    print(f"\n{'='*50}")
    print(f"✓ VÍDEO FINAL PRONTO: {video_final}")
    print(f"  Duração: {duracao_final:.1f}s | Takes: {n_takes} | Formato: {WIDTH}x{HEIGHT}")
    print(f"{'='*50}")

    return video_final


# ============================================================
# CLI
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compõe o vídeo final de 25s para TikTok Shop")
    parser.add_argument("--imagens-meta", type=str, help="JSON de metadados das imagens")
    parser.add_argument("--audio-meta", type=str, help="JSON de metadados do áudio")
    parser.add_argument("--prefixo", type=str, default="produto", help="Prefixo para os arquivos")

    args = parser.parse_args()

    if not args.imagens_meta or not args.audio_meta:
        print("Erro: Forneça --imagens-meta e --audio-meta")
        sys.exit(1)

    with open(args.imagens_meta, encoding="utf-8") as f:
        img_meta = json.load(f)

    with open(args.audio_meta, encoding="utf-8") as f:
        aud_meta = json.load(f)

    video = compor_video_final(img_meta.get("imagens", {}), aud_meta, args.prefixo)
    print(f"\nVídeo final: {video}")
