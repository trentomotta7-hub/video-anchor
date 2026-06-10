#!/bin/bash
# ============================================================
# rodar_perpetuo.sh — Executor Perpétuo do Pipeline UGC
# Video Anchor | MANUOS IA
#
# Executa o pipeline de geração de roteiros UGC continuamente,
# minerando produtos do TikTok Shop e gerando roteiros prontos
# para produção de vídeo.
#
# Uso:
#   bash rodar_perpetuo.sh                    # Execução única
#   bash rodar_perpetuo.sh --loop             # Loop contínuo (a cada 6h)
#   bash rodar_perpetuo.sh --loop --intervalo 3600  # Loop a cada 1h
#   bash rodar_perpetuo.sh --produto "Creme Anti-Idade" --nicho beleza
# ============================================================

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS_DIR="$REPO_DIR/scripts"
OUTPUT_DIR="$REPO_DIR/gc_output"
LOG_DIR="$REPO_DIR/logs"
mkdir -p "$LOG_DIR"

# Configurações padrão
LOOP=false
INTERVALO=21600  # 6 horas em segundos
LIMITE=5
NICHO=""
TODAS_PERSONAS=false
PRODUTO=""
CATEGORIA="geral"
PRECO="R\$99,90"

# Parsear argumentos
while [[ $# -gt 0 ]]; do
  case $1 in
    --loop) LOOP=true; shift ;;
    --intervalo) INTERVALO="$2"; shift 2 ;;
    --limite) LIMITE="$2"; shift 2 ;;
    --nicho) NICHO="$2"; shift 2 ;;
    --todas-personas) TODAS_PERSONAS=true; shift ;;
    --produto) PRODUTO="$2"; shift 2 ;;
    --categoria) CATEGORIA="$2"; shift 2 ;;
    --preco) PRECO="$2"; shift 2 ;;
    *) echo "Argumento desconhecido: $1"; shift ;;
  esac
done

# Função de execução
executar() {
  TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')
  LOG_FILE="$LOG_DIR/pipeline_$TIMESTAMP.log"

  echo "============================================================"
  echo "  PIPELINE PERPÉTUO UGC — $(date '+%d/%m/%Y %H:%M:%S')"
  echo "============================================================"

  cd "$REPO_DIR"

  if [[ -n "$PRODUTO" ]]; then
    # Modo produto específico
    CMD="python3 $SCRIPTS_DIR/gc_pipeline_perpetuo.py --produto \"$PRODUTO\" --categoria \"$CATEGORIA\" --preco \"$PRECO\""
  else
    # Modo mineração
    CMD="python3 $SCRIPTS_DIR/gc_pipeline_perpetuo.py --minerar --limite $LIMITE"
    [[ -n "$NICHO" ]] && CMD="$CMD --nicho \"$NICHO\""
    [[ "$TODAS_PERSONAS" == "true" ]] && CMD="$CMD --todas-personas"
  fi

  echo "  Executando: $CMD"
  eval "$CMD" 2>&1 | tee "$LOG_FILE"

  # Checkpoint automático após execução
  if [[ -f "$REPO_DIR/update-checkpoint.sh" ]]; then
    echo ""
    echo "  [CHECKPOINT] Atualizando repositório..."
    bash "$REPO_DIR/update-checkpoint.sh"
    git -C "$REPO_DIR" add -A
    git -C "$REPO_DIR" commit -m "feat: pipeline perpétuo — roteiros gerados em $TIMESTAMP [skip ci]" 2>/dev/null || true
    git -C "$REPO_DIR" push origin main 2>/dev/null || true
    echo "  [CHECKPOINT] ✓ Push realizado"
  fi

  echo ""
  echo "  ✓ Execução concluída. Log: $LOG_FILE"
  echo "============================================================"
}

# Execução
if [[ "$LOOP" == "true" ]]; then
  echo "  Modo LOOP ativo — intervalo: ${INTERVALO}s ($(( INTERVALO / 3600 ))h)"
  while true; do
    executar
    echo "  Próxima execução em $(( INTERVALO / 3600 ))h..."
    sleep "$INTERVALO"
  done
else
  executar
fi
