"""
exportar_videos.py — Exportação de Vídeos para Google Drive e Dropbox
Video Anchor | The Anchor Records

Permite enviar os vídeos finais diretamente para:
- Google Drive (via API OAuth2 ou service account)
- Dropbox (via API com token de acesso)
- Pasta local personalizada (fallback)

Configuração:
  Crie um arquivo .env na raiz do repositório com:
    GOOGLE_DRIVE_FOLDER_ID=<id_da_pasta_no_drive>
    DROPBOX_ACCESS_TOKEN=<token_do_dropbox>

Uso:
  python exportar_videos.py --destino drive --pasta videos_final
  python exportar_videos.py --destino dropbox --pasta videos_final
  python exportar_videos.py --destino ambos --pasta videos_final
  python exportar_videos.py --destino local --pasta videos_final --local-dir /caminho/destino
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

# ============================================================
# CONFIGURAÇÕES
# ============================================================
REPO_DIR = Path(__file__).parent.parent
EXPORT_LOG = REPO_DIR / "queue" / "export_log.json"
EXPORT_LOG.parent.mkdir(exist_ok=True)

# Carregar variáveis de ambiente do .env se existir
def load_env():
    env_path = REPO_DIR / ".env"
    env = {}
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    env[key.strip()] = val.strip().strip('"').strip("'")
    # Sobrescrever com variáveis de ambiente do sistema
    for key in ("GOOGLE_DRIVE_FOLDER_ID", "DROPBOX_ACCESS_TOKEN"):
        if key in os.environ:
            env[key] = os.environ[key]
    return env


# ============================================================
# REGISTRO DE EXPORTAÇÕES
# ============================================================

def load_export_log() -> list:
    if not EXPORT_LOG.exists():
        return []
    with open(EXPORT_LOG) as f:
        return json.load(f)


def save_export_log(log: list):
    with open(EXPORT_LOG, "w") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def registrar_exportacao(arquivo: str, destino: str, url: str, status: str, erro: str = ""):
    log = load_export_log()
    log.append({
        "arquivo": arquivo,
        "destino": destino,
        "url": url,
        "status": status,
        "erro": erro,
        "timestamp": datetime.utcnow().isoformat(),
    })
    save_export_log(log)


# ============================================================
# EXPORTAÇÃO PARA GOOGLE DRIVE
# ============================================================

def exportar_para_drive(arquivo_path: Path, folder_id: str = None) -> dict:
    """
    Faz upload de um arquivo para o Google Drive.

    Requer:
        pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

    Autenticação:
        Coloque o arquivo credentials.json (OAuth2 desktop) na raiz do repositório,
        ou defina GOOGLE_APPLICATION_CREDENTIALS para uma service account.

    Returns:
        dict com 'success', 'file_id', 'url', 'error'
    """
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
        import pickle
    except ImportError:
        return {
            "success": False,
            "error": (
                "Dependências do Google Drive não instaladas. Execute:\n"
                "  sudo pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
            )
        }

    SCOPES = ["https://www.googleapis.com/auth/drive.file"]
    creds = None
    token_path = REPO_DIR / "token_drive.pickle"
    creds_path = REPO_DIR / "credentials.json"
    sa_path = REPO_DIR / "service_account.json"

    # Tentar service account primeiro
    if sa_path.exists():
        creds = service_account.Credentials.from_service_account_file(
            str(sa_path), scopes=SCOPES
        )
    # Tentar token OAuth2 salvo
    elif token_path.exists():
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
    # Fluxo OAuth2 interativo
    elif creds_path.exists():
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, "wb") as token:
                pickle.dump(creds, token)
    else:
        return {
            "success": False,
            "error": (
                "Credenciais do Google Drive não encontradas.\n"
                "Coloque credentials.json ou service_account.json na raiz do repositório.\n"
                "Consulte: https://developers.google.com/drive/api/quickstart/python"
            )
        }

    try:
        service = build("drive", "v3", credentials=creds)
        file_metadata = {
            "name": arquivo_path.name,
            "mimeType": "video/mp4",
        }
        if folder_id:
            file_metadata["parents"] = [folder_id]

        media = MediaFileUpload(str(arquivo_path), mimetype="video/mp4", resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink"
        ).execute()

        file_id = file.get("id")
        url = file.get("webViewLink", f"https://drive.google.com/file/d/{file_id}/view")
        return {"success": True, "file_id": file_id, "url": url, "error": ""}

    except Exception as e:
        return {"success": False, "file_id": None, "url": None, "error": str(e)}


# ============================================================
# EXPORTAÇÃO PARA DROPBOX
# ============================================================

def exportar_para_dropbox(arquivo_path: Path, access_token: str, dropbox_folder: str = "/VideoAnchor") -> dict:
    """
    Faz upload de um arquivo para o Dropbox.

    Requer:
        pip install dropbox

    Returns:
        dict com 'success', 'url', 'error'
    """
    try:
        import dropbox
        from dropbox.exceptions import ApiError, AuthError
    except ImportError:
        return {
            "success": False,
            "error": (
                "Dependência Dropbox não instalada. Execute:\n"
                "  sudo pip3 install dropbox"
            )
        }

    if not access_token:
        return {
            "success": False,
            "error": (
                "Token do Dropbox não configurado.\n"
                "Adicione DROPBOX_ACCESS_TOKEN no arquivo .env ou como variável de ambiente."
            )
        }

    try:
        dbx = dropbox.Dropbox(access_token)
        dropbox_path = f"{dropbox_folder}/{arquivo_path.name}"

        file_size = arquivo_path.stat().st_size
        CHUNK_SIZE = 150 * 1024 * 1024  # 150 MB

        with open(arquivo_path, "rb") as f:
            if file_size <= CHUNK_SIZE:
                # Upload simples
                result = dbx.files_upload(
                    f.read(),
                    dropbox_path,
                    mode=dropbox.files.WriteMode.overwrite
                )
            else:
                # Upload em partes (para arquivos grandes)
                upload_session_start_result = dbx.files_upload_session_start(f.read(CHUNK_SIZE))
                cursor = dropbox.files.UploadSessionCursor(
                    session_id=upload_session_start_result.session_id,
                    offset=f.tell()
                )
                commit = dropbox.files.CommitInfo(
                    path=dropbox_path,
                    mode=dropbox.files.WriteMode.overwrite
                )
                while f.tell() < file_size:
                    if (file_size - f.tell()) <= CHUNK_SIZE:
                        result = dbx.files_upload_session_finish(f.read(CHUNK_SIZE), cursor, commit)
                    else:
                        dbx.files_upload_session_append_v2(f.read(CHUNK_SIZE), cursor)
                        cursor.offset = f.tell()

        # Criar link compartilhável
        try:
            link_result = dbx.sharing_create_shared_link_with_settings(dropbox_path)
            url = link_result.url
        except Exception:
            url = f"dropbox://{dropbox_path}"

        return {"success": True, "url": url, "error": ""}

    except Exception as e:
        return {"success": False, "url": None, "error": str(e)}


# ============================================================
# EXPORTAÇÃO LOCAL
# ============================================================

def exportar_local(arquivo_path: Path, destino_dir: Path) -> dict:
    """Copia o arquivo para um diretório local."""
    import shutil
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino = destino_dir / arquivo_path.name
    shutil.copy2(str(arquivo_path), str(destino))
    return {"success": True, "url": str(destino), "error": ""}


# ============================================================
# ORQUESTRADOR PRINCIPAL
# ============================================================

def exportar_pasta(pasta: str, destino: str, local_dir: str = None, dry_run: bool = False):
    """
    Exporta todos os vídeos MP4 de uma pasta para o destino especificado.

    Args:
        pasta: Nome da pasta de vídeos ('videos_final', 'videos_v4', etc.)
        destino: 'drive', 'dropbox', 'local', 'ambos'
        local_dir: Diretório local de destino (apenas para destino='local')
        dry_run: Se True, apenas lista os arquivos sem exportar
    """
    env = load_env()
    pasta_path = REPO_DIR / pasta

    if not pasta_path.exists():
        print(f"[ERRO] Pasta não encontrada: {pasta_path}")
        return

    arquivos = sorted(pasta_path.rglob("*.mp4"))
    if not arquivos:
        print(f"[AVISO] Nenhum arquivo .mp4 encontrado em {pasta_path}")
        return

    print(f"\n{'='*60}")
    print(f"Exportação de Vídeos — Video Anchor")
    print(f"Pasta: {pasta} | Destino: {destino} | Arquivos: {len(arquivos)}")
    print(f"{'='*60}")

    if dry_run:
        print("\n[DRY RUN] Arquivos que seriam exportados:")
        for f in arquivos:
            size = f.stat().st_size / (1024 * 1024)
            print(f"  {f.name} ({size:.1f} MB)")
        return

    resultados = []

    for arquivo in arquivos:
        size = arquivo.stat().st_size / (1024 * 1024)
        print(f"\nExportando: {arquivo.name} ({size:.1f} MB)")

        if destino in ("drive", "ambos"):
            folder_id = env.get("GOOGLE_DRIVE_FOLDER_ID")
            print(f"  → Google Drive (folder_id={folder_id or 'raiz'})...")
            res = exportar_para_drive(arquivo, folder_id)
            status = "ok" if res["success"] else "erro"
            url = res.get("url", "")
            erro = res.get("error", "")
            print(f"    {'✓' if res['success'] else '✗'} {url or erro}")
            registrar_exportacao(arquivo.name, "drive", url, status, erro)
            resultados.append(("drive", arquivo.name, status, url or erro))

        if destino in ("dropbox", "ambos"):
            token = env.get("DROPBOX_ACCESS_TOKEN")
            print(f"  → Dropbox...")
            res = exportar_para_dropbox(arquivo, token)
            status = "ok" if res["success"] else "erro"
            url = res.get("url", "")
            erro = res.get("error", "")
            print(f"    {'✓' if res['success'] else '✗'} {url or erro}")
            registrar_exportacao(arquivo.name, "dropbox", url, status, erro)
            resultados.append(("dropbox", arquivo.name, status, url or erro))

        if destino == "local":
            dest_dir = Path(local_dir) if local_dir else REPO_DIR / "export"
            print(f"  → Local ({dest_dir})...")
            res = exportar_local(arquivo, dest_dir)
            status = "ok" if res["success"] else "erro"
            url = res.get("url", "")
            erro = res.get("error", "")
            print(f"    {'✓' if res['success'] else '✗'} {url or erro}")
            registrar_exportacao(arquivo.name, "local", url, status, erro)
            resultados.append(("local", arquivo.name, status, url or erro))

    # Resumo final
    print(f"\n{'='*60}")
    print("RESUMO DA EXPORTAÇÃO:")
    ok_count = sum(1 for _, _, s, _ in resultados if s == "ok")
    err_count = len(resultados) - ok_count
    print(f"  Sucesso: {ok_count} | Erros: {err_count}")
    for dest, nome, status, info in resultados:
        icon = "✓" if status == "ok" else "✗"
        print(f"  {icon} [{dest}] {nome}: {info[:80]}")
    print(f"{'='*60}")
    print(f"\nLog salvo em: {EXPORT_LOG}")


def mostrar_log():
    """Exibe o histórico de exportações."""
    log = load_export_log()
    if not log:
        print("Nenhuma exportação registrada.")
        return
    print(f"\n{'='*70}")
    print(f"{'ARQUIVO':35} {'DESTINO':10} {'STATUS':8} {'DATA':20}")
    print(f"{'='*70}")
    for entry in reversed(log[-20:]):  # Últimas 20
        ts = entry["timestamp"][:16]
        print(f"{entry['arquivo'][:34]:35} {entry['destino']:10} {entry['status']:8} {ts:20}")
        if entry.get("url"):
            print(f"  URL: {entry['url'][:70]}")
        if entry.get("erro"):
            print(f"  Erro: {entry['erro'][:70]}")
    print(f"{'='*70}")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Exportar vídeos do Video Anchor para Google Drive, Dropbox ou local"
    )
    parser.add_argument(
        "--destino",
        choices=["drive", "dropbox", "local", "ambos"],
        default="local",
        help="Destino da exportação (padrão: local)"
    )
    parser.add_argument(
        "--pasta",
        default="videos_final",
        help="Pasta de vídeos para exportar (padrão: videos_final)"
    )
    parser.add_argument(
        "--local-dir",
        default=None,
        help="Diretório local de destino (apenas para --destino=local)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Apenas listar arquivos sem exportar"
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="Exibir histórico de exportações"
    )

    args = parser.parse_args()

    if args.log:
        mostrar_log()
    else:
        exportar_pasta(
            pasta=args.pasta,
            destino=args.destino,
            local_dir=args.local_dir,
            dry_run=args.dry_run,
        )
