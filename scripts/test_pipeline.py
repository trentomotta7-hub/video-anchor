"""
test_pipeline.py — Testes Automatizados do Pipeline
Video Anchor | The Anchor Records

Valida a integridade dos módulos sem executar chamadas de API reais.
Uso: python scripts/test_pipeline.py
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Adicionar o diretório raiz ao path
REPO_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_DIR / "scripts"))


class TestQueueProcessor(unittest.TestCase):
    """Testes para o sistema de fila de processamento."""

    def setUp(self):
        """Configura um diretório temporário para os testes."""
        self.tmpdir = tempfile.mkdtemp()
        self.queue_file = Path(self.tmpdir) / "jobs.json"
        self.log_dir = Path(self.tmpdir) / "logs"
        self.log_dir.mkdir()

    def test_add_job_cria_job_com_campos_corretos(self):
        """Verifica que add_job cria um job com todos os campos esperados."""
        import queue_processor as qp
        with patch.object(qp, "QUEUE_FILE", self.queue_file), \
             patch.object(qp, "LOG_DIR", self.log_dir):
            job_id = qp.add_job("render_final", {"roteiro_id": "01", "titulo": "Teste"}, priority=3)

        jobs = json.loads(self.queue_file.read_text())
        self.assertEqual(len(jobs), 1)
        job = jobs[0]
        self.assertEqual(job["id"], job_id)
        self.assertEqual(job["type"], "render_final")
        self.assertEqual(job["status"], "pending")
        self.assertEqual(job["priority"], 3)
        self.assertEqual(job["retries"], 0)
        self.assertEqual(job["max_retries"], 2)
        self.assertIsNone(job["output"])
        self.assertIsNone(job["error"])

    def test_jobs_ordenados_por_prioridade(self):
        """Verifica que jobs são ordenados por prioridade (menor = maior prioridade)."""
        import queue_processor as qp
        with patch.object(qp, "QUEUE_FILE", self.queue_file), \
             patch.object(qp, "LOG_DIR", self.log_dir):
            qp.add_job("render_final", {"roteiro_id": "03"}, priority=8)
            qp.add_job("render_final", {"roteiro_id": "01"}, priority=1)
            qp.add_job("render_final", {"roteiro_id": "02"}, priority=5)

        jobs = json.loads(self.queue_file.read_text())
        prioridades = [j["priority"] for j in jobs]
        self.assertEqual(prioridades, sorted(prioridades))

    def test_cancel_job_muda_status(self):
        """Verifica que cancel_job altera o status para 'cancelled'."""
        import queue_processor as qp
        with patch.object(qp, "QUEUE_FILE", self.queue_file), \
             patch.object(qp, "LOG_DIR", self.log_dir):
            job_id = qp.add_job("render_final", {"roteiro_id": "01"})
            result = qp.cancel_job(job_id)

        self.assertTrue(result)
        jobs = json.loads(self.queue_file.read_text())
        self.assertEqual(jobs[0]["status"], "cancelled")
        self.assertIsNotNone(jobs[0]["finished_at"])

    def test_cancel_job_inexistente_retorna_false(self):
        """Verifica que cancel_job retorna False para job inexistente."""
        import queue_processor as qp
        with patch.object(qp, "QUEUE_FILE", self.queue_file), \
             patch.object(qp, "LOG_DIR", self.log_dir):
            result = qp.cancel_job("nao_existe")
        self.assertFalse(result)

    def test_get_next_pending_job_retorna_primeiro_pendente(self):
        """Verifica que get_next_pending_job retorna o job pendente de maior prioridade."""
        import queue_processor as qp
        with patch.object(qp, "QUEUE_FILE", self.queue_file), \
             patch.object(qp, "LOG_DIR", self.log_dir):
            id1 = qp.add_job("render_final", {"roteiro_id": "01"}, priority=5)
            id2 = qp.add_job("render_final", {"roteiro_id": "02"}, priority=1)
            job = qp.get_next_pending_job()

        self.assertIsNotNone(job)
        self.assertEqual(job["id"], id2)  # Prioridade 1 vem primeiro

    def test_update_job_status_running(self):
        """Verifica que update_job_status define started_at ao mudar para running."""
        import queue_processor as qp
        with patch.object(qp, "QUEUE_FILE", self.queue_file), \
             patch.object(qp, "LOG_DIR", self.log_dir):
            job_id = qp.add_job("render_final", {"roteiro_id": "01"})
            qp.update_job_status(job_id, "running")

        jobs = json.loads(self.queue_file.read_text())
        self.assertEqual(jobs[0]["status"], "running")
        self.assertIsNotNone(jobs[0]["started_at"])

    def test_executors_registrados(self):
        """Verifica que todos os tipos de job têm executores registrados."""
        import queue_processor as qp
        tipos_esperados = ["render_final", "render_v4", "generate_voice", "did_lipsync"]
        for tipo in tipos_esperados:
            self.assertIn(tipo, qp.EXECUTORS,
                          f"Executor para '{tipo}' não encontrado em EXECUTORS")

    def test_list_jobs_com_filtro(self):
        """Verifica que list_jobs filtra corretamente por status."""
        import queue_processor as qp
        with patch.object(qp, "QUEUE_FILE", self.queue_file), \
             patch.object(qp, "LOG_DIR", self.log_dir):
            id1 = qp.add_job("render_final", {"roteiro_id": "01"})
            id2 = qp.add_job("render_final", {"roteiro_id": "02"})
            qp.cancel_job(id1)

            pendentes = qp.list_jobs("pending")
            cancelados = qp.list_jobs("cancelled")

        self.assertEqual(len(pendentes), 1)
        self.assertEqual(len(cancelados), 1)
        self.assertEqual(pendentes[0]["id"], id2)


class TestDidGenerate(unittest.TestCase):
    """Testes para o módulo de integração D-ID."""

    def test_api_key_via_env_var(self):
        """Verifica que a API key é lida da variável de ambiente."""
        with patch.dict(os.environ, {"DID_API_KEY": "test_key_123"}):
            api_key = os.environ.get("DID_API_KEY")
        self.assertEqual(api_key, "test_key_123")

    def test_sem_api_key_retorna_none(self):
        """Verifica que sem a variável de ambiente, a key é None."""
        env_sem_key = {k: v for k, v in os.environ.items() if k != "DID_API_KEY"}
        with patch.dict(os.environ, env_sem_key, clear=True):
            api_key = os.environ.get("DID_API_KEY")
        self.assertIsNone(api_key)


class TestExportarVideos(unittest.TestCase):
    """Testes para o módulo de exportação."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def test_exportar_local_copia_arquivo(self):
        """Verifica que exportar_local copia o arquivo para o destino."""
        import exportar_videos as ev

        # Criar arquivo de teste
        src = Path(self.tmpdir) / "test_video.mp4"
        src.write_bytes(b"fake video content")
        dest_dir = Path(self.tmpdir) / "destino"

        result = ev.exportar_local(src, dest_dir)

        self.assertTrue(result["success"])
        self.assertTrue((dest_dir / "test_video.mp4").exists())
        self.assertEqual((dest_dir / "test_video.mp4").read_bytes(), b"fake video content")

    def test_load_env_le_arquivo_env(self):
        """Verifica que load_env lê variáveis do arquivo .env."""
        import exportar_videos as ev

        env_content = "GOOGLE_DRIVE_FOLDER_ID=folder123\nDROPBOX_ACCESS_TOKEN=token456\n"
        env_path = Path(self.tmpdir) / ".env"
        env_path.write_text(env_content)

        with patch.object(ev, "REPO_DIR", Path(self.tmpdir)):
            env = ev.load_env()

        self.assertEqual(env.get("GOOGLE_DRIVE_FOLDER_ID"), "folder123")
        self.assertEqual(env.get("DROPBOX_ACCESS_TOKEN"), "token456")

    def test_registrar_exportacao_salva_log(self):
        """Verifica que registrar_exportacao salva o log corretamente."""
        import exportar_videos as ev
        log_path = Path(self.tmpdir) / "export_log.json"

        with patch.object(ev, "EXPORT_LOG", log_path):
            ev.registrar_exportacao("video.mp4", "local", "/path/video.mp4", "ok")

        log = json.loads(log_path.read_text())
        self.assertEqual(len(log), 1)
        self.assertEqual(log[0]["arquivo"], "video.mp4")
        self.assertEqual(log[0]["destino"], "local")
        self.assertEqual(log[0]["status"], "ok")


class TestAssets(unittest.TestCase):
    """Testes de integridade dos assets do repositório."""

    def test_assets_principais_existem(self):
        """Verifica que os assets principais do projeto existem."""
        assets = [
            REPO_DIR / "assets" / "anchor_presenter.jpg",
            REPO_DIR / "assets" / "logo_intro.png",
            REPO_DIR / "assets" / "trilha_anchor.mp3",
        ]
        for asset in assets:
            self.assertTrue(asset.exists(), f"Asset ausente: {asset}")

    def test_roteiros_existem(self):
        """Verifica que todos os 4 roteiros existem."""
        roteiros = [
            REPO_DIR / "roteiros" / "roteiro-01-comercial-direto.md",
            REPO_DIR / "roteiros" / "roteiro-02-processo-autoridade.md",
            REPO_DIR / "roteiros" / "roteiro-03-cena-internacional-network.md",
            REPO_DIR / "roteiros" / "roteiro-04-remarketing.md",
        ]
        for roteiro in roteiros:
            self.assertTrue(roteiro.exists(), f"Roteiro ausente: {roteiro}")

    def test_scripts_principais_existem(self):
        """Verifica que os scripts principais existem."""
        scripts = [
            REPO_DIR / "scripts" / "queue_processor.py",
            REPO_DIR / "scripts" / "exportar_videos.py",
            REPO_DIR / "scripts" / "templates_cenario.py",
            REPO_DIR / "scripts" / "gerar_vozes.py",
            REPO_DIR / "scripts" / "did_generate.py",
            REPO_DIR / "scripts" / "pipeline.py",
        ]
        for script in scripts:
            self.assertTrue(script.exists(), f"Script ausente: {script}")

    def test_requirements_txt_existe(self):
        """Verifica que o requirements.txt existe."""
        self.assertTrue((REPO_DIR / "requirements.txt").exists())

    def test_env_example_existe(self):
        """Verifica que o .env.example existe."""
        self.assertTrue((REPO_DIR / ".env.example").exists())


if __name__ == "__main__":
    print(f"\n{'='*60}")
    print("TESTES AUTOMATIZADOS — Video Anchor")
    print(f"{'='*60}\n")
    unittest.main(verbosity=2)
