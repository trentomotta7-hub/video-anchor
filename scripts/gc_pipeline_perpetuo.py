#!/usr/bin/env python3
"""
gc_pipeline_perpetuo.py — Pipeline Perpétuo UGC TikTok Shop (v10 - Vídeo Contínuo)
Video Anchor | MANUOS IA

Sistema autônomo que:
1. Minera produtos mais vendidos no TikTok Shop
2. Seleciona a persona ideal para cada produto/nicho
3. Gera roteiro com storytelling: Problema → Solução → CTA (fala única)
4. Gera keyframes (início e fim) para garantir continuidade
5. Gera o vídeo final de 24s em tomada única (sem cortes, com lip-sync nativo)
6. Salva e registra no checkpoint

Uso:
  python gc_pipeline_perpetuo.py --produto "Creme Anti-Idade" --nicho beleza
  python gc_pipeline_perpetuo.py --minerar --limite 5
"""

import argparse
import json
import os
import sys
import time
import random
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from openai import OpenAI

# ─── Configuração ─────────────────────────────────────────────────────────────
REPO_DIR = Path(__file__).parent.parent
ASSETS_DIR = REPO_DIR / "gc_assets"
INPUTS_DIR = ASSETS_DIR / "inputs"
OUTPUT_DIR = REPO_DIR / "gc_output"
PERSONAS_FILE = ASSETS_DIR / "personas.json"
TEMP_DIR = Path("/tmp/ugc_pipeline")
TRILHA = ASSETS_DIR / "trilha_fundo.mp3"

for d in [INPUTS_DIR, OUTPUT_DIR, TEMP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

client = OpenAI()
MODEL_ROTEIRO = "gpt-4.1-mini"

# ─── Carregar Personas ─────────────────────────────────────────────────────────
def carregar_personas() -> dict:
    with open(PERSONAS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {p["id"]: p for p in data["personas"]}

PERSONAS = carregar_personas()

# ─── Mapeamento Nicho → Persona ────────────────────────────────────────────────
NICHO_PERSONA_MAP = {
    "beleza":       ["especialista", "usuario_comum", "influenciadora_estilo"],
    "saude":        ["especialista", "usuario_comum", "mae_pratica"],
    "skincare":     ["especialista", "usuario_comum", "influenciadora_estilo"],
    "suplementos":  ["especialista", "comparador", "solucionador_pratico"],
    "casa":         ["mae_pratica", "solucionador_pratico", "usuario_comum"],
    "moda":         ["influenciadora_estilo", "usuario_comum", "comparador"],
    "tecnologia":   ["comparador", "solucionador_pratico", "usuario_comum"],
    "pet":          ["mae_pratica", "usuario_comum", "especialista"],
    "alimentacao":  ["mae_pratica", "especialista", "usuario_comum"],
    "organizacao":  ["solucionador_pratico", "mae_pratica", "usuario_comum"],
    "acessorios":   ["influenciadora_estilo", "usuario_comum", "comparador"],
    "limpeza":      ["mae_pratica", "solucionador_pratico", "usuario_comum"],
    "fitness":      ["especialista", "usuario_comum", "comparador"],
    "geral":        ["usuario_comum", "especialista", "comparador"],
}

def selecionar_persona(nicho: str, indice: int = 0) -> dict:
    """Seleciona a persona mais adequada para o nicho."""
    nicho_lower = nicho.lower()
    for key in NICHO_PERSONA_MAP:
        if key in nicho_lower or nicho_lower in key:
            personas_ids = NICHO_PERSONA_MAP[key]
            persona_id = personas_ids[indice % len(personas_ids)]
            return PERSONAS[persona_id]
    personas_ids = NICHO_PERSONA_MAP["geral"]
    persona_id = personas_ids[indice % len(personas_ids)]
    return PERSONAS[persona_id]

# ─── Mineração de Produtos ─────────────────────────────────────────────────────
PRODUTOS_DEMO = [
    {
        "nome": "Creme Hidratante Facial Anti-Idade com Colágeno",
        "descricao": "Creme facial com colágeno, vitamina C e ácido hialurônico. Reduz rugas em 30 dias.",
        "categoria": "skincare",
        "preco": "R$89,90",
        "gmv_estimado": 250000,
        "unidades_vendidas": 15000,
    },
    {
        "nome": "Suplemento Emagrecedor Termogênico Natural",
        "descricao": "Cápsulas termogênicas com extrato de chá verde, cafeína e gengibre. Acelera o metabolismo.",
        "categoria": "saude",
        "preco": "R$69,90",
        "gmv_estimado": 180000,
        "unidades_vendidas": 12000,
    },
]

def minerar_produtos_tiktok(limite: int = 5, nicho: str = "") -> list:
    print(f"\n{'='*55}")
    print(f"  MINERAÇÃO DE PRODUTOS TIKTOK SHOP")
    print(f"{'='*55}")

    apify_token = os.environ.get("APIFY_API_TOKEN", "")

    if apify_token:
        print(f"  [MINERADOR] Usando Apify API para dados reais...")
        return _minerar_via_apify(limite, nicho, apify_token)
    else:
        print(f"  [MINERADOR] Modo demo — usando produtos de alta conversão pré-validados")
        produtos = PRODUTOS_DEMO[:limite]
        if nicho:
            produtos = [p for p in PRODUTOS_DEMO if nicho.lower() in p["categoria"].lower()][:limite]
            if not produtos:
                produtos = PRODUTOS_DEMO[:limite]
        print(f"  [MINERADOR] ✓ {len(produtos)} produtos selecionados")
        return produtos

def _minerar_via_apify(limite: int, nicho: str, token: str) -> list:
    import urllib.request
    import urllib.parse

    url = "https://api.apify.com/v2/acts/salmanrajz~trending-products-scraper/run-sync-get-dataset-items"
    params = {
        "token": token,
        "limit": limite,
        "days": 7,
        "region": "us",
    }

    try:
        full_url = f"{url}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(full_url, method="POST",
                                     data=json.dumps({"limit": limite, "days": 7}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            produtos = []
            for item in data[:limite]:
                produtos.append({
                    "nome": item.get("name", "Produto TikTok Shop"),
                    "descricao": f"Produto trending: {item.get('name', '')}",
                    "categoria": item.get("categories", ["geral"])[0] if item.get("categories") else "geral",
                    "preco": item.get("price_display", "R$99,90"),
                    "gmv_estimado": item.get("gmv", 0),
                    "unidades_vendidas": item.get("units_sold", 0),
                    "product_url": item.get("product_url", ""),
                    "image_url": item.get("product_img_url", ""),
                })
            return produtos
    except Exception as e:
        print(f"  [MINERADOR] ⚠ Erro na API Apify: {e}. Usando dados demo.")
        return PRODUTOS_DEMO[:limite]

# ─── Geração de Roteiro ────────────────────────────────────────────────────────
def gerar_roteiro(produto: dict, persona: dict) -> dict:
    print(f"\n  [ROTEIRO] Gerando para: {produto['nome'][:40]}... | Persona: {persona['nome']}")

    tom = persona["tom_de_voz"]
    estilo = persona["estilo_fala"]

    prompt = f"""Você é um especialista em TikTok Shop Brasil e copywriting de alta conversão.

PRODUTO: {produto['nome']}
DESCRIÇÃO: {produto['descricao']}
CATEGORIA: {produto['categoria']}
PREÇO: {produto['preco']}

PERSONA: {persona['nome']} — {persona['arquetipo']}
TOM DE VOZ: {tom}
GATILHOS EMOCIONAIS: {', '.join(persona['gatilhos_emocionais'])}

REFERÊNCIA DE ESTILO DE FALA:
- Take 1 (Dor): {estilo['take1_dor']}
- Take 2 (Solução): {estilo['take2_solucao']}
- Take 3 (CTA): {estilo['take3_cta']}

FRAMEWORK OBRIGATÓRIO — VÍDEO ÚNICO E CONTÍNUO de 24 segundos (sem cortes):
- O vídeo deve fluir naturalmente entre os blocos de Problema, Solução e CTA.
- A apresentadora começa sem produto, expressando a dor de forma confessional. Em seguida, pega o produto da mesa e o apresenta como solução. Finaliza com o produto em mãos, apontando para baixo para o CTA.
- Sem legendas ou banners na tela.

REGRAS:
- A fala total deve ter no máximo 75 palavras (para caber em ~24s de narração natural).
- Tom 100% brasileiro informal, como a persona descrita.
- CTA: "Clica no link", "Corre no link", "Aproveita agora", com preço e escassez.
- Linguagem da persona, não corporativa.

Retorne APENAS JSON válido:
{{
  "fala_completa": "fala completa do vídeo (máx 75 palavras)",
  "hook": "primeira frase impactante da fala completa",
  "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#TikTokShop", "#Brasil"]
}}"""

    response = client.chat.completions.create(
        model=MODEL_ROTEIRO,
        messages=[
            {"role": "system", "content": "Especialista em TikTok Shop Brasil. Retorne APENAS JSON válido, sem markdown."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800,
        temperature=0.8,
    )

    content = response.choices[0].message.content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    if content.endswith("```"):
        content = content[:-3]

    roteiro = json.loads(content.strip())
    print(f"  [ROTEIRO] ✓ Roteiro gerado | Hook: {roteiro.get('hook', '')[:50]}...")
    return roteiro

# ─── Geração de Keyframes ──────────────────────────────────────────────────────
def gerar_keyframes(persona: dict, produto: dict) -> dict:
    print(f"  [IMAGEM] Gerando keyframes para vídeo contínuo...")

    kf_dir = ASSETS_DIR / "kf_v10"
    kf_dir.mkdir(parents=True, exist_ok=True)

    produto_desc = f"{produto['nome']} ({produto['descricao'][:80]})"

    kf_start_path = kf_dir / "take1_start.png"
    kf_start_prompt = f"UGC TikTok video still frame. {persona['prompt_base_imagem']}. She has NO product in her hands. Her expression is vulnerable and uncomfortable — hand touching her cheek, eyes slightly downcast, like she is confessing something embarrassing to a friend. Authentic, raw, no makeup-heavy look. Vertical 9:16. Ultra-realistic photographic quality."

    kf_end_path = kf_dir / "take3_end.png"
    kf_end_prompt = f"UGC TikTok video still frame. {persona['prompt_base_imagem']}. She holds {produto_desc} in her left hand raised up clearly visible, and points her right index finger urgently DOWN toward the bottom of the screen. Big enthusiastic smile, high energy, direct eye contact. Vertical 9:16. Ultra-realistic photographic quality."

    print(f"  [IMAGEM] ✓ Keyframes gerados (prompts e paths)")
    return {
        "kf_start_path": kf_start_path,
        "kf_start_prompt": kf_start_prompt,
        "kf_end_path": kf_end_path,
        "kf_end_prompt": kf_end_prompt,
    }

# ─── Montagem do Vídeo Final (apenas trilha) ───────────────────────────────────
def montar_video_final(video_path: Path) -> Path:
    print(f"\n  [MONTAGEM] Adicionando trilha de fundo ao vídeo contínuo...")

    final_output_path = video_path.parent / f"{video_path.stem}_FINAL.mp4"

    if TRILHA.exists():
        subprocess.run([
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(TRILHA),
            "-filter_complex",
            "[0:a]volume=1.0[voz];[1:a]volume=0.06[trilha];"
            "[voz][trilha]amix=inputs=2:duration=first[audio_final]",
            "-map", "0:v",
            "-map", "[audio_final]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            str(final_output_path)
        ], check=True, capture_output=True)
    else:
        shutil.copy(str(video_path), str(final_output_path))
        print(f"  [MONTAGEM] Sem trilha — usando apenas áudio nativo")

    print(f"  [MONTAGEM] ✓ Vídeo final com trilha salvo: {final_output_path.name}")
    return final_output_path

# ─── Pipeline Principal ────────────────────────────────────────────────────────
def pipeline_ugc(produto_info: dict, todas_personas: bool = False):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    produto_nome_curto = produto_info["nome"].replace(" ", "_")[:20]

    if todas_personas:
        personas_a_usar = PERSONAS.values()
    else:
        personas_a_usar = [selecionar_persona(produto_info["categoria"])]

    for persona in personas_a_usar:
        prefixo = f"{timestamp}_{produto_nome_curto}_{persona['id']}"
        print(f"\n{'='*60}\n  PROCESSANDO: {produto_info['nome']} | PERSONA: {persona['nome']}\n{'='*60}")

        # 1. Gerar Roteiro
        roteiro = gerar_roteiro(produto_info, persona)
        roteiro_path = INPUTS_DIR / f"{prefixo}_roteiro.json"
        with open(roteiro_path, "w", encoding="utf-8") as f:
            json.dump(roteiro, f, ensure_ascii=False, indent=2)
        print(f"  [ARQUIVO] ✓ Roteiro salvo: {roteiro_path.name}")

        # 2. Gerar Keyframes (Apenas prepara os prompts e paths, a geração real é feita via API Manus)
        keyframes_data = gerar_keyframes(persona, produto_info)
        
        # 3. Preparar Prompt do Vídeo Contínuo
        video_path = OUTPUT_DIR / f"{prefixo}_raw.mp4"
        video_prompt = f"""UGC TikTok Shop video, vertical 9:16. EXACT SAME woman as reference image: {persona['prompt_base_imagem']}. Static camera, medium shot waist up, eye level.

She starts with NO product in hands, expressing a relatable problem. Then, she naturally reaches to the side, picks up {produto_info['nome']} from a table, and presents it with relief and surprise. Finally, she holds the product and points her finger DOWN toward the bottom of the screen with high energy for the CTA.

The entire video is ONE CONTINUOUS SHOT, no cuts, no scene changes. Her movements are fluid and organic, transitioning smoothly between problem, solution, and CTA.

She speaks in Brazilian Portuguese with natural lip sync, emotional and raw tone:
\"{roteiro['fala_completa']}\"

Her mouth moves naturally in sync with the speech. No on-screen text, no banners.
"""
        
        print(f"  [PIPELINE] O script Python preparou os prompts. A geração de mídia (imagens e vídeo) deve ser feita pela API Manus.")
        print(f"  [PIPELINE] Keyframe Start Prompt: {keyframes_data['kf_start_prompt']}")
        print(f"  [PIPELINE] Keyframe End Prompt: {keyframes_data['kf_end_prompt']}")
        print(f"  [PIPELINE] Video Prompt: {video_prompt}")
        
        # Salvar os prompts para uso posterior
        prompts_path = INPUTS_DIR / f"{prefixo}_prompts.json"
        with open(prompts_path, "w", encoding="utf-8") as f:
            json.dump({
                "kf_start_prompt": keyframes_data['kf_start_prompt'],
                "kf_start_path": str(keyframes_data['kf_start_path']),
                "kf_end_prompt": keyframes_data['kf_end_prompt'],
                "kf_end_path": str(keyframes_data['kf_end_path']),
                "video_prompt": video_prompt,
                "video_path": str(video_path)
            }, f, ensure_ascii=False, indent=2)

# ─── Execução ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline Perpétuo UGC TikTok Shop")
    parser.add_argument("--produto", type=str, help="Nome do produto para gerar o vídeo.")
    parser.add_argument("--descricao", type=str, help="Descrição do produto.")
    parser.add_argument("--categoria", type=str, default="geral", help="Categoria do produto.")
    parser.add_argument("--preco", type=str, default="R$XX,XX", help="Preço do produto.")
    parser.add_argument("--minerar", action="store_true", help="Minera produtos em alta no TikTok Shop.")
    parser.add_argument("--limite", type=int, default=1, help="Limite de produtos a minerar.")
    parser.add_argument("--todas-personas", action="store_true", help="Gera vídeo para todas as personas do nicho.")
    args = parser.parse_args()

    if args.minerar:
        produtos_minerados = minerar_produtos_tiktok(args.limite, args.categoria)
        for produto in produtos_minerados:
            pipeline_ugc(produto, args.todas_personas)
    elif args.produto and args.descricao:
        produto_info = {
            "nome": args.produto,
            "descricao": args.descricao,
            "categoria": args.categoria,
            "preco": args.preco,
        }
        pipeline_ugc(produto_info)
    else:
        print("Uso: python gc_pipeline_perpetuo.py --produto \"Nome\" --descricao \"Desc\" [--categoria \"Cat\"]")
        print("   ou: python gc_pipeline_perpetuo.py --minerar [--limite N] [--categoria \"Cat\"] [--todas-personas]")
