"""
gc_image_gen.py — Geração de Imagens Ultra-Realistas para TikTok Shop
Video Anchor | MANUOS IA

Gera 3 imagens ultra-realistas de um produto com ângulos distintos:
  - Ângulo 1: Produto em destaque (Vontade/Desejo)
  - Ângulo 2: Contexto de uso / problema (Dor/Urgência)
  - Ângulo 3: Resultado / solução (Solução/CTA)

Uso:
  python gc_image_gen.py --produto "Tênis Nike Air Max" --descricao "Tênis esportivo branco"
  python gc_image_gen.py --json produto.json
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

from openai import OpenAI

# ============================================================
# CONFIGURAÇÃO
# ============================================================
REPO_DIR = Path(__file__).parent.parent
ASSETS_DIR = REPO_DIR / "gc_assets"
IMAGES_DIR = ASSETS_DIR / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

client = OpenAI()

# ============================================================
# PROMPTS DE ÂNGULOS (Templates)
# ============================================================
ANGLE_TEMPLATES = {
    "angulo_1_desejo": """
Ultra-realistic product photography, studio quality, 8K resolution.
Product: {produto}
Description: {descricao}
Scene: Clean white or gradient background, dramatic studio lighting with soft shadows.
The product is perfectly centered, showcasing its best features.
Style: Commercial product photography for luxury e-commerce, razor-sharp focus,
photorealistic texture details, professional color grading.
Shot: Front-facing hero shot, slightly elevated angle.
NO text, NO watermarks, NO people.
""",

    "angulo_2_contexto": """
Ultra-realistic lifestyle photography, cinematic quality, 8K resolution.
Product: {produto}
Description: {descricao}
Scene: The product being used in a real Brazilian home/urban environment.
Natural lighting, warm tones. A person's hands or body partially visible using the product.
The scene conveys a problem being solved or a desire being fulfilled.
Style: Authentic UGC-style but with professional quality, candid moment, relatable.
Shot: Medium close-up showing product in action, shallow depth of field.
NO text, NO watermarks.
""",

    "angulo_3_resultado": """
Ultra-realistic aspirational photography, cinematic quality, 8K resolution.
Product: {produto}
Description: {descricao}
Scene: The final result after using the product. Happy Brazilian person (25-40 years old)
in a beautiful setting, product visible. Conveys transformation, satisfaction and success.
Warm golden hour lighting or bright natural light.
Style: Aspirational lifestyle photography, premium feel, emotionally engaging.
Shot: Wide or medium shot showing person and product together, joyful expression.
NO text, NO watermarks.
"""
}

# ============================================================
# FUNÇÕES PRINCIPAIS
# ============================================================

def gerar_prompts_produto(produto: str, descricao: str, categoria: str = "") -> dict:
    """Usa o LLM para gerar prompts customizados para o produto específico."""
    print(f"  [IMG] Gerando prompts customizados para: {produto}")

    system_prompt = """Você é um especialista em fotografia de produto para TikTok Shop Brasil.
Sua tarefa é criar 3 prompts ultra-detalhados para geração de imagens realistas de produtos.
Cada prompt deve ser em inglês, técnico e específico para o produto.
Retorne APENAS um JSON válido com as chaves: angulo_1, angulo_2, angulo_3."""

    user_prompt = f"""Produto: {produto}
Descrição: {descricao}
Categoria: {categoria}

Crie 3 prompts de imagem ultra-realistas:
1. Ângulo 1 (Desejo): Produto em destaque puro, fundo limpo, iluminação dramática de estúdio. Faz o cliente querer ter o produto.
2. Ângulo 2 (Dor/Contexto): Produto sendo usado em contexto real brasileiro. Mostra o problema que resolve.
3. Ângulo 3 (Solução/Resultado): Pessoa brasileira feliz com o resultado de usar o produto. Aspiracional.

Cada prompt deve ter: tipo de shot, iluminação, ambiente, detalhes do produto, estilo fotográfico.
Todos em inglês, ultra-detalhados, no estilo de prompts para DALL-E 3.
Retorne APENAS o JSON."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.7
    )

    prompts = json.loads(response.choices[0].message.content)
    return prompts


def gerar_imagem(prompt: str, nome_arquivo: str, tamanho: str = "1024x1792") -> Path:
    """Gera uma imagem ultra-realista usando DALL-E 3 e salva localmente."""
    print(f"  [IMG] Gerando imagem: {nome_arquivo}")

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=tamanho,  # 9:16 para TikTok
            quality="hd",
            n=1
        )

        image_url = response.data[0].url

        # Download da imagem
        import urllib.request
        output_path = IMAGES_DIR / f"{nome_arquivo}.png"
        urllib.request.urlretrieve(image_url, output_path)

        size_kb = output_path.stat().st_size / 1024
        print(f"  [IMG] ✓ Salva: {output_path.name} ({size_kb:.0f} KB)")
        return output_path

    except Exception as e:
        print(f"  [IMG] ✗ Erro ao gerar {nome_arquivo}: {e}")
        raise


def gerar_tres_angulos(produto: str, descricao: str, categoria: str = "", prefixo: str = "produto") -> dict:
    """
    Pipeline completo: gera os 3 ângulos do produto.
    Retorna dict com paths das imagens geradas.
    """
    print(f"\n{'='*50}")
    print(f"GERAÇÃO DE IMAGENS: {produto}")
    print(f"{'='*50}")

    # Etapa 1: Gerar prompts customizados via LLM
    try:
        prompts = gerar_prompts_produto(produto, descricao, categoria)
        print(f"  [IMG] ✓ Prompts customizados gerados")
    except Exception as e:
        print(f"  [IMG] ⚠ Erro no LLM, usando templates padrão: {e}")
        prompts = {
            "angulo_1": ANGLE_TEMPLATES["angulo_1_desejo"].format(produto=produto, descricao=descricao),
            "angulo_2": ANGLE_TEMPLATES["angulo_2_contexto"].format(produto=produto, descricao=descricao),
            "angulo_3": ANGLE_TEMPLATES["angulo_3_resultado"].format(produto=produto, descricao=descricao),
        }

    # Etapa 2: Gerar as 3 imagens
    imagens = {}
    angulos = [
        ("angulo_1", f"{prefixo}_angulo1_desejo"),
        ("angulo_2", f"{prefixo}_angulo2_contexto"),
        ("angulo_3", f"{prefixo}_angulo3_resultado"),
    ]

    for chave_prompt, nome_arquivo in angulos:
        prompt = prompts.get(chave_prompt, "")
        if not prompt:
            print(f"  [IMG] ⚠ Prompt vazio para {chave_prompt}, pulando...")
            continue

        try:
            path = gerar_imagem(prompt, nome_arquivo)
            imagens[chave_prompt] = str(path)
            time.sleep(1)  # Rate limit
        except Exception as e:
            print(f"  [IMG] ✗ Falha em {nome_arquivo}: {e}")

    # Salvar metadados
    meta = {
        "produto": produto,
        "descricao": descricao,
        "categoria": categoria,
        "prompts": prompts,
        "imagens": imagens
    }
    meta_path = IMAGES_DIR / f"{prefixo}_meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"\n  [IMG] ✓ {len(imagens)}/3 imagens geradas")
    print(f"  [IMG] ✓ Metadados: {meta_path}")
    return imagens


# ============================================================
# CLI
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera 3 imagens ultra-realistas de um produto")
    parser.add_argument("--produto", type=str, help="Nome do produto")
    parser.add_argument("--descricao", type=str, default="", help="Descrição do produto")
    parser.add_argument("--categoria", type=str, default="", help="Categoria do produto")
    parser.add_argument("--prefixo", type=str, default="produto", help="Prefixo para os arquivos")
    parser.add_argument("--json", type=str, help="Arquivo JSON com dados do produto")

    args = parser.parse_args()

    if args.json:
        with open(args.json, encoding="utf-8") as f:
            dados = json.load(f)
        produto = dados.get("nome", "Produto")
        descricao = dados.get("descricao", "")
        categoria = dados.get("categoria", "")
        prefixo = dados.get("prefixo", "produto")
    elif args.produto:
        produto = args.produto
        descricao = args.descricao
        categoria = args.categoria
        prefixo = args.prefixo
    else:
        print("Erro: Forneça --produto ou --json")
        sys.exit(1)

    imagens = gerar_tres_angulos(produto, descricao, categoria, prefixo)

    print("\nImagens geradas:")
    for angulo, path in imagens.items():
        print(f"  {angulo}: {path}")
