#!/usr/bin/env python3
"""
Creative 001 v6 — montagem com footage real.

Usa preview real de banco de vídeo como base para evitar alucinações de IA:
mesma pessoa, mesmo produto, mesmo fundo e movimento humano real. A saída é um
vídeo vertical 9:16 de 24s com três takes de 8s.
"""

from pathlib import Path
import subprocess

ROOT = Path('/home/ubuntu/trabalho_video/video-anchor')
IN = ROOT / 'gc_output' / 'real_footage' / 'vecteezy_serum_3.mp4'
OUT_DIR = ROOT / 'gc_output' / 'creative_001_v6_real_footage'
OUT_DIR.mkdir(parents=True, exist_ok=True)
FINAL = ROOT / 'gc_output' / 'creative_001_v6_24s_three_takes_REAL_FOOTAGE_DRAFT.mp4'

# Três takes de 8s. O clipe original tem 22s; o terceiro take usa trecho final com leve desaceleração para completar 8s.
segments = [
    {'ss': 0.0, 't': 8.0, 'name': 'take1_hook_produto', 'crop': 'crop=324:576:350:0,scale=1080:1920', 'text1': 'parece simples', 'text2': 'mas a textura vende'},
    {'ss': 7.0, 't': 8.0, 'name': 'take2_aplicacao', 'crop': 'crop=324:576:330:0,scale=1080:1920', 'text1': 'gota real', 'text2': 'aplicação limpa'},
    {'ss': 14.0, 't': 8.0, 'name': 'take3_cta', 'crop': 'crop=324:576:345:0,scale=1080:1920', 'text1': 'rotina noturna', 'text2': 'produto no carrinho'},
]

font = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
parts = []
for i, seg in enumerate(segments, 1):
    out = OUT_DIR / f"{i}_{seg['name']}.mp4"
    # Edição vertical realista: crop 9:16, leve nitidez, cortes secos, texto TikTok discreto.
    vf = (
        f"{seg['crop']},"
        "eq=contrast=1.03:brightness=0.005:saturation=1.02,"
        "unsharp=5:5:0.35:3:3:0.18,"
        f"drawtext=fontfile={font}:text='{seg['text1']}':x=54:y=h-305:fontsize=58:fontcolor=white:"
        "box=1:boxcolor=black@0.42:boxborderw=24:enable='between(t,0.7,5.9)',"
        f"drawtext=fontfile={font}:text='{seg['text2']}':x=54:y=h-225:fontsize=48:fontcolor=white:"
        "box=1:boxcolor=black@0.36:boxborderw=20:enable='between(t,1.2,6.6)'"
    )
    cmd = [
        'ffmpeg','-y','-ss',str(seg['ss']),'-i',str(IN),'-t',str(seg['t']),
        '-vf',vf,
        '-an','-r','30','-c:v','libx264','-pix_fmt','yuv420p','-preset','medium','-crf','20',str(out)
    ]
    subprocess.run(cmd, check=True)
    parts.append(out)

concat = OUT_DIR / 'concat.txt'
concat.write_text(''.join(f"file {p}\n" for p in parts), encoding='utf-8')

# Adiciona room tone baixo para não ficar mudo; não usa voz sintética.
audio = OUT_DIR / 'room_tone.wav'
subprocess.run([
    'ffmpeg','-y','-f','lavfi','-i','anoisesrc=color=pink:amplitude=0.004:duration=24',
    '-af','highpass=f=120,lowpass=f=2800,volume=0.12',str(audio)
], check=True)

video_joined = OUT_DIR / 'joined_no_audio.mp4'
subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(video_joined)], check=True)
subprocess.run([
    'ffmpeg','-y','-i',str(video_joined),'-i',str(audio),'-t','24',
    '-c:v','copy','-c:a','aac','-b:a','96k','-movflags','+faststart',str(FINAL)
], check=True)

print(FINAL)
