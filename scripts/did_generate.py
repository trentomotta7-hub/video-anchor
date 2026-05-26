import requests
import time
import os
import json

from pathlib import Path

# Carregar variáveis de ambiente do .env se existir
REPO_DIR = Path(__file__).parent.parent
env_path = REPO_DIR / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

DID_API_KEY = os.environ.get("DID_API_KEY", "")
if not DID_API_KEY:
    print("AVISO: DID_API_KEY não encontrada nas variáveis de ambiente ou .env")
    
BASE_URL = "https://api.d-id.com"
HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Basic {DID_API_KEY}"
}
HEADERS_UPLOAD = {
    "accept": "application/json",
    "authorization": f"Basic {DID_API_KEY}"
}

PRESENTER_IMG = str(REPO_DIR / "assets" / "anchor_presenter.jpg")
VOZES_DIR = str(REPO_DIR / "assets" / "vozes")
TALKS_DIR = str(REPO_DIR / "videos_did")
os.makedirs(TALKS_DIR, exist_ok=True)

ROTEIROS = [
    {"id": "01", "titulo": "Comercial_Direto"},
    {"id": "02", "titulo": "Processo_Autoridade"},
    {"id": "03", "titulo": "Cena_Network"},
    {"id": "04", "titulo": "Remarketing"},
]

# ============================================================
# PASSO 1: Upload da imagem da apresentadora
# ============================================================
def upload_image():
    print("Fazendo upload da imagem...")
    with open(PRESENTER_IMG, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/images",
            headers=HEADERS_UPLOAD,
            files={"image": ("presenter.jpg", f, "image/jpeg")}
        )
    print(f"  Status: {resp.status_code} | {resp.text[:200]}")
    if resp.status_code in (200, 201):
        url = resp.json().get("url")
        print(f"  URL da imagem: {url}")
        return url
    return None

# ============================================================
# PASSO 2: Upload do áudio
# ============================================================
def upload_audio(audio_path):
    print(f"  Upload do áudio: {os.path.basename(audio_path)}")
    with open(audio_path, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/audios",
            headers=HEADERS_UPLOAD,
            files={"audio": (os.path.basename(audio_path), f, "audio/wav")}
        )
    print(f"    Status: {resp.status_code} | {resp.text[:200]}")
    if resp.status_code in (200, 201):
        return resp.json().get("url")
    return None

# ============================================================
# PASSO 3: Criar talk (lip-sync)
# ============================================================
def create_talk(image_url, audio_url, name):
    print(f"  Criando talk: {name}")
    payload = {
        "source_url": image_url,
        "script": {
            "type": "audio",
            "audio_url": audio_url
        },
        "config": {
            "fluent": True,
            "pad_audio": 0.0,
            "stitch": True,
            "result_format": "mp4"
        },
        "name": name
    }
    resp = requests.post(f"{BASE_URL}/talks", headers=HEADERS, json=payload)
    print(f"    Status: {resp.status_code} | {resp.text[:300]}")
    if resp.status_code == 201:
        return resp.json().get("id")
    return None

# ============================================================
# PASSO 4: Aguardar e baixar o vídeo
# ============================================================
def wait_and_download(talk_id, output_path, timeout=300):
    print(f"  Aguardando talk {talk_id}...")
    url = f"{BASE_URL}/talks/{talk_id}"
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(url, headers=HEADERS)
        data = resp.json()
        status = data.get("status")
        print(f"    Status: {status} ({int(time.time()-start)}s)")
        if status == "done":
            result_url = data.get("result_url")
            print(f"    Baixando de: {result_url}")
            r = requests.get(result_url, stream=True)
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            size = os.path.getsize(output_path) / (1024*1024)
            print(f"    Salvo: {output_path} ({size:.1f} MB)")
            return True
        elif status == "error":
            print(f"    ERRO: {data}")
            return False
        time.sleep(8)
    print("    TIMEOUT!")
    return False

# ============================================================
# EXECUÇÃO
# ============================================================

# Upload da imagem (uma vez só)
image_url = upload_image()
if not image_url:
    print("FALHA no upload da imagem. Abortando.")
    exit(1)

# Salvar IDs dos talks para acompanhamento
talks_info = []

for r in ROTEIROS:
    rid = r["id"]
    titulo = r["titulo"]
    voz_path = f"{VOZES_DIR}/roteiro_{rid}_voz.wav"
    output_path = f"{TALKS_DIR}/talk_{rid}_{titulo}.mp4"

    print(f"\n{'='*50}")
    print(f"Roteiro {rid}: {titulo}")

    # Upload do áudio
    audio_url = upload_audio(voz_path)
    if not audio_url:
        print(f"  FALHA no upload do áudio {rid}. Pulando.")
        continue

    # Criar talk
    talk_id = create_talk(image_url, audio_url, f"anchor_r{rid}")
    if not talk_id:
        print(f"  FALHA ao criar talk {rid}. Pulando.")
        continue

    talks_info.append({
        "id": rid,
        "titulo": titulo,
        "talk_id": talk_id,
        "output": output_path
    })
    print(f"  Talk criado: {talk_id}")

# Salvar talks_info para referência
with open(f"{TALKS_DIR}/talks_info.json", "w") as f:
    json.dump(talks_info, f, indent=2)

print(f"\n{'='*50}")
print(f"Talks criados: {len(talks_info)}")
print("Aguardando processamento...")

# Aguardar e baixar todos
for t in talks_info:
    print(f"\nBaixando Roteiro {t['id']}...")
    ok = wait_and_download(t["talk_id"], t["output"])
    t["downloaded"] = ok

print(f"\n{'='*50}")
print("RESUMO:")
for t in talks_info:
    status = "OK" if t.get("downloaded") else "FALHOU"
    print(f"  R{t['id']} {t['titulo']}: {status}")
