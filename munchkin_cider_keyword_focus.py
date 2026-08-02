import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# 한글 폰트 설정 (Windows 기본 맑은 고딕)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('webtoon_clean.csv')
munchkin = df[df['is_munchkin'] == 1].copy()

# '사이다' 개념 키워드: 답답한 상황이 속 시원하게 해결되는 즉각적인 카타르시스,
# 빠른 사건 전개, 불합리함의 신속한 응징 -> 제목/태그/줄거리 전체에서 탐색
KEYWORDS = ['사이다', '통쾌', '속시원', '속 시원', '카타르시스', '참교육', '응징', '정의구현', '무쌍']
combined_text = (
    munchkin['titleName'].fillna('') + ' ' +
    munchkin['tags'].fillna('') + ' ' +
    munchkin['synopsis'].fillna('')
)
munchkin['has_cider_concept'] = combined_text.str.contains('|'.join(KEYWORDS), na=False, regex=True)

group_yes = munchkin[munchkin['has_cider_concept']]
group_no = munchkin[~munchkin['has_cider_concept']]

def summarize(series):
    return {
        'n': len(series), 'mean': series.mean(), 'median': series.median(),
        'sem': series.std() / np.sqrt(len(series)),
    }

fav_yes, fav_no = summarize(group_yes['favoriteCount']), summarize(group_no['favoriteCount'])
log_yes, log_no = np.log10(group_yes['favoriteCount']), np.log10(group_no['favoriteCount'])
logfav_yes, logfav_no = summarize(log_yes), summarize(log_no)
star_yes, star_no = summarize(group_yes['starScore']), summarize(group_no['starScore'])

fav_t, fav_p = stats.ttest_ind(group_yes['favoriteCount'], group_no['favoriteCount'], equal_var=False)
fav_u, fav_up = stats.mannwhitneyu(group_yes['favoriteCount'], group_no['favoriteCount'], alternative='two-sided')
logfav_t, logfav_p = stats.ttest_ind(log_yes, log_no, equal_var=False)
star_t, star_p = stats.ttest_ind(group_yes['starScore'], group_no['starScore'], equal_var=False)

def sig_mark(p):
    if p < 0.001:
        return '*** (p<0.001)'
    elif p < 0.01:
        return '** (p<0.01)'
    elif p < 0.05:
        return '* (p<0.05)'
    elif p < 0.10:
        return f'† (p={p:.3f}, 근접하나 미달)'
    else:
        return 'n.s. (유의하지 않음)'

result_text = "=" * 60 + "\n"
result_text += "[먼치킨 장르 전용] '사이다' 개념 키워드 등장 여부 비교\n"
result_text += "탐색 범위: 제목 + 태그 + 줄거리\n"
result_text += f"탐색 키워드: {', '.join(KEYWORDS)}\n"
result_text += "=" * 60 + "\n"
result_text += f"먼치킨 전체        : {len(munchkin)}개\n"
result_text += f"  - 키워드 O       : {fav_yes['n']}개\n"
result_text += f"  - 키워드 X       : {fav_no['n']}개\n\n"

result_text += "-" * 60 + "\n"
result_text += "[1] 평균 관심수(favoriteCount) - 원값\n"
result_text += "-" * 60 + "\n"
result_text += f"키워드 O : 평균 {fav_yes['mean']:,.0f} / 중앙값 {fav_yes['median']:,.0f}\n"
result_text += f"키워드 X : 평균 {fav_no['mean']:,.0f} / 중앙값 {fav_no['median']:,.0f}\n"
result_text += f"차이(O-X) : {fav_yes['mean'] - fav_no['mean']:+,.0f} ({(fav_yes['mean']/fav_no['mean']-1)*100:+.1f}%)\n"
result_text += f"Welch t-검정   : t={fav_t:.3f}, p={fav_p:.4f} -> {sig_mark(fav_p)}\n"
result_text += f"Mann-Whitney U : p={fav_up:.4f} -> {sig_mark(fav_up)}\n\n"

result_text += "-" * 60 + "\n"
result_text += "[2] 평균 관심수 - log10 변환 (이상치 영향 완화)\n"
result_text += "-" * 60 + "\n"
result_text += f"키워드 O : log10 평균 {logfav_yes['mean']:.3f} (환산 ~{10**logfav_yes['mean']:,.0f})\n"
result_text += f"키워드 X : log10 평균 {logfav_no['mean']:.3f} (환산 ~{10**logfav_no['mean']:,.0f})\n"
result_text += f"Welch t-검정   : t={logfav_t:.3f}, p={logfav_p:.4f} -> {sig_mark(logfav_p)}\n\n"

result_text += "-" * 60 + "\n"
result_text += "[3] 평균 별점 (보조 지표)\n"
result_text += "-" * 60 + "\n"
result_text += f"키워드 O : 평균 {star_yes['mean']:.3f}\n"
result_text += f"키워드 X : 평균 {star_no['mean']:.3f}\n"
result_text += f"Welch t-검정   : t={star_t:.3f}, p={star_p:.4f} -> {sig_mark(star_p)}\n"

print(result_text)
with open('munchkin_cider_keyword_focus_results.txt', 'w', encoding='utf-8') as f:
    f.write(result_text)
print("결과 저장 완료: munchkin_cider_keyword_focus_results.txt")

# ---------------- 시각화 (먼치킨 전용, 3-패널) ----------------
COLOR_YES = '#eb6834'
COLOR_NO = '#898781'
COLOR_GRID = '#e1e0d9'
COLOR_TEXT_PRIMARY = '#0b0b0b'
COLOR_TEXT_SECONDARY = '#52514e'
SURFACE = '#fcfcfb'

labels = ['키워드 O', '키워드 X']
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
        ax.spines[spine].set_color(COLOR_NO)

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15.5, 5.5), facecolor=SURFACE)

# 패널 1: 평균 관심수 (원값)
style_axis(ax1)
ax1.bar(x, [fav_yes['mean'], fav_no['mean']], yerr=[fav_yes['sem'], fav_no['sem']],
        capsize=5, width=width, color=[COLOR_YES, COLOR_NO], zorder=3)
for xi, val in zip(x, [fav_yes['mean'], fav_no['mean']]):
    ax1.annotate(f'{val:,.0f}', (xi, val), textcoords="offset points",
                 xytext=(0, 10), ha='center', fontsize=10, color=COLOR_TEXT_PRIMARY)
ax1.set_title(f'평균 관심수 (원값)  {sig_mark(fav_p).split(" ")[0]}',
              color=COLOR_TEXT_PRIMARY, fontsize=12, loc='left', pad=12)
ax1.set_ylabel('평균 관심수', color=COLOR_TEXT_SECONDARY, rotation=0, labelpad=30, va='center')

# 패널 2: 평균 관심수 (log10)
style_axis(ax2)
ax2.bar(x, [logfav_yes['mean'], logfav_no['mean']], yerr=[logfav_yes['sem'], logfav_no['sem']],
        capsize=5, width=width, color=[COLOR_YES, COLOR_NO], zorder=3)
for xi, val in zip(x, [logfav_yes['mean'], logfav_no['mean']]):
    ax2.annotate(f'{val:.2f}\n(~{10**val:,.0f})', (xi, val), textcoords="offset points",
                 xytext=(0, 10), ha='center', fontsize=9, color=COLOR_TEXT_PRIMARY)
ax2.set_ylim(4.5, 5.7)
ax2.set_title(f'평균 관심수 (log10 변환)  {sig_mark(logfav_p).split(" ")[0]}',
              color=COLOR_TEXT_PRIMARY, fontsize=12, loc='left', pad=12)
ax2.set_ylabel('log10\n(관심수)', color=COLOR_TEXT_SECONDARY, rotation=0, labelpad=30, va='center')

# 패널 3: 평균 별점
style_axis(ax3)
ax3.bar(x, [star_yes['mean'], star_no['mean']], yerr=[star_yes['sem'], star_no['sem']],
        capsize=5, width=width, color=[COLOR_YES, COLOR_NO], zorder=3)
for xi, val in zip(x, [star_yes['mean'], star_no['mean']]):
    ax3.annotate(f'{val:.2f}', (xi, val), textcoords="offset points",
                 xytext=(0, 10), ha='center', fontsize=10, color=COLOR_TEXT_PRIMARY)
ax3.set_ylim(9, 10.1)
ax3.set_title(f'평균 별점  {sig_mark(star_p).split(" ")[0]}',
              color=COLOR_TEXT_PRIMARY, fontsize=12, loc='left', pad=12)
ax3.set_ylabel('평균 별점', color=COLOR_TEXT_SECONDARY, rotation=0, labelpad=30, va='center')

fig.suptitle(f"먼치킨 장르 내 '사이다' 개념 키워드 등장 여부 비교 (O:{fav_yes['n']}개 / X:{fav_no['n']}개)",
             color=COLOR_TEXT_PRIMARY, fontsize=14, y=1.02)
fig.tight_layout()
out_path = 'munchkin_cider_keyword_focus.png'
fig.savefig(out_path, dpi=150, facecolor=SURFACE, bbox_inches='tight')
print(f"그래프 저장 완료: {out_path}")
