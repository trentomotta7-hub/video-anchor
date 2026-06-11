#!/usr/bin/env python3
"""
Monta o Creative 001 v4 usando base stock real.
Foco: evitar alucinações de IA, deformações anatômicas e variação de produto/ambiente.
Saída: 24s, 3 takes de 8s, vertical 9:16, sem texto.
"""
from pathlib import Path
import subprocess
import json

ROOT = Path('/home/ubuntu/trabalho_video/video-anchor')
OUT = ROOT / 'gc_output'
REF = Path('/home/ubuntu/upload/search_images/dDmhVvKoiSge.jpg')
if not REF.exists():
    raise FileNotFoundError(f'Base stock real não encontrada: {REF}')

WORK = OUT / 'creative_001_v4_stock_real'
WORK.mkdir(parents=True, exist_ok=True)

# Para imagem horizontal 500x281, os recortes priorizam produto/mãos e evitam inventar anatomia.
TAKES = [
    {
        'name': 'take1_hook_contexto_banheiro_real',
        'crop': (210, 0, 158, 281),
        'z0': 1.00, 'z1': 1.035,
        'desc': 'Take 1: contexto real de banheiro, pessoa parcialmente visível, frasco e conta-gotas presentes.'
    },
    {
        'name': 'take2_close_produto_maos_reais',
        'crop': (130, 0, 158, 281),
        'z0': 1.02, 'z1': 1.065,
        'desc': 'Take 2: aproximação em mãos, conta-gotas e frasco reais, sem geração de novos dedos ou objetos.'
    },
    {
        'name': 'take3_cta_visual_produto_fixo',
        'crop': (175, 0, 158, 281),
        'z0': 1.04, 'z1': 1.00,
        'desc': 'Take 3: produto e gesto de uso continuam fixos; CTA implícito para carrinho sem texto.'
    },
]

take_paths = []
for i, t in enumerate(TAKES, start=1):
    x, y, w, h = t['crop']
    out = WORK / f"creative_001_v4_{i}_{t['name']}.mp4"
    zoom_expr = f"if(lte(on,1),{t['z0']},{t['z0']}+({t['z1']}-{t['z0']})*on/240)"
    vf = (
        f"crop={w}:{h}:{x}:{y},"
        "scale=1080:1920:flags=lanczos,"
        f"zoompan=z='{zoom_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=240:s=1080x1920:fps=30,"
        "eq=contrast=1.01:brightness=0.004:saturation=0.99,"
        "noise=alls=1.2:allf=t,format=yuv420p"
    )
    subprocess.run([
        'ffmpeg', '-y', '-loop', '1', '-i', str(REF), '-t', '8',
        '-vf', vf,
        '-r', '30', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
        '-movflags', '+faststart', '-an', str(out)
    ], check=True)
    take_paths.append(out)

concat_file = WORK / 'concat_v4.txt'
concat_file.write_text(''.join(f"file {p.resolve()}\n" for p in take_paths), encoding='utf-8')
final = OUT / 'creative_001_v4_24s_three_takes_STOCK_REAL.mp4'
subprocess.run([
    'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(concat_file),
    '-c', 'copy', str(final)
], check=True)

probe = subprocess.run([
    'ffprobe', '-v', 'error', '-show_entries',
    'format=duration,size:stream=width,height,avg_frame_rate,codec_name',
    '-of', 'json', str(final)
], capture_output=True, text=True, check=True)
(OUT / 'creative_001_v4_technical_report.json').write_text(probe.stdout, encoding='utf-8')

notes = OUT / 'creative_001_v4_production_notes.md'
notes.write_text(f"""# Creative 001 v4 — Stock Real Locked

Esta versão substitui a geração livre de vídeo por uma montagem de três takes baseada em **uma única imagem stock real**. O objetivo é cumprir a exigência de não haver alucinação, troca de personagem, troca de ambiente ou mutação de produto.

| Item | Caminho |
|---|---|
| Base visual real | `{REF}` |
| Take 1 | `{take_paths[0]}` |
| Take 2 | `{take_paths[1]}` |
| Take 3 | `{take_paths[2]}` |
| Vídeo final | `{final}` |

## Decisão criativa

A imagem-base mostra uma pessoa real em banheiro real manipulando frasco de sérum com conta-gotas. Os três takes são recortes diferentes da mesma cena, com movimento de câmera mínimo. Isso cria estrutura de vídeo de 24 segundos com três takes sem depender de geração de movimento por IA, que foi a origem das reprovações anteriores.

## Limitações honestas

O vídeo tem movimento sutil de câmera sobre imagem real, portanto não possui ação corporal fluida como uma filmagem completa. Ainda assim, é a versão mais segura contra aparência artificial, porque não inventa mãos, produto, reflexos ou ambiente.
""", encoding='utf-8')
print(final)
