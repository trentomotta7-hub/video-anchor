#!/usr/bin/env python3
"""
Monta o Creative 001 v3 em 24s usando uma única imagem-base fixa.
Objetivo: maximizar consistência visual e eliminar mutações típicas de geração de vídeo por IA.
Saída: 3 takes de 8s com movimento sutil de câmera, todos derivados da mesma referência.
"""
from pathlib import Path
import subprocess
import json
import shutil

ROOT = Path('/home/ubuntu/trabalho_video/video-anchor')
OUT = ROOT / 'gc_output'
REF_CANDIDATES = [
    OUT / 'creative_001_reference_no_face_clean.png',
    OUT / 'creative_001_reference_no_face_real_bathroom.png',
    OUT / 'creative_001_reference_bia_skincare.png',
]
REF = next((p for p in REF_CANDIDATES if p.exists()), None)
if REF is None:
    raise FileNotFoundError('Nenhuma referência visual encontrada para montar o vídeo v3.')

WORK = OUT / 'creative_001_v3_still_locked'
WORK.mkdir(parents=True, exist_ok=True)

TAKES = [
    {
        'name': 'take1_hook_produto_fixo',
        'x': 0.08, 'y': 0.05, 'w': 0.84, 'h': 0.92,
        'zoom_start': 1.00, 'zoom_end': 1.045,
        'pan_x': 0.00, 'pan_y': 0.00,
        'description': 'Take 1: plano geral vertical, mesma pessoa, mesmo banheiro, mesmo frasco visível.'
    },
    {
        'name': 'take2_close_aplicacao_fixa',
        'x': 0.18, 'y': 0.10, 'w': 0.66, 'h': 0.82,
        'zoom_start': 1.00, 'zoom_end': 1.060,
        'pan_x': -0.01, 'pan_y': 0.01,
        'description': 'Take 2: aproximação para mão/rosto/produto sem gerar novos elementos.'
    },
    {
        'name': 'take3_cta_produto_ambiente_fixo',
        'x': 0.10, 'y': 0.06, 'w': 0.80, 'h': 0.90,
        'zoom_start': 1.035, 'zoom_end': 1.000,
        'pan_x': 0.01, 'pan_y': -0.005,
        'description': 'Take 3: retorno ao plano geral com CTA implícito; sem texto, sem gráfico, sem troca de cenário.'
    },
]

# Gerar metadados da imagem
probe = subprocess.run([
    'ffprobe', '-v', 'error', '-select_streams', 'v:0',
    '-show_entries', 'stream=width,height', '-of', 'json', str(REF)
], capture_output=True, text=True, check=True)
meta = json.loads(probe.stdout)
width = meta['streams'][0]['width']
height = meta['streams'][0]['height']

# A saída final é 1080x1920 vertical. Cada take usa crop estático diferente + zoom sutil.
take_paths = []
for i, t in enumerate(TAKES, start=1):
    x = int(width * t['x'])
    y = int(height * t['y'])
    cw = int(width * t['w'])
    ch = int(height * t['h'])
    # Ajusta crop para 9:16 dentro da região desejada.
    target_ratio = 9/16
    if cw / ch > target_ratio:
        new_cw = int(ch * target_ratio)
        x += max(0, (cw - new_cw)//2)
        cw = new_cw
    else:
        new_ch = int(cw / target_ratio)
        y += max(0, (ch - new_ch)//2)
        ch = new_ch
    # Garante pares para libx264.
    cw -= cw % 2
    ch -= ch % 2
    x -= x % 2
    y -= y % 2
    out = WORK / f"creative_001_v3_{i}_{t['name']}.mp4"
    # 8 segundos, 30fps; zoompan gera movimento mínimo sem transformar conteúdo.
    z0 = t['zoom_start']
    z1 = t['zoom_end']
    zoom_expr = f"if(lte(on,1),{z0},{z0}+({z1}-{z0})*on/240)"
    vf = (
        f"crop={cw}:{ch}:{x}:{y},"
        f"scale=1440:2560:flags=lanczos,"
        f"zoompan=z='{zoom_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=240:s=1080x1920:fps=30,"
        f"eq=contrast=1.02:brightness=0.005:saturation=0.98,"
        f"noise=alls=2:allf=t,format=yuv420p"
    )
    subprocess.run([
        'ffmpeg', '-y', '-loop', '1', '-i', str(REF), '-t', '8',
        '-vf', vf,
        '-r', '30', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
        '-movflags', '+faststart', '-an', str(out)
    ], check=True)
    take_paths.append(out)

concat_file = WORK / 'concat_v3.txt'
concat_file.write_text(''.join(f"file {p.resolve()}\n" for p in take_paths), encoding='utf-8')
final = OUT / 'creative_001_v3_24s_three_takes_LOCKED.mp4'
subprocess.run([
    'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(concat_file),
    '-c', 'copy', str(final)
], check=True)

# Gerar relatório técnico simples.
probe_final = subprocess.run([
    'ffprobe', '-v', 'error', '-show_entries',
    'format=duration:stream=width,height,avg_frame_rate,codec_name',
    '-of', 'json', str(final)
], capture_output=True, text=True, check=True)
report = OUT / 'creative_001_v3_technical_report.json'
report.write_text(probe_final.stdout, encoding='utf-8')

spec = OUT / 'creative_001_v3_production_notes.md'
spec.write_text(f"""# Creative 001 v3 — Still Locked Production Notes

Esta versão foi montada a partir de **uma única referência visual fixa** para eliminar as falhas das versões v1 e v2: troca de produto, troca de cenário, artefatos de texto, reflexos inconsistentes e mutação de personagem.

## Arquivos

| Item | Caminho |
|---|---|
| Referência visual | `{REF}` |
| Take 1 | `{take_paths[0]}` |
| Take 2 | `{take_paths[1]}` |
| Take 3 | `{take_paths[2]}` |
| Vídeo final | `{final}` |
| Relatório técnico | `{report}` |

## Decisão de qualidade

A v3 usa movimento de câmera sutil em cima de imagem fixa, e não geração livre de vídeo. Isso reduz movimento orgânico, mas aumenta a confiabilidade: personagem, produto, ambiente e iluminação permanecem fixos durante todos os 24 segundos. É a rota de menor alucinação disponível nesta sessão.

## Restrições respeitadas

- Três takes de 8 segundos.
- Formato vertical 9:16.
- Sem legenda, sem banner, sem gráfico e sem texto gerado.
- Mesmo ambiente, mesma pessoa e mesmo produto.
- Sem variação de personagem ou cenário.
""", encoding='utf-8')

print(final)
