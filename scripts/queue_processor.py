"""
queue_processor.py — Sistema de Fila de Processamento de Vídeos
Video Anchor | The Anchor Records

Gerencia uma fila persistente de tarefas de renderização, permitindo:
- Adicionar vídeos à fila sem bloquear o terminal
- Processar em background com controle de status
- Retomar tarefas interrompidas
- Relatório de progresso em tempo real
"""

import json
import os
import subprocess
import time
import uuid
from datetime import datetime
from pathlib import Path

# ============================================================
# CONFIGURAÇÕES
# ============================================================
REPO_DIR = Path(__file__).parent.parent
QUEUE_FILE = REPO_DIR / "queue" / "jobs.json"
LOG_DIR = REPO_DIR / "queue" / "logs"
OUTPUT_DIR = REPO_DIR / "videos_final"

QUEUE_DIR = REPO_DIR / "queue"
QUEUE_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Status possíveis de um job
STATUS_PENDING = "pending"
STATUS_RUNNING = "running"
STATUS_DONE = "done"
STATUS_FAILED = "failed"
STATUS_CANCELLED = "cancelled"


# ============================================================
# GERENCIAMENTO DA FILA
# ============================================================

def load_queue() -> list:
    """Carrega a fila de jobs do arquivo JSON."""
    if not QUEUE_FILE.exists():
        return []
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_queue(jobs: list):
    """Salva a fila de jobs no arquivo JSON."""
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)


def add_job(job_type: str, params: dict, priority: int = 5) -> str:
    """
    Adiciona um novo job à fila.

    Args:
        job_type: Tipo do job ('render_final', 'render_v4', 'generate_voice', 'did_lipsync')
        params: Parâmetros específicos do job
        priority: Prioridade (1=mais alta, 10=mais baixa)

    Returns:
        ID único do job criado
    """
    jobs = load_queue()
    job_id = str(uuid.uuid4())[:8]
    job = {
        "id": job_id,
        "type": job_type,
        "params": params,
        "priority": priority,
        "status": STATUS_PENDING,
        "created_at": datetime.utcnow().isoformat(),
        "started_at": None,
        "finished_at": None,
        "output": None,
        "error": None,
        "retries": 0,
        "max_retries": 2,
    }
    jobs.append(job)
    # Ordenar por prioridade (menor número = maior prioridade)
    jobs.sort(key=lambda x: (x["priority"], x["created_at"]))
    save_queue(jobs)
    print(f"[QUEUE] Job adicionado: {job_id} | tipo={job_type} | prioridade={priority}")
    return job_id


def update_job_status(job_id: str, status: str, output: str = None, error: str = None):
    """Atualiza o status de um job na fila."""
    jobs = load_queue()
    for job in jobs:
        if job["id"] == job_id:
            job["status"] = status
            if status == STATUS_RUNNING:
                job["started_at"] = datetime.utcnow().isoformat()
            elif status in (STATUS_DONE, STATUS_FAILED, STATUS_CANCELLED):
                job["finished_at"] = datetime.utcnow().isoformat()
            if output:
                job["output"] = output
            if error:
                job["error"] = error
            break
    save_queue(jobs)


def get_next_pending_job() -> dict | None:
    """Retorna o próximo job pendente com maior prioridade."""
    jobs = load_queue()
    for job in jobs:
        if job["status"] == STATUS_PENDING:
            return job
    return None


def list_jobs(status_filter: str = None) -> list:
    """Lista jobs, opcionalmente filtrados por status."""
    jobs = load_queue()
    if status_filter:
        return [j for j in jobs if j["status"] == status_filter]
    return jobs


def cancel_job(job_id: str) -> bool:
    """Cancela um job pendente."""
    jobs = load_queue()
    for job in jobs:
        if job["id"] == job_id and job["status"] == STATUS_PENDING:
            job["status"] = STATUS_CANCELLED
            job["finished_at"] = datetime.utcnow().isoformat()
            save_queue(jobs)
            print(f"[QUEUE] Job {job_id} cancelado.")
            return True
    print(f"[QUEUE] Job {job_id} não encontrado ou não está pendente.")
    return False


# ============================================================
# EXECUTORES DE JOBS
# ============================================================

def run_cmd(cmd: list, log_path: Path, label: str = "") -> tuple[bool, str]:
    """Executa um comando e registra o output no log."""
    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\n[{datetime.utcnow().isoformat()}] CMD: {' '.join(cmd)}\n")
        result = subprocess.run(cmd, capture_output=True, text=True)
        log.write(result.stdout)
        log.write(result.stderr)
        if result.returncode != 0:
            msg = f"ERRO em '{label}': {result.stderr[-500:]}"
            log.write(f"\n[ERRO] {msg}\n")
            return False, msg
        return True, ""


def execute_render_final(job: dict) -> tuple[bool, str, str]:
    """
    Executa a renderização final: logo + talk D-ID + logo + trilha.

    Params esperados:
        roteiro_id: '01', '02', '03', '04'
        titulo: nome do roteiro
        talk_path: caminho do MP4 do D-ID
        logo_dur: duração do logo em segundos (padrão: 3.0)
        music_vol: volume da trilha (padrão: 0.10)
    """
    params = job["params"]
    rid = params["roteiro_id"]
    titulo = params["titulo"]
    talk_path = params.get("talk_path", str(REPO_DIR / "videos_did" / f"talk_{rid}_{titulo}.mp4"))
    logo_dur = float(params.get("logo_dur", 3.0))
    music_vol = float(params.get("music_vol", 0.10))
    fade = 1.0

    logo = str(REPO_DIR / "assets" / "logo_intro.png")
    trilha = str(REPO_DIR / "assets" / "trilha_anchor.mp3")
    output = str(OUTPUT_DIR / f"video_{rid}_{titulo}_FINAL.mp4")
    log_path = LOG_DIR / f"job_{job['id']}.log"

    with open(log_path, "w", encoding="utf-8") as log:
        log.write(f"Job {job['id']} | render_final | {datetime.utcnow().isoformat()}\n")
        log.write(f"Roteiro: {rid} | {titulo}\n")

    # Verificar se o talk existe
    if not Path(talk_path).exists():
        return False, "", f"Talk não encontrado: {talk_path}"

    # Obter duração do talk
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", talk_path],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        return False, "", f"ffprobe falhou: {r.stderr}"
    talk_dur = float(r.stdout.strip())
    total_dur = logo_dur + talk_dur + logo_dur
    voz_delay_ms = int(logo_dur * 1000)

    # 1. Escalar talk
    ok, err = run_cmd([
        "ffmpeg", "-y", "-i", talk_path,
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1",
        "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-r", "30",
        "-c:a", "aac", "-b:a", "192k",
        f"/tmp/q_talk_scaled_{rid}.mp4"
    ], log_path, "scale talk")
    if not ok:
        return False, "", err

    # 2. Logos
    for tag, path in [("open", f"/tmp/q_logo_open_{rid}.mp4"), ("close", f"/tmp/q_logo_close_{rid}.mp4")]:
        ok, err = run_cmd([
            "ffmpeg", "-y",
            "-loop", "1", "-t", str(logo_dur), "-i", logo,
            "-vf", f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fade=t=in:st=0:d={fade},fade=t=out:st={logo_dur-fade}:d={fade}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-r", "30", "-an",
            path
        ], log_path, f"logo {tag}")
        if not ok:
            return False, "", err

    # 3. Concatenar
    concat_list = f"/tmp/q_concat_{rid}.txt"
    with open(concat_list, "w") as f:
        f.write(f"file '/tmp/q_logo_open_{rid}.mp4'\n")
        f.write(f"file '/tmp/q_talk_scaled_{rid}.mp4'\n")
        f.write(f"file '/tmp/q_logo_close_{rid}.mp4'\n")

    ok, err = run_cmd([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_list,
        "-c:v", "libx264", "-preset", "fast", "-crf", "17",
        "-c:a", "aac", "-b:a", "192k",
        f"/tmp/q_concat_{rid}.mp4"
    ], log_path, "concat")
    if not ok:
        return False, "", err

    # 4. Trilha
    ok, err = run_cmd([
        "ffmpeg", "-y",
        "-i", f"/tmp/q_concat_{rid}.mp4",
        "-i", f"/tmp/q_talk_scaled_{rid}.mp4",
        "-stream_loop", "-1", "-i", trilha,
        "-filter_complex",
        f"[1:a]adelay={voz_delay_ms}|{voz_delay_ms},volume=1.0[voz];"
        f"[2:a]atrim=0:{total_dur},volume={music_vol},afade=t=in:st=0:d=2,afade=t=out:st={total_dur-2}:d=2[music];"
        f"[voz][music]amix=inputs=2:duration=first[audio_out]",
        "-map", "0:v",
        "-map", "[audio_out]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(total_dur),
        output
    ], log_path, "trilha")
    if not ok:
        return False, "", err

    size = Path(output).stat().st_size / (1024 * 1024)
    with open(log_path, "a") as log:
        log.write(f"\n[OK] Saída: {output} ({size:.1f} MB)\n")

    return True, output, ""


# ============================================================
# WORKER PRINCIPAL
# ============================================================

def execute_render_v4(job: dict) -> tuple[bool, str, str]:
    """Executa a renderização v4 usando os templates de cenário."""
    params = job["params"]
    rid = params["roteiro_id"]
    template = params.get("template", "default")
    
    # Importar dinamicamente para evitar ciclo se houvesse
    import sys
    scripts_dir = str(REPO_DIR / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
        
    try:
        from templates_cenario import montar_com_template, ROTEIROS
        
        # Encontrar o roteiro
        roteiro = next((r for r in ROTEIROS if r["id"] == rid), None)
        if not roteiro:
            return False, "", f"Roteiro {rid} não encontrado nos templates."
            
        output_path = montar_com_template(roteiro, template)
        return True, output_path, ""
    except Exception as e:
        return False, "", str(e)


def execute_generate_voice(job: dict) -> tuple[bool, str, str]:
    """Gera a voz para um roteiro usando a API da OpenAI."""
    params = job["params"]
    rid = params["roteiro_id"]
    
    # Importar dinamicamente o gerar_vozes e executar apenas para o roteiro específico
    try:
        import subprocess
        
        # Como o gerar_vozes.py roda tudo no nível do módulo atualmente,
        # vamos usar uma abordagem simples: chamar o script.
        # Numa refatoração futura, gerar_vozes.py deveria ter funções.
        log_path = LOG_DIR / f"job_{job['id']}.log"
        script_path = REPO_DIR / "scripts" / "gerar_vozes.py"
        
        ok, err = run_cmd([
            "python3", str(script_path)
        ], log_path, "gerar_vozes")
        
        if not ok:
            return False, "", err
            
        output_path = str(REPO_DIR / "assets" / "vozes" / f"roteiro_{rid}_voz.wav")
        if Path(output_path).exists():
            return True, output_path, ""
        return False, "", f"Arquivo de voz não gerado: {output_path}"
    except Exception as e:
        return False, "", str(e)


def execute_did_lipsync(job: dict) -> tuple[bool, str, str]:
    """Gera o vídeo D-ID para um roteiro."""
    params = job["params"]
    rid = params["roteiro_id"]
    
    try:
        # Mesma abordagem do generate_voice por enquanto
        log_path = LOG_DIR / f"job_{job['id']}.log"
        script_path = REPO_DIR / "scripts" / "did_generate.py"
        
        ok, err = run_cmd([
            "python3", str(script_path)
        ], log_path, "did_generate")
        
        if not ok:
            return False, "", err
            
        # O nome do arquivo depende do título do roteiro
        from scripts.did_generate import ROTEIROS
        roteiro = next((r for r in ROTEIROS if r["id"] == rid), None)
        if not roteiro:
            return False, "", f"Roteiro {rid} não encontrado."
            
        output_path = str(REPO_DIR / "videos_did" / f"talk_{rid}_{roteiro['titulo']}.mp4")
        if Path(output_path).exists():
            return True, output_path, ""
        return False, "", f"Vídeo D-ID não gerado: {output_path}"
    except Exception as e:
        return False, "", str(e)


EXECUTORS = {
    "render_final": execute_render_final,
    "render_v4": execute_render_v4,
    "generate_voice": execute_generate_voice,
    "did_lipsync": execute_did_lipsync,
}


def process_next_job() -> bool:
    """
    Processa o próximo job pendente na fila.
    Retorna True se um job foi processado, False se a fila estava vazia.
    """
    job = get_next_pending_job()
    if not job:
        return False

    job_id = job["id"]
    job_type = job["type"]
    print(f"\n[WORKER] Iniciando job {job_id} | tipo={job_type}")
    update_job_status(job_id, STATUS_RUNNING)

    executor = EXECUTORS.get(job_type)
    if not executor:
        update_job_status(job_id, STATUS_FAILED, error=f"Tipo desconhecido: {job_type}")
        print(f"[WORKER] ERRO: tipo de job desconhecido '{job_type}'")
        return True

    try:
        success, output, error = executor(job)
        if success:
            update_job_status(job_id, STATUS_DONE, output=output)
            print(f"[WORKER] Job {job_id} concluído: {output}")
        else:
            # Verificar se deve tentar novamente
            jobs = load_queue()
            for j in jobs:
                if j["id"] == job_id:
                    if j["retries"] < j["max_retries"]:
                        j["retries"] += 1
                        j["status"] = STATUS_PENDING
                        j["error"] = error
                        save_queue(jobs)
                        print(f"[WORKER] Job {job_id} falhou (tentativa {j['retries']}/{j['max_retries']}): {error}")
                    else:
                        update_job_status(job_id, STATUS_FAILED, error=error)
                        print(f"[WORKER] Job {job_id} FALHOU definitivamente: {error}")
                    break
    except Exception as e:
        update_job_status(job_id, STATUS_FAILED, error=str(e))
        print(f"[WORKER] EXCEÇÃO no job {job_id}: {e}")

    return True


def run_worker(max_jobs: int = None, sleep_interval: int = 5):
    """
    Executa o worker em loop contínuo até a fila esvaziar.

    Args:
        max_jobs: Número máximo de jobs a processar (None = ilimitado)
        sleep_interval: Segundos de espera quando a fila está vazia
    """
    print(f"[WORKER] Iniciando worker | max_jobs={max_jobs or 'ilimitado'}")
    processed = 0
    while True:
        had_job = process_next_job()
        if had_job:
            processed += 1
            if max_jobs and processed >= max_jobs:
                print(f"[WORKER] Limite de {max_jobs} jobs atingido. Encerrando.")
                break
        else:
            pending = list_jobs(STATUS_PENDING)
            if not pending:
                print(f"[WORKER] Fila vazia. {processed} jobs processados. Encerrando.")
                break
            print(f"[WORKER] Aguardando... ({len(pending)} pendentes)")
            time.sleep(sleep_interval)


# ============================================================
# INTERFACE DE LINHA DE COMANDO
# ============================================================

def print_status():
    """Imprime o status atual da fila."""
    jobs = load_queue()
    if not jobs:
        print("Fila vazia.")
        return

    print(f"\n{'='*70}")
    print(f"{'ID':8} {'TIPO':15} {'STATUS':12} {'PRIORIDADE':10} {'CRIADO':20} {'SAÍDA'}")
    print(f"{'='*70}")
    for j in jobs:
        created = j["created_at"][:16] if j["created_at"] else "-"
        output = Path(j["output"]).name if j["output"] else (j["error"] or "-")
        print(f"{j['id']:8} {j['type']:15} {j['status']:12} {j['priority']:10} {created:20} {output}")
    print(f"{'='*70}")

    counts = {}
    for j in jobs:
        counts[j["status"]] = counts.get(j["status"], 0) + 1
    print("Resumo: " + " | ".join(f"{s}={n}" for s, n in counts.items()))


def add_all_roteiros_to_queue():
    """Adiciona todos os 4 roteiros à fila de renderização final."""
    roteiros = [
        {"id": "01", "titulo": "Comercial_Direto"},
        {"id": "02", "titulo": "Processo_Autoridade"},
        {"id": "03", "titulo": "Cena_Network"},
        {"id": "04", "titulo": "Remarketing"},
    ]
    for r in roteiros:
        add_job("render_final", {
            "roteiro_id": r["id"],
            "titulo": r["titulo"],
        }, priority=5)
    print(f"\n[QUEUE] {len(roteiros)} jobs adicionados à fila.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"

    if cmd == "status":
        print_status()

    elif cmd == "add-all":
        add_all_roteiros_to_queue()

    elif cmd == "add":
        # Uso: python queue_processor.py add <roteiro_id> <titulo> [prioridade]
        if len(sys.argv) < 4:
            print("Uso: python queue_processor.py add <roteiro_id> <titulo> [prioridade]")
            sys.exit(1)
        rid = sys.argv[2]
        titulo = sys.argv[3]
        priority = int(sys.argv[4]) if len(sys.argv) > 4 else 5
        jid = add_job("render_final", {"roteiro_id": rid, "titulo": titulo}, priority=priority)
        print(f"Job adicionado: {jid}")

    elif cmd == "run":
        # Processar todos os jobs pendentes
        run_worker()

    elif cmd == "run-one":
        # Processar apenas o próximo job
        process_next_job()

    elif cmd == "cancel":
        if len(sys.argv) < 3:
            print("Uso: python queue_processor.py cancel <job_id>")
            sys.exit(1)
        cancel_job(sys.argv[2])

    elif cmd == "clear":
        # Limpar jobs concluídos/cancelados
        jobs = load_queue()
        before = len(jobs)
        jobs = [j for j in jobs if j["status"] in (STATUS_PENDING, STATUS_RUNNING)]
        save_queue(jobs)
        print(f"Removidos {before - len(jobs)} jobs finalizados. Restam {len(jobs)}.")

    else:
        print(f"Comando desconhecido: {cmd}")
        print("Comandos disponíveis: status | add-all | add | run | run-one | cancel | clear")
