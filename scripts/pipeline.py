"""
pipeline.py — Pipeline Completo de Produção de Vídeos
Video Anchor | The Anchor Records

Orquestra o fluxo completo de produção:
  1. Geração de vozes (TTS via OpenAI)
  2. Lip-sync com avatar (D-ID API)
  3. Renderização final (logo + talk + trilha)
  4. Exportação (Drive / Dropbox / local)

Uso:
  python pipeline.py --etapa all
  python pipeline.py --etapa vozes
  python pipeline.py --etapa lipsync
  python pipeline.py --etapa render
  python pipeline.py --etapa exportar --destino drive
  python pipeline.py --status
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

REPO_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = REPO_DIR / "scripts"

# ============================================================
# UTILITÁRIOS
# ============================================================

def log(msg: str, level: str = "INFO"):
    ts = datetime.utcnow().strftime("%H:%M:%S")
    icons = {"INFO": "ℹ", "OK": "✓", "ERRO": "✗", "AVISO": "⚠", "ETAPA": "▶"}
    icon = icons.get(level, "•")
    print(f"[{ts}] {icon} {msg}")


def run_script(script_name: str, args: list = None) -> bool:
    """Executa um script Python e retorna True se bem-sucedido."""
    script_path = SCRIPTS_DIR / script_name
    cmd = [sys.executable, str(script_path)] + (args or [])
    log(f"Executando: {script_name}", "ETAPA")
    result = subprocess.run(cmd, cwd=str(REPO_DIR))
    if result.returncode == 0:
        log(f"{script_name} concluído com sucesso.", "OK")
        return True
    else:
        log(f"{script_name} falhou (código {result.returncode}).", "ERRO")
        return False


def check_env_var(var: str) -> bool:
    """Verifica se uma variável de ambiente está definida."""
    val = os.environ.get(var)
    if not val:
        log(f"Variável de ambiente '{var}' não definida.", "AVISO")
        return False
    return True


def check_assets():
    """Verifica se os assets necessários existem."""
    required = [
        REPO_DIR / "assets" / "anchor_presenter.jpg",
        REPO_DIR / "assets" / "logo_intro.png",
        REPO_DIR / "assets" / "trilha_anchor.mp3",
    ]
    ok = True
    for path in required:
        if not path.exists():
            log(f"Asset ausente: {path.relative_to(REPO_DIR)}", "AVISO")
            ok = False
        else:
            log(f"Asset OK: {path.relative_to(REPO_DIR)}", "OK")
    return ok


def check_vozes():
    """Verifica se os arquivos de voz existem."""
    vozes_dir = REPO_DIR / "assets" / "vozes"
    roteiros = ["01", "02", "03", "04"]
    ok = True
    for rid in roteiros:
        wav = vozes_dir / f"roteiro_{rid}_voz.wav"
        if not wav.exists():
            log(f"Voz ausente: {wav.name}", "AVISO")
            ok = False
        else:
            log(f"Voz OK: {wav.name}", "OK")
    return ok


def check_talks():
    """Verifica se os vídeos D-ID existem."""
    talks_dir = REPO_DIR / "videos_did"
    roteiros = [
        ("01", "Comercial_Direto"),
        ("02", "Processo_Autoridade"),
        ("03", "Cena_Network"),
        ("04", "Remarketing"),
    ]
    ok = True
    for rid, titulo in roteiros:
        mp4 = talks_dir / f"talk_{rid}_{titulo}.mp4"
        if not mp4.exists():
            log(f"Talk ausente: {mp4.name}", "AVISO")
            ok = False
        else:
            size_mb = mp4.stat().st_size / (1024 * 1024)
            log(f"Talk OK: {mp4.name} ({size_mb:.1f} MB)", "OK")
    return ok


def check_videos_final():
    """Verifica se os vídeos finais existem."""
    videos_dir = REPO_DIR / "videos_final"
    roteiros = [
        ("01", "Comercial_Direto"),
        ("02", "Processo_Autoridade"),
        ("03", "Cena_Network"),
        ("04", "Remarketing"),
    ]
    ok = True
    for rid, titulo in roteiros:
        mp4 = videos_dir / f"video_{rid}_{titulo}_FINAL.mp4"
        if not mp4.exists():
            log(f"Vídeo final ausente: {mp4.name}", "AVISO")
            ok = False
        else:
            size_mb = mp4.stat().st_size / (1024 * 1024)
            log(f"Vídeo final OK: {mp4.name} ({size_mb:.1f} MB)", "OK")
    return ok


# ============================================================
# ETAPAS DO PIPELINE
# ============================================================

def etapa_status():
    """Exibe o status completo do pipeline."""
    print(f"\n{'='*60}")
    print("STATUS DO PIPELINE — Video Anchor")
    print(f"{'='*60}")

    print("\n[1/4] ASSETS")
    check_assets()

    print("\n[2/4] VOZES")
    vozes_ok = check_vozes()
    if not vozes_ok:
        log("Execute: python pipeline.py --etapa vozes", "INFO")

    print("\n[3/4] TALKS (D-ID)")
    talks_ok = check_talks()
    if not talks_ok:
        log("Execute: python pipeline.py --etapa lipsync", "INFO")

    print("\n[4/4] VÍDEOS FINAIS")
    videos_ok = check_videos_final()
    if not videos_ok:
        log("Execute: python pipeline.py --etapa render", "INFO")

    print(f"\n{'='*60}")
    all_ok = vozes_ok and talks_ok and videos_ok
    if all_ok:
        log("Pipeline completo! Todos os vídeos estão prontos.", "OK")
        log("Para exportar: python pipeline.py --etapa exportar --destino drive", "INFO")
    else:
        log("Pipeline incompleto. Verifique os itens acima.", "AVISO")
    print(f"{'='*60}\n")


def etapa_vozes():
    """Etapa 1: Gerar vozes via TTS."""
    print(f"\n{'='*60}")
    print("ETAPA 1: Geração de Vozes (TTS)")
    print(f"{'='*60}")

    if not check_env_var("OPENAI_API_KEY"):
        log("Defina OPENAI_API_KEY no arquivo .env ou como variável de ambiente.", "ERRO")
        return False

    return run_script("gerar_vozes.py")


def etapa_lipsync():
    """Etapa 2: Gerar lip-sync via D-ID."""
    print(f"\n{'='*60}")
    print("ETAPA 2: Lip-sync com Avatar (D-ID API)")
    print(f"{'='*60}")

    if not check_env_var("DID_API_KEY"):
        log("Defina DID_API_KEY no arquivo .env ou como variável de ambiente.", "ERRO")
        return False

    if not check_vozes():
        log("Vozes não encontradas. Execute primeiro: python pipeline.py --etapa vozes", "ERRO")
        return False

    return run_script("did_generate.py")


def etapa_render():
    """Etapa 3: Renderizar vídeos finais."""
    print(f"\n{'='*60}")
    print("ETAPA 3: Renderização Final")
    print(f"{'='*60}")

    if not check_talks():
        log("Talks D-ID não encontrados. Execute: python pipeline.py --etapa lipsync", "ERRO")
        return False

    # Usar a fila de processamento
    log("Adicionando todos os roteiros à fila de renderização...", "INFO")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "queue_processor.py"), "add-all"],
        cwd=str(REPO_DIR)
    )
    if result.returncode != 0:
        log("Falha ao adicionar jobs à fila.", "ERRO")
        return False

    log("Processando fila...", "INFO")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "queue_processor.py"), "run"],
        cwd=str(REPO_DIR)
    )
    return result.returncode == 0


def etapa_exportar(destino: str = "local", local_dir: str = None):
    """Etapa 4: Exportar vídeos."""
    print(f"\n{'='*60}")
    print(f"ETAPA 4: Exportação de Vídeos → {destino.upper()}")
    print(f"{'='*60}")

    if not check_videos_final():
        log("Vídeos finais não encontrados. Execute: python pipeline.py --etapa render", "ERRO")
        return False

    args = ["--destino", destino, "--pasta", "videos_final"]
    if local_dir:
        args += ["--local-dir", local_dir]

    return run_script("exportar_videos.py", args)


def etapa_all(destino: str = "local"):
    """Executa o pipeline completo."""
    print(f"\n{'='*60}")
    print("PIPELINE COMPLETO — Video Anchor")
    print(f"{'='*60}\n")

    etapas = [
        ("Vozes", etapa_vozes),
        ("Lip-sync", etapa_lipsync),
        ("Render", etapa_render),
    ]

    for nome, func in etapas:
        ok = func()
        if not ok:
            log(f"Pipeline interrompido na etapa: {nome}", "ERRO")
            return False

    return etapa_exportar(destino)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pipeline de produção de vídeos — Video Anchor / The Anchor Records",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python pipeline.py --status
  python pipeline.py --etapa vozes
  python pipeline.py --etapa lipsync
  python pipeline.py --etapa render
  python pipeline.py --etapa exportar --destino drive
  python pipeline.py --etapa exportar --destino dropbox
  python pipeline.py --etapa exportar --destino local --local-dir /caminho/destino
  python pipeline.py --etapa all --destino drive
        """
    )
    parser.add_argument(
        "--etapa",
        choices=["vozes", "lipsync", "render", "exportar", "all"],
        help="Etapa do pipeline a executar"
    )
    parser.add_argument(
        "--destino",
        choices=["drive", "dropbox", "local", "ambos"],
        default="local",
        help="Destino da exportação (padrão: local)"
    )
    parser.add_argument(
        "--local-dir",
        default=None,
        help="Diretório local de destino (apenas para --destino=local)"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Exibe o status atual do pipeline"
    )

    args = parser.parse_args()

    if args.status or not args.etapa:
        etapa_status()
    elif args.etapa == "vozes":
        etapa_vozes()
    elif args.etapa == "lipsync":
        etapa_lipsync()
    elif args.etapa == "render":
        etapa_render()
    elif args.etapa == "exportar":
        etapa_exportar(args.destino, args.local_dir)
    elif args.etapa == "all":
        etapa_all(args.destino)
