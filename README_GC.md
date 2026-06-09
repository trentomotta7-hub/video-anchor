# Pipeline GC — Gerador de Vídeos para TikTok Shop Brasil

> **Meta:** 500 vendas/semana por produto | Vídeos ultra-realistas de 25s gerados por IA

---

## Visão Geral

O Pipeline GC é um sistema de geração automática de vídeos para TikTok Shop Brasil. A partir do nome e descrição de um produto, ele gera um vídeo de 25 segundos pronto para publicação, com:

- **3 imagens ultra-realistas** geradas por IA (3 ângulos distintos do produto)
- **Roteiro de alta conversão** baseado no framework Vontade → Urgência → Dor → Solução
- **Narração em português brasileiro** com voz natural e expressiva
- **Efeito Ken Burns** (zoom/pan suave) em cada take para dinamismo visual
- **Legendas TikTok-style** queimadas no vídeo
- **Trilha de fundo** mixada em volume baixo
- **Entrega:** 1 arquivo MP4 final, 1080x1920 (9:16), 30fps, ~27s

---

## Estrutura do Vídeo

| Take | Tempo | Narrativa | Visual |
|------|-------|-----------|--------|
| Take 1 | 0–9s | **VONTADE** — Hook forte, cria desejo | Produto em destaque, fundo limpo |
| Take 2 | 9–18s | **URGÊNCIA + DOR** — Problema sem o produto | Pessoa com dor/problema, uso real |
| Take 3 | 18–27s | **SOLUÇÃO + CTA** — Produto resolve, CTA | Pessoa feliz com resultado |

---

## Uso Rápido

### 1. Gerar vídeo completo (pipeline único)

```bash
# Produto simples
python scripts/gc_montar_final.py --prefixo meu_produto

# Antes, gerar roteiro e imagens:
python scripts/gc_roteiro_gen.py \
  --produto "Nome do Produto" \
  --descricao "Descrição detalhada" \
  --categoria "Categoria" \
  --preco "R$ 99,90" \
  --prefixo "meu_produto"
```

### 2. Via arquivo JSON

Crie um arquivo em `gc_assets/inputs/meu_produto.json`:

```json
{
  "nome": "Creme Hidratante Facial Anti-Idade",
  "descricao": "Creme com vitamina C, colágeno e ácido hialurônico",
  "categoria": "Beleza e Cuidados Pessoais",
  "preco": "R$ 89,90",
  "prefixo": "creme_facial"
}
```

Depois execute:

```bash
python scripts/gc_roteiro_gen.py --json gc_assets/inputs/meu_produto.json
```

---

## Estrutura de Diretórios

```
video-anchor/
├── scripts/
│   ├── gc_roteiro_gen.py      # Gera roteiro + prompts de imagem via LLM
│   ├── gc_montar_final.py     # Monta o vídeo final (Ken Burns + legendas + áudio)
│   ├── gc_image_gen.py        # Geração de imagens via DALL-E (requer API)
│   ├── gc_audio_gen.py        # Geração de TTS via OpenAI (requer API)
│   └── gc_pipeline.py         # Orquestrador completo (requer APIs externas)
├── gc_assets/
│   ├── inputs/                # JSONs de produto e roteiros gerados
│   ├── images/                # Imagens geradas (3 ângulos por produto)
│   ├── audio/                 # Narração TTS e trilha
│   └── temp/                  # Takes individuais e SRT (temporários)
└── gc_output/                 # Vídeos finais prontos para TikTok Shop
```

---

## Fluxo de Produção Completo

```
1. PRODUTO (nome + descrição)
         ↓
2. LLM (claude-sonnet) → ROTEIRO (3 takes) + PROMPTS DE IMAGEM
         ↓
3. IA → 3 IMAGENS ULTRA-REALISTAS (9:16, 1080x1920)
         ↓
4. TTS → NARRAÇÃO (27s, voz brasileira)
         ↓
5. FFMPEG → 3 TAKES com Ken Burns (zoom/pan 9.3s cada)
         ↓
6. FFMPEG → CROSSFADE entre takes
         ↓
7. FFMPEG → LEGENDAS TikTok-style queimadas
         ↓
8. FFMPEG → MIXAGEM (narração + trilha de fundo)
         ↓
9. VÍDEO FINAL MP4 (1080x1920, 30fps, ~27s)
```

---

## Exemplo de Roteiro Gerado

**Produto:** Creme Hidratante Facial Anti-Idade

| Take | Texto |
|------|-------|
| **Take 1 — VONTADE** | "Imagina acordar todo dia com a pele lisinha, hidratada e sem uma ruga? Isso é possível sim, olha só!" |
| **Take 2 — URGÊNCIA + DOR** | "Enquanto você ignora sua pele, as rugas aparecem mais rápido. Cada dia sem cuidado é difícil de recuperar depois." |
| **Take 3 — SOLUÇÃO + CTA** | "Esse creme com vitamina C, colágeno e ácido hialurônico reduz rugas em 30 dias! Por só R$89,90, clica no link agora!" |

---

## Dependências

```bash
# Python
pip install openai

# Sistema
sudo apt install ffmpeg
```

---

## Integração com manuos-ia-page

O pipeline GC está alinhado com a plataforma MANUOS IA e usa os frameworks definidos em `manuos-ia-skill`:

- **Framework de Copy:** Vontade → Urgência → Dor → Solução
- **Framework de Ângulos:** 3 ângulos distintos por produto
- **Compliance TikTok:** Sem claims médicos, sem escassez falsa

---

*Pipeline GC — Video Anchor | MANUOS IA | 2026*
