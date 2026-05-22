#!/bin/bash
# ============================================================
# ATUALIZAÇÃO MANUAL DO CHECKPOINT
# ============================================================
# Execute este script na raiz de qualquer repositório para
# atualizar o CONTEXT.md e CHANGELOG.md manualmente.
#
# Uso: bash update-checkpoint.sh
# ============================================================

DATE=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
BRANCH=$(git branch --show-current)
TOTAL_COMMITS=$(git rev-list --count HEAD)
LAST_COMMIT=$(git log -1 --format="%H %s")
LAST_COMMIT_DATE=$(git log -1 --format="%ci")
ALL_AUTHORS=$(git log --format="%aN <%aE>" | sort -u)
FILE_COUNT=$(find . -not -path './.git/*' -not -path './.github/*' -type f | wc -l)
DIR_STRUCTURE=$(find . -maxdepth 2 -type d -not -path './.git*' | sort)
COMMIT_HISTORY=$(git log --oneline -50)
REMOTE_URL=$(git remote get-url origin 2>/dev/null)
REPO_NAME=$(basename $(git rev-parse --show-toplevel))

# Detectar tecnologias
TECHS=""
[ -f "package.json" ] && TECHS="$TECHS Node.js/JavaScript,"
[ -f "requirements.txt" ] && TECHS="$TECHS Python,"
[ -f "tsconfig.json" ] && TECHS="$TECHS TypeScript,"
[ -f "vite.config.ts" ] || [ -f "vite.config.js" ] && TECHS="$TECHS Vite,"
[ -f "tailwind.config.js" ] || [ -f "tailwind.config.ts" ] && TECHS="$TECHS TailwindCSS,"
[ -f "docker-compose.yml" ] || [ -f "Dockerfile" ] && TECHS="$TECHS Docker,"
[ -f "drizzle.config.ts" ] && TECHS="$TECHS Drizzle ORM,"
TECHS=$(echo "$TECHS" | sed 's/,$//' | sed 's/^[ ]*//')

cat > CONTEXT.md << EOF
# 📋 CONTEXTO DO PROJETO — ${REPO_NAME}

> **Documento de checkpoint perpétuo** — Atualizado automaticamente a cada alteração.
> Qualquer desenvolvedor que acessar este repositório terá contexto completo do projeto.

---

## 🔄 Última Atualização

| Campo | Valor |
|-------|-------|
| **Data** | ${DATE} |
| **Branch Principal** | ${BRANCH} |
| **Total de Commits** | ${TOTAL_COMMITS} |
| **Último Commit** | ${LAST_COMMIT} |
| **Data do Último Commit** | ${LAST_COMMIT_DATE} |

---

## 🏗️ Visão Geral do Projeto

**Repositório:** ${REPO_NAME}  
**URL:** ${REMOTE_URL}  
**Tecnologias:** ${TECHS}  
**Total de Arquivos:** ${FILE_COUNT}

---

## 👥 Autores/Contribuidores

\`\`\`
${ALL_AUTHORS}
\`\`\`

---

## 📁 Estrutura de Diretórios

\`\`\`
${DIR_STRUCTURE}
\`\`\`

---

## 📜 Histórico de Commits (Últimos 50)

\`\`\`
${COMMIT_HISTORY}
\`\`\`

---

## 🎯 Status Atual

Este projeto está **ATIVO** e em desenvolvimento contínuo.

### Para Novos Desenvolvedores:
1. Leia este CONTEXT.md primeiro
2. Consulte o CHANGELOG.md para evolução cronológica
3. Verifique o histórico de commits para detalhes

---

## 🔧 Padrão de Commits

- \`feat:\` — nova funcionalidade
- \`fix:\` — correção de bug
- \`docs:\` — documentação
- \`chore:\` — manutenção
- \`refactor:\` — refatoração
- \`ci:\` — integração contínua
- \`checkpoint:\` — atualização automática

---

*Gerado automaticamente pelo sistema de checkpoint perpétuo — trentomotta7-hub*
EOF

# Gerar CHANGELOG.md
cat > CHANGELOG.md << 'HEADER'
# 📝 CHANGELOG — Histórico Completo de Alterações

> **Registro perpétuo** — Atualizado automaticamente a cada push.

---

HEADER

git log --format="### %cd%n| Commit | Autor | Mensagem |%n|--------|-------|----------|%n| \`%h\` | %aN | %s |%n" --date=short >> CHANGELOG.md

echo "" >> CHANGELOG.md
echo "---" >> CHANGELOG.md
echo "*Última atualização: ${DATE}*" >> CHANGELOG.md

echo "✅ CONTEXT.md e CHANGELOG.md atualizados para: $REPO_NAME"
