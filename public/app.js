import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import {
  getFirestore,
  collection,
  query,
  orderBy,
  limit,
  startAfter,
  getDocs,
} from "https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore.js";
import { firebaseConfig } from "./firebase-config.js";

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

const COLLECTION_NAME = "webtoons";
const PAGE_SIZE = 100;

const tableBody = document.getElementById("tableBody");
const summary = document.getElementById("summary");
const searchInput = document.getElementById("searchInput");
const sortSelect = document.getElementById("sortSelect");
const loadMoreBtn = document.getElementById("loadMoreBtn");

let currentRows = [];
let lastDoc = null;
let hasMore = true;

async function loadData(sortField) {
  tableBody.innerHTML = `<tr><td colspan="8" class="loading">불러오는 중...</td></tr>`;
  currentRows = [];
  lastDoc = null;
  hasMore = true;

  await fetchNextPage(sortField);
}

async function fetchNextPage(sortField) {
  const col = collection(db, COLLECTION_NAME);
  const q = lastDoc
    ? query(col, orderBy(sortField, "desc"), startAfter(lastDoc), limit(PAGE_SIZE))
    : query(col, orderBy(sortField, "desc"), limit(PAGE_SIZE));

  const snapshot = await getDocs(q);

  hasMore = snapshot.docs.length === PAGE_SIZE;
  lastDoc = snapshot.docs.at(-1) ?? lastDoc;

  currentRows = currentRows.concat(snapshot.docs.map((doc) => doc.data()));

  summary.textContent = `총 ${currentRows.length}개 작품 표시 중 (기준: ${sortSelect.selectedOptions[0].text})`;
  loadMoreBtn.hidden = !hasMore;
  renderRows(currentRows);
}

function renderRows(rows) {
  if (rows.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="8" class="empty">검색 결과가 없습니다.</td></tr>`;
    return;
  }

  tableBody.innerHTML = rows
    .map(
      (row, i) => `
      <tr>
        <td>${i + 1}</td>
        <td class="title-cell">${escapeHtml(row.titleName ?? "")}</td>
        <td>${escapeHtml(row.author ?? "")}</td>
        <td>${escapeHtml(row.status ?? "")}</td>
        <td>${(row.starScore ?? 0).toFixed(2)}</td>
        <td>${(row.viewCount ?? 0).toLocaleString()}</td>
        <td>${(row.favoriteCount ?? 0).toLocaleString()}</td>
        <td>${row.year ?? ""}</td>
      </tr>`
    )
    .join("");
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

searchInput.addEventListener("input", () => {
  const keyword = searchInput.value.trim().toLowerCase();
  const filtered = keyword
    ? currentRows.filter((row) =>
        (row.titleName ?? "").toLowerCase().includes(keyword)
      )
    : currentRows;
  renderRows(filtered);
});

sortSelect.addEventListener("change", () => {
  loadData(sortSelect.value);
});

loadMoreBtn.addEventListener("click", () => {
  fetchNextPage(sortSelect.value);
});

loadData(sortSelect.value);
