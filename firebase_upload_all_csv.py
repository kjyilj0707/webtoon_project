"""
프로젝트에서 수집한 CSV 파일 5개를 각각 별도의 Firestore 컬렉션으로 업로드하는 스크립트.
(webtoon_clean.csv는 기존 firebase_migrate.py가 'webtoons' 컬렉션으로 이미 관리 중이므로 여기서 재사용)

사전 준비: firebase_migrate.py와 동일 (serviceAccountKey.json 필요)
"""

import os
import math
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

CRED_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")
BATCH_SIZE = 400  # Firestore 배치 쓰기 최대 500건 제한

# (csv 파일, 컬렉션명, titleId를 문서ID로 써도 되는지 여부)
FILES = [
    ("webtoon_raw.csv", "webtoon_raw", False),
    ("webtoon_detail_temp.csv", "webtoon_detail_temp", False),
    ("webtoon_detail.csv", "webtoon_detail", False),
    ("webtoon_errors.csv", "webtoon_errors", False),
    ("webtoon_clean.csv", "webtoons", True),
]

cred = credentials.Certificate(CRED_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()


def clean_record(record: dict) -> dict:
    return {
        k: (None if isinstance(v, float) and math.isnan(v) else v)
        for k, v in record.items()
    }


def upload_csv(csv_path: str, collection_name: str, use_title_id_as_doc_id: bool):
    df = pd.read_csv(csv_path)
    collection_ref = db.collection(collection_name)

    batch = db.batch()
    count = 0

    for idx, row in df.iterrows():
        record = clean_record(row.to_dict())
        if use_title_id_as_doc_id:
            doc_ref = collection_ref.document(str(row["titleId"]))
        else:
            # 원본/중간/에러 CSV는 titleId 중복이 있어 인덱스를 붙여 고유 문서ID 생성
            doc_ref = collection_ref.document(f"{row['titleId']}_{idx}")
        batch.set(doc_ref, record)
        count += 1

        if count % BATCH_SIZE == 0:
            batch.commit()
            batch = db.batch()
            print(f"  {collection_name}: {count}/{len(df)}건 업로드됨...")

    batch.commit()
    print(f"완료: {collection_name} 총 {count}건 업로드됨 (source: {csv_path})")


if __name__ == "__main__":
    for csv_path, collection_name, use_title_id in FILES:
        print(f"[{csv_path}] -> Firestore 컬렉션 '{collection_name}' 업로드 시작")
        upload_csv(csv_path, collection_name, use_title_id)
