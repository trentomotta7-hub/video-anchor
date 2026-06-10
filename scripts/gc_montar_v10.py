import argparse
import subprocess
from pathlib import Path

def run(cmd, description):
    print(f"  [FFMPEG] {description}...")
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"  [FFMPEG] ✓ {description} concluído.")
    except subprocess.CalledProcessError as e:
        print(f"  [FFMPEG] ❌ Erro ao {description}: {e.stderr.decode()}")
        raise

def montar_video_final(video_path: Path, output_path: Path, trilha_path: Path):
    print(f"\n{'='*60}")
    print(f"  MONTAGEM UGC v10 — Vídeo Contínuo (sem banners)")
    print(f"{'='*60}")

    # Normalizar vídeo (resolução, fps)
    temp_normalized_video = video_path.parent / f"{video_path.stem}_normalized.mp4"
    run([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", "scale=720:1280,fps=24",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k",
        str(temp_normalized_video)
    ], "Normalizar vídeo (720x1280, 24fps)")

    # Adicionar trilha de fundo
    if trilha_path.exists():
        run([
            "ffmpeg", "-y",
            "-i", str(temp_normalized_video),
            "-i", str(trilha_path),
            "-filter_complex",
            "[0:a]volume=1.0[voz];[1:a]volume=0.06[trilha];"
            "[voz][trilha]amix=inputs=2:duration=first[audio_final]",
            "-map", "0:v",
            "-map", "[audio_final]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            str(output_path)
        ], "Mixar voz nativa + trilha de fundo")
    else:
        # Se não houver trilha, apenas copia o vídeo normalizado
        run([
            "ffmpeg", "-y",
            "-i", str(temp_normalized_video),
            "-c", "copy",
            str(output_path)
        ], "Copiar vídeo normalizado (sem trilha)")

    print(f"\n{'='*60}")
    print(f"  ✓ VÍDEO FINAL v10 GERADO!")
    print(f"  Arquivo  : {output_path.name}")
    print(f"{'='*60}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Montagem de Vídeo UGC Contínuo v10")
    parser.add_argument("--video", type=str, required=True, help="Caminho para o vídeo contínuo gerado.")
    parser.add_argument("--output", type=str, required=True, help="Caminho para o vídeo final de saída.")
    parser.add_argument("--trilha", type=str, default="", help="Caminho para o arquivo de trilha de fundo (opcional).")
    args = parser.parse_args()

    video_path = Path(args.video)
    output_path = Path(args.output)
    trilha_path = Path(args.trilha) if args.trilha else Path(__file__).parent.parent / "gc_assets" / "trilha_fundo.mp3"

    montar_video_final(video_path, output_path, trilha_path)
