"""
gc_audio_gen.py — Geração de Áudio (TTS) e Legendas para TikTok Shop
Video Anchor | MANUOS IA

Gera a narração do roteiro usando OpenAI TTS e cria o arquivo SRT de legendas.
Framework narrativo: Vontade → Urgência → Dor → Solução

Uso:
  python gc_audio_gen.py --produto "Tênis Nike" --descricao "Tênis esportivo"
  python gc_audio_gen.py --json produto.json
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
AUDIO_DIR = ASSETS_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

client = OpenAI()

# Voz padrão: nova, expressiva, brasileira
DEFAULT_VOICE = "nova"  # Opções: alloy, echo, fable, onyx, nova, shimmer
DEFAULT_SPEED = 1.05    # Ligeiramente mais rápido para TikTok

# Duração alvo por take (segundos)
TAKE_DURATION = 8.0
TOTAL_DURATION = 25.0

# ============================================================
# GERAÇÃO DE ROTEIRO VIA LLM
# ============================================================

def gerar_roteiro(produto: str, descricao: str, categoria: str = "", preco: str = "") -> dict:
    """
    Usa GPT-4o para gerar um roteiro de 25s baseado no framework:
    Vontade (0-8s) → Urgência (8-16s) → Dor (16-20s) → Solução (20-25s)
    """
    print(f"  [AUDIO] Gerando roteiro para: {produto}")

    system_prompt = """Você é um copywriter especialista em TikTok Shop Brasil.
Crie roteiros de vídeo curtos (25 segundos) que vendem produtos de forma autêntica.
Framework obrigatório: Vontade → Urgência → Dor → Solução.
O texto deve soar natural, conversacional e brasileiro.
Retorne APENAS um JSON válido."""

    user_prompt = f"""Produto: {produto}
Descrição: {descricao}
Categoria: {categoria}
Preço: {preco}

Crie um roteiro de vídeo de 25 segundos para TikTok Shop Brasil.
O roteiro deve ter EXATAMENTE 3 blocos (takes), cada um com ~8 segundos de fala.

Framework obrigatório:
- Take 1 (0-8s): VONTADE — Cria desejo. Faz o espectador querer o produto. Hook forte.
- Take 2 (8-16s): URGÊNCIA + DOR — Mostra o problema sem o produto. Cria urgência.
- Take 3 (16-25s): SOLUÇÃO + CTA — Apresenta o produto como solução. Chamada para ação clara.

Regras:
- Máximo 25-30 palavras por take (para caber em 8 segundos)
- Tom: direto, empolgante, autêntico (não corporativo)
- Incluir 1 CTA no Take 3 (ex: "Clica no link", "Compra agora", "Aproveita")
- Linguagem 100% brasileira informal

Retorne JSON com:
{{
  "take_1_vontade": "texto do take 1",
  "take_2_urgencia_dor": "texto do take 2",
  "take_3_solucao_cta": "texto do take 3",
  "roteiro_completo": "texto completo unificado",
  "hook": "primeira frase impactante",
  "cta": "chamada para ação final"
}}"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.8
    )

    roteiro = json.loads(response.choices[0].message.content)
    print(f"  [AUDIO] ✓ Roteiro gerado")
    print(f"  [AUDIO]   Take 1: {roteiro.get('take_1_vontade', '')[:50]}...")
    print(f"  [AUDIO]   Take 2: {roteiro.get('take_2_urgencia_dor', '')[:50]}...")
    print(f"  [AUDIO]   Take 3: {roteiro.get('take_3_solucao_cta', '')[:50]}...")
    return roteiro


# ============================================================
# GERAÇÃO DE ÁUDIO TTS
# ============================================================

def gerar_tts(texto: str, nome_arquivo: str, voz: str = DEFAULT_VOICE, velocidade: float = DEFAULT_SPEED) -> Path:
    """Gera áudio TTS via OpenAI e salva como MP3."""
    print(f"  [AUDIO] Gerando TTS: {nome_arquivo}")

    output_path = AUDIO_DIR / f"{nome_arquivo}.mp3"

    response = client.audio.speech.create(
        model="tts-1-hd",
        voice=voz,
        input=texto,
        speed=velocidade
    )

    response.stream_to_file(str(output_path))

    size_kb = output_path.stat().st_size / 1024
    print(f"  [AUDIO] ✓ TTS salvo: {output_path.name} ({size_kb:.0f} KB)")
    return output_path


def obter_duracao_audio(path: Path) -> float:
    """Obtém a duração de um arquivo de áudio usando ffprobe."""
    import subprocess
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", str(path)],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "audio":
            return float(stream.get("duration", 0))
    return 0.0


# ============================================================
# GERAÇÃO DE LEGENDAS (SRT)
# ============================================================

def sec_to_srt(s: float) -> str:
    """Converte segundos para formato SRT (HH:MM:SS,mmm)."""
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    ms = int((s % 1) * 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def gerar_srt_takes(roteiro: dict, duracoes_takes: list, nome_arquivo: str) -> Path:
    """
    Gera arquivo SRT com legendas divididas por take.
    duracoes_takes: [dur_take1, dur_take2, dur_take3] em segundos
    """
    print(f"  [AUDIO] Gerando legendas SRT: {nome_arquivo}")

    takes_texto = [
        roteiro.get("take_1_vontade", ""),
        roteiro.get("take_2_urgencia_dor", ""),
        roteiro.get("take_3_solucao_cta", ""),
    ]

    output_path = AUDIO_DIR / f"{nome_arquivo}.srt"
    offset = 0.0

    with open(output_path, "w", encoding="utf-8") as f:
        for i, (texto, duracao) in enumerate(zip(takes_texto, duracoes_takes), 1):
            if not texto:
                continue

            # Divide o texto em 2 partes para melhor leitura
            palavras = texto.split()
            meio = len(palavras) // 2
            parte1 = " ".join(palavras[:meio])
            parte2 = " ".join(palavras[meio:])

            # Primeira metade do take
            t1_start = offset
            t1_end = offset + duracao * 0.5
            f.write(f"{i*2-1}\n")
            f.write(f"{sec_to_srt(t1_start)} --> {sec_to_srt(t1_end)}\n")
            f.write(f"{parte1}\n\n")

            # Segunda metade do take
            t2_start = t1_end
            t2_end = offset + duracao
            f.write(f"{i*2}\n")
            f.write(f"{sec_to_srt(t2_start)} --> {sec_to_srt(t2_end)}\n")
            f.write(f"{parte2}\n\n")

            offset += duracao

    print(f"  [AUDIO] ✓ SRT salvo: {output_path.name}")
    return output_path


# ============================================================
# PIPELINE COMPLETO DE ÁUDIO
# ============================================================

def gerar_audio_completo(produto: str, descricao: str, categoria: str = "",
                          preco: str = "", prefixo: str = "produto") -> dict:
    """
    Pipeline completo: gera roteiro, TTS por take e SRT.
    Retorna dict com paths e metadados.
    """
    print(f"\n{'='*50}")
    print(f"GERAÇÃO DE ÁUDIO: {produto}")
    print(f"{'='*50}")

    # Etapa 1: Gerar roteiro
    roteiro = gerar_roteiro(produto, descricao, categoria, preco)

    # Etapa 2: Gerar TTS para cada take
    takes_audio = {}
    takes_texto = {
        "take_1": roteiro.get("take_1_vontade", ""),
        "take_2": roteiro.get("take_2_urgencia_dor", ""),
        "take_3": roteiro.get("take_3_solucao_cta", ""),
    }

    for take_id, texto in takes_texto.items():
        if not texto:
            continue
        nome = f"{prefixo}_{take_id}"
        path = gerar_tts(texto, nome)
        duracao = obter_duracao_audio(path)
        takes_audio[take_id] = {
            "path": str(path),
            "duracao": duracao,
            "texto": texto
        }
        time.sleep(0.5)

    # Etapa 3: Gerar TTS do roteiro completo (para narração contínua)
    roteiro_completo = roteiro.get("roteiro_completo", " ".join(takes_texto.values()))
    audio_completo_path = gerar_tts(roteiro_completo, f"{prefixo}_naracao_completa")
    duracao_total = obter_duracao_audio(audio_completo_path)

    # Etapa 4: Gerar SRT
    duracoes = [takes_audio.get(f"take_{i}", {}).get("duracao", TAKE_DURATION) for i in range(1, 4)]
    srt_path = gerar_srt_takes(roteiro, duracoes, f"{prefixo}_legendas")

    # Salvar metadados
    resultado = {
        "produto": produto,
        "roteiro": roteiro,
        "takes_audio": takes_audio,
        "audio_completo": str(audio_completo_path),
        "duracao_total": duracao_total,
        "srt": str(srt_path),
        "duracoes_takes": duracoes
    }

    meta_path = AUDIO_DIR / f"{prefixo}_audio_meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"\n  [AUDIO] ✓ Pipeline de áudio completo")
    print(f"  [AUDIO]   Duração total: {duracao_total:.1f}s")
    print(f"  [AUDIO]   Áudio: {audio_completo_path.name}")
    print(f"  [AUDIO]   Legendas: {srt_path.name}")

    return resultado


# ============================================================
# CLI
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera áudio TTS e legendas para vídeo de produto")
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

    resultado = gerar_audio_completo(produto, descricao, categoria, preco, prefixo)

    print("\nAudios gerados:")
    for take, info in resultado.get("takes_audio", {}).items():
        print(f"  {take}: {info['path']} ({info['duracao']:.1f}s)")
