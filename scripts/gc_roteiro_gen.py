"""
gc_roteiro_gen.py — Geração de Roteiro e Prompts de Imagem via LLM
Video Anchor | MANUOS IA

Usa o LLM disponível (gpt-5 / claude-sonnet) para gerar:
1. Roteiro de 25s com framework Vontade → Urgência → Dor → Solução
2. 3 prompts detalhados para geração de imagens ultra-realistas
3. Texto de narração completo

Uso:
  python gc_roteiro_gen.py --produto "Tênis Nike" --descricao "Tênis esportivo"
  python gc_roteiro_gen.py --json produto.json
"""

import argparse
import json
import os
import sys
from pathlib import Path
from openai import OpenAI

REPO_DIR = Path(__file__).parent.parent
ASSETS_DIR = REPO_DIR / "gc_assets"
INPUTS_DIR = ASSETS_DIR / "inputs"
INPUTS_DIR.mkdir(parents=True, exist_ok=True)

client = OpenAI()
MODEL = "gpt-5"  # Modelo com melhor suporte a JSON


def gerar_roteiro_e_prompts(produto: str, descricao: str, categoria: str = "", preco: str = "") -> dict:
    """
    Gera roteiro completo + prompts de imagem via LLM.
    Retorna dict com roteiro e prompts.
    """
    print(f"  [LLM] Gerando roteiro e prompts para: {produto}")

    prompt = f"""Você é um especialista em TikTok Shop Brasil e copywriting de alta conversão.

PRODUTO: {produto}
DESCRIÇÃO: {descricao}
CATEGORIA: {categoria}
PREÇO: {preco}

Crie um pacote completo para um vídeo de 25 segundos para TikTok Shop Brasil.

FRAMEWORK OBRIGATÓRIO (Vontade → Urgência → Dor → Solução):
- Take 1 (0-8s): VONTADE — Hook forte que cria desejo imediato pelo produto
- Take 2 (8-16s): URGÊNCIA + DOR — Mostra o problema sem o produto, cria urgência
- Take 3 (16-25s): SOLUÇÃO + CTA — Produto como solução, chamada para ação clara

REGRAS DO ROTEIRO:
- Máximo 25-30 palavras por take (para caber em ~8 segundos de narração)
- Tom: direto, empolgante, autêntico, 100% brasileiro informal
- CTA no Take 3: "Clica no link", "Compra agora", "Aproveita hoje"
- Linguagem conversacional, não corporativa

PROMPTS DE IMAGEM (em inglês, ultra-detalhados para DALL-E 3 / Midjourney):
- Ângulo 1 (Desejo): Produto em destaque puro, fundo clean, iluminação dramática de estúdio
- Ângulo 2 (Contexto/Dor): Produto em uso real, ambiente brasileiro, pessoa com problema sendo resolvido
- Ângulo 3 (Resultado): Pessoa brasileira feliz com resultado, aspiracional, golden hour

Retorne APENAS um JSON válido com esta estrutura exata:
{{
  "roteiro": {{
    "take_1_vontade": "texto do take 1",
    "take_2_urgencia_dor": "texto do take 2",
    "take_3_solucao_cta": "texto do take 3",
    "roteiro_completo": "take1 + take2 + take3 unificados",
    "hook": "primeira frase impactante do take 1",
    "cta": "chamada para ação do take 3"
  }},
  "prompts_imagem": {{
    "angulo_1_desejo": "prompt detalhado em inglês para imagem 1",
    "angulo_2_contexto": "prompt detalhado em inglês para imagem 2",
    "angulo_3_resultado": "prompt detalhado em inglês para imagem 3"
  }},
  "hashtags": ["hashtag1", "hashtag2", "hashtag3", "hashtag4", "hashtag5"],
  "titulo_video": "título sugerido para o vídeo no TikTok"
}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Você é um especialista em marketing digital e TikTok Shop. Retorne APENAS JSON válido, sem markdown, sem explicações."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("LLM retornou conteúdo vazio")

    # Limpar possível markdown
    content = content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    if content.endswith("```"):
        content = content[:-3]

    resultado = json.loads(content.strip())
    print(f"  [LLM] ✓ Roteiro e prompts gerados")
    return resultado


def salvar_roteiro(resultado: dict, prefixo: str) -> Path:
    """Salva o roteiro gerado em JSON."""
    output_path = INPUTS_DIR / f"{prefixo}_roteiro.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    print(f"  [LLM] ✓ Roteiro salvo: {output_path}")
    return output_path


def exibir_roteiro(resultado: dict):
    """Exibe o roteiro de forma formatada."""
    roteiro = resultado.get("roteiro", {})
    prompts = resultado.get("prompts_imagem", {})

    print("\n" + "="*60)
    print("📋 ROTEIRO GERADO")
    print("="*60)
    print(f"\n🎯 TAKE 1 — VONTADE (0-8s):")
    print(f"   {roteiro.get('take_1_vontade', 'N/A')}")
    print(f"\n⚡ TAKE 2 — URGÊNCIA + DOR (8-16s):")
    print(f"   {roteiro.get('take_2_urgencia_dor', 'N/A')}")
    print(f"\n✅ TAKE 3 — SOLUÇÃO + CTA (16-25s):")
    print(f"   {roteiro.get('take_3_solucao_cta', 'N/A')}")
    print(f"\n🔥 HOOK: {roteiro.get('hook', 'N/A')}")
    print(f"📣 CTA:  {roteiro.get('cta', 'N/A')}")
    print(f"\n🏷️  Título: {resultado.get('titulo_video', 'N/A')}")
    print(f"#️⃣  Hashtags: {' '.join(resultado.get('hashtags', []))}")

    print("\n" + "="*60)
    print("🖼️  PROMPTS DE IMAGEM")
    print("="*60)
    for angulo, prompt in prompts.items():
        print(f"\n{angulo}:")
        print(f"  {prompt[:150]}...")
    print("="*60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera roteiro e prompts de imagem via LLM")
    parser.add_argument("--produto", type=str, help="Nome do produto")
    parser.add_argument("--descricao", type=str, default="", help="Descrição do produto")
    parser.add_argument("--categoria", type=str, default="", help="Categoria do produto")
    parser.add_argument("--preco", type=str, default="", help="Preço do produto")
    parser.add_argument("--prefixo", type=str, default="produto", help="Prefixo para os arquivos")
    parser.add_argument("--json", type=str, help="Arquivo JSON com dados do produto")

    args = parser.parse_args()

    if args.json:
        with open(args.json, encoding="utf-8") as f:
            dados = json.load(f)
        produto = dados.get("nome", "Produto")
        descricao = dados.get("descricao", "")
        categoria = dados.get("categoria", "")
        preco = dados.get("preco", "")
        prefixo = dados.get("prefixo", "produto")
    elif args.produto:
        produto = args.produto
        descricao = args.descricao
        categoria = args.categoria
        preco = args.preco
        prefixo = args.prefixo
    else:
        print("Erro: Forneça --produto ou --json")
        sys.exit(1)

    resultado = gerar_roteiro_e_prompts(produto, descricao, categoria, preco)
    exibir_roteiro(resultado)
    path = salvar_roteiro(resultado, prefixo)
    print(f"\nArquivo salvo: {path}")
