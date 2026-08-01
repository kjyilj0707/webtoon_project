import pandas as pd
import matplotlib.pyplot as plt

# 한글 폰트 설정 (Windows 기본 맑은 고딕)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('webtoon_clean.csv')

# ---------------- 테이블 ----------------
year_stats = df.groupby('year').agg(
    total_new=('is_munchkin', 'size'),
    munchkin_new=('is_munchkin', 'sum')
).reset_index()
year_stats['ratio(%)'] = (year_stats['munchkin_new'] / year_stats['total_new'] * 100).round(2)
year_stats = year_stats.sort_values('year').reset_index(drop=True)
year_stats.columns = ['연도', '전체 신작', '먼치킨 신작', '비중(%)']

result_text = "=" * 50 + "\n"
result_text += "연도별 먼치킨 신작 비중\n"
result_text += "=" * 50 + "\n"
result_text += year_stats.to_string(index=False) + "\n"

print(result_text)

with open('analysis_results.txt', 'w', encoding='utf-8') as f:
    f.write(result_text)
print("테이블 저장 완료: analysis_results.txt")

# ---------------- 그래프 ----------------
COLOR_MUNCHKIN = '#eb6834'  # 팔레트 slot 2 (orange)
COLOR_MUTED = '#898781'
COLOR_GRID = '#e1e0d9'
COLOR_TEXT_PRIMARY = '#0b0b0b'
COLOR_TEXT_SECONDARY = '#52514e'
SURFACE = '#fcfcfb'

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 9), facecolor=SURFACE)

years = year_stats['연도']
x = range(len(years))
width = 0.55

# 위: 막대 (먼치킨 신작 개수)
ax1.set_facecolor(SURFACE)
ax1.bar(list(x), year_stats['먼치킨 신작'], width=width,
        color=COLOR_MUNCHKIN, label='먼치킨 신작', zorder=3)
ax1.set_xticks(list(x))
ax1.set_xticklabels(years, color=COLOR_TEXT_SECONDARY)
ax1.set_title('연도별 먼치킨 신작 개수', color=COLOR_TEXT_PRIMARY, fontsize=13, loc='left', pad=12)
ax1.set_ylabel('먼치킨 신작 수', color=COLOR_TEXT_SECONDARY)
ax1.tick_params(colors=COLOR_TEXT_SECONDARY)
ax1.grid(axis='y', color=COLOR_GRID, linewidth=0.8, zorder=0)
for spine in ['top', 'right']:
    ax1.spines[spine].set_visible(False)
for spine in ['left', 'bottom']:
    ax1.spines[spine].set_color(COLOR_MUTED)

# 아래: 비중(%) 라인
ax2.set_facecolor(SURFACE)
ax2.plot(list(x), year_stats['비중(%)'], color=COLOR_MUNCHKIN, linewidth=2,
         marker='o', markersize=6, zorder=3)
for xi, yi in zip(x, year_stats['비중(%)']):
    ax2.annotate(f'{yi:.1f}%', (xi, yi), textcoords="offset points",
                 xytext=(0, 8), ha='center', fontsize=9, color=COLOR_TEXT_SECONDARY)
ax2.set_xticks(list(x))
ax2.set_xticklabels(years, color=COLOR_TEXT_SECONDARY)
ax2.set_title('연도별 먼치킨 신작 비중(%)', color=COLOR_TEXT_PRIMARY, fontsize=13, loc='left', pad=12)
ax2.set_ylabel('비중(%)', color=COLOR_TEXT_SECONDARY)
ax2.tick_params(colors=COLOR_TEXT_SECONDARY)
ax2.grid(axis='y', color=COLOR_GRID, linewidth=0.8, zorder=0)
for spine in ['top', 'right']:
    ax2.spines[spine].set_visible(False)
for spine in ['left', 'bottom']:
    ax2.spines[spine].set_color(COLOR_MUTED)

fig.tight_layout()
out_path = 'munchkin_yearly_analysis.png'
fig.savefig(out_path, dpi=150, facecolor=SURFACE)
print(f"그래프 저장 완료: {out_path}")
