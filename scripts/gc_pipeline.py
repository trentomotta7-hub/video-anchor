"""
gc_pipeline.py — Orquestrador Principal do Pipeline GC para TikTok Shop
Video Anchor | MANUOS IA

Pipeline completo de geração de vídeos de produto para TikTok Shop Brasil.
Meta: 500 vendas/semana por produto.

Framework narrativo: Vontade → Urgência → Dor → Solução
Formato: 3 takes de ~8s = vídeo final de 25s, 1080x1920 (9:16), ultra-realista

Uso:
  # Produto simples
  python gc_pipeline.py --produto "Tênis Nike Air Max" --descricao "Tênis esportivo branco"

  # Com todas as opções
  python gc_pipeline.py \\
    --produto "Creme Hidratante Facial" \\
    --descricao "Creme anti-idade com vitamina C" \\
    --categoria "Beleza e Cuidados" \\
    --preco "R$ 89,90" \\
    --prefixo "creme_facial"

  # Via arquivo JSON
  python gc_pipeline.py --json produto.json

Exemplo de produto.json:
  {
    "nome": "Tênis Nike Air Max",
    "descricao": "Tênis esportivo branco com amortecimento",
    "categoria": "Moda e Calçados",
    "preco": "R$ 299,90",
    "prefixo": "tenis_nike"
  }
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# ============================================================
# CONFIGURAÇÃO
# ============================================================
REPO_DIR = Path(__file__).parent.parent
ASSETS_DIR = REPO_DIR / "gc_assets"
OUTPUT_DIR = REPO_DIR / "gc_output"
LOGS_DIR = REPO_DIR / "gc_logs"

ASSETS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# LOGGER
# ============================================================

def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    icons = {
        "INFO": "ℹ",
        "OK": "✓",
        "ERRO": "✗",
        "AVISO": "⚠",
        "ETAPA": "▶",
        "INICIO": "🚀",
        "FIM": "🎬"
    }
    icon = icons.get(level, "•")
    print(f"[{ts}] {icon} {msg}")


# ============================================================
# IMPORTAR MÓDULOS DO PIPELINE
# ============================================================

def importar_modulos():
    """Importa os módulos do pipeline e verifica dependências."""
    scripts_dir = Path(__file__).parent
    sys.path.insert(0, str(scripts_dir))

    try:
        from gc_image_gen import gerar_tres_angulos
        from gc_audio_gen import gerar_audio_completo
        from gc_video_composer import compor_video_final
        return gerar_tres_angulos, gerar_audio_completo, compor_video_final
    except ImportError as e:
        log(f"Erro ao importar módulos: {e}", "ERRO")
        log("Verifique se gc_image_gen.py, gc_audio_gen.py e gc_video_composer.py estão em scripts/", "ERRO")
        sys.exit(1)


# ============================================================
# VERIFICAÇÃO DE DEPENDÊNCIAS
# ============================================================

def verificar_dependencias():
    """Verifica se FFmpeg e outras dependências estão instaladas."""
    import subprocess

    deps = {
        "ffmpeg": ["ffmpeg", "-version"],
        "ffprobe": ["ffprobe", "-version"],
    }

    ok = True
    for nome, cmd in deps.items():
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode == 0:
            log(f"{nome}: OK", "OK")
        else:
            log(f"{nome}: NÃO ENCONTRADO", "ERRO")
            ok = False

    # Verificar OpenAI API Key
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key:
        log("OPENAI_API_KEY: OK", "OK")
    else:
        log("OPENAI_API_KEY: NÃO DEFINIDA", "ERRO")
        ok = False

    return ok


# ============================================================
# PIPELINE PRINCIPAL
# ============================================================

def executar_pipeline(produto: str, descricao: str, categoria: str = "",
                       preco: str = "", prefixo: str = None) -> dict:
    """
    Executa o pipeline completo de geração de vídeo GC.

    Etapas:
    1. Geração de 3 imagens ultra-realistas (3 ângulos)
    2. Geração de roteiro + TTS + legendas
    3. Composição e montagem do vídeo final (25s)

    Retorna dict com resultado e paths dos arquivos gerados.
    """
    inicio = time.time()

    # Gerar prefixo automático se não fornecido
    if not prefixo:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefixo = f"produto_{ts}"

    log(f"INICIANDO PIPELINE GC", "INICIO")
    log(f"Produto: {produto}")
    log(f"Descrição: {descricao}")
    log(f"Categoria: {categoria}")
    log(f"Preço: {preco}")
    log(f"Prefixo: {prefixo}")

    # Verificar dependências
    log("Verificando dependências...", "ETAPA")
    if not verificar_dependencias():
        log("Dependências ausentes. Abortando.", "ERRO")
        sys.exit(1)

    # Importar módulos
    gerar_tres_angulos, gerar_audio_completo, compor_video_final = importar_modulos()

    resultado = {
        "produto": produto,
        "descricao": descricao,
        "categoria": categoria,
        "preco": preco,
        "prefixo": prefixo,
        "inicio": datetime.now().isoformat(),
        "status": "em_progresso",
        "imagens": {},
        "audio": {},
        "video_final": None,
        "erros": []
    }

    # ─────────────────────────────────────────────────────────
    # ETAPA 1: GERAÇÃO DE IMAGENS
    # ─────────────────────────────────────────────────────────
    log("ETAPA 1/3: Gerando imagens ultra-realistas...", "ETAPA")
    try:
        imagens = gerar_tres_angulos(produto, descricao, categoria, prefixo)
        resultado["imagens"] = imagens
        log(f"Imagens geradas: {len(imagens)}/3", "OK")
    except Exception as e:
        erro = f"Falha na geração de imagens: {e}"
        log(erro, "ERRO")
        resultado["erros"].append(erro)
        resultado["status"] = "erro_imagens"
        salvar_log(resultado, prefixo)
        raise

    # ─────────────────────────────────────────────────────────
    # ETAPA 2: GERAÇÃO DE ÁUDIO E ROTEIRO
    # ─────────────────────────────────────────────────────────
    log("ETAPA 2/3: Gerando roteiro, narração e legendas...", "ETAPA")
    try:
        audio_meta = gerar_audio_completo(produto, descricao, categoria, preco, prefixo)
        resultado["audio"] = audio_meta
        log(f"Áudio gerado: {audio_meta.get('duracao_total', 0):.1f}s", "OK")
        log(f"Roteiro Take 1: {audio_meta.get('roteiro', {}).get('take_1_vontade', '')[:60]}...", "INFO")
        log(f"Roteiro Take 2: {audio_meta.get('roteiro', {}).get('take_2_urgencia_dor', '')[:60]}...", "INFO")
        log(f"Roteiro Take 3: {audio_meta.get('roteiro', {}).get('take_3_solucao_cta', '')[:60]}...", "INFO")
    except Exception as e:
        erro = f"Falha na geração de áudio: {e}"
        log(erro, "ERRO")
        resultado["erros"].append(erro)
        resultado["status"] = "erro_audio"
        salvar_log(resultado, prefixo)
        raise

    # ─────────────────────────────────────────────────────────
    # ETAPA 3: COMPOSIÇÃO DO VÍDEO FINAL
    # ─────────────────────────────────────────────────────────
    log("ETAPA 3/3: Compondo vídeo final de 25s...", "ETAPA")
    try:
        video_final = compor_video_final(imagens, audio_meta, prefixo)
        resultado["video_final"] = str(video_final)
        resultado["status"] = "concluido"
        log(f"Vídeo final: {video_final}", "OK")
    except Exception as e:
        erro = f"Falha na composição do vídeo: {e}"
        log(erro, "ERRO")
        resultado["erros"].append(erro)
        resultado["status"] = "erro_video"
        salvar_log(resultado, prefixo)
        raise

    # ─────────────────────────────────────────────────────────
    # RESUMO FINAL
    # ─────────────────────────────────────────────────────────
    tempo_total = time.time() - inicio
    resultado["tempo_total_segundos"] = round(tempo_total, 1)
    resultado["fim"] = datetime.now().isoformat()

    log(f"PIPELINE CONCLUÍDO em {tempo_total:.0f}s", "FIM")
    log(f"Vídeo final: {resultado['video_final']}", "FIM")

    salvar_log(resultado, prefixo)
    return resultado


def salvar_log(resultado: dict, prefixo: str):
    """Salva o log do pipeline em JSON."""
    log_path = LOGS_DIR / f"{prefixo}_pipeline_log.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    log(f"Log salvo: {log_path.name}", "INFO")


# ============================================================
# EXIBIR ROTEIRO (preview)
# ============================================================

def exibir_roteiro(resultado: dict):
    """Exibe o roteiro gerado de forma formatada."""
    roteiro = resultado.get("audio", {}).get("roteiro", {})
    if not roteiro:
        return

    print("\n" + "="*60)
    print("📋 ROTEIRO GERADO (Framework: Vontade → Urgência → Dor → Solução)")
    print("="*60)
    print(f"\n🎯 TAKE 1 — VONTADE (0-8s):")
    print(f"   {roteiro.get('take_1_vontade', 'N/A')}")
    print(f"\n⚡ TAKE 2 — URGÊNCIA + DOR (8-16s):")
    print(f"   {roteiro.get('take_2_urgencia_dor', 'N/A')}")
    print(f"\n✅ TAKE 3 — SOLUÇÃO + CTA (16-25s):")
    print(f"   {roteiro.get('take_3_solucao_cta', 'N/A')}")
    print(f"\n🔥 HOOK: {roteiro.get('hook', 'N/A')}")
    print(f"📣 CTA:  {roteiro.get('cta', 'N/A')}")
    print("="*60)


# ============================================================
# CLI
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pipeline GC — Gera vídeo de 25s para TikTok Shop",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python gc_pipeline.py --produto "Tênis Nike Air Max" --descricao "Tênis esportivo branco"
  python gc_pipeline.py --json produto.json
        """
    )
    parser.add_argument("--produto", type=str, help="Nome do produto")
    parser.add_argument("--descricao", type=str, default="", help="Descrição do produto")
    parser.add_argument("--categoria", type=str, default="", help="Categoria do produto")
    parser.add_argument("--preco", type=str, default="", help="Preço do produto (ex: R$ 99,90)")
    parser.add_argument("--prefixo", type=str, default=None, help="Prefixo para os arquivos gerados")
    parser.add_argument("--json", type=str, help="Arquivo JSON com dados do produto")
    parser.add_argument("--apenas-roteiro", action="store_true", help="Gera apenas o roteiro (sem imagens/vídeo)")

    args = parser.parse_args()

    # Carregar dados do produto
    if args.json:
        with open(args.json, encoding="utf-8") as f:
            dados = json.load(f)
        produto = dados.get("nome", "Produto")
        descricao = dados.get("descricao", "")
        categoria = dados.get("categoria", "")
        preco = dados.get("preco", "")
        prefixo = dados.get("prefixo", None)
    elif args.produto:
        produto = args.produto
        descricao = args.descricao
        categoria = args.categoria
        preco = args.preco
        prefixo = args.prefixo
    else:
        print("Erro: Forneça --produto ou --json")
        print("Use --help para ver as opções disponíveis")
        sys.exit(1)

    # Executar pipeline
    try:
        resultado = executar_pipeline(produto, descricao, categoria, preco, prefixo)
        exibir_roteiro(resultado)

        print(f"\n🎬 VÍDEO FINAL PRONTO:")
        print(f"   {resultado.get('video_final', 'N/A')}")
        print(f"\n⏱  Tempo total: {resultado.get('tempo_total_segundos', 0):.0f}s")

    except Exception as e:
        log(f"Pipeline falhou: {e}", "ERRO")
        sys.exit(1)
