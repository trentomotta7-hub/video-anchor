# PROMPT MESTRE ANTI-IA — Sistema de Geração de Vídeos UGC
## Video Anchor | Versão 1.0 — Junho 2026

---

## PRINCÍPIO FUNDAMENTAL

O objetivo não é gerar um vídeo bonito. É gerar um vídeo que o cérebro humano identifique como filmado por uma pessoa real com um celular real num banheiro real. Cada elemento do prompt deve servir a esse objetivo.

**Os 3 elementos que fazem IA parecer IA (e como eliminar cada um):**

| Elemento | Como a IA falha | Como corrigir no prompt |
|---|---|---|
| **Produto** | Label distorcida, embalagem "flutuando", iluminação inconsistente | Descrever produto com luz que bate no mesmo ângulo da cena, sombra natural |
| **Pessoa** | Pele plástica, olhos sem profundidade, expressão "congelada", mãos perfeitas demais | Especificar imperfeições: poros, manchas, olheiras, fios soltos, unhas sem esmalte |
| **Câmera** | Estabilização perfeita demais, enquadramento centralizado, foco uniforme | Especificar tremor de mão, leve desalinhamento, foco ligeiramente irregular |

---

## PROMPT MESTRE — IMAGEM (GPT Image 2)

### Bloco 1 — Câmera e Dispositivo (FIXO em todos os criativos)
```
Shot on iPhone 15 front camera, selfie mode, 1x zoom, slight natural hand tremor visible, 
camera held at slight upward angle (15 degrees above eye level), 
frame slightly off-center (subject positioned 5% left of center), 
natural lens distortion from wide-angle front camera, 
slight chromatic aberration at frame edges, 
no stabilization artifacts, no gimbal smoothness.
```

### Bloco 2 — Iluminação (FIXO — banheiro com luz natural)
```
Lighting: single natural light source from window on left side, 
soft diffused morning light (7am-9am quality), 
slight warm cast on left side of face, 
right side in natural shadow (no fill light), 
no ring light, no softbox, no studio lighting, 
slight lens flare from window if window is in frame.
```

### Bloco 3 — Pele e Rosto (FIXO — imperfeições humanas reais)
```
Skin: visible pores on nose bridge and cheeks, 
slight redness around nose, 
faint freckles on cheeks and nose, 
natural under-eye shadows (not dark circles, just normal fatigue), 
one or two small blemishes or post-acne marks, 
no foundation, no concealer, no filter, 
skin texture visible at normal viewing distance, 
natural lip color (no lipstick), 
slightly chapped lip texture.
```

### Bloco 4 — Cabelo (FIXO — imperfeições humanas reais)
```
Hair: dark brown, loosely tied messy bun, 
multiple strands falling across forehead and cheeks, 
visible frizz and flyaways catching the window light, 
slightly damp or just-washed texture, 
no hair products visible (no gel, no serum shine), 
bun held by a single elastic, slightly asymmetrical.
```

### Bloco 5 — Roupa (FIXO — camiseta branca, NUNCA muda entre takes)
```
OUTFIT — LOCKED FOR ALL TAKES: plain white crew-neck cotton t-shirt, 
slightly wrinkled at collar and chest area, 
no logos, no patterns, no prints, 
fabric shows natural creases from being worn, 
collar slightly stretched from previous washes.
THIS EXACT OUTFIT MUST APPEAR IN EVERY SINGLE TAKE. DO NOT CHANGE.
```

### Bloco 6 — Ambiente (FIXO — banheiro doméstico brasileiro)
```
Setting: real Brazilian home bathroom, 
white ceramic wall tiles (standard 20x20cm), 
granite or marble countertop visible at bottom of frame, 
personal items on counter: pump soap dispenser, toothbrush holder with 2 toothbrushes, 
small stack of cotton pads in clear container, 
mirror partially visible on right edge, 
no professional decor, no plants, no candles, 
slightly steamy atmosphere from recent shower.
```

### Bloco 7 — Produto (VARIÁVEL por criativo)
```
Product: [DESCREVER PRODUTO AQUI]
Product lighting: same window light as scene, 
product casts natural shadow on hand/counter, 
label facing camera at slight angle (not perfectly perpendicular), 
product shows signs of use (not brand new, not pristine), 
hand grip is natural and relaxed (not posed, not perfect).
```

### Bloco 8 — Expressão e Postura (VARIÁVEL por take)
```
[TAKE 1 — HOOK]: Wide eyes, slight jaw drop, mouth open mid-sentence, 
eyebrows raised in genuine surprise, 
head tilted 10 degrees to the right, 
direct eye contact with camera lens (not slightly off to the side).

[TAKE 2 — DEMO]: Eyes gently closed or looking at product, 
relaxed smile, slight head tilt forward, 
shoulders relaxed and slightly rounded (not posed upright).

[TAKE 3 — CTA]: Warm genuine smile showing teeth naturally, 
direct eye contact, 
left index finger pointing casually downward, 
slight shoulder shrug of enthusiasm.
```

### Bloco 9 — Anti-IA (FIXO em todos os criativos)
```
CRITICAL ANTI-AI REQUIREMENTS:
- This must look like a real person filmed themselves on a phone, NOT an AI render
- Skin must show texture, pores, and minor imperfections — NOT smooth or plastic
- Eyes must have depth, slight redness in corners, natural moisture — NOT glassy or perfect
- Hands must show natural veins, knuckles, and skin folds — NOT perfectly smooth
- The overall image must feel like it was taken in 0.3 seconds, not posed for 30 minutes
- No symmetry perfection — real faces are slightly asymmetrical
- No perfect lighting — real selfies have uneven illumination
```

---

## PROMPT MESTRE — VÍDEO (generate_video)

### Template de Prompt de Vídeo (preencher por take)

```
Hyper-realistic UGC TikTok selfie video, vertical 9:16, shot on iPhone front camera.

CRITICAL: This must look like a real person filmed themselves. NOT AI-generated. 
The motion must include: natural micro-tremors in hand holding phone, 
slight breathing movement in chest and shoulders, 
natural eye blinks (every 3-4 seconds, not synchronized), 
micro-expressions between sentences (slight lip compression, nostril flare, eyebrow micro-movement),
natural head micro-movements while speaking (not static like a statue).

CHARACTER: [DESCRIÇÃO DA PERSONAGEM — copiar do keyframe mestre]
OUTFIT: plain white crew-neck cotton t-shirt — SAME AS REFERENCE IMAGE, DO NOT CHANGE
SETTING: same bathroom as reference image — white tiles, window light from left

MOVEMENT: [DESCREVER MOVIMENTO ESPECÍFICO DO TAKE]

AUDIO: She speaks in Brazilian Portuguese, natural conversational tone, 
NOT a voice actor, NOT a commercial voice, 
natural pauses between thoughts, 
slight breath sounds between sentences, 
occasional slight vocal fry at end of phrases,
speaking pace: 130-150 words per minute (normal conversation, not rushed).

SPEECH: "[FALA DO TAKE]"

CAMERA: Slight natural hand tremor throughout, 
camera occasionally drifts 2-3 pixels then self-corrects (natural selfie hold), 
no gimbal stabilization, no professional steadiness,
natural auto-focus micro-adjustments when she moves.

DURATION: 8 seconds exactly.
NO text overlays, NO music, NO cuts, NO transitions.
```

---

## HOOKS DE ALTA CONVERSÃO — FORMATO EXATO

O hook que o usuário descreveu: *"Gente, eu tive que parar o que eu tava fazendo pra falar isso pra vocês. Esse produto aqui é muito bom. Olha o que aconteceu, minha pele mudou totalmente."*

**Anatomia desse hook:**
1. **Interrupção de rotina** ("eu tive que parar o que eu tava fazendo") — cria urgência e autenticidade
2. **Afirmação direta** ("esse produto é muito bom") — sem rodeios, sem buildup
3. **Prova visual implícita** ("olha o que aconteceu") — chama para ver antes de mostrar
4. **Resultado específico** ("minha pele mudou totalmente") — transformação clara

**Banco de hooks no mesmo formato:**

| # | Hook | Tom |
|---|---|---|
| 1 | "Gente, eu tive que parar o que eu tava fazendo pra falar isso pra vocês. Esse sérum aqui é absurdo. Olha o que ele fez na minha pele em duas semanas." | Urgência + Resultado |
| 2 | "Eu não ia postar isso não, mas eu preciso falar. Esse produto aqui mudou minha rotina de skincare completamente." | Confissão + Impacto |
| 3 | "Para tudo. Eu achei que era mais um hypado, mas olha isso. Minha pele nunca ficou assim." | Ceticismo convertido |
| 4 | "Sério, eu tô usando isso há duas semanas e as pessoas tão me perguntando o que eu fiz diferente. É esse sérum aqui." | Prova social indireta |
| 5 | "Eu comprei sem acreditar muito não. Mas olha o resultado. Eu não consigo parar de usar." | Jornada de descoberta |
| 6 | "Alguém me recomendou esse produto e eu fui sem expectativa. Cara. Olha a textura da minha pele agora." | Recomendação orgânica |

---

## ROTEIRO COMPLETO V11 — CREATIVE 001

**Produto:** Sérum facial com aplicador roller (âmbar, 30ml)  
**Persona:** Bia — mulher brasileira, 28 anos, morena, banheiro doméstico  
**Formato:** 3 takes de 8s = 24s total

### Take 1 — Hook (0–8s)
**Fala:** *"Gente, eu tive que parar o que eu tava fazendo pra falar isso pra vocês. Esse sérum aqui é absurdo. Olha o que ele fez na minha pele."*  
**Ação:** Segura o sérum levantado na altura do rosto, olhos arregalados, expressão de surpresa genuína  
**Energia:** Alta, urgente, como se fosse um recado de última hora

### Take 2 — Demo (8–16s)
**Fala:** *"Eu uso o roller assim, em movimentos circulares. Ele desliza fácil, dá uma sensação geladinha e a pele absorve na hora. Zero meleca."*  
**Ação:** Aplica o roller na bochecha em movimentos circulares, olhos fechados de prazer, depois abre e olha para a câmera  
**Energia:** Relaxada, sensorial, íntima

### Take 3 — CTA (16–24s)
**Fala:** *"Não é milagre, mas é o único passo que eu realmente consigo manter. Se quiser testar, deixei no carrinho aqui embaixo."*  
**Ação:** Segura o produto perto do rosto com sorriso natural, aponta para baixo com o dedo indicador esquerdo  
**Energia:** Calorosa, amiga, sem pressão

---

## CHECKLIST DE VALIDAÇÃO ANTI-IA

Antes de aprovar qualquer frame ou vídeo, verificar:

- [ ] A pele tem textura visível (poros, imperfeições)? Se parecer plástica → reprovar
- [ ] Os olhos têm profundidade e leve vermelhidão natural? Se parecerem vítreos → reprovar
- [ ] As mãos têm veias e dobras naturais? Se parecerem perfeitas demais → reprovar
- [ ] A roupa é a mesma nos 3 takes? Se mudou → reprovar imediatamente
- [ ] A câmera tem tremor natural? Se estiver perfeitamente estabilizada → reprovar
- [ ] A iluminação é assimétrica (mais luz de um lado)? Se for uniforme demais → reprovar
- [ ] O enquadramento está levemente off-center? Se estiver perfeitamente centralizado → reprovar
- [ ] O produto tem sombra natural na mão? Se parecer "colado" digitalmente → reprovar
