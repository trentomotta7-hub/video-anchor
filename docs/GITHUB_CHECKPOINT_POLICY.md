# Política de Checkpoint e Sincronização GitHub

Este projeto deve operar com **checkpoint perpétuo**: toda alteração relevante em roteiro, prompt, persona, estratégia, script, dados ou documentação precisa ser salva em arquivo, registrada em commit e enviada ao GitHub.

## 1. Regra principal

Nenhuma decisão importante deve ficar apenas na conversa. Sempre que um novo avanço for feito, ele deve ser materializado em um destes locais:

| Tipo de alteração | Local recomendado |
|---|---|
| Estratégia comercial, pesquisa e playbooks | `docs/` |
| Dados estruturados e análises | `data/` |
| Roteiros prontos | `roteiros/` ou `gc_assets/` |
| Prompts de geração | `gc_assets/` ou `docs/` |
| Scripts e pipelines | `scripts/` |
| Estado do projeto e próximos passos | `.project-memory/` |

## 2. Procedimento obrigatório nesta sessão

Antes de encerrar qualquer bloco de trabalho, executar:

```bash
cd /home/ubuntu/trabalho_video/video-anchor
bash update-checkpoint.sh
git status --short
git add <arquivos alterados>
git commit -m "tipo: mensagem clara"
git push origin main
git log -1 --oneline
```

O comando `bash update-checkpoint.sh` atualiza `CONTEXT.md` e `CHANGELOG.md`, mantendo o repositório compreensível para retomada futura.

## 3. Limitação operacional observada

Foi preparado um workflow remoto para atualizar checkpoints automaticamente no GitHub, mas o push de arquivos em `.github/workflows/` foi recusado pelo GitHub porque a credencial disponível nesta sessão não possui permissão `workflows`. Por segurança, esse arquivo não foi enviado ao repositório neste checkpoint.

> Enquanto a permissão de workflows não for concedida, a política válida é: **todo avanço feito durante a sessão deve ser commitado e enviado manualmente ao GitHub imediatamente após a alteração**.

## 4. Como ativar o checkpoint remoto no futuro

Para ativar automação via GitHub Actions, será necessário usar uma credencial com permissão para criar/alterar workflows ou adicionar manualmente o workflow no GitHub. O conteúdo pode ser recriado a partir desta política quando a permissão estiver disponível.

## 5. Mensagens de commit recomendadas

| Prefixo | Uso |
|---|---|
| `docs:` | Estratégia, playbooks, documentação e pesquisa. |
| `feat:` | Nova funcionalidade, novo pipeline ou novo artefato operacional. |
| `fix:` | Correções de bug, prompt ou comportamento. |
| `checkpoint:` | Atualização de contexto, changelog e memória. |
| `data:` | Dados estruturados, análises e tabelas. |
| `creative:` | Roteiros, personas, prompts e variações de vídeo. |

## 6. Compromisso operacional

A partir deste documento, o fluxo padrão do projeto é: **pensar, salvar, versionar, enviar ao GitHub e só então avançar**. Isso protege o trabalho criativo, permite auditoria de evolução e evita perda de contexto entre sessões.
