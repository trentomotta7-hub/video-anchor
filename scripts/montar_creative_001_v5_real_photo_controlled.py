#!/usr/bin/env python3
"""
Creative 001 v5 — montagem controlada a partir de fotografia real.

Objetivo: entregar vídeo vertical 9:16 de 24 segundos em três takes de 8s,
sem geração livre de IA em movimento, sem troca de personagem, sem troca de ambiente
e sem mutação de produto. A base visual é uma única foto real de frasco de sérum
em banheiro. O movimento é apenas edição programática: crop, pan, zoom, grão sutil,
leve respiração de câmera e transições secas.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import math
import os
import subprocess
import shutil
import random

ROOT = Path('/home/ubuntu/trabalho_video/video-anchor')
SRC = Path('/home/ubuntu/upload/search_images/Hww1yGspxjlN.jpeg')
OUT_DIR = ROOT / 'gc_output' / 'creative_001_v5_real_photo_controlled'
FRAMES = OUT_DIR / 'frames'
FINAL = ROOT / 'gc_output' / 'creative_001_v5_24s_three_takes_REAL_PHOTO_CONTROLLED.mp4'
TMP_VIDEO = OUT_DIR / 'video_no_audio.mp4'
AUDIO = OUT_DIR / 'room_tone.wav'
W, H = 1080, 1920
FPS = 30
TAKE_SEC = 8
TOTAL_SEC = 24
TOTAL_FRAMES = FPS * TOTAL_SEC

OUT_DIR.mkdir(parents=True, exist_ok=True)
if FRAMES.exists():
    shutil.rmtree(FRAMES)
FRAMES.mkdir(parents=True, exist_ok=True)

img = Image.open(SRC).convert('RGB')
sw, sh = img.size

# Fontes do sistema.
def load_font(size, bold=False):
    candidates = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf',
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()

FONT_BIG = load_font(46, True)
FONT_MED = load_font(34, True)
FONT_SMALL = load_font(27, False)

# O crop usa coordenadas normalizadas no retrato original.
# Take 1: contexto banheiro + produto visível.
# Take 2: close no frasco, mantendo o mesmo produto.
# Take 3: composição aberta para CTA visual.
TAKES = [
    {
        'name': 'hook_contexto_banheiro_real',
        'crop_start': (0.05, 0.08, 0.95, 0.98),
        'crop_end': (0.08, 0.10, 0.94, 0.96),
        'overlay': ['testei antes de dormir', 'a textura é leve de verdade'],
        'overlay_time': (0.8, 5.6),
    },
    {
        'name': 'close_produto_real',
        'crop_start': (0.36, 0.36, 0.98, 0.99),
        'crop_end': (0.39, 0.38, 0.96, 0.97),
        'overlay': ['não fica pegajoso', 'absorve rápido'],
        'overlay_time': (8.6, 13.8),
    },
    {
        'name': 'cta_produto_no_banheiro',
        'crop_start': (0.16, 0.22, 0.98, 0.99),
        'crop_end': (0.12, 0.18, 0.96, 0.96),
        'overlay': ['se aparecer no carrinho', 'eu compraria de novo'],
        'overlay_time': (16.8, 22.2),
    },
]

random.seed(11)

def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * t)

def interp(a, b, t):
    return a + (b - a) * t

def crop_to_916(base, box_norm):
    x1, y1, x2, y2 = box_norm
    bx1, by1, bx2, by2 = int(x1*sw), int(y1*sh), int(x2*sw), int(y2*sh)
    bx1, by1 = max(0, bx1), max(0, by1)
    bx2, by2 = min(sw, bx2), min(sh, by2)
    # Ajustar para 9:16 mantendo centro.
    cw, ch = bx2-bx1, by2-by1
    target = 9/16
    cur = cw/ch
    cx, cy = (bx1+bx2)/2, (by1+by2)/2
    if cur > target:
        cw2 = ch * target
        bx1 = int(cx - cw2/2); bx2 = int(cx + cw2/2)
    else:
        ch2 = cw / target
        by1 = int(cy - ch2/2); by2 = int(cy + ch2/2)
    bx1, by1 = max(0, bx1), max(0, by1)
    bx2, by2 = min(sw, bx2), min(sh, by2)
    return base.crop((bx1, by1, bx2, by2)).resize((W, H), Image.Resampling.LANCZOS)

def add_phone_grain(frame, idx):
    # Pequena variação de exposição/contraste comum em celular, sem deformar produto.
    exposure = 1.0 + 0.015 * math.sin(idx * 0.031)
    contrast = 1.015 + 0.01 * math.sin(idx * 0.017)
    frame = ImageEnhance.Brightness(frame).enhance(exposure)
    frame = ImageEnhance.Contrast(frame).enhance(contrast)
    # Vinheta sutil.
    overlay = Image.new('RGBA', (W, H), (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    for r in range(0, 360, 8):
        alpha = int((r/360)**2 * 3)
        draw.rectangle((r, r, W-r, H-r), outline=(0,0,0,alpha), width=8)
    return Image.alpha_composite(frame.convert('RGBA'), overlay).convert('RGB')

def rounded_rect(draw, xy, radius, fill):
    draw.rounded_rectangle(xy, radius=radius, fill=fill)

def add_overlay(frame, lines, alpha):
    if alpha <= 0:
        return frame
    fr = frame.convert('RGBA')
    layer = Image.new('RGBA', (W,H), (0,0,0,0))
    d = ImageDraw.Draw(layer)
    text = '\n'.join(lines)
    # Usar caixa baixa, estética TikTok orgânica, sem promessa médica.
    bbox = d.multiline_textbbox((0,0), text, font=FONT_BIG, spacing=12)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    pad_x, pad_y = 34, 26
    x = 54
    y = H - th - 260
    bg_alpha = int(168 * alpha)
    rounded_rect(d, (x-pad_x, y-pad_y, x+tw+pad_x, y+th+pad_y), 28, (20,20,20,bg_alpha))
    # sombra + texto branco levemente imperfeito
    d.multiline_text((x+2,y+2), text, font=FONT_BIG, spacing=12, fill=(0,0,0,int(105*alpha)))
    d.multiline_text((x,y), text, font=FONT_BIG, spacing=12, fill=(255,255,255,int(245*alpha)))
    # Indicador discreto de gesto real, sem interface fake.
    pill = 'produto na rotina noturna'
    pb = d.textbbox((0,0), pill, font=FONT_SMALL)
    px, py = 54, 94
    rounded_rect(d, (px-22, py-16, px+(pb[2]-pb[0])+22, py+(pb[3]-pb[1])+18), 18, (255,255,255,int(132*alpha)))
    d.text((px,py), pill, font=FONT_SMALL, fill=(34,34,34,int(230*alpha)))
    return Image.alpha_composite(fr, layer).convert('RGB')

for idx in range(TOTAL_FRAMES):
    t_global = idx / FPS
    take_i = min(2, int(t_global // TAKE_SEC))
    take = TAKES[take_i]
    local = (idx - take_i*TAKE_SEC*FPS) / (TAKE_SEC*FPS - 1)
    e = ease(local)
    box = tuple(interp(a, b, e) for a, b in zip(take['crop_start'], take['crop_end']))
    frame = crop_to_916(img, box)

    # Micro hand-held: deslocamento máximo 5 px, sem mexer no objeto relativo ao fundo.
    dx = int(4 * math.sin(idx * 0.041 + take_i))
    dy = int(3 * math.sin(idx * 0.033 + 2*take_i))
    canvas = Image.new('RGB', (W, H), (245,245,242))
    resized = frame.resize((W+12, H+12), Image.Resampling.LANCZOS)
    canvas.paste(resized, (-6+dx, -6+dy))
    frame = canvas
    frame = add_phone_grain(frame, idx)

    start, end = take['overlay_time']
    fade = 0
    if start <= t_global <= end:
        fade = min(1, (t_global-start)/0.35, (end-t_global)/0.45)
    frame = add_overlay(frame, take['overlay'], fade)

    # Flash muito sutil no corte, simulando jump cut de celular, não transição gerada.
    if idx in (TAKE_SEC*FPS, 2*TAKE_SEC*FPS):
        frame = ImageEnhance.Brightness(frame).enhance(1.06)

    frame.save(FRAMES / f'frame_{idx:04d}.jpg', quality=92, optimize=True)

# Room tone sintético baixíssimo para o arquivo não ficar mudo; não há voz IA.
subprocess.run([
    'ffmpeg','-y',
    '-f','lavfi','-i','anoisesrc=color=pink:amplitude=0.006:duration=24',
    '-af','highpass=f=120,lowpass=f=2500,volume=0.18',
    str(AUDIO)
], check=True)

subprocess.run([
    'ffmpeg','-y',
    '-framerate',str(FPS),
    '-i',str(FRAMES / 'frame_%04d.jpg'),
    '-i',str(AUDIO),
    '-c:v','libx264','-pix_fmt','yuv420p','-profile:v','high','-level','4.1',
    '-r',str(FPS),
    '-c:a','aac','-b:a','96k',
    '-shortest',
    '-movflags','+faststart',
    str(FINAL)
], check=True)

print(FINAL)
