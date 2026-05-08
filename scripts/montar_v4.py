import subprocess
import os

# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================
CLIPS = [
    "/home/ubuntu/video-anchor/clips/presenter_v3_base.mp4",
    "/home/ubuntu/video-anchor/clips/presenter_v3_b.mp4",
    "/home/ubuntu/video-anchor/clips/presenter_v3_c.mp4",
]
VOZES_DIR = "/home/ubuntu/video-anchor/assets/vozes"
LOGO = "/home/ubuntu/video-anchor/assets/logo_intro.png"
TRILHA = "/home/ubuntu/video-anchor/assets/trilha_anchor.mp3"
OUTPUT_DIR = "/home/ubuntu/video-anchor/videos_v4"
os.makedirs(OUTPUT_DIR, exist_ok=True)

LOGO_DUR = 3.0
FADE = 1.0
MUSIC_VOL = 0.10
GROOVER_URL = "groover.co/band/signup/referral/influencer/26997"

# Estilo das legendas: branco, negrito, fundo escuro semi-transparente
SUBTITLE_STYLE = (
    "FontName=Arial,"
    "FontSize=30,"
    "PrimaryColour=&H00FFFFFF,"
    "OutlineColour=&H00000000,"
    "BackColour=&H99000000,"
    "Bold=1,"
    "Outline=2,"
    "Shadow=0,"
    "MarginV=70,"
    "Alignment=2"
)

# ============================================================
# DADOS DOS ROTEIROS: (id, titulo, voz_dur, subtitles)
# ============================================================

roteiros = [
    {
        "id": "01",
        "titulo": "Comercial_Direto",
        "voz_dur": 35.05,
        "subtitles": [
            (0.0,   2.5,  "How many great songs stay unreleased..."),
            (2.5,   5.2,  "just because launching feels too complicated?"),
            (5.8,   7.8,  "I'm an artist, just like you."),
            (7.8,  10.5,  "And for a long time, I also thought"),
            (10.5, 13.8,  "releasing music was expensive and bureaucratic."),
            (13.8, 16.5,  "Until I discovered The Anchor Records."),
            (17.2, 19.5,  "Today, my music can be released"),
            (19.5, 22.5,  "and monetized on more than 50 platforms worldwide,"),
            (22.5, 25.5,  "with a professional standard from the beginning."),
            (26.0, 28.5,  "The artist keeps 90% of the royalties,"),
            (28.5, 30.5,  "with clear contracts and security."),
            (31.0, 33.0,  "If you have a song you believe in,"),
            (33.0, 35.0,  "submit your demo."),
        ]
    },
    {
        "id": "02",
        "titulo": "Processo_Autoridade",
        "voz_dur": 37.05,
        "subtitles": [
            (0.0,   2.5,  "The truth is simple:"),
            (2.5,   5.0,  "talent alone is not enough in the music industry."),
            (5.0,   7.0,  "You need structure."),
            (7.5,  10.0,  "At The Anchor Records,"),
            (10.0, 13.0,  "every release goes through a complete process:"),
            (13.0, 16.0,  "curation, technical preparation,"),
            (16.0, 19.5,  "professional mastering, and global distribution."),
            (20.0, 22.5,  "Your music reaches the world's main platforms"),
            (22.5, 25.5,  "with quality and positioning from the start."),
            (26.0, 29.0,  "All tracks are mastered and signed by Nytron,"),
            (29.0, 32.5,  "a best-selling artist with 150+ tracks in Beatport Top 100."),
            (33.0, 35.5,  "The artist keeps 90% of the royalties."),
            (35.5, 37.0,  "Submit your demo."),
        ]
    },
    {
        "id": "03",
        "titulo": "Cena_Network",
        "voz_dur": 46.05,
        "subtitles": [
            (0.0,   3.0,  "The question isn't whether your music is good..."),
            (3.0,   6.0,  "it's whether it's reaching the right people."),
            (6.5,   9.0,  "The Anchor Records was born inside electronic music culture."),
            (9.0,  12.0,  "Since 2015, we've produced events with artists like"),
            (12.0, 16.0,  "Volac, Beltran, Dashdot, Fluxzone, Mandragora, and Holt 88."),
            (16.5, 20.0,  "We've hosted events in 3 of Brazil's Top 50 clubs:"),
            (20.0, 24.0,  "Field Club, Like Music Club, and Chakra Club."),
            (24.5, 28.0,  "For almost a year, we were represented in Barcelona, Spain."),
            (28.0, 31.5,  "A unique experience that connected us to the global scene."),
            (32.0, 35.5,  "When your music is released with us,"),
            (35.5, 39.0,  "it gains something many artists don't have: real network."),
            (40.0, 43.0,  "The Anchor Records."),
            (43.0, 46.0,  "From the dancefloor to the world."),
        ]
    },
    {
        "id": "04",
        "titulo": "Remarketing",
        "voz_dur": 40.70,
        "subtitles": [
            (0.0,   3.0,  "I'm pretty sure you've seen some of our videos..."),
            (3.0,   6.0,  "but you still haven't decided to submit your music."),
            (6.0,   9.0,  "Maybe you're wondering if it's really worth it."),
            (9.5,  13.0,  "Hundreds of artists have already released with The Anchor Records."),
            (13.0, 16.5,  "We're a label born inside the electronic scene,"),
            (16.5, 20.0,  "producing events since 2015 with Volac, Beltran, and Dashdot."),
            (20.5, 24.0,  "Global releases delivered with professional standards from day one."),
            (24.5, 27.5,  "The artist keeps 90% of the royalties,"),
            (27.5, 30.5,  "with clear contracts and real industry structure."),
            (31.0, 34.5,  "If you believe in your music,"),
            (34.5, 37.5,  "this might be the opportunity you've been waiting for."),
            (37.5, 40.5,  "Click the link and submit your demo."),
        ]
    },
]

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def sec_to_srt(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    ms = int((s - int(s)) * 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"

def gerar_srt(subtitles, offset, srt_path):
    with open(srt_path, "w") as f:
        for i, (start, end, text) in enumerate(subtitles, 1):
            f.write(f"{i}\n")
            f.write(f"{sec_to_srt(start + offset)} --> {sec_to_srt(end + offset)}\n")
            f.write(f"{text}\n\n")
        # CTA final: link do Groover aparece nos últimos 4 segundos do corpo
        cta_start = subtitles[-1][1] + 0.5 + offset
        cta_end = cta_start + 3.5
        f.write(f"{len(subtitles)+1}\n")
        f.write(f"{sec_to_srt(cta_start)} --> {sec_to_srt(cta_end)}\n")
        f.write(f"groover.co/band/signup/referral/influencer/26997\n\n")

def run(cmd, label=""):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERRO em {label}: {result.stderr[-300:]}")
        raise RuntimeError(f"Falha: {label}")
    return result

def montar_video(r):
    rid = r["id"]
    titulo = r["titulo"]
    voz_dur = r["voz_dur"]
    subtitles = r["subtitles"]
    total_dur = LOGO_DUR + voz_dur + LOGO_DUR

    print(f"\n{'='*50}")
    print(f"Roteiro {rid}: {titulo}")
    print(f"Duração: logo({LOGO_DUR}s) + voz({voz_dur}s) + logo({LOGO_DUR}s) = {total_dur:.1f}s")

    voz_path = f"{VOZES_DIR}/roteiro_{rid}_voz.wav"
    srt_path = f"/tmp/r{rid}.srt"
    output = f"{OUTPUT_DIR}/video_{rid}_{titulo}.mp4"

    # 1. Gerar SRT com offset do logo
    gerar_srt(subtitles, LOGO_DUR, srt_path)
    print("  [1/5] SRT gerado")

    # 2. Loop dos 3 clipes alternados para cobrir a duração da voz
    # Concatenar os 3 clipes repetidamente até cobrir voz_dur
    clips_needed = int(voz_dur / 8) + 2
    concat_list = f"/tmp/loop_{rid}.txt"
    with open(concat_list, "w") as f:
        for i in range(clips_needed):
            clip = CLIPS[i % len(CLIPS)]
            f.write(f"file '{clip}'\n")

    run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_list,
        "-t", str(voz_dur),
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1",
        "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-r", "30", "-an",
        f"/tmp/presenter_{rid}.mp4"
    ], "loop clipes")
    print("  [2/5] Loop da apresentadora OK")

    # 3. Criar logos de abertura e fechamento
    for tag, path in [("open", f"/tmp/logo_open_{rid}.mp4"), ("close", f"/tmp/logo_close_{rid}.mp4")]:
        run([
            "ffmpeg", "-y",
            "-loop", "1", "-t", str(LOGO_DUR), "-i", LOGO,
            "-vf", f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fade=t=in:st=0:d={FADE},fade=t=out:st={LOGO_DUR - FADE}:d={FADE}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-r", "30", "-an",
            path
        ], f"logo {tag}")
    print("  [3/5] Logos OK")

    # 4. Concatenar logo + apresentadora + logo e queimar legendas
    concat_final = f"/tmp/concat_final_{rid}.txt"
    with open(concat_final, "w") as f:
        f.write(f"file '/tmp/logo_open_{rid}.mp4'\n")
        f.write(f"file '/tmp/presenter_{rid}.mp4'\n")
        f.write(f"file '/tmp/logo_close_{rid}.mp4'\n")

    run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_final,
        "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-an",
        f"/tmp/raw_{rid}.mp4"
    ], "concat")

    # Queimar legendas
    run([
        "ffmpeg", "-y",
        "-i", f"/tmp/raw_{rid}.mp4",
        "-vf", f"subtitles={srt_path}:force_style='{SUBTITLE_STYLE}'",
        "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-an",
        f"/tmp/subtitled_{rid}.mp4"
    ], "legendas")
    print("  [4/5] Vídeo com legendas OK")

    # 5. Adicionar áudio: voz + trilha
    voz_delay_ms = int(LOGO_DUR * 1000)
    run([
        "ffmpeg", "-y",
        "-i", f"/tmp/subtitled_{rid}.mp4",
        "-i", voz_path,
        "-stream_loop", "-1", "-i", TRILHA,
        "-filter_complex",
        f"[1:a]adelay={voz_delay_ms}|{voz_delay_ms},volume=1.0[voz];"
        f"[2:a]atrim=0:{total_dur},volume={MUSIC_VOL},afade=t=in:st=0:d=2,afade=t=out:st={total_dur - 2}:d=2[music];"
        f"[voz][music]amix=inputs=2:duration=first[audio_out]",
        "-map", "0:v",
        "-map", "[audio_out]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(total_dur),
        output
    ], "áudio")

    size = os.path.getsize(output) / (1024 * 1024)
    print(f"  [5/5] PRONTO: {output} ({size:.1f} MB)")
    return output

# ============================================================
# EXECUTAR TODOS OS ROTEIROS
# ============================================================
resultados = []
for r in roteiros:
    try:
        out = montar_video(r)
        resultados.append((r["id"], r["titulo"], out, "OK"))
    except Exception as e:
        resultados.append((r["id"], r["titulo"], "", f"ERRO: {e}"))

print("\n" + "="*50)
print("RESUMO FINAL:")
for rid, titulo, out, status in resultados:
    print(f"  R{rid} {titulo}: {status}")
print("="*50)
