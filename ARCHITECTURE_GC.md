# Arquitetura: Pipeline de Vídeos GC para TikTok Shop

Este documento define a arquitetura para o novo pipeline de geração de vídeos focado em vendas no TikTok Shop Brasil, com meta de 500 vendas/semana por produto.

## 1. Visão Geral do Pipeline

O novo sistema (`gc_pipeline.py`) será uma evolução do `pipeline.py` atual, focado em geração 100% autônoma baseada em produtos.

### Especificações do Vídeo Final
- **Duração Total:** ~25 segundos
- **Estrutura Visual:** 3 takes contínuos de ~8 segundos cada (sem cortes secos)
- **Imagens:** 3 ângulos diferentes do produto, gerados por IA (ultra-realistas)
- **Narrativa (Áudio/Legenda):** Vontade → Urgência → Dor → Solução
- **Formato:** GC (Grid Composition / Graphic Content) com proporção 9:16 (TikTok)

## 2. Fluxo de Execução (Workflow)

O processo ocorrerá em 4 etapas principais:

### Etapa 1: Geração de Roteiro e Prompts (LLM)
- **Entrada:** Nome/Descrição do Produto
- **Processamento:**
  - Gera a copy baseada no framework: Vontade (0-6s) → Urgência (6-12s) → Dor (12-18s) → Solução (18-25s)
  - Gera 3 prompts detalhados para imagens ultra-realistas (3 ângulos diferentes)

### Etapa 2: Geração de Assets Visuais e Áudio
- **Imagens:** Utiliza a API de geração de imagens (DALL-E 3 ou similar) para criar 3 fotos ultra-realistas baseadas nos prompts.
- **Áudio:** Utiliza TTS (Text-to-Speech) via OpenAI para gerar a narração do roteiro.

### Etapa 3: Animação e Composição (Vídeo Base)
- Transforma as 3 imagens estáticas em takes de 8 segundos usando efeitos de Ken Burns (zoom/pan suave) para manter o dinamismo sem cortes bruscos.
- **Take 1:** Imagem 1 (Vontade/Urgência)
- **Take 2:** Imagem 2 (Dor)
- **Take 3:** Imagem 3 (Solução/CTA)

### Etapa 4: Montagem Final (FFmpeg)
- Concatena os 3 takes com transições suaves (crossfade).
- Sincroniza a narração (TTS).
- Adiciona legendas dinâmicas (estilo TikTok).
- Adiciona trilha sonora de fundo.
- Renderiza o vídeo final (`.mp4`).

## 3. Estrutura de Diretórios e Arquivos

```
video-anchor/
├── scripts/
│   ├── gc_pipeline.py          # Orquestrador principal
│   ├── gc_image_gen.py         # Geração de imagens ultra-realistas
│   ├── gc_audio_gen.py         # Geração de TTS e legendas
│   └── gc_video_composer.py    # Montagem final com FFmpeg
├── gc_assets/
│   ├── inputs/                 # Dados do produto (JSON)
│   ├── images/                 # Imagens geradas (3 ângulos)
│   ├── audio/                  # TTS e trilha
│   └── temp/                   # Takes individuais e SRT
└── gc_output/                  # Vídeos finais de 25s
```

## 4. Tecnologias Utilizadas

- **Orquestração:** Python 3.11
- **Geração de Imagens:** OpenAI DALL-E 3 (via `openai` lib)
- **Geração de Áudio (TTS):** OpenAI TTS API
- **Edição e Composição:** FFmpeg (filtros `zoompan`, `fade`, `subtitles`, `amix`)
- **Legendas:** Geração de SRT com timestamps calculados baseados no texto.

## 5. Integração com Repositórios Existentes

- **manuos-ia-skill:** O framework de copy (Vontade, Urgência, Dor, Solução) será codificado diretamente no prompt do LLM na Etapa 1.
- **video-anchor:** Reutilizaremos lógicas de chamada do FFmpeg e geração de SRT já presentes no `montar_v4.py`.
