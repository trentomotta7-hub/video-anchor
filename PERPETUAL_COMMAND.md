# ♾️ COMANDO PERPÉTUO — Sistema de Checkpoint Automático

> **Documento mestre** do sistema de documentação perpétua aplicado em todos os repositórios de `trentomotta7-hub`.

---

## O Que É

O **Comando Perpétuo** é um sistema que garante que:

1. **Todo repositório tem contexto completo** — qualquer desenvolvedor novo entende imediatamente o projeto
2. **Toda alteração é registrada** — CHANGELOG.md é atualizado automaticamente
3. **Checkpoints são criados a cada push** — CONTEXT.md reflete o estado atual sempre

---

## Repositórios Cobertos

| Repositório | Status | Checkpoint |
|-------------|--------|------------|
| burger_prime | ✅ Ativo | CONTEXT.md + CHANGELOG.md |
| manuos-ia-page | ✅ Ativo | CONTEXT.md + CHANGELOG.md |
| manuos-ia-skill | ✅ Ativo | CONTEXT.md + CHANGELOG.md |
| adforge-ai | ✅ Ativo | CONTEXT.md + CHANGELOG.md |
| copa_panini_shop | ✅ Ativo | CONTEXT.md + CHANGELOG.md |
| cresceweb-digital-presentation | ✅ Ativo | CONTEXT.md + CHANGELOG.md |
| chinelos-patriotas-2026 | ✅ Ativo | CONTEXT.md + CHANGELOG.md |
| auto-checkpoint-skill | ✅ Ativo | CONTEXT.md + CHANGELOG.md |
| video-anchor | ✅ Ativo | CONTEXT.md + CHANGELOG.md |

---

## Como Funciona

### Automático (GitHub Actions)
Quando o workflow `perpetual-checkpoint.yml` está ativo:
- A cada push na branch `main`, o CONTEXT.md e CHANGELOG.md são regenerados
- Um commit automático é feito com a mensagem `checkpoint: atualização automática após commit XXXXX`
- Nenhuma ação manual necessária

### Manual (Script)
Se o workflow não estiver ativo, use:
```bash
bash update-checkpoint.sh
git add CONTEXT.md CHANGELOG.md
git commit -m "checkpoint: atualização manual"
git push
```

---

## Ativar GitHub Actions (Workflow)

Para ativar a atualização 100% automática:

```bash
# 1. Faça login com permissão de workflows
gh auth login --scopes workflow

# 2. Execute o script de setup
bash setup_workflow.sh
```

---

## Para Novos Desenvolvedores

Se você é um novo desenvolvedor acessando qualquer repositório:

1. **Leia o `CONTEXT.md`** na raiz — ele tem TUDO sobre o projeto
2. **Consulte o `CHANGELOG.md`** — evolução cronológica completa
3. **Verifique os commits** — mensagens descritivas explicam cada mudança
4. **Siga o padrão de commits** — use prefixos como `feat:`, `fix:`, `docs:`, etc.

---

## Estrutura do Sistema

```
repositório/
├── CONTEXT.md                              # Contexto completo do projeto
├── CHANGELOG.md                            # Histórico de alterações
├── update-checkpoint.sh                    # Script de atualização manual
└── .github/
    └── workflows/
        └── perpetual-checkpoint.yml        # Automação perpétua
```

---

## Comandos Úteis

```bash
# Atualizar checkpoint manualmente
bash update-checkpoint.sh && git add -A && git commit -m "checkpoint: manual" && git push

# Ver status de todos os repos
for dir in */; do echo "=== $dir ===" && cd "$dir" && git status -s && cd ..; done

# Atualizar todos os repos de uma vez
for dir in */; do cd "$dir" && bash update-checkpoint.sh && git add -A && git commit -m "checkpoint: batch update" && git push && cd ..; done
```

---

*Sistema criado em 2026-05-22 — Comando Perpétuo v2.0*
