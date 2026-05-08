#!/bin/bash
set -e

CLIPS_DIR="/home/ubuntu/video-anchor/clips"
VOZES_DIR="/home/ubuntu/video-anchor/assets/vozes"
LOGO_IMG="/home/ubuntu/video-anchor/assets/logo_intro.png"
TRILHA="/home/ubuntu/video-anchor/assets/trilha_anchor.mp3"
OUTPUT_DIR="/home/ubuntu/video-anchor/videos_v2"
mkdir -p "$OUTPUT_DIR"

LOGO_DUR=3
FADE=1.0
MUSIC_VOL=0.10

montar_roteiro() {
  local RID=$1
  local TITULO=$2
  shift 2
  local CLIPS=("$@")

  echo ""
  echo "=== Montando Roteiro $RID: $TITULO ==="

  local VOZ="$VOZES_DIR/roteiro_${RID}_voz.wav"
  local OUTPUT="$OUTPUT_DIR/video_${RID}_${TITULO}.mp4"

  # 1. Concatenar clipes da apresentadora
  local CONCAT_LIST="/tmp/concat_${RID}.txt"
  > "$CONCAT_LIST"
  for clip in "${CLIPS[@]}"; do
    echo "file '$clip'" >> "$CONCAT_LIST"
  done

  ffmpeg -y -f concat -safe 0 -i "$CONCAT_LIST" \
    -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1" \
    -c:v libx264 -preset fast -crf 18 -an \
    "/tmp/presenter_${RID}.mp4" 2>/dev/null
  echo "  Clipes concatenados"

  local PRES_DUR
  PRES_DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "/tmp/presenter_${RID}.mp4")
  local TOTAL_DUR
  TOTAL_DUR=$(echo "$LOGO_DUR + $PRES_DUR + $LOGO_DUR" | bc)
  echo "  Duração: logo(${LOGO_DUR}s) + apresentadora(${PRES_DUR}s) + logo(${LOGO_DUR}s) = ${TOTAL_DUR}s"

  # 2. Criar vídeo da logo (abertura)
  ffmpeg -y -loop 1 -t "$LOGO_DUR" -i "$LOGO_IMG" \
    -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fade=t=in:st=0:d=${FADE},fade=t=out:st=$(echo "$LOGO_DUR - $FADE" | bc):d=${FADE}" \
    -c:v libx264 -preset fast -crf 18 -r 30 -an \
    "/tmp/logo_open_${RID}.mp4" 2>/dev/null

  # 3. Criar vídeo da logo (fechamento)
  ffmpeg -y -loop 1 -t "$LOGO_DUR" -i "$LOGO_IMG" \
    -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fade=t=in:st=0:d=${FADE},fade=t=out:st=$(echo "$LOGO_DUR - $FADE" | bc):d=${FADE}" \
    -c:v libx264 -preset fast -crf 18 -r 30 -an \
    "/tmp/logo_close_${RID}.mp4" 2>/dev/null

  echo "  Logos criadas"

  # 4. Concatenar logo + apresentadora + logo
  cat > "/tmp/final_concat_${RID}.txt" << EOF
file '/tmp/logo_open_${RID}.mp4'
file '/tmp/presenter_${RID}.mp4'
file '/tmp/logo_close_${RID}.mp4'
EOF

  ffmpeg -y -f concat -safe 0 -i "/tmp/final_concat_${RID}.txt" \
    -c:v libx264 -preset fast -crf 18 -an \
    "/tmp/video_noaudio_${RID}.mp4" 2>/dev/null
  echo "  Vídeo sem áudio montado"

  # 5. Mixar voz + trilha e adicionar ao vídeo
  local VOZ_DELAY_MS=$(echo "$LOGO_DUR * 1000" | bc | cut -d. -f1)
  local TRILHA_DUR
  TRILHA_DUR=$(echo "$TOTAL_DUR + 2" | bc)

  ffmpeg -y \
    -i "/tmp/video_noaudio_${RID}.mp4" \
    -i "$VOZ" \
    -stream_loop -1 -i "$TRILHA" \
    -filter_complex "
      [1:a]adelay=${VOZ_DELAY_MS}|${VOZ_DELAY_MS},volume=1.0[voz];
      [2:a]atrim=0:${TRILHA_DUR},volume=${MUSIC_VOL},afade=t=in:st=0:d=2,afade=t=out:st=$(echo "$TOTAL_DUR - 2" | bc):d=2[music];
      [voz][music]amix=inputs=2:duration=first[audio_out]
    " \
    -map "0:v" -map "[audio_out]" \
    -c:v copy -c:a aac -b:a 192k \
    -t "$TOTAL_DUR" \
    "$OUTPUT" 2>/dev/null

  local SIZE
  SIZE=$(du -sh "$OUTPUT" | cut -f1)
  echo "  PRONTO: $OUTPUT ($SIZE)"
}

# Roteiro 01 — Comercial Direto (5 clipes = ~38s + 6s logo abertura/fechamento = ~44s total)
montar_roteiro "01" "Comercial_Direto" \
  "$CLIPS_DIR/r01_clip1.mp4" \
  "$CLIPS_DIR/r01_clip2.mp4" \
  "$CLIPS_DIR/r01_clip3.mp4" \
  "$CLIPS_DIR/r01_clip4.mp4" \
  "$CLIPS_DIR/r01_clip5.mp4"

echo ""
echo "Roteiro 01 concluído!"

# Roteiro 02 — Processo + Autoridade (4 clipes = ~32s + 6s logo = ~38s total)
montar_roteiro "02" "Processo_Autoridade" \
  "$CLIPS_DIR/r02_clip1.mp4" \
  "$CLIPS_DIR/r02_clip2.mp4" \
  "$CLIPS_DIR/r02_clip3.mp4" \
  "$CLIPS_DIR/r02_clip4.mp4"

echo ""
echo "Roteiro 02 concluído!"

# Roteiro 03 — Cena + Network (5 clipes = ~40s + 6s logo = ~46s total)
montar_roteiro "03" "Cena_Network" \
  "$CLIPS_DIR/r03_clip1.mp4" \
  "$CLIPS_DIR/r03_clip2.mp4" \
  "$CLIPS_DIR/r03_clip3.mp4" \
  "$CLIPS_DIR/r03_clip4.mp4" \
  "$CLIPS_DIR/r03_clip5.mp4"

echo ""
echo "Roteiro 03 concluído!"

# Roteiro 04 — Remarketing (4 clipes = ~32s + 6s logo = ~38s total)
montar_roteiro "04" "Remarketing" \
  "$CLIPS_DIR/r04_clip1.mp4" \
  "$CLIPS_DIR/r04_clip2.mp4" \
  "$CLIPS_DIR/r04_clip3.mp4" \
  "$CLIPS_DIR/r04_clip4.mp4"

echo ""
echo "Roteiro 04 concluído!"
echo ""
echo "=== TODOS OS VÍDEOS PRONTOS ==="
ls -lh "$OUTPUT_DIR/"
