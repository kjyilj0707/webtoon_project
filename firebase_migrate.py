"""
webtoon_clean.csv 데이터를 Firebase Firestore로 업로드하는 스크립트.

사전 준비:
1. Firebase 콘솔(https://console.firebase.google.com)에서 프로젝트 생성
2. Firestore Database 활성화 (테스트 모드로 시작)
3. 프로젝트 설정 > 서비스 계정 > "새 비공개 키 생성"으로 JSON 다운로드
4. 다운로드한 파일을 이 프로젝트 폴더에 serviceAccountKey.json 이름으로 저장
   (이 파일은 .gitignore에 이미 등록되어 있어 git에 올라가지 않음)
"""

import os
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

CRED_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")
CSV_PATH = "webtoon_clean.csv"
COLLECTION_NAME = "webtoons"
BATCH_SIZE = 400  # Firestore 배치 쓰기 최대 500건 제한

cred = credentials.Certificate(CRED_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()


def upload_csv_to_firestore():
    df = pd.read_csv(CSV_PATH)
    collection_ref = db.collection(COLLECTION_NAME)

    batch = db.batch()
    count = 0

    for _, row in df.iterrows():
        doc_ref = collection_ref.document(str(row["titleId"]))
        batch.set(doc_ref, row.to_dict())
        count += 1

        if count % BATCH_SIZE == 0:
            batch.commit()
            batch = db.batch()
            print(f"{count}건 업로드됨...")

    batch.commit()
    print(f"완료: 총 {count}건 업로드됨")


def verify_top5_by_view():
    docs = (
        db.collection(COLLECTION_NAME)
        .order_by("viewCount", direction=firestore.Query.DESCENDING)
        .limit(5)
        .stream()
    )
    for doc in docs:
        data = doc.to_dict()
        print(doc.id, data.get("titleName"), data.get("viewCount"))


if __name__ == "__main__":
    upload_csv_to_firestore()
    verify_top5_by_view()
