# Decisions — video-anchor

> Registro de decisões arquiteturais e de design tomadas ao longo do projeto.

---

## 2026-05-24 — Sessão Manus: Implementação dos 3 próximos passos

### D1: Fila de processamento baseada em JSON (sem Redis/Celery)

**Contexto:** Precisávamos de uma fila de processamento para renderização de vídeos longos em background.

**Decisão:** Implementar fila persistente em `queue/jobs.json` com worker Python puro.

**Razão:** O volume de jobs (4–20 por lote) não justifica a complexidade de Redis ou Celery. A solução JSON é zero-dependência, portátil, legível e suficiente. Suporta prioridades, retries automáticos (até 2 tentativas), logs individuais por job e cancelamento.

**Trade-offs:** Não suporta múltiplos workers paralelos (race condition no JSON). Para escalar, migrar para SQLite ou Redis.

---

### D2: Templates de cenário via filtros FFmpeg (sem assets externos)

**Contexto:** Precisávamos de variações de cenário (escritório, lifestyle, estúdio) sem depender de imagens de fundo adicionais.

**Decisão:** Implementar templates como combinações de cor de fundo de padding FFmpeg + bordas decorativas via `drawbox`.

**Razão:** Elimina dependência de assets externos, funciona com os clips da apresentadora já existentes, e cada template tem identidade visual distinta através de paleta de cores e estilo de legenda customizado.

**Trade-offs:** Menos impacto visual do que um fundo real de escritório/estúdio. Para maior realismo, substituir pelo fundo real quando disponível.

---

### D3: Exportação com credenciais em .env (não no código)

**Contexto:** Precisávamos integrar exportação para Google Drive e Dropbox sem expor credenciais no repositório.

**Decisão:** Ler `GOOGLE_DRIVE_FOLDER_ID` e `DROPBOX_ACCESS_TOKEN` do arquivo `.env` (não versionado) ou de variáveis de ambiente do sistema.

**Razão:** Segurança básica — credenciais não devem ser commitadas. O `.env` deve estar no `.gitignore`.

**Ação necessária:** Verificar se `.env` está no `.gitignore` antes de criar o arquivo.

---

## 2026-05-08 — Sessão original: Pipeline inicial

### D4: D-ID API para lip-sync (em vez de Wav2Lip local)

**Contexto:** Precisávamos de lip-sync realista para a apresentadora.

**Decisão:** Usar a API do D-ID em vez de rodar Wav2Lip localmente.

**Razão:** Qualidade superior, sem necessidade de GPU local, integração simples via REST API.

**Trade-offs:** Custo por vídeo, dependência de serviço externo, latência de processamento.

---

### D5: Apresentadora única com imagem estática (anchor_presenter.jpg)

**Contexto:** Escolha do avatar para os vídeos.

**Decisão:** Usar uma única imagem da apresentadora (`anchor_presenter.jpg`) para todos os vídeos.

**Razão:** Consistência de marca, simplicidade de produção, fácil substituição futura.

## 2026-05-24 23:26:24 +0000

**Decisions:**

- Fila baseada em JSON (sem Redis/Celery) por ser zero-dependência e suficiente para o volume atual. Templates via filtros FFmpeg puro sem assets externos.
