"""
지금까지 진행한 데이터 분석 결과를 Firestore 'analysis_reports' 컬렉션에 정리해서 저장하는 스크립트.
원본 수치는 매번 webtoon_clean.csv에서 다시 계산하여 문서에 기록한다 (하드코딩 방지).

사전 준비: firebase_migrate.py와 동일 (serviceAccountKey.json 필요)
"""

import os
import numpy as np
import pandas as pd
from scipy import stats
import firebase_admin
from firebase_admin import credentials, firestore

CRED_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")
CSV_PATH = "webtoon_clean.csv"
COLLECTION_NAME = "analysis_reports"

cred = credentials.Certificate(CRED_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()

df = pd.read_csv(CSV_PATH)


def build_star_score_doc():
    s = df['starScore']
    return {
        'title': '전체 웹툰 별점 분포',
        'created_at': firestore.SERVER_TIMESTAMP,
        'sample_size': int(len(df)),
        'mean': round(float(s.mean()), 3),
        'median': round(float(s.median()), 3),
        'min': round(float(s.min()), 3),
        'max': round(float(s.max()), 3),
        'summary': '별점은 9.5~10점에 극도로 쏠린 천장효과(ceiling effect)를 보이며, 소수 저평점 작품이 평균을 소폭 끌어내리는 왼쪽 꼬리 분포.',
        'chart_files': ['star_score_scatter.png'],
    }


def compare_groups(sub_df, has_keyword):
    yes = sub_df[has_keyword.loc[sub_df.index]]
    no = sub_df[~has_keyword.loc[sub_df.index]]
    log_yes, log_no = np.log10(yes['favoriteCount']), np.log10(no['favoriteCount'])

    fav_t, fav_p = stats.ttest_ind(yes['favoriteCount'], no['favoriteCount'], equal_var=False)
    logfav_t, logfav_p = stats.ttest_ind(log_yes, log_no, equal_var=False)
    star_t, star_p = stats.ttest_ind(yes['starScore'], no['starScore'], equal_var=False)

    return {
        'n_yes': int(len(yes)), 'n_no': int(len(no)),
        'favoriteCount_mean_yes': round(float(yes['favoriteCount'].mean()), 1),
        'favoriteCount_mean_no': round(float(no['favoriteCount'].mean()), 1),
        'favoriteCount_pct_diff': round(float((yes['favoriteCount'].mean() / no['favoriteCount'].mean() - 1) * 100), 1),
        'favoriteCount_ttest_p': round(float(fav_p), 4),
        'favoriteCount_log10_ttest_p': round(float(logfav_p), 4),
        'starScore_mean_yes': round(float(yes['starScore'].mean()), 3),
        'starScore_mean_no': round(float(no['starScore'].mean()), 3),
        'starScore_ttest_p': round(float(star_p), 4),
    }


def build_cider_demand_doc():
    munchkin = df[df['is_munchkin'] == 1]

    # 분석 1~2: 정확한 '사이다' 태그만
    has_tag = df['tags'].str.contains('사이다', na=False)
    stage_tag = compare_groups(munchkin, has_tag)

    # 분석 3~4: 확장 키워드 (제목+태그+줄거리)
    KEYWORDS = ['사이다', '통쾌', '속시원', '속 시원', '카타르시스', '참교육', '응징', '정의구현', '무쌍']
    combined_text = df['titleName'].fillna('') + ' ' + df['tags'].fillna('') + ' ' + df['synopsis'].fillna('')
    has_keyword = combined_text.str.contains('|'.join(KEYWORDS), na=False, regex=True)

    stage_all = compare_groups(df, has_keyword)
    stage_munchkin = compare_groups(munchkin, has_keyword)
    stage_nonmunchkin = compare_groups(df[df['is_munchkin'] == 0], has_keyword)

    return {
        'title': "독자 수요 차원의 확장 분석 — 먼치킨 '사이다' 심리 검증",
        'created_at': firestore.SERVER_TIMESTAMP,
        'background': (
            "먼치킨 장르 상위 동반 태그 4개 중 1~3위(액션/판타지/소설원작)는 서사 진행·제작 방식 태그인 반면, "
            "4위 '사이다'는 독자가 서사를 보며 느끼는 반응 차원의 태그. "
            "먼치킨 수요층이 '사이다(즉각적 카타르시스)'를 원한다는 가설을 데이터로 검증."
        ),
        'cider_definition': '답답한 상황이 속 시원하게 해결되는 즉각적인 카타르시스, 빠른 사건 전개, 불합리함의 신속한 응징',
        'method_note': (
            "관심수(favoriteCount) 비교를 메인 지표로 채택. "
            "평점은 천장효과로 판별력이 낮고, 태그 비중 분석은 선정 근거를 반복하는 순환논리이므로 제외."
        ),
        'stage_1_2_tag_only': {
            'description': "먼치킨 내 '사이다' 태그 단순 비교 + log10 변환",
            **stage_tag,
        },
        'stage_3_keywords_all_webtoons': {
            'description': '확장 키워드(사이다/통쾌/참교육/응징 등, 제목+태그+줄거리) 기준, 전체 웹툰 대상',
            'keywords': KEYWORDS,
            **stage_all,
        },
        'stage_3_keywords_nonmunchkin': {
            'description': '동일 키워드 기준, 비(非)먼치킨 장르만',
            **stage_nonmunchkin,
        },
        'stage_4_keywords_munchkin_focus': {
            'description': '동일 키워드 기준, 먼치킨 장르만 재초점',
            **stage_munchkin,
        },
        'key_interpretation': (
            "'사이다' 수요는 먼치킨에 국한되지 않은 웹툰 독자 전반의 보편적 흥행 요인으로 보임. "
            "먼치킨 장르는 설정 자체가 이미 사이다적 쾌감을 내장하고 있어, "
            "키워드 유무가 주는 한계효과가 상대적으로 작아지는 포화(saturation) 효과 가능성."
        ),
        'limitations': [
            '표본 크기 부족(먼치킨 키워드 O군 78개) → 통계 검정력 낮음',
            '키워드 목록 선정의 주관성',
            '텍스트 매칭(단어 등장 여부) != 실제 서사 구조 확인',
            '상관관계이지 인과관계 아님(역인과 가능성 배제 못함)',
            '평점은 천장효과로 판별력 낮음',
            '작가 인지도·연재기간·완결여부 등 교란변수 미통제(단순 그룹 비교, 회귀분석 아님)',
            '크롤링 시점 스냅샷 데이터로 시간 효과 미반영',
        ],
        'next_steps': [
            '연재기간/작가 인지도를 통제한 회귀분석으로 순수 효과 추정',
            '표본 확대(유사 계열 태그까지 포함한 카타르시스 스코어 구성)',
        ],
        'chart_files': [
            'munchkin_cider_comparison.png',
            'cider_keyword_comparison.png',
            'munchkin_cider_keyword_focus.png',
        ],
    }


def upload():
    star_doc = build_star_score_doc()
    cider_doc = build_cider_demand_doc()

    db.collection(COLLECTION_NAME).document('star_score_overview').set(star_doc)
    print("저장 완료: analysis_reports/star_score_overview")

    db.collection(COLLECTION_NAME).document('munchkin_cider_demand_analysis').set(cider_doc)
    print("저장 완료: analysis_reports/munchkin_cider_demand_analysis")


def verify():
    lines = []
    for doc_id in ['star_score_overview', 'munchkin_cider_demand_analysis']:
        doc = db.collection(COLLECTION_NAME).document(doc_id).get()
        lines.append(f"--- {doc_id} (exists={doc.exists}) ---")
        lines.append(repr(doc.to_dict()))
    with open('_firebase_verify.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print("검증 결과 저장: _firebase_verify.txt")


if __name__ == "__main__":
    upload()
    verify()
