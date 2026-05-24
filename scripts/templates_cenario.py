"""
templates_cenario.py — Templates de Cenários para Vídeos
Video Anchor | The Anchor Records

Define variações de cenário para os vídeos de prospecção:
- escritorio: Fundo corporativo com gradiente escuro e moldura profissional
- lifestyle: Fundo vibrante com cores quentes e overlay de partículas
- estudio: Fundo de estúdio musical com iluminação neon
- default: Template original (fundo neutro)

Cada template gera um overlay de fundo via FFmpeg sem necessidade
de assets externos adicionais.
"""

import subprocess
import os
from pathlib import Path

REPO_DIR = Path(__file__).parent.parent
ASSETS_DIR = REPO_DIR / "assets"
OUTPUT_DIR = REPO_DIR / "videos_v4"
VOZES_DIR = ASSETS_DIR / "vozes"
LOGO = str(ASSETS_DIR / "logo_intro.png")
TRILHA = str(ASSETS_DIR / "trilha_anchor.mp3")

# ============================================================
# DEFINIÇÃO DOS TEMPLATES
# ============================================================

TEMPLATES = {
    "escritorio": {
        "nome": "Escritório",
        "descricao": "Ambiente corporativo — gradiente escuro azul-marinho com borda sutil",
        "bg_color": "0x0a1628",          # Azul-marinho profundo
        "overlay_color": "0x1a2a4a",     # Azul médio para gradiente
        "accent_color": "0x2a5298",      # Azul corporativo
        "subtitle_style": (
            "FontName=Arial,"
            "FontSize=30,"
            "PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H002a5298,"
            "BackColour=&H99000000,"
            "Bold=1,"
            "Outline=2,"
            "Shadow=1,"
            "MarginV=70,"
            "Alignment=2"
        ),
        "vf_extra": "drawbox=x=0:y=0:w=iw:h=8:color=2a5298@0.8:t=fill,"
                    "drawbox=x=0:y=ih-8:w=iw:h=8:color=2a5298@0.8:t=fill",
    },
    "lifestyle": {
        "nome": "Lifestyle",
        "descricao": "Ambiente vibrante — gradiente quente laranja-roxo para artistas modernos",
        "bg_color": "0x1a0a2e",          # Roxo escuro
        "overlay_color": "0x2d1b69",     # Roxo médio
        "accent_color": "0xff6b35",      # Laranja vibrante
        "subtitle_style": (
            "FontName=Arial,"
            "FontSize=30,"
            "PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H0035b5ff,"
            "BackColour=&HCC1a0a2e,"
            "Bold=1,"
            "Outline=2,"
            "Shadow=1,"
            "MarginV=70,"
            "Alignment=2"
        ),
        "vf_extra": "drawbox=x=0:y=0:w=iw:h=6:color=ff6b35@0.9:t=fill,"
                    "drawbox=x=0:y=ih-6:w=iw:h=6:color=ff6b35@0.9:t=fill",
    },
    "estudio": {
        "nome": "Estúdio",
        "descricao": "Ambiente de estúdio musical — neon verde/ciano sobre fundo preto",
        "bg_color": "0x050505",          # Preto quase puro
        "overlay_color": "0x0d1f0d",     # Verde muito escuro
        "accent_color": "0x00ff88",      # Verde neon
        "subtitle_style": (
            "FontName=Arial,"
            "FontSize=30,"
            "PrimaryColour=&H0088ff00,"
            "OutlineColour=&H00000000,"
            "BackColour=&HCC050505,"
            "Bold=1,"
            "Outline=2,"
            "Shadow=1,"
            "MarginV=70,"
            "Alignment=2"
        ),
        "vf_extra": "drawbox=x=0:y=0:w=iw:h=5:color=00ff88@1.0:t=fill,"
                    "drawbox=x=0:y=ih-5:w=iw:h=5:color=00ff88@1.0:t=fill,"
                    "drawbox=x=0:y=0:w=5:h=ih:color=00ff88@0.5:t=fill,"
                    "drawbox=x=iw-5:y=0:w=5:h=ih:color=00ff88@0.5:t=fill",
    },
    "default": {
        "nome": "Padrão",
        "descricao": "Template original — fundo neutro escuro",
        "bg_color": "0x1a1a2e",
        "overlay_color": "0x16213e",
        "accent_color": "0xe94560",
        "subtitle_style": (
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
        ),
        "vf_extra": None,
    },
}

# ============================================================
# DADOS DOS ROTEIROS
# ============================================================

ROTEIROS = [
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

GROOVER_URL = "groover.co/band/signup/referral/influencer/26997"
LOGO_DUR = 3.0
FADE = 1.0
MUSIC_VOL = 0.10
CLIPS = [
    str(REPO_DIR / "clips" / "presenter_v3_base.mp4"),
    str(REPO_DIR / "clips" / "presenter_v3_b.mp4"),
    str(REPO_DIR / "clips" / "presenter_v3_c.mp4"),
]


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def sec_to_srt(s: float) -> str:
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    ms = int((s - int(s)) * 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def gerar_srt(subtitles: list, offset: float, srt_path: str, groover_url: str = GROOVER_URL):
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, (start, end, text) in enumerate(subtitles, 1):
            f.write(f"{i}\n")
            f.write(f"{sec_to_srt(start + offset)} --> {sec_to_srt(end + offset)}\n")
            f.write(f"{text}\n\n")
        # CTA final
        cta_start = subtitles[-1][1] + 0.5 + offset
        cta_end = cta_start + 3.5
        f.write(f"{len(subtitles)+1}\n")
        f.write(f"{sec_to_srt(cta_start)} --> {sec_to_srt(cta_end)}\n")
        f.write(f"{groover_url}\n\n")


def run(cmd: list, label: str = ""):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERRO em {label}: {result.stderr[-300:]}")
        raise RuntimeError(f"Falha: {label}")
    return result


# ============================================================
# RENDERIZAÇÃO COM TEMPLATE
# ============================================================

def montar_com_template(roteiro: dict, template_key: str, output_dir: str = None) -> str:
    """
    Renderiza um vídeo usando o template de cenário especificado.

    Args:
        roteiro: Dicionário com dados do roteiro (id, titulo, voz_dur, subtitles)
        template_key: Chave do template ('escritorio', 'lifestyle', 'estudio', 'default')
        output_dir: Diretório de saída (padrão: videos_v4/<template>/)

    Returns:
        Caminho do arquivo de vídeo gerado
    """
    if template_key not in TEMPLATES:
        raise ValueError(f"Template '{template_key}' não existe. Disponíveis: {list(TEMPLATES.keys())}")

    tmpl = TEMPLATES[template_key]
    rid = roteiro["id"]
    titulo = roteiro["titulo"]
    voz_dur = roteiro["voz_dur"]
    subtitles = roteiro["subtitles"]
    total_dur = LOGO_DUR + voz_dur + LOGO_DUR

    # Diretório de saída
    if output_dir is None:
        out_dir = REPO_DIR / "videos_v4" / template_key
    else:
        out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    output = str(out_dir / f"video_{rid}_{titulo}_{template_key}.mp4")
    voz_path = str(VOZES_DIR / f"roteiro_{rid}_voz.wav")
    srt_path = f"/tmp/tmpl_{template_key}_{rid}.srt"

    print(f"\n{'='*55}")
    print(f"Template: {tmpl['nome']} | Roteiro {rid}: {titulo}")
    print(f"Duração: {LOGO_DUR}s + {voz_dur}s + {LOGO_DUR}s = {total_dur:.1f}s")

    # 1. Gerar SRT
    gerar_srt(subtitles, LOGO_DUR, srt_path)
    print("  [1/5] SRT gerado")

    # 2. Loop dos clipes da apresentadora
    clips_needed = int(voz_dur / 8) + 2
    concat_list = f"/tmp/tmpl_loop_{template_key}_{rid}.txt"
    with open(concat_list, "w") as f:
        for i in range(clips_needed):
            clip = CLIPS[i % len(CLIPS)]
            f.write(f"file '{clip}'\n")

    # Filtro de vídeo: escalar + overlay de cor de fundo (via colorchannelmixer/overlay)
    # Aplicamos um overlay de cor semi-transparente sobre o clipe da apresentadora
    bg_hex = tmpl["bg_color"].replace("0x", "")
    vf_presenter = (
        f"scale=1920:1080:force_original_aspect_ratio=decrease,"
        f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color={bg_hex},"
        f"setsar=1"
    )
    # Adicionar bordas decorativas se o template tiver
    if tmpl.get("vf_extra"):
        vf_presenter += "," + tmpl["vf_extra"]

    run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_list,
        "-t", str(voz_dur),
        "-vf", vf_presenter,
        "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-r", "30", "-an",
        f"/tmp/tmpl_presenter_{template_key}_{rid}.mp4"
    ], "loop clipes")
    print("  [2/5] Clipes da apresentadora OK")

    # 3. Logos de abertura e fechamento com cor de fundo do template
    for tag, path in [("open", f"/tmp/tmpl_logo_open_{template_key}_{rid}.mp4"),
                      ("close", f"/tmp/tmpl_logo_close_{template_key}_{rid}.mp4")]:
        run([
            "ffmpeg", "-y",
            "-loop", "1", "-t", str(LOGO_DUR), "-i", LOGO,
            "-vf", (
                f"scale=1920:1080:force_original_aspect_ratio=decrease,"
                f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color={bg_hex},"
                f"setsar=1,"
                f"fade=t=in:st=0:d={FADE},"
                f"fade=t=out:st={LOGO_DUR - FADE}:d={FADE}"
            ),
            "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-r", "30", "-an",
            path
        ], f"logo {tag}")
    print("  [3/5] Logos OK")

    # 4. Concatenar + queimar legendas com estilo do template
    concat_final = f"/tmp/tmpl_concat_{template_key}_{rid}.txt"
    with open(concat_final, "w") as f:
        f.write(f"file '/tmp/tmpl_logo_open_{template_key}_{rid}.mp4'\n")
        f.write(f"file '/tmp/tmpl_presenter_{template_key}_{rid}.mp4'\n")
        f.write(f"file '/tmp/tmpl_logo_close_{template_key}_{rid}.mp4'\n")

    run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_final,
        "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-an",
        f"/tmp/tmpl_raw_{template_key}_{rid}.mp4"
    ], "concat")

    run([
        "ffmpeg", "-y",
        "-i", f"/tmp/tmpl_raw_{template_key}_{rid}.mp4",
        "-vf", f"subtitles={srt_path}:force_style='{tmpl['subtitle_style']}'",
        "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-an",
        f"/tmp/tmpl_subtitled_{template_key}_{rid}.mp4"
    ], "legendas")
    print("  [4/5] Vídeo com legendas OK")

    # 5. Áudio: voz + trilha
    voz_delay_ms = int(LOGO_DUR * 1000)
    run([
        "ffmpeg", "-y",
        "-i", f"/tmp/tmpl_subtitled_{template_key}_{rid}.mp4",
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

    size = Path(output).stat().st_size / (1024 * 1024)
    print(f"  [5/5] PRONTO: {output} ({size:.1f} MB)")
    return output


def listar_templates():
    """Lista todos os templates disponíveis."""
    print("\nTemplates de Cenário Disponíveis:")
    print(f"{'='*55}")
    for key, tmpl in TEMPLATES.items():
        print(f"  {key:12} — {tmpl['nome']}: {tmpl['descricao']}")
    print(f"{'='*55}")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        listar_templates()
        print("\nUso: python templates_cenario.py <template> [roteiro_id]")
        print("  template: escritorio | lifestyle | estudio | default | all")
        print("  roteiro_id: 01 | 02 | 03 | 04 | all (padrão: all)")
        sys.exit(0)

    template_arg = sys.argv[1]
    roteiro_arg = sys.argv[2] if len(sys.argv) > 2 else "all"

    # Selecionar roteiros
    if roteiro_arg == "all":
        roteiros_selecionados = ROTEIROS
    else:
        roteiros_selecionados = [r for r in ROTEIROS if r["id"] == roteiro_arg]
        if not roteiros_selecionados:
            print(f"Roteiro '{roteiro_arg}' não encontrado.")
            sys.exit(1)

    # Selecionar templates
    if template_arg == "all":
        templates_selecionados = list(TEMPLATES.keys())
    elif template_arg in TEMPLATES:
        templates_selecionados = [template_arg]
    else:
        print(f"Template '{template_arg}' não existe.")
        listar_templates()
        sys.exit(1)

    # Renderizar
    resultados = []
    for tmpl_key in templates_selecionados:
        for rot in roteiros_selecionados:
            try:
                out = montar_com_template(rot, tmpl_key)
                resultados.append((tmpl_key, rot["id"], rot["titulo"], out, "OK"))
            except Exception as e:
                resultados.append((tmpl_key, rot["id"], rot["titulo"], "", f"ERRO: {e}"))

    print(f"\n{'='*55}")
    print("RESUMO:")
    for tmpl_key, rid, titulo, out, status in resultados:
        print(f"  [{tmpl_key}] R{rid} {titulo}: {status}")
    print(f"{'='*55}")
