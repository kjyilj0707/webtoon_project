import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# 한글 폰트 설정 (Windows 기본 맑은 고딕)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('webtoon_clean.csv')

# ---------------------------------------------------------------
# '사이다' 개념 키워드 정의
# 정의: 답답한 상황이 속 시원하게 해결되는 즉각적인 카타르시스,
#       빠른 사건 전개, 불합리함의 신속한 응징
# -> 단일 태그 '사이다'만으로는 이 개념을 다 담지 못하므로,
#    제목/태그/줄거리 전체에서 같은 개념을 표현하는 단어들을 함께 탐색
# ---------------------------------------------------------------
KEYWORDS = ['사이다', '통쾌', '속시원', '속 시원', '카타르시스', '참교육', '응징', '정의구현', '무쌍']

combined_text = (
    df['titleName'].fillna('') + ' ' +
    df['tags'].fillna('') + ' ' +
    df['synopsis'].fillna('')
)
pattern = '|'.join(KEYWORDS)
has_cider_concept = combined_text.str.contains(pattern, na=False, regex=True)
df['has_cider_concept'] = has_cider_concept

# 키워드별 등장 빈도(진단용, 어떤 단어가 실제로 얼마나 기여했는지 확인)
kw_counts = {kw: combined_text.str.contains(kw, na=False, regex=False).sum() for kw in KEYWORDS}

def summarize(series):
    return {
        'n': len(series),
        'mean': series.mean(),
        'median': series.median(),
        'sem': series.std() / np.sqrt(len(series)),
    }

def compare(sub_df, label):
    yes = sub_df[sub_df['has_cider_concept']]
    no = sub_df[~sub_df['has_cider_concept']]
    fav_yes, fav_no = summarize(yes['favoriteCount']), summarize(no['favoriteCount'])
    log_yes = np.log10(yes['favoriteCount'])
    log_no = np.log10(no['favoriteCount'])
    logfav_yes, logfav_no = summarize(log_yes), summarize(log_no)
    star_yes, star_no = summarize(yes['starScore']), summarize(no['starScore'])

    fav_t, fav_p = stats.ttest_ind(yes['favoriteCount'], no['favoriteCount'], equal_var=False)
    fav_u, fav_up = stats.mannwhitneyu(yes['favoriteCount'], no['favoriteCount'], alternative='two-sided')
    logfav_t, logfav_p = stats.ttest_ind(log_yes, log_no, equal_var=False)
    star_t, star_p = stats.ttest_ind(yes['starScore'], no['starScore'], equal_var=False)

    return {
        'label': label, 'fav_yes': fav_yes, 'fav_no': fav_no,
        'logfav_yes': logfav_yes, 'logfav_no': logfav_no,
        'star_yes': star_yes, 'star_no': star_no,
        'fav_t': fav_t, 'fav_p': fav_p, 'fav_u': fav_u, 'fav_up': fav_up,
        'logfav_t': logfav_t, 'logfav_p': logfav_p,
        'star_t': star_t, 'star_p': star_p,
    }

result_all = compare(df, '전체 웹툰')
result_munchkin = compare(df[df['is_munchkin'] == 1], '먼치킨 장르만')
result_nonmunchkin = compare(df[df['is_munchkin'] == 0], '비(非)먼치킨 장르만')

def sig_mark(p):
    if p < 0.001:
        return '*** (p<0.001)'
    elif p < 0.01:
        return '** (p<0.01)'
    elif p < 0.05:
        return '* (p<0.05)'
    else:
        return 'n.s. (유의하지 않음)'

def format_block(r):
    t = "-" * 60 + "\n"
    t += f"[{r['label']}]  키워드 O: {r['fav_yes']['n']}개 / 키워드 X: {r['fav_no']['n']}개\n"
    t += "-" * 60 + "\n"
    t += f"관심수(원값) 평균   : O={r['fav_yes']['mean']:,.0f}  X={r['fav_no']['mean']:,.0f}  "
    t += f"차이 {(r['fav_yes']['mean']/r['fav_no']['mean']-1)*100:+.1f}%\n"
    t += f"  Welch t={r['fav_t']:.3f}, p={r['fav_p']:.4f} -> {sig_mark(r['fav_p'])}\n"
    t += f"  Mann-Whitney p={r['fav_up']:.4f} -> {sig_mark(r['fav_up'])}\n"
    t += f"관심수(log10) 평균  : O={r['logfav_yes']['mean']:.3f}(~{10**r['logfav_yes']['mean']:,.0f})  "
    t += f"X={r['logfav_no']['mean']:.3f}(~{10**r['logfav_no']['mean']:,.0f})\n"
    t += f"  Welch t={r['logfav_t']:.3f}, p={r['logfav_p']:.4f} -> {sig_mark(r['logfav_p'])}\n"
    t += f"평균 별점           : O={r['star_yes']['mean']:.3f}  X={r['star_no']['mean']:.3f}  "
    t += f"차이 {r['star_yes']['mean']-r['star_no']['mean']:+.3f}\n"
    t += f"  Welch t={r['star_t']:.3f}, p={r['star_p']:.4f} -> {sig_mark(r['star_p'])}\n\n"
    return t

result_text = "=" * 60 + "\n"
result_text += "'사이다' 개념 키워드(제목/태그/줄거리) 등장 여부에 따른 비교\n"
result_text += "=" * 60 + "\n"
result_text += f"탐색 키워드: {', '.join(KEYWORDS)}\n"
result_text += "키워드별 등장 작품 수(중복 가능):\n"
for kw, cnt in kw_counts.items():
    result_text += f"  - {kw}: {cnt}개\n"
result_text += f"키워드 1개 이상 등장 작품 수: {has_cider_concept.sum()}개 / 전체 {len(df)}개\n\n"

result_text += format_block(result_all)
result_text += format_block(result_munchkin)
result_text += format_block(result_nonmunchkin)

print(result_text)
with open('cider_keyword_results.txt', 'w', encoding='utf-8') as f:
    f.write(result_text)
print("결과 저장 완료: cider_keyword_results.txt")

# ---------------------------------------------------------------
# 시각화
# ---------------------------------------------------------------
COLOR_YES = '#eb6834'
COLOR_NO = '#898781'
COLOR_GRID = '#e1e0d9'
COLOR_TEXT_PRIMARY = '#0b0b0b'
COLOR_TEXT_SECONDARY = '#52514e'
SURFACE = '#fcfcfb'

def style_axis(ax, xticks, xticklabels):
    ax.set_facecolor(SURFACE)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels, color=COLOR_TEXT_SECONDARY)
    ax.tick_params(colors=COLOR_TEXT_SECONDARY)
    ax.grid(axis='y', color=COLOR_GRID, linewidth=0.8, zorder=0)
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color(COLOR_NO)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), facecolor=SURFACE)

# 왼쪽: 전체 웹툰 기준 log10(관심수) 비교
style_axis(ax1, [0, 1], ['키워드 O', '키워드 X'])
vals1 = [result_all['logfav_yes']['mean'], result_all['logfav_no']['mean']]
errs1 = [result_all['logfav_yes']['sem'], result_all['logfav_no']['sem']]
ax1.bar([0, 1], vals1, yerr=errs1, capsize=5, width=0.5, color=[COLOR_YES, COLOR_NO], zorder=3)
for xi, val in zip([0, 1], vals1):
    ax1.annotate(f'{val:.2f}\n(~{10**val:,.0f})', (xi, val), textcoords="offset points",
                 xytext=(0, 10), ha='center', fontsize=9, color=COLOR_TEXT_PRIMARY)
ax1.set_title(f"전체 웹툰: log10(관심수)  {sig_mark(result_all['logfav_p']).split(' ')[0]}",
              color=COLOR_TEXT_PRIMARY, fontsize=12, loc='left', pad=12)
ax1.set_ylabel('log10\n(관심수)', color=COLOR_TEXT_SECONDARY, rotation=0, labelpad=30, va='center')

# 오른쪽: 먼치킨 vs 비먼치킨 그룹별 log10(관심수) 비교 (2x2 grouped bar)
style_axis(ax2, [0.3, 1.3], ['먼치킨', '비(非)먼치킨'])
group_x = [0, 0.6, 1.0, 1.6]
vals2 = [result_munchkin['logfav_yes']['mean'], result_munchkin['logfav_no']['mean'],
         result_nonmunchkin['logfav_yes']['mean'], result_nonmunchkin['logfav_no']['mean']]
errs2 = [result_munchkin['logfav_yes']['sem'], result_munchkin['logfav_no']['sem'],
         result_nonmunchkin['logfav_yes']['sem'], result_nonmunchkin['logfav_no']['sem']]
colors2 = [COLOR_YES, COLOR_NO, COLOR_YES, COLOR_NO]
ax2.bar(group_x, vals2, yerr=errs2, capsize=4, width=0.4, color=colors2, zorder=3)
for xi, val in zip(group_x, vals2):
    ax2.annotate(f'{val:.2f}', (xi, val), textcoords="offset points",
                 xytext=(0, 8), ha='center', fontsize=9, color=COLOR_TEXT_PRIMARY)
ax2.set_xticks([0.3, 1.3])
ax2.set_title('장르별 log10(관심수): 먼치킨에서 키워드 효과가 더 큰가?',
              color=COLOR_TEXT_PRIMARY, fontsize=12, loc='left', pad=12)
ax2.set_ylabel('log10\n(관심수)', color=COLOR_TEXT_SECONDARY, rotation=0, labelpad=30, va='center')

from matplotlib.patches import Patch
legend_elems = [Patch(facecolor=COLOR_YES, label='키워드 O'), Patch(facecolor=COLOR_NO, label='키워드 X')]
ax2.legend(handles=legend_elems, loc='upper right', frameon=False, labelcolor=COLOR_TEXT_SECONDARY)

fig.suptitle("'사이다' 개념 키워드 등장 여부와 관심수의 관계", color=COLOR_TEXT_PRIMARY, fontsize=14, y=1.02)
fig.tight_layout()
out_path = 'cider_keyword_comparison.png'
fig.savefig(out_path, dpi=150, facecolor=SURFACE, bbox_inches='tight')
print(f"그래프 저장 완료: {out_path}")
