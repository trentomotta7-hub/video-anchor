import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ─────────────────────────────────────────────
# DADOS DE SCORING DOS ROTEIROS
# Critérios avaliados (0–10):
#   1. Força do Hook (primeiros 3s / primeiras linhas)
#   2. Clareza da Proposta de Valor
#   3. Prova Social / Autoridade
#   4. Urgência / Motivação para Ação
#   5. CTA (Call to Action)
#   6. Adequação ao Formato de Vídeo Curto
#   7. Potencial de Retenção (ThruPlay estimado)
#   8. Diferenciação Competitiva
# ─────────────────────────────────────────────

roteiros = {
    "R1\nComercial\nDireto": {
        "Hook": 8.5,
        "Proposta de Valor": 8.0,
        "Prova Social": 5.5,
        "Urgência / Motivação": 7.0,
        "CTA": 8.5,
        "Formato Vídeo Curto": 9.0,
        "Retenção Estimada": 7.5,
        "Diferenciação": 6.5,
    },
    "R2\nProcesso +\nAutoridade": {
        "Hook": 6.5,
        "Proposta de Valor": 9.0,
        "Prova Social": 9.5,
        "Urgência / Motivação": 6.5,
        "CTA": 7.5,
        "Formato Vídeo Curto": 7.0,
        "Retenção Estimada": 7.0,
        "Diferenciação": 9.0,
    },
    "R3\nCena +\nNetwork": {
        "Hook": 7.5,
        "Proposta de Valor": 7.5,
        "Prova Social": 10.0,
        "Urgência / Motivação": 6.0,
        "CTA": 7.0,
        "Formato Vídeo Curto": 6.0,
        "Retenção Estimada": 6.5,
        "Diferenciação": 9.5,
    },
    "R4\nRemarketing": {
        "Hook": 9.0,
        "Proposta de Valor": 8.5,
        "Prova Social": 8.5,
        "Urgência / Motivação": 9.5,
        "CTA": 9.5,
        "Formato Vídeo Curto": 8.0,
        "Retenção Estimada": 8.5,
        "Diferenciação": 7.5,
    },
}

criterios = list(list(roteiros.values())[0].keys())
nomes = list(roteiros.keys())
cores = ["#1DB954", "#1E90FF", "#FF6B35", "#FFD700"]

# ─────────────────────────────────────────────
# GRÁFICO 1 — RADAR CHART (Spider)
# ─────────────────────────────────────────────
N = len(criterios)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
fig.patch.set_facecolor('#0D0D0D')
ax.set_facecolor('#1A1A1A')

for i, (nome, dados) in enumerate(roteiros.items()):
    valores = list(dados.values())
    valores += valores[:1]
    ax.plot(angles, valores, 'o-', linewidth=2.5, color=cores[i], label=nome.replace('\n', ' '))
    ax.fill(angles, valores, alpha=0.12, color=cores[i])

ax.set_xticks(angles[:-1])
ax.set_xticklabels(criterios, size=10, color='white', fontweight='bold')
ax.set_ylim(0, 10)
ax.set_yticks([2, 4, 6, 8, 10])
ax.set_yticklabels(['2', '4', '6', '8', '10'], color='#888888', size=8)
ax.grid(color='#333333', linestyle='--', linewidth=0.8)
ax.spines['polar'].set_color('#444444')

legend = ax.legend(
    loc='upper right', bbox_to_anchor=(1.35, 1.15),
    fontsize=11, framealpha=0.3,
    facecolor='#1A1A1A', edgecolor='#444444',
    labelcolor='white'
)

ax.set_title('Análise Comparativa dos Roteiros\nThe Anchor Records',
             size=14, color='white', fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('/home/ubuntu/video-anchor/analise/radar_roteiros.png',
            dpi=150, bbox_inches='tight', facecolor='#0D0D0D')
plt.close()
print("Radar salvo.")

# ─────────────────────────────────────────────
# GRÁFICO 2 — SCORE TOTAL (Barra Horizontal)
# ─────────────────────────────────────────────
scores_totais = {nome: np.mean(list(dados.values())) for nome, dados in roteiros.items()}
nomes_bar = [n.replace('\n', ' ') for n in scores_totais.keys()]
valores_bar = list(scores_totais.values())

fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor('#0D0D0D')
ax.set_facecolor('#1A1A1A')

bars = ax.barh(nomes_bar, valores_bar, color=cores, height=0.55, edgecolor='#333333')

for bar, val in zip(bars, valores_bar):
    ax.text(val + 0.05, bar.get_y() + bar.get_height() / 2,
            f'{val:.1f}/10', va='center', ha='left',
            color='white', fontsize=12, fontweight='bold')

ax.set_xlim(0, 11)
ax.set_xlabel('Score Médio (0–10)', color='white', fontsize=11)
ax.set_title('Score Total por Roteiro\nThe Anchor Records', color='white', fontsize=14, fontweight='bold')
ax.tick_params(colors='white')
ax.spines['bottom'].set_color('#444444')
ax.spines['left'].set_color('#444444')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.xaxis.label.set_color('white')
ax.yaxis.label.set_color('white')
for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_color('white')

ax.axvline(x=7.5, color='#FFD700', linestyle='--', linewidth=1.2, alpha=0.7, label='Benchmark mínimo (7.5)')
ax.legend(facecolor='#1A1A1A', edgecolor='#444444', labelcolor='white', fontsize=9)

plt.tight_layout()
plt.savefig('/home/ubuntu/video-anchor/analise/score_total.png',
            dpi=150, bbox_inches='tight', facecolor='#0D0D0D')
plt.close()
print("Score total salvo.")

# ─────────────────────────────────────────────
# GRÁFICO 3 — HEATMAP de critérios por roteiro
# ─────────────────────────────────────────────
import matplotlib.colors as mcolors

matrix = np.array([[dados[c] for c in criterios] for dados in roteiros.values()])
nomes_heat = [n.replace('\n', ' ') for n in nomes]

fig, ax = plt.subplots(figsize=(12, 5))
fig.patch.set_facecolor('#0D0D0D')
ax.set_facecolor('#0D0D0D')

cmap = plt.cm.RdYlGn
im = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=10, aspect='auto')

ax.set_xticks(range(len(criterios)))
ax.set_xticklabels(criterios, rotation=30, ha='right', color='white', fontsize=10)
ax.set_yticks(range(len(nomes_heat)))
ax.set_yticklabels(nomes_heat, color='white', fontsize=11)

for i in range(len(nomes_heat)):
    for j in range(len(criterios)):
        val = matrix[i, j]
        text_color = 'black' if 4 < val < 8 else 'white'
        ax.text(j, i, f'{val:.1f}', ha='center', va='center',
                color=text_color, fontsize=11, fontweight='bold')

cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
cbar.ax.yaxis.set_tick_params(color='white')
plt.setp(cbar.ax.yaxis.get_ticklabels(), color='white')
cbar.set_label('Score', color='white')

ax.set_title('Heatmap de Performance — Critérios por Roteiro\nThe Anchor Records',
             color='white', fontsize=13, fontweight='bold', pad=15)

ax.spines[:].set_color('#444444')
plt.tight_layout()
plt.savefig('/home/ubuntu/video-anchor/analise/heatmap_roteiros.png',
            dpi=150, bbox_inches='tight', facecolor='#0D0D0D')
plt.close()
print("Heatmap salvo.")

# ─────────────────────────────────────────────
# GRÁFICO 4 — ThruPlay Estimado vs Benchmark
# ─────────────────────────────────────────────
thruplay_estimado = {
    "R1 Comercial\nDireto": 32,
    "R2 Processo +\nAutoridade": 27,
    "R3 Cena +\nNetwork": 24,
    "R4\nRemarketing": 38,
}

fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor('#0D0D0D')
ax.set_facecolor('#1A1A1A')

x = np.arange(len(thruplay_estimado))
bars = ax.bar(x, list(thruplay_estimado.values()), color=cores, width=0.5, edgecolor='#333333')

ax.axhline(y=25, color='#1DB954', linestyle='--', linewidth=1.5, label='Bom (25%+)')
ax.axhline(y=35, color='#FFD700', linestyle='--', linewidth=1.5, label='Excelente (35%+)')

for bar, val in zip(bars, thruplay_estimado.values()):
    ax.text(bar.get_x() + bar.get_width() / 2, val + 0.5,
            f'{val}%', ha='center', va='bottom', color='white', fontsize=12, fontweight='bold')

ax.set_xticks(x)
ax.set_xticklabels(list(thruplay_estimado.keys()), color='white', fontsize=10)
ax.set_ylabel('ThruPlay Rate Estimado (%)', color='white', fontsize=11)
ax.set_ylim(0, 50)
ax.set_title('ThruPlay Rate Estimado vs Benchmarks do Setor\nThe Anchor Records',
             color='white', fontsize=13, fontweight='bold')
ax.tick_params(colors='white')
ax.spines['bottom'].set_color('#444444')
ax.spines['left'].set_color('#444444')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_color('white')

ax.legend(facecolor='#1A1A1A', edgecolor='#444444', labelcolor='white', fontsize=10)

plt.tight_layout()
plt.savefig('/home/ubuntu/video-anchor/analise/thruplay_estimado.png',
            dpi=150, bbox_inches='tight', facecolor='#0D0D0D')
plt.close()
print("ThruPlay salvo.")

print("\nScores finais:")
for nome, score in scores_totais.items():
    print(f"  {nome.replace(chr(10), ' ')}: {score:.2f}/10")
