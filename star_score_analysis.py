import pandas as pd
import matplotlib.pyplot as plt

# 한글 폰트 설정 (Windows 기본 맑은 고딕)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('webtoon_clean.csv')

# ---------------- 평균 계산 ----------------
mean_score = df['starScore'].mean()
median_score = df['starScore'].median()
min_score = df['starScore'].min()
max_score = df['starScore'].max()

result_text = "=" * 50 + "\n"
result_text += "네이버 웹툰 전체 작품 별점 통계\n"
result_text += "=" * 50 + "\n"
result_text += f"작품 수      : {len(df):,}개\n"
result_text += f"평균 별점    : {mean_score:.3f}\n"
result_text += f"중앙값       : {median_score:.3f}\n"
result_text += f"최저 별점    : {min_score:.3f}\n"
result_text += f"최고 별점    : {max_score:.3f}\n"

print(result_text)

with open('star_score_results.txt', 'w', encoding='utf-8') as f:
    f.write(result_text)
print("결과 저장 완료: star_score_results.txt")

# ---------------- 산점도 ----------------
COLOR_MAIN = '#eb6834'      # 팔레트 slot 2 (orange)
COLOR_MEAN = '#3c6ddb'      # 평균선 강조용 blue
COLOR_MUTED = '#898781'
COLOR_GRID = '#e1e0d9'
COLOR_TEXT_PRIMARY = '#0b0b0b'
COLOR_TEXT_SECONDARY = '#52514e'
SURFACE = '#fcfcfb'

sorted_scores = df['starScore'].sort_values().reset_index(drop=True)

fig, ax = plt.subplots(figsize=(10, 6), facecolor=SURFACE)
ax.set_facecolor(SURFACE)

ax.scatter(range(len(sorted_scores)), sorted_scores,
           s=10, color=COLOR_MAIN, alpha=0.5, zorder=3, label='작품별 별점')

ax.axhline(mean_score, color=COLOR_MEAN, linewidth=1.5, linestyle='--', zorder=4,
           label=f'평균 {mean_score:.2f}점')

ax.set_title('네이버 웹툰 전체 작품 별점 분포', color=COLOR_TEXT_PRIMARY, fontsize=13, loc='left', pad=12)
ax.set_xlabel('작품 (별점 오름차순 정렬)', color=COLOR_TEXT_SECONDARY)
ax.set_ylabel('별점', color=COLOR_TEXT_SECONDARY, rotation=0, labelpad=20, va='center')
ax.tick_params(colors=COLOR_TEXT_SECONDARY)
ax.grid(axis='y', color=COLOR_GRID, linewidth=0.8, zorder=0)
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)
for spine in ['left', 'bottom']:
    ax.spines[spine].set_color(COLOR_MUTED)

legend = ax.legend(loc='lower right', frameon=False, labelcolor=COLOR_TEXT_SECONDARY)

fig.tight_layout()
out_path = 'star_score_scatter.png'
fig.savefig(out_path, dpi=150, facecolor=SURFACE)
print(f"그래프 저장 완료: {out_path}")
