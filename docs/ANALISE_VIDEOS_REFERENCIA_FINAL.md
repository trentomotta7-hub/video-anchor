# Análise Completa dos Vídeos de Referência
## IMG_0197.MOV e IMG_0198.MOV — Extração para Geração de Vídeo UGC

---

## O que são esses vídeos

Ambos os vídeos são gravações da tela de um smartphone mostrando uma conversa com o Manus. O usuário filmou a tela para registrar o processo de criação dos criativos UGC — o que revela, de forma indireta, **o que ele considera importante** e **o que estava faltando** nas versões anteriores.

---

## Textos Extraídos — Vídeo 1 (IMG_0197.MOV)

**Mensagem principal do Manus visível na tela:**

> "Perfeito, agora ficou claro o critério correto: podemos usar personagens criados por IA, e inclusive haverá transparência dizendo que o personagem foi criado por IA; **o que não pode acontecer é o visual parecer artificial, com mutação, troca de rosto, troca de cenário, mãos estranhas, produto deformado ou estética 'plástica'**."

> "Vou ajustar a rota: em vez de fugir de IA, vou trabalhar com **personagens IA hiper-realistas e consistentes**, usando referência fixa, prompts travados, estilo UGC real e validação rígida antes de considerar qualquer vídeo entregável."

**Tarefas visíveis no plano de execução:**
- ✅ Gerar referência fixa de personagem, produto e ambiente hiper-realistas
- ✅ Gerar três takes consistentes de 8 segundos e montar vídeo final de 24 segundos
- ⏳ Validar realismo, consistência e transparência de IA antes da entrega

**Ações visíveis no log:**
- "Gerando Vídeo — Concluído"
- "Vou montar os três takes v7 em um vídeo..."
- "Vou normalizar o vídeo final para 1080x1..."
- "Vou versionar os três takes, a montagem..."
- "Consegui montar e normalizar o vídeo de 24 segundos com personagem hiper-realista, garantindo formato vertical 1080x1920, pronto para validação de realismo e transparência da IA."
- "Você não tem créditos suficientes. Por favor, faça upgrade..."

---

## Textos Extraídos — Vídeo 2 (IMG_0198.MOV)

**Mensagem principal do Manus visível na tela:**

> "O vídeo v7 foi reprovado devido a artefatos de IA visíveis, **especialmente nas mãos, boca e pele, e o rótulo em branco do produto**. Realizei uma pesquisa sobre ferramentas de geração de vídeo por IA e compilei um relatório detalhado em `docs/ai_video_generation_tools_research.md` e uma proposta de reavaliação da estratégia em `docs/strategy_reassessment_v8.md`."

> "As ferramentas **Percify e Synthesia** foram identificadas como as mais promissoras para gerar avatares realistas."

**Título do documento pesquisado:**
> "Ferramentas de Geração de Vídeo por IA para Realismo Humano"

**Seção Percify:**

> "A Percify se destaca por seu foco na criação de avatares completos e realistas, com ênfase particular na **geração de mãos sem artefatos** e na superação do 'uncanny valley'."

**Como a Percify consegue mãos realistas:**
- Dados de Treinamento Extensos: modelos treinados em vasto conjunto de imagens e vídeos de mãos de alta qualidade
- Integração Perfeita: geração de mãos totalmente integrada com outros recursos de avatar e geração de vídeo, garantindo consistência e coerência em todo o avatar

**Benefícios da Percify para mãos realistas:**
- Economia de Tempo e Esforço: automatiza o processo de geração de mãos
- Melhora da Qualidade: produz mãos realistas e de alta qualidade de forma consistente
- Aumento do Engajamento: mãos realistas melhoram o engajamento do usuário e criam uma experiência mais imersiva

**Seção Synthesia:**

> "A Synthesia é uma plataforma de vídeo AI para negócios que permite criar vídeos com avatares AI e narrações em mais de 160 idiomas. Ela se concentra em **avatares expressivos** e na capacidade de **traduzir vídeos com sincronização labial**."

**Conclusão Preliminar do documento:**

> "Ambas as ferramentas oferecem avanços significativos na geração de vídeo por IA. A Percify parece ter um foco mais específico na superação dos artefatos de mãos e no 'uncanny valley' para avatares completos, enquanto a Synthesia oferece uma solução mais abrangente para criação de vídeo corporativo com avatares expressivos e recursos de localização."

> "Para o nosso objetivo de criar um personagem IA hiper-realista para UGC, **a capacidade da Percify de gerar mãos e expressões faciais mais naturais pode ser crucial**. No entanto, a Synthesia também menciona avatares expressivos e sincronização labial, que são importantes para a autenticidade."

> "**O desafio do rótulo do produto em branco ainda precisa ser abordado**, e nenhuma das ferramentas pesquisadas oferece uma solução explícita para isso, além de mencionar a importância da consistência da marca. Será necessário investigar se essas plataformas permitem a personalização de produtos ou a integração de imagens de produtos com rótulos específicos."

---

## Diagnóstico Consolidado — O que estava errado e o que precisa mudar

Com base nos dois vídeos, os **5 problemas críticos** que causaram reprovação dos vídeos anteriores são:

| Problema | Onde aparece | Impacto |
|---|---|---|
| **Mãos deformadas** | Dedos fundidos, proporções erradas ao segurar produto | Denuncia IA imediatamente |
| **Boca artificial** | Dentes como bloco único, sincronização labial mecânica | Quebra credibilidade |
| **Pele plástica** | Textura uniforme, sem poros, sem imperfeições | Parece render 3D |
| **Rótulo em branco ou digital** | Produto sem texto real, embalagem "flutuante" | Remove autenticidade do produto |
| **Troca de roupa/cenário entre takes** | Personagem muda de look entre os 3 takes | Destrói continuidade narrativa |

---

## Regras Definitivas para o PROMPT MESTRE (atualização)

### Regra 1 — Mãos
Especificar **sempre**: veias visíveis no dorso, nós dos dedos com textura real, unhas sem esmalte com leve sujeira nas bordas, grip natural e relaxado (não posado), sombra da mão no produto.

### Regra 2 — Boca e sincronização labial
Descrever: lábios levemente assimétricos, dentes com pequenas variações de tonalidade (não brancos perfeitos), movimento de boca que inclui pausas naturais, respiração visível, leve tensão muscular ao falar.

### Regra 3 — Pele
Especificar: poros visíveis no nariz e bochechas, sardas, vermelhidão leve, olheiras naturais, uma ou duas marcas pós-acne, **zero filtro**, textura visível a distância normal de selfie.

### Regra 4 — Produto e rótulo
O produto deve ter: rótulo com texto legível (mesmo que fictício), sombra natural da mão sobre a embalagem, produto com sinais de uso (não lacrado/novo demais), ângulo levemente inclinado (não perpendicular perfeito).

### Regra 5 — Consistência entre takes
A roupa deve ser descrita com instrução explícita de bloqueio: "OUTFIT LOCKED — THIS EXACT OUTFIT MUST APPEAR IN EVERY SINGLE TAKE. DO NOT CHANGE." Usar a imagem-âncora mestre como referência obrigatória em todos os takes.

### Regra 6 — Câmera e ambiente
Câmera: tremor natural de mão, drift de 2-3 pixels, sem gimbal, foco com micro-ajustes. Ambiente: banheiro doméstico real, sem decoração de estúdio, itens pessoais visíveis, iluminação assimétrica de janela.

---

## Aplicação Imediata

Esses achados já foram incorporados ao `PROMPT_MESTRE_ANTI_IA_V1.md` e aplicados na geração do Creative 001 v11. O próximo passo é usar esse diagnóstico para refinar ainda mais os prompts de vídeo, especialmente o tratamento de mãos e sincronização labial.
