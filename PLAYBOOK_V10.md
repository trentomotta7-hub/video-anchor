# PLAYBOOK UGC TikTok Shop — v10 (Vídeo Contínuo)

## Visão Geral

Este playbook detalha a estratégia de geração de vídeos UGC para TikTok Shop na versão v10 do pipeline. O foco é a criação de um **vídeo único e contínuo de 24 segundos**, sem cortes bruscos ou legendas na tela, priorizando a performance orgânica da apresentadora e um storytelling emocional de alta conversão.

## Princípios Chave

1.  **Tomada Única e Contínua:** O vídeo é gerado como uma única cena de 24 segundos, eliminando cortes bruscos e promovendo uma experiência fluida e natural para o espectador.
2.  **Zero Legendas/Banners:** Nenhuma informação textual é sobreposta no vídeo. A comunicação é 100% verbal e visual, através da performance da apresentadora.
3.  **Hook Confessional:** O vídeo começa com um gancho emocional e confessional, expondo uma dor real e relatable, sem o uso de estatísticas ou informações genéricas.
4.  **Storytelling Orgânico:** A transição entre Problema, Solução e CTA é feita de forma natural pela apresentadora, com movimentos fluidos (ex: pegar o produto da mesa).
5.  **Lip-sync Nativo:** O áudio é gerado junto com o vídeo, garantindo que o movimento labial da apresentadora esteja perfeitamente sincronizado com a fala.
6.  **Persona Relatável:** Prioriza-se personas que gerem identificação imediata com o público-alvo, como a "Usuária Comum", para construir confiança e conexão.

## Estrutura do Vídeo (24 segundos)

| Bloco | Tempo | Narrativa | Direção de Cena |
|-------|-------|-----------|-----------------|
| **Hook + Problema** | 0–8s | Confissão pessoal da dor, expressão de vergonha/desconforto. | Apresentadora sem produto. Mão no rosto, olhar de desabafo. Tom confessional. |
| **Solução + Revelação** | 8–16s | Descoberta do produto, gesto de pegar da mesa, alívio e surpresa. | Apresentadora pega o produto da mesa, apresenta com sorriso de alívio. |
| **CTA Urgente** | 16–24s | Chamada para ação com preço e escassez, apontando para baixo. | Apresentadora com produto em mãos, aponta dedo para baixo com energia. |

## Roteiro Exemplo (Creme Hidratante Facial Anti-Idade)

**FALA COMPLETA (24 segundos):**

*"Minha pele tava me envergonhando. Eu evitava foto, evitava espelho. Com 32 anos me sentindo com 50. Aí uma amiga me mandou esse creme. Eu nem acreditei. Mas em duas semanas minha pele ficou outra. Olha a diferença. Tá com R$89,90 no TikTok Shop. Corre porque esgota rápido. Link tá aqui embaixo."*

## Keyframes de Referência (Exemplo)

Para garantir a continuidade e os movimentos específicos, são utilizados keyframes de início e fim para o vídeo contínuo:

-   **`keyframes.first`**: Imagem da apresentadora sem produto, com expressão de dor/vergonha (início do Take 1).
-   **`keyframes.last`**: Imagem da apresentadora com produto em mãos, apontando para baixo (fim do Take 3).

## Script de Geração

O script `gc_pipeline_perpetuo.py` será atualizado para gerar um único vídeo de 24 segundos, utilizando o `generate_video` com `duration_seconds=24` e os `keyframes` apropriados. O script de montagem (`gc_montar_v10.py`) será simplificado para apenas normalizar o vídeo e adicionar a trilha de fundo, sem sobrepor textos ou banners.
