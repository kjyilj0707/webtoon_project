import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# 한글 폰트 설정 (Windows 기본 맑은 고딕)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('webtoon_clean.csv')
munchkin = df[df['is_munchkin'] == 1].copy()

has_cider = munchkin['tags'].str.contains('사이다', na=False)
group_cider = munchkin[has_cider]
group_none = munchkin[~has_cider]

def summarize(series):
    return {
        'n': len(series),
        'mean': series.mean(),
        'median': series.median(),
        'std': series.std(),
        'sem': series.std() / np.sqrt(len(series)),
    }

fav_cider = summarize(group_cider['favoriteCount'])
fav_none = summarize(group_none['favoriteCount'])
star_cider = summarize(group_cider['starScore'])
star_none = summarize(group_none['starScore'])

# 로그변환: 관심수는 오른쪽 꼬리가 매우 긴 분포라 소수 초인기작이 평균을 왜곡함.
# log10을 씌워 값의 간격을 압축한 뒤 같은 비교를 반복 (기하평균 비교 효과)
log_fav_cider = np.log10(group_cider['favoriteCount'])
log_fav_none = np.log10(group_none['favoriteCount'])
logfav_cider = summarize(log_fav_cider)
logfav_none = summarize(log_fav_none)

# 관심수: 분포가 크게 치우쳐 있어(오른쪽 꼬리) t-검정과 함께
# 순위 기반 비모수 검정(Mann-Whitney U)도 같이 확인
fav_t, fav_p = stats.ttest_ind(group_cider['favoriteCount'], group_none['favoriteCount'], equal_var=False)
fav_u, fav_up = stats.mannwhitneyu(group_cider['favoriteCount'], group_none['favoriteCount'], alternative='two-sided')

logfav_t, logfav_p = stats.ttest_ind(log_fav_cider, log_fav_none, equal_var=False)

star_t, star_p = stats.ttest_ind(group_cider['starScore'], group_none['starScore'], equal_var=False)
star_u, star_up = stats.mannwhitneyu(group_cider['starScore'], group_none['starScore'], alternative='two-sided')

def sig_mark(p):
    if p < 0.001:
        return '*** (p<0.001)'
    elif p < 0.01:
        return '** (p<0.01)'
    elif p < 0.05:
        return '* (p<0.05)'
    else:
        return 'n.s. (유의하지 않음)'

result_text = "=" * 60 + "\n"
result_text += "먼치킨 장르 내 '사이다' 태그 동반 여부에 따른 비교\n"
result_text += "=" * 60 + "\n"
result_text += f"전체 먼치킨 작품 수 : {len(munchkin)}개\n"
result_text += f"  - 사이다 태그 O   : {fav_cider['n']}개\n"
result_text += f"  - 사이다 태그 X   : {fav_none['n']}개\n\n"

result_text += "-" * 60 + "\n"
result_text += "[1] 평균 관심수(favoriteCount) 비교\n"
result_text += "-" * 60 + "\n"
result_text += f"사이다 O : 평균 {fav_cider['mean']:,.0f} / 중앙값 {fav_cider['median']:,.0f}\n"
result_text += f"사이다 X : 평균 {fav_none['mean']:,.0f} / 중앙값 {fav_none['median']:,.0f}\n"
result_text += f"차이(O-X) : 평균 {fav_cider['mean'] - fav_none['mean']:,.0f} "
result_text += f"({(fav_cider['mean'] / fav_none['mean'] - 1) * 100:+.1f}%)\n"
result_text += f"Welch t-검정      : t={fav_t:.3f}, p={fav_p:.4f} -> {sig_mark(fav_p)}\n"
result_text += f"Mann-Whitney U    : U={fav_u:.1f}, p={fav_up:.4f} -> {sig_mark(fav_up)}\n\n"

result_text += "-" * 60 + "\n"
result_text += "[1-log] 관심수 로그변환(log10) 후 비교\n"
result_text += "-" * 60 + "\n"
result_text += f"사이다 O : log10 평균 {logfav_cider['mean']:.3f} (= 원값 환산 {10**logfav_cider['mean']:,.0f})\n"
result_text += f"사이다 X : log10 평균 {logfav_none['mean']:.3f} (= 원값 환산 {10**logfav_none['mean']:,.0f})\n"
result_text += f"차이(O-X) : log10 {logfav_cider['mean'] - logfav_none['mean']:+.3f}\n"
result_text += f"Welch t-검정      : t={logfav_t:.3f}, p={logfav_p:.4f} -> {sig_mark(logfav_p)}\n\n"

result_text += "-" * 60 + "\n"
result_text += "[2] 평균 별점(starScore) 비교 (보조 지표)\n"
result_text += "-" * 60 + "\n"
result_text += f"사이다 O : 평균 {star_cider['mean']:.3f} / 중앙값 {star_cider['median']:.3f}\n"
result_text += f"사이다 X : 평균 {star_none['mean']:.3f} / 중앙값 {star_none['median']:.3f}\n"
result_text += f"차이(O-X) : 평균 {star_cider['mean'] - star_none['mean']:+.3f}\n"
result_text += f"Welch t-검정      : t={star_t:.3f}, p={star_p:.4f} -> {sig_mark(star_p)}\n"
result_text += f"Mann-Whitney U    : U={star_u:.1f}, p={star_up:.4f} -> {sig_mark(star_up)}\n"

print(result_text)
with open('munchkin_cider_results.txt', 'w', encoding='utf-8') as f:
    f.write(result_text)
print("결과 저장 완료: munchkin_cider_results.txt")

# ---------------- 시각화 ----------------
COLOR_CIDER = '#eb6834'   # 팔레트 slot 2 (orange) - 사이다 O
COLOR_NONE = '#898781'    # muted grey - 사이다 X
COLOR_GRID = '#e1e0d9'
COLOR_TEXT_PRIMARY = '#0b0b0b'
COLOR_TEXT_SECONDARY = '#52514e'
SURFACE = '#fcfcfb'

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15.5, 5.5), facecolor=SURFACE)
labels = ['사이다 O', '사이다 X']
x = [0, 1]
width = 0.5

def style_axis(ax):
    ax.set_facecolor(SURFACE)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, color=COLOR_TEXT_SECONDARY)
    ax.tick_params(colors=COLOR_TEXT_SECONDARY)
    ax.grid(axis='y', color=COLOR_GRID, linewidth=0.8, zorder=0)
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color(COLOR_NONE)

# 왼쪽: 평균 관심수 (원값)
style_axis(ax1)
ax1.bar(x, [fav_cider['mean'], fav_none['mean']],
        yerr=[fav_cider['sem'], fav_none['sem']], capsize=5,
        width=width, color=[COLOR_CIDER, COLOR_NONE], zorder=3)
for xi, val in zip(x, [fav_cider['mean'], fav_none['mean']]):
    ax1.annotate(f'{val:,.0f}', (xi, val), textcoords="offset points",
                 xytext=(0, 10), ha='center', fontsize=10, color=COLOR_TEXT_PRIMARY)
ax1.set_title(f'평균 관심수 (원값)  {sig_mark(fav_p).split(" ")[0]}',
              color=COLOR_TEXT_PRIMARY, fontsize=12, loc='left', pad=12)
ax1.set_ylabel('평균 관심수', color=COLOR_TEXT_SECONDARY, rotation=0, labelpad=30, va='center')

# 가운데: 관심수 로그변환(log10) 비교
style_axis(ax2)
ax2.bar(x, [logfav_cider['mean'], logfav_none['mean']],
        yerr=[logfav_cider['sem'], logfav_none['sem']], capsize=5,
        width=width, color=[COLOR_CIDER, COLOR_NONE], zorder=3)
for xi, val in zip(x, [logfav_cider['mean'], logfav_none['mean']]):
    ax2.annotate(f'{val:.2f}\n(~{10**val:,.0f})', (xi, val), textcoords="offset points",
                 xytext=(0, 10), ha='center', fontsize=9, color=COLOR_TEXT_PRIMARY)
ax2.set_ylim(4.5, 5.7)
ax2.set_title(f'평균 관심수 (log10 변환)  {sig_mark(logfav_p).split(" ")[0]}',
              color=COLOR_TEXT_PRIMARY, fontsize=12, loc='left', pad=12)
ax2.set_ylabel('log10(관심수)', color=COLOR_TEXT_SECONDARY, rotation=0, labelpad=30, va='center')

# 오른쪽: 평균 별점
style_axis(ax3)
ax3.bar(x, [star_cider['mean'], star_none['mean']],
        yerr=[star_cider['sem'], star_none['sem']], capsize=5,
        width=width, color=[COLOR_CIDER, COLOR_NONE], zorder=3)
for xi, val in zip(x, [star_cider['mean'], star_none['mean']]):
    ax3.annotate(f'{val:.2f}', (xi, val), textcoords="offset points",
                 xytext=(0, 10), ha='center', fontsize=10, color=COLOR_TEXT_PRIMARY)
ax3.set_ylim(9, 10.1)
ax3.set_title(f'평균 별점  {sig_mark(star_p).split(" ")[0]}',
              color=COLOR_TEXT_PRIMARY, fontsize=12, loc='left', pad=12)
ax3.set_ylabel('평균 별점', color=COLOR_TEXT_SECONDARY, rotation=0, labelpad=30, va='center')

fig.suptitle("먼치킨 장르 내 '사이다' 태그 동반 여부 비교", color=COLOR_TEXT_PRIMARY, fontsize=14, y=1.02)
fig.tight_layout()
out_path = 'munchkin_cider_comparison.png'
fig.savefig(out_path, dpi=150, facecolor=SURFACE, bbox_inches='tight')
print(f"그래프 저장 완료: {out_path}")
