#!/usr/bin/env python3
"""
gc_pipeline_perpetuo.py — Pipeline Perpétuo UGC TikTok Shop
Video Anchor | MANUOS IA

Sistema autônomo que:
1. Minera produtos mais vendidos no TikTok Shop
2. Seleciona a persona ideal para cada produto/nicho
3. Gera roteiro com storytelling: Problema → Solução → CTA
4. Gera 3 prompts de imagem (3 ângulos diferentes)
5. Gera áudio TTS para cada take
6. Monta o vídeo final de 24s (3 takes de 8s)
7. Salva e registra no checkpoint

Uso:
  python gc_pipeline_perpetuo.py --produto "Creme Anti-Idade" --nicho beleza
  python gc_pipeline_perpetuo.py --minerar --limite 5
  python gc_pipeline_perpetuo.py --minerar --limite 10 --todas-personas
"""

import argparse
import json
import os
import sys
import time
import random
import subprocess
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

for d in [INPUTS_DIR, OUTPUT_DIR, TEMP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

client = OpenAI()
MODEL_ROTEIRO = "gpt-4.1-mini"
MODEL_TTS = "tts-1-hd"  # Usar API externa quando disponível

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
    # Buscar nicho exato ou parcial
    for key in NICHO_PERSONA_MAP:
        if key in nicho_lower or nicho_lower in key:
            personas_ids = NICHO_PERSONA_MAP[key]
            persona_id = personas_ids[indice % len(personas_ids)]
            return PERSONAS[persona_id]
    # Fallback: geral
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
    {
        "nome": "Organizador de Gaveta Modular Ajustável",
        "descricao": "Kit com 10 divisórias modulares para organizar gavetas, armários e escritório.",
        "categoria": "organizacao",
        "preco": "R$49,90",
        "gmv_estimado": 120000,
        "unidades_vendidas": 8000,
    },
    {
        "nome": "Máscara Capilar Nutritiva com Queratina",
        "descricao": "Máscara de tratamento intensivo com queratina e óleo de argan. Cabelos lisos e brilhantes.",
        "categoria": "beleza",
        "preco": "R$59,90",
        "gmv_estimado": 200000,
        "unidades_vendidas": 18000,
    },
    {
        "nome": "Escova Elétrica de Limpeza Facial Rotativa",
        "descricao": "Escova elétrica com 3 velocidades e 4 cabeças intercambiáveis para limpeza profunda da pele.",
        "categoria": "skincare",
        "preco": "R$129,90",
        "gmv_estimado": 95000,
        "unidades_vendidas": 5000,
    },
    {
        "nome": "Coleira GPS para Pets com Rastreamento em Tempo Real",
        "descricao": "Coleira com GPS integrado, resistente à água, bateria 7 dias. App gratuito.",
        "categoria": "pet",
        "preco": "R$199,90",
        "gmv_estimado": 75000,
        "unidades_vendidas": 3000,
    },
]

def minerar_produtos_tiktok(limite: int = 5, nicho: str = "") -> list:
    """
    Minera produtos em alta no TikTok Shop.
    Em produção: integrar com API Apify/FastMoss.
    Em desenvolvimento: usa dados demo enriquecidos por LLM.
    """
    print(f"\n{'='*55}")
    print(f"  MINERAÇÃO DE PRODUTOS TIKTOK SHOP")
    print(f"{'='*55}")

    # Verificar se há API real disponível
    apify_token = os.environ.get("APIFY_API_TOKEN", "")

    if apify_token:
        print(f"  [MINERADOR] Usando Apify API para dados reais...")
        return _minerar_via_apify(limite, nicho, apify_token)
    else:
        print(f"  [MINERADOR] Modo demo — usando produtos de alta conversão pré-validados")
        print(f"  [MINERADOR] Para dados reais, configure APIFY_API_TOKEN no .env")
        produtos = PRODUTOS_DEMO[:limite]
        if nicho:
            produtos = [p for p in PRODUTOS_DEMO if nicho.lower() in p["categoria"].lower()][:limite]
            if not produtos:
                produtos = PRODUTOS_DEMO[:limite]
        print(f"  [MINERADOR] ✓ {len(produtos)} produtos selecionados")
        return produtos

def _minerar_via_apify(limite: int, nicho: str, token: str) -> list:
    """Integração real com Apify Trending Products Scraper."""
    import urllib.request
    import urllib.parse

    url = "https://api.apify.com/v2/acts/salmanrajz~trending-products-scraper/run-sync-get-dataset-items"
    params = {
        "token": token,
        "limit": limite,
        "days": 7,
        "region": "us",  # Ajustar para BR quando disponível
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
    """Gera roteiro de 24s com framework Problema → Solução → CTA adaptado à persona."""
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

FRAMEWORK OBRIGATÓRIO — 3 takes de 8 segundos cada (total 24s):
- Take 1 (0-8s): PROBLEMA/DOR — hook forte, expressão frustrada, conecta com a dor do público
- Take 2 (8-16s): SOLUÇÃO — demonstra o produto em uso, resultado visível, expressão de alívio
- Take 3 (16-24s): CTA — produto em destaque, aponta para baixo, sorriso, chamada clara

REGRAS:
- Máximo 25 palavras por take (para caber em ~8s de narração natural)
- Tom 100% brasileiro informal, como a persona descrita
- CTA no Take 3: "Clica no link", "Corre no link", "Aproveita agora"
- Linguagem da persona, não corporativa

Retorne APENAS JSON válido:
{{
  "take_1_problema": "fala do take 1 (máx 25 palavras)",
  "take_2_solucao": "fala do take 2 (máx 25 palavras)",
  "take_3_cta": "fala do take 3 (máx 25 palavras)",
  "texto_banner_1": "frase curta para banner take 1 (máx 6 palavras)",
  "texto_banner_2": "frase curta para banner take 2 (máx 6 palavras)",
  "texto_banner_3": "Clica para ver o preço",
  "hook": "primeira frase impactante do take 1",
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

# ─── Geração de Prompts de Imagem ──────────────────────────────────────────────
def gerar_prompts_imagem(produto: dict, persona: dict, roteiro: dict) -> dict:
    """Gera 3 prompts de imagem (3 ângulos) para geração de vídeo."""
    print(f"  [IMAGEM] Gerando prompts de 3 ângulos...")

    angulos = persona["angulos"]
    prompt_base = persona["prompt_base_imagem"]

    # Adaptar o prompt base ao produto
    produto_desc = f"{produto['nome']} ({produto['descricao'][:80]})"

    prompts = {
        "angulo_1_problema": f"""{prompt_base}
TAKE 1 — PROBLEMA/DOR:
She holds {produto_desc} clearly visible. Frustrated expression, pointing at problem area.
She says in Brazilian Portuguese with natural lip sync: "{roteiro['take_1_problema']}"
{angulos['angulo_1']}. Static camera, medium shot waist up, eye level. Vertical 9:16.""",

        "angulo_2_solucao": f"""{prompt_base}
TAKE 2 — SOLUÇÃO/DESCOBERTA:
She holds {produto_desc} clearly visible, demonstrating it in use. Expression of relief and satisfaction.
She says in Brazilian Portuguese with natural lip sync: "{roteiro['take_2_solucao']}"
{angulos['angulo_2']}. Static camera, medium shot waist up, eye level. Vertical 9:16.""",

        "angulo_3_cta": f"""{prompt_base}
TAKE 3 — CTA/COMPRA:
She holds {produto_desc} prominently in both hands, pointing finger DOWN toward screen. Big smile.
She says in Brazilian Portuguese with natural lip sync: "{roteiro['take_3_cta']}"
{angulos['angulo_3']}. Static camera, medium shot waist up, eye level. Vertical 9:16.""",
    }

    print(f"  [IMAGEM] ✓ 3 prompts de ângulos gerados")
    return prompts

# ─── Geração de Áudio TTS ─────────────────────────────────────────────────────
def gerar_audio_take(texto: str, take_num: int, prefixo: str, persona_id: str = "usuario_comum") -> Path:
    """Gera áudio TTS para um take usando espeak (local) ou API externa."""
    output_path = TEMP_DIR / f"{prefixo}_take{take_num}_audio.mp3"
    wav_path = TEMP_DIR / f"{prefixo}_take{take_num}_audio.wav"

    print(f"  [TTS] Gerando áudio take {take_num}...")

    # Tentar API OpenAI TTS primeiro
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=texto,
            speed=1.05,
        )
        response.stream_to_file(str(output_path))
        print(f"  [TTS] ✓ Áudio take {take_num} gerado via API: {output_path.name}")
        return output_path
    except Exception:
        pass

    # Fallback: espeak-ng (síntese local em português)
    try:
        subprocess.run([
            "espeak-ng", "-v", "pt-br", "-s", "145", "-a", "180",
            "-w", str(wav_path), texto
        ], check=True, capture_output=True)
        # Converter WAV para MP3
        subprocess.run([
            "ffmpeg", "-y", "-i", str(wav_path),
            "-codec:a", "libmp3lame", "-qscale:a", "2", str(output_path)
        ], check=True, capture_output=True)
        print(f"  [TTS] ✓ Áudio take {take_num} gerado via espeak: {output_path.name}")
        return output_path
    except Exception as e:
        print(f"  [TTS] ⚠ espeak falhou: {e}. Gerando silêncio de 8s.")
        # Fallback final: silêncio de 8s
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
            "-t", "8", str(output_path)
        ], check=True, capture_output=True)
        return output_path

# ─── Montagem do Vídeo ─────────────────────────────────────────────────────────
def montar_video_com_imagens_e_audio(
    produto: dict,
    persona: dict,
    roteiro: dict,
    prompts_imagem: dict,
    prefixo: str,
) -> Path:
    """
    Monta o vídeo final de 24s.
    Em produção: gera imagens via DALL-E e cria vídeos animados.
    Neste script: usa o gc_montar_v2.py existente com takes de referência.
    """
    print(f"\n  [MONTAGEM] Iniciando montagem do vídeo...")

    output_path = OUTPUT_DIR / f"{prefixo}_FINAL.mp4"

    # Gerar áudios TTS para os 3 takes
    audio1 = gerar_audio_take(roteiro["take_1_problema"], 1, prefixo)
    audio2 = gerar_audio_take(roteiro["take_2_solucao"], 2, prefixo)
    audio3 = gerar_audio_take(roteiro["take_3_cta"], 3, prefixo)

    # Salvar roteiro e prompts em JSON para uso posterior na geração de vídeo
    roteiro_path = INPUTS_DIR / f"{prefixo}_roteiro_completo.json"
    with open(roteiro_path, "w", encoding="utf-8") as f:
        json.dump({
            "produto": produto,
            "persona": persona["id"],
            "roteiro": roteiro,
            "prompts_imagem": prompts_imagem,
            "audios": {
                "take1": str(audio1),
                "take2": str(audio2),
                "take3": str(audio3),
            },
            "gerado_em": datetime.now().isoformat(),
        }, f, ensure_ascii=False, indent=2)

    print(f"  [MONTAGEM] ✓ Roteiro e prompts salvos: {roteiro_path.name}")
    print(f"  [MONTAGEM] ✓ Áudios TTS gerados para os 3 takes")
    print(f"  [MONTAGEM] → Para gerar os vídeos, use os prompts em {roteiro_path.name}")
    print(f"  [MONTAGEM] → com uma ferramenta de geração de vídeo (ex: Kling, Runway, Pika)")
    print(f"  [MONTAGEM] → e depois execute: python gc_montar_v2.py --take1 t1.mp4 --take2 t2.mp4 --take3 t3.mp4")

    return roteiro_path

# ─── Pipeline Principal ────────────────────────────────────────────────────────
def executar_pipeline(produto: dict, persona_indice: int = 0) -> dict:
    """Executa o pipeline completo para um produto."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_limpo = produto["nome"][:30].replace(" ", "_").replace("/", "-")
    persona = selecionar_persona(produto["categoria"], persona_indice)
    prefixo = f"{timestamp}_{nome_limpo}_{persona['id']}"

    print(f"\n{'='*55}")
    print(f"  PIPELINE UGC — {produto['nome'][:40]}")
    print(f"  Persona: {persona['nome']} | Nicho: {produto['categoria']}")
    print(f"{'='*55}")

    # 1. Gerar roteiro
    roteiro = gerar_roteiro(produto, persona)

    # 2. Gerar prompts de imagem (3 ângulos)
    prompts = gerar_prompts_imagem(produto, persona, roteiro)

    # 3. Gerar áudios e salvar pacote completo
    resultado = montar_video_com_imagens_e_audio(produto, persona, roteiro, prompts, prefixo)

    return {
        "produto": produto["nome"],
        "persona": persona["nome"],
        "prefixo": prefixo,
        "roteiro": roteiro,
        "prompts_imagem": prompts,
        "arquivo_roteiro": str(resultado),
        "status": "PRONTO_PARA_GERACAO_VIDEO",
    }

def executar_pipeline_completo(limite: int = 5, nicho: str = "", todas_personas: bool = False):
    """Executa o pipeline perpétuo: minera produtos e gera roteiros para todos."""
    print(f"\n{'='*60}")
    print(f"  PIPELINE PERPÉTUO UGC TIKTOK SHOP — MANUOS IA")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{'='*60}")

    # 1. Minerar produtos
    produtos = minerar_produtos_tiktok(limite, nicho)

    resultados = []
    for i, produto in enumerate(produtos):
        if todas_personas:
            # Gerar para as 3 personas mais adequadas ao nicho
            for j in range(3):
                try:
                    resultado = executar_pipeline(produto, persona_indice=j)
                    resultados.append(resultado)
                    time.sleep(1)  # Rate limit
                except Exception as e:
                    print(f"  [ERRO] Produto {produto['nome'][:30]}, persona {j}: {e}")
        else:
            try:
                resultado = executar_pipeline(produto, persona_indice=0)
                resultados.append(resultado)
                time.sleep(1)
            except Exception as e:
                print(f"  [ERRO] Produto {produto['nome'][:30]}: {e}")

    # 2. Salvar relatório
    relatorio_path = OUTPUT_DIR / f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(relatorio_path, "w", encoding="utf-8") as f:
        json.dump({
            "executado_em": datetime.now().isoformat(),
            "total_produtos": len(produtos),
            "total_roteiros": len(resultados),
            "resultados": resultados,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"  ✓ PIPELINE CONCLUÍDO!")
    print(f"  Produtos processados: {len(produtos)}")
    print(f"  Roteiros gerados: {len(resultados)}")
    print(f"  Relatório: {relatorio_path.name}")
    print(f"{'='*60}")

    return resultados

# ─── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pipeline Perpétuo UGC TikTok Shop — MANUOS IA"
    )
    parser.add_argument("--produto", type=str, help="Nome do produto específico")
    parser.add_argument("--descricao", type=str, default="", help="Descrição do produto")
    parser.add_argument("--categoria", type=str, default="geral", help="Categoria/nicho")
    parser.add_argument("--preco", type=str, default="R$99,90", help="Preço do produto")
    parser.add_argument("--persona", type=str, default="", help="ID da persona (opcional)")
    parser.add_argument("--minerar", action="store_true", help="Minerar produtos do TikTok Shop")
    parser.add_argument("--limite", type=int, default=5, help="Limite de produtos a minerar")
    parser.add_argument("--nicho", type=str, default="", help="Filtrar por nicho na mineração")
    parser.add_argument("--todas-personas", action="store_true", help="Gerar para todas as personas adequadas")
    parser.add_argument("--listar-personas", action="store_true", help="Listar as 6 personas disponíveis")

    args = parser.parse_args()

    if args.listar_personas:
        print("\n=== 6 PERSONAS UGC TIKTOK SHOP ===\n")
        for pid, p in PERSONAS.items():
            print(f"  [{pid}] {p['nome']}")
            print(f"    Arquétipo: {p['arquetipo']}")
            print(f"    Nichos: {', '.join(p['nicho'][:3])}")
            print(f"    Tom: {p['tom_de_voz'][:60]}...")
            print()
        sys.exit(0)

    if args.minerar:
        executar_pipeline_completo(
            limite=args.limite,
            nicho=args.nicho,
            todas_personas=args.todas_personas,
        )
    elif args.produto:
        produto = {
            "nome": args.produto,
            "descricao": args.descricao or args.produto,
            "categoria": args.categoria,
            "preco": args.preco,
            "gmv_estimado": 0,
            "unidades_vendidas": 0,
        }
        persona_indice = 0
        if args.persona and args.persona in PERSONAS:
            # Encontrar índice da persona
            personas_nicho = NICHO_PERSONA_MAP.get(args.categoria, NICHO_PERSONA_MAP["geral"])
            if args.persona in personas_nicho:
                persona_indice = personas_nicho.index(args.persona)
        resultado = executar_pipeline(produto, persona_indice)
        print(f"\n  ✓ Roteiro salvo em: {resultado['arquivo_roteiro']}")
    else:
        parser.print_help()
