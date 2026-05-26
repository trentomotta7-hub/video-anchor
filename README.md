# Video Anchor — The Anchor Records

Ferramenta de produção automatizada de vídeos publicitários (VSLs e Criativos) usando avatares de IA com lip-sync realista para a **The Anchor Records**.

## Visão Geral

O pipeline completo transforma roteiros em vídeos prontos para veiculação:

```
Roteiro (Markdown) → Voz (TTS) → Avatar Lip-sync (D-ID) → Edição Final (FFmpeg) → Exportação
```

## Estrutura do Projeto

```
video-anchor/
├── roteiros/                     # Roteiros em Markdown (PT-BR / EN)
├── assets/
│   ├── vozes/                    # Áudios gerados (WAV)
│   ├── anchor_presenter.jpg      # Imagem da apresentadora
│   ├── logo_intro.png            # Logo para abertura/fechamento
│   └── trilha_anchor.mp3         # Trilha de fundo
├── clips/                        # Clipes de vídeo da apresentadora
├── videos_did/                   # Vídeos com lip-sync (D-ID)
├── videos_final/                 # Vídeos finais (logo + talk + trilha)
├── videos_v4/                    # Vídeos com templates de cenário
├── scripts/
│   ├── pipeline.py               # Orquestrador do pipeline completo ⭐
│   ├── queue_processor.py        # Fila de processamento em background
│   ├── gerar_vozes.py            # Geração de voz via TTS (OpenAI)
│   ├── did_generate.py           # Lip-sync via D-ID API
│   ├── exportar_videos.py        # Exportação para Drive/Dropbox/local
│   ├── templates_cenario.py      # Templates visuais de cenário
│   ├── montar_videos.py          # Montagem básica (v1)
│   ├── montar_v4.py              # Montagem com legendas e CTA (v4)
│   ├── montar_did_final.py       # Montagem final com D-ID
│   └── test_pipeline.py          # Testes automatizados
├── analise/
│   ├── scoring_roteiros.py       # Análise de performance dos roteiros
│   └── relatorio_performance.md  # Relatório de análise
├── requirements.txt              # Dependências Python
├── .env.example                  # Modelo de variáveis de ambiente
└── update-checkpoint.sh          # Atualização manual do checkpoint
```

## Roteiros Disponíveis

| # | Título | Duração Estimada | Idiomas |
|---|--------|-----------------|---------|
| 1 | Comercial Direto | 28–32s | PT-BR / EN |
| 2 | Processo + Autoridade | 30–35s | PT-BR / EN |
| 3 | Cena + Internacional + Network | 33–38s | PT-BR / EN |
| 4 | Remarketing | 30–35s | PT-BR / EN |

## Configuração

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite o .env com suas credenciais
```

Variáveis necessárias:

| Variável | Descrição | Obrigatória |
|----------|-----------|-------------|
| `OPENAI_API_KEY` | Chave da API OpenAI (TTS) | Para gerar vozes |
| `DID_API_KEY` | Chave da API D-ID (lip-sync) | Para lip-sync |
| `GOOGLE_DRIVE_FOLDER_ID` | ID da pasta no Google Drive | Para exportar ao Drive |
| `DROPBOX_ACCESS_TOKEN` | Token do Dropbox | Para exportar ao Dropbox |

### 3. Verificar FFmpeg

```bash
ffmpeg -version
```

## Uso

### Pipeline Completo (recomendado)

```bash
# Ver status atual do pipeline
python scripts/pipeline.py --status

# Executar etapas individualmente
python scripts/pipeline.py --etapa vozes
python scripts/pipeline.py --etapa lipsync
python scripts/pipeline.py --etapa render
python scripts/pipeline.py --etapa exportar --destino drive

# Executar tudo de uma vez
python scripts/pipeline.py --etapa all --destino drive
```

### Fila de Processamento

```bash
# Ver status da fila
python scripts/queue_processor.py status

# Adicionar todos os roteiros à fila
python scripts/queue_processor.py add-all

# Processar a fila
python scripts/queue_processor.py run

# Adicionar um roteiro específico
python scripts/queue_processor.py add 01 Comercial_Direto 3
```

### Templates de Cenário

```bash
# Listar templates disponíveis
python scripts/templates_cenario.py list

# Renderizar um template específico
python scripts/templates_cenario.py escritorio 01
python scripts/templates_cenario.py lifestyle all

# Templates disponíveis: escritorio, lifestyle, estudio, default
```

### Testes Automatizados

```bash
python scripts/test_pipeline.py
```

## Versões dos Vídeos

| Versão | Descrição | Diretório |
|--------|-----------|-----------|
| v1 | Imagem estática + voz + trilha | `videos/` |
| v2 | Clipes reais da apresentadora | `videos_v2/` |
| v4 | Apresentadora + legendas + CTA Groover | `videos_v4/` |
| D-ID | Lip-sync realista via D-ID API | `videos_did/` |
| Final | Logo + Lip-sync + Trilha (produção) | `videos_final/` |

## Análise de Performance

Os roteiros foram avaliados em 8 critérios (0–10):

| Critério | R1 | R2 | R3 | R4 |
|----------|----|----|----|----|
| Hook | 8.5 | 6.5 | 7.5 | **9.0** |
| Proposta de Valor | 8.0 | **9.0** | 7.5 | 8.5 |
| Prova Social | 5.5 | 9.5 | **10.0** | 8.5 |
| Urgência | 7.0 | 6.5 | 6.0 | **9.5** |
| CTA | 8.5 | 7.5 | 7.0 | **9.5** |
| Formato Curto | **9.0** | 7.0 | 6.0 | 8.0 |
| Retenção Estimada | 7.5 | 7.0 | 6.5 | **8.5** |
| Diferenciação | 6.5 | 9.0 | **9.5** | 7.5 |
| **Score Médio** | 7.6 | 7.8 | 7.5 | **8.6** |

> **R4 (Remarketing)** tem o maior score geral (8.6/10) e ThruPlay estimado de 38%.

## Sobre a The Anchor Records

Label de música eletrônica fundada em 2015. Distribui músicas em mais de 50 plataformas globais, com o artista mantendo **90% dos royalties**. Todos os lançamentos são masterizados e assinados por **Nytron**, artista best-seller com mais de 150 tracks no Beatport Top 100.

## Padrão de Commits

| Prefixo | Uso |
|---------|-----|
| `feat:` | Nova funcionalidade |
| `fix:` | Correção de bug |
| `docs:` | Documentação |
| `refactor:` | Refatoração |
| `test:` | Testes |
| `chore:` | Manutenção |
| `checkpoint:` | Atualização automática |
