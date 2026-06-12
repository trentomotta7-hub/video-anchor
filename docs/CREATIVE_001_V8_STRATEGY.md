# Creative 001 — Estratégia v8 (Nova Geração)

**Data:** 2026-06-12  
**Autor:** Manus AI  
**Status:** Em produção

---

## Diagnóstico das versões anteriores

### Problemas identificados (v7 e v9)

| Problema | Causa raiz | Solução v8 |
|---|---|---|
| Mãos/dedos deformados | Prompt não restringia posição das mãos; modelo gerou mão segurando produto em ângulo difícil | Mão segura produto em posição lateral simples, produto visível mas não em close extremo |
| Troca de roupa entre takes | Cada take gerado independentemente sem âncora fixa de roupa | Descrever roupa com máxima especificidade: "robe de algodão bege claro, decote V, sem estampas" |
| Pele plástica | Prompt não especificava imperfeições naturais | Adicionar "pele com textura natural, poros visíveis sutilmente, sem filtro de beleza" |
| Produto com rótulo em branco | Modelo evita texto em imagens | Aceitar rótulo branco/minimalista como característica do produto, não como falha |
| Boca robótica | Geração de vídeo com lip-sync de IA ainda tem limitações | Focar em takes sem fala explícita no vídeo (fala adicionada em pós) ou aceitar como limitação declarada |
| Produto aparência digital | Iluminação do produto não batia com ambiente | Especificar que o produto deve ter sombra natural e reflexo de luz ambiente |

---

## Estratégia v8: Abordagem por imagem estática + animação mínima

### Decisão técnica

Em vez de tentar gerar vídeo com lip-sync nativo (que produz artefatos de boca), a v8 adota a seguinte abordagem:

1. **Gerar 3 imagens-âncora de alta qualidade** usando a referência candidata B como base visual
2. **Animar cada imagem** com movimento mínimo e natural (respiração, micro-movimento de cabeça)
3. **Adicionar narração em áudio** separada via TTS
4. **Montar o vídeo final** concatenando os 3 takes com trilha de fundo

Esta abordagem elimina os problemas de lip-sync e mãos deformadas, pois:
- As imagens estáticas são muito mais controláveis que vídeos gerados
- A animação mínima (img2vid com movimento sutil) não deforma mãos
- O áudio TTS é gerado separadamente com qualidade controlada

---

## Prompts v8 — Imagens âncora

### Prompt base (fixo para os 3 takes)

```
Vertical portrait 9:16, hyper-realistic UGC selfie style for TikTok Shop. Brazilian woman, 28-32 years old, natural appearance, minimal makeup, visible skin texture with subtle pores, no beauty filter. Hair: medium-length dark brown hair loosely tied up with some strands falling naturally. Clothing: light beige cotton wrap robe, V-neck, no patterns, same throughout. Setting: realistic home bathroom, white ceramic tiles, natural soft window light from left side, bathroom counter visible with a few personal items. She holds a small amber glass bottle with roller-ball applicator (30ml serum bottle, white label, no text), product held naturally at chest level, fingers wrapped around bottle naturally. Camera: front-facing smartphone camera angle, slightly below eye level, slight natural hand shake. No studio lighting, no professional photography aesthetics, no text on image, no watermarks.
```

### Take 1 — Hook (0–8s)
```
[BASE PROMPT] + Expression: honest, slightly surprised, looking directly at camera with a "I need to tell you something" expression. Product is held up showing it to camera. Mouth slightly open as if about to speak.
```

### Take 2 — Demonstração (8–17s)
```
[BASE PROMPT] + She is applying the roller-ball serum to her cheek, roller touching skin, natural circular motion implied, eyes slightly closed in pleasure, product clearly visible. Same robe, same hair, same bathroom.
```

### Take 3 — CTA (17–24s)
```
[BASE PROMPT] + She holds product near face, smiling naturally and discretely, index finger of free hand pointing downward casually (TikTok Shop CTA gesture). Same robe, same hair, same bathroom.
```

---

## Prompt negativo (aplicar em todos os takes)

```
deformed hands, extra fingers, fused fingers, missing fingers, plastic skin, overly smooth skin, beauty filter, studio lighting, professional photography, text on image, watermark, logo, brand name, different outfit, different background, different person, different hair, CGI render, 3D avatar, artificial look, uncanny valley, robotic expression, stiff pose, commercial advertisement aesthetic, before/after medical claims
```

---

## Critérios de aprovação v8

| Critério | Mínimo aceitável |
|---|---|
| Consistência de personagem | Mesmo rosto, mesmo cabelo, mesma roupa nos 3 takes |
| Realismo de pele | Textura natural visível, sem aspecto plástico |
| Mãos | Dedos naturais, sem fusão ou deformação |
| Produto | Mesmo frasco âmbar com roller, mesmo formato |
| Ambiente | Mesmo banheiro, mesma luz |
| Duração total | 22–26 segundos |
| Formato | Vertical 9:16, 1080x1920 |

---

## Próximas ações

1. Gerar 3 imagens âncora com prompt v8
2. Gerar vídeos de 8s por take (img2vid com movimento mínimo)
3. Gerar narração TTS em português brasileiro
4. Montar vídeo final com trilha de fundo
5. Validar com análise multimodal
6. Commit no GitHub
