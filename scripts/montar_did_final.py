import subprocess
import os

TALKS_DIR = "/home/ubuntu/video-anchor/videos_did"
LOGO = "/home/ubuntu/video-anchor/assets/logo_intro.png"
TRILHA = "/home/ubuntu/video-anchor/assets/trilha_anchor.mp3"
OUTPUT_DIR = "/home/ubuntu/video-anchor/videos_final"
os.makedirs(OUTPUT_DIR, exist_ok=True)

LOGO_DUR = 3.0
FADE = 1.0
MUSIC_VOL = 0.10

roteiros = [
    {"id": "01", "titulo": "Comercial_Direto"},
    {"id": "02", "titulo": "Processo_Autoridade"},
    {"id": "03", "titulo": "Cena_Network"},
    {"id": "04", "titulo": "Remarketing"},
]

def get_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True
    )
    return float(r.stdout.strip())

def run(cmd, label=""):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ERRO [{label}]: {r.stderr[-400:]}")
        raise RuntimeError(label)

for rot in roteiros:
    rid = rot["id"]
    titulo = rot["titulo"]
    talk_path = f"{TALKS_DIR}/talk_{rid}_{titulo}.mp4"
    output = f"{OUTPUT_DIR}/video_{rid}_{titulo}_FINAL.mp4"

    talk_dur = get_duration(talk_path)
    total_dur = LOGO_DUR + talk_dur + LOGO_DUR

    print(f"\n=== Roteiro {rid}: {titulo} ===")
    print(f"  Talk: {talk_dur:.1f}s | Total: {total_dur:.1f}s")

    # 1. Escalar o talk para 1920x1080 mantendo proporção
    run([
        "ffmpeg", "-y", "-i", talk_path,
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1",
        "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-r", "30",
        "-c:a", "aac", "-b:a", "192k",
        f"/tmp/talk_scaled_{rid}.mp4"
    ], "scale talk")

    # 2. Criar logo abertura e fechamento
    for tag, path in [("open", f"/tmp/logo_open_{rid}.mp4"), ("close", f"/tmp/logo_close_{rid}.mp4")]:
        run([
            "ffmpeg", "-y",
            "-loop", "1", "-t", str(LOGO_DUR), "-i", LOGO,
            "-vf", f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fade=t=in:st=0:d={FADE},fade=t=out:st={LOGO_DUR-FADE}:d={FADE}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-r", "30", "-an",
            path
        ], f"logo {tag}")

    # 3. Concatenar logo + talk + logo
    concat_list = f"/tmp/concat_final_{rid}.txt"
    with open(concat_list, "w") as f:
        f.write(f"file '/tmp/logo_open_{rid}.mp4'\n")
        f.write(f"file '/tmp/talk_scaled_{rid}.mp4'\n")
        f.write(f"file '/tmp/logo_close_{rid}.mp4'\n")

    run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_list,
        "-c:v", "libx264", "-preset", "fast", "-crf", "17",
        "-c:a", "aac", "-b:a", "192k",
        f"/tmp/concat_{rid}.mp4"
    ], "concat")

    # 4. Adicionar trilha de fundo
    # O concat só tem vídeo (logo é muda). O áudio vem do talk original com delay do logo.
    voz_delay_ms = int(LOGO_DUR * 1000)
    run([
        "ffmpeg", "-y",
        "-i", f"/tmp/concat_{rid}.mp4",          # 0: vídeo
        "-i", f"/tmp/talk_scaled_{rid}.mp4",     # 1: áudio do talk
        "-stream_loop", "-1", "-i", TRILHA,      # 2: trilha
        "-filter_complex",
        f"[1:a]adelay={voz_delay_ms}|{voz_delay_ms},volume=1.0[voz];"
        f"[2:a]atrim=0:{total_dur},volume={MUSIC_VOL},afade=t=in:st=0:d=2,afade=t=out:st={total_dur-2}:d=2[music];"
        f"[voz][music]amix=inputs=2:duration=first[audio_out]",
        "-map", "0:v",
        "-map", "[audio_out]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(total_dur),
        output
    ], "trilha")

    size = os.path.getsize(output) / (1024*1024)
    print(f"  PRONTO: {output} ({size:.1f} MB)")

print("\n=== TODOS OS VÍDEOS FINAIS PRONTOS ===")
import subprocess
result = subprocess.run(["ls", "-lh", OUTPUT_DIR], capture_output=True, text=True)
print(result.stdout)
