import subprocess
import os

# Caminhos dos assets
LOGO_IMG = "/home/ubuntu/video-anchor/assets/logo_intro.png"
PRESENTER_IMG = "/home/ubuntu/video-anchor/assets/presenter_16x9.png"
TRILHA = "/home/ubuntu/video-anchor/assets/trilha_anchor.mp3"
VOZES_DIR = "/home/ubuntu/video-anchor/assets/vozes"
OUTPUT_DIR = "/home/ubuntu/video-anchor/videos"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configurações
LOGO_DURATION = 3.0   # segundos de abertura/fechamento da logo
FADE_DURATION = 1.0   # segundos de fade in/out
MUSIC_VOLUME = 0.12   # volume da trilha de fundo (12% para não cobrir a voz)
VOICE_VOLUME = 1.0    # volume da voz

roteiros = [
    {"id": "01", "titulo": "Comercial_Direto"},
    {"id": "02", "titulo": "Processo_Autoridade"},
    {"id": "03", "titulo": "Cena_Network"},
    {"id": "04", "titulo": "Remarketing"},
]

def get_duration(filepath):
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", filepath],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())

def montar_video(roteiro):
    rid = roteiro["id"]
    titulo = roteiro["titulo"]
    voz_path = f"{VOZES_DIR}/roteiro_{rid}_voz.wav"
    output_path = f"{OUTPUT_DIR}/video_{rid}_{titulo}.mp4"

    voz_dur = get_duration(voz_path)
    total_dur = LOGO_DURATION + voz_dur + LOGO_DURATION

    print(f"\n[Roteiro {rid}] Duração voz: {voz_dur:.1f}s | Total: {total_dur:.1f}s")
    print(f"  Saída: {output_path}")

    # Comando ffmpeg para montar o vídeo completo:
    # - Abertura: logo com fade in (3s)
    # - Corpo: imagem da apresentadora com a voz (duração da voz)
    # - Fechamento: logo com fade out (3s)
    # - Trilha de fundo em todo o vídeo com volume baixo
    # - Voz começa após a abertura da logo

    cmd = [
        "ffmpeg", "-y",
        # Inputs
        "-loop", "1", "-t", str(total_dur), "-i", LOGO_IMG,        # 0: logo (loop)
        "-loop", "1", "-t", str(total_dur), "-i", PRESENTER_IMG,   # 1: apresentadora (loop)
        "-i", voz_path,                                              # 2: voz
        "-stream_loop", "-1", "-i", TRILHA,                         # 3: trilha (loop)

        # Filtros de vídeo e áudio
        "-filter_complex",
        f"""
        [0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,
        fade=t=in:st=0:d={FADE_DURATION},fade=t=out:st={LOGO_DURATION - FADE_DURATION}:d={FADE_DURATION}[logo_open];

        [1:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1[presenter];

        [0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,
        fade=t=in:st=0:d={FADE_DURATION},fade=t=out:st={LOGO_DURATION - FADE_DURATION}:d={FADE_DURATION}[logo_close];

        [logo_open][presenter][logo_close]concat=n=3:v=1:a=0[v_out];

        [2:a]adelay={int(LOGO_DURATION * 1000)}|{int(LOGO_DURATION * 1000)},volume={VOICE_VOLUME}[voice_delayed];
        [3:a]atrim=0:{total_dur},volume={MUSIC_VOLUME},afade=t=in:st=0:d=2,afade=t=out:st={total_dur - 2}:d=2[music_trimmed];
        [voice_delayed][music_trimmed]amix=inputs=2:duration=longest[a_out]
        """,

        "-map", "[v_out]",
        "-map", "[a_out]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-r", "30",
        "-pix_fmt", "yuv420p",
        "-t", str(total_dur),
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"  OK! Arquivo: {size:.1f} MB")
    else:
        print(f"  ERRO: {result.stderr[-500:]}")

    return result.returncode

for r in roteiros:
    montar_video(r)

print("\n\nTodos os vídeos processados!")
