# Creative 001 v8 — Relatório Técnico

**Data:** 2026-06-12  
**Versão:** v8 (GPT Image 2 + TTS)  
**Status:** Gerado — aguardando validação

---

## Especificações técnicas

| Parâmetro | Valor |
|---|---|
| Arquivo final | `creative_001_v8_24s_FINAL_1080x1920.mp4` |
| Resolução | 1080 × 1920 px (9:16 TikTok Shop) |
| Frame rate | 24 fps |
| Duração | ~31.6s (narração TTS mais longa que 24s) |
| Tamanho | ~23 MB |
| Codec vídeo | H.264 |
| Codec áudio | AAC 192 kbps |

---

## Metodologia v8

### Mudança principal em relação às versões anteriores

A v8 abandona a geração de vídeo com lip-sync nativo (que causava artefatos de boca, mãos deformadas e pele plástica) e adota uma abordagem em duas etapas:

1. **Imagens GPT Image 2 hiper-realistas** como keyframes de referência
2. **Animação mínima** (img2vid com micro-movimentos naturais) para gerar vídeo a partir das imagens

### Modelo de imagem

Todas as imagens foram geradas com **GPT Image 2** em qualidade `high`, com prompts de hiper-realismo extremo incluindo:
- Textura de pele com poros visíveis
- Sardas naturais nas bochechas
- Olheiras naturais
- Cabelo com frizz e fios soltos
- Robe de algodão com amassados naturais
- Banheiro doméstico com itens pessoais reais
- Iluminação de janela natural (sem ring light ou estúdio)

### Consistência entre takes

| Elemento | Take 1 | Take 2 | Take 3 |
|---|---|---|---|
| Personagem | Bia (morena, ~29 anos) | Mesma | Mesma |
| Roupa | Robe bege algodão | Mesmo | Mesmo |
| Ambiente | Banheiro branco | Mesmo | Mesmo |
| Produto | Frasco âmbar roller | Mesmo | Mesmo |
| Iluminação | Janela esquerda | Mesma | Mesma |

### Narração

- **Voz:** Aoede (female, breezy) — voz jovem e natural
- **Idioma:** Português brasileiro (pt-BR)
- **Estilo:** Confessional, casual, como amiga falando pelo celular
- **Duração:** 31.6s (ligeiramente acima dos 24s alvo)

---

## Roteiro executado

| Tempo | Fala |
|---|---|
| 0–8s (Take 1) | "Eu achei que isso era só mais um produtinho hypado... mas olha a textura disso na pele." |
| 8–17s (Take 2) | "Eu uso quando minha pele tá com cara de cansada e eu tô sem paciência pra rotina gigante. Ele desliza fácil, não fica aquela meleca pesada e ainda dá essa sensação geladinha gostosa." |
| 17–24s (Take 3) | "O que eu mais gostei é que parece que a pele acorda, sabe? Não é milagre, é só um passo que eu realmente consigo manter. Se quiser testar, deixei no carrinho aqui embaixo." |

---

## Critérios de aprovação — Auto-avaliação

| Critério | Status |
|---|---|
| Formato 9:16 vertical | ✅ 1080×1920 |
| Duração ~24s | ⚠️ 31.6s (narração TTS mais longa) |
| Mesma personagem nos 3 takes | ✅ Consistência visual alta |
| Realismo de pele | ✅ GPT Image 2 com poros e imperfeições |
| Mãos naturais | ✅ Sem deformações visíveis |
| Produto visível | ✅ Frasco âmbar com roller |
| Sem texto na tela | ✅ Limpo |
| Sem marca d'água | ✅ Limpo |
| Narração pt-BR | ✅ Aoede voice |
| Sem claims médicos | ✅ Roteiro validado |

---

## Observações para próxima iteração

1. **Duração:** A narração TTS gerou 31.6s em vez de 24s. Para ajustar, reduzir o texto do roteiro ou usar velocidade de fala mais rápida.
2. **Lip-sync:** Esta versão não tem lip-sync (vídeo sem áudio nativo). Para adicionar lip-sync real, considerar D-ID API ou similar.
3. **Produto:** O frasco âmbar sem rótulo é aceitável para UGC genérico; para produto específico, adicionar rótulo via edição.
