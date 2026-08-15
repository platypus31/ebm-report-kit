#!/usr/bin/env bash
# ebm-report-kit bootstrap — 一鍵安裝依賴並自我驗證（冪等，可重複執行）
#
# 用法：
#   bash bootstrap.sh              # 安裝缺的東西 + self-check
#   bash bootstrap.sh --check-only # 只檢查不安裝
#
# 裝完後：claude 進到本目錄，打 /ebm-from-paper <PMID> 開始使用。
set -u

CHECK_ONLY=0
[ "${1:-}" = "--check-only" ] && CHECK_ONLY=1

KIT_DIR="$(cd "$(dirname "$0")" && pwd)"
PPT_MASTER="${PPT_MASTER_DIR:-${HOME}/ppt-master}"
VENV_PY="${KIT_DIR}/.venv/bin/python"
VENV_PIP="${KIT_DIR}/.venv/bin/pip"
PASS=0; FAIL=0; SKIP=0
REQMISS=0  # 必裝依賴缺失——--check-only 時不算 FAIL 但不得宣告就緒

say()  { printf '%s\n' "$*"; }
ok()   { PASS=$((PASS+1)); say "  ✅ $*"; }
bad()  { FAIL=$((FAIL+1)); say "  ❌ $*"; }
note() { SKIP=$((SKIP+1)); say "  ⚠️  $*"; }

say "== ebm-report-kit bootstrap =="
say ""
say "[1/5] 基本工具"
if command -v git >/dev/null 2>&1; then ok "git $(git --version | cut -d' ' -f3)"; else bad "缺 git — 請先安裝"; fi
if command -v python3 >/dev/null 2>&1; then
  PYV="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
  if python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)'; then
    ok "python3 ${PYV}"
  else
    bad "python3 ${PYV} 過舊 — 需 3.9+"
  fi
else
  bad "缺 python3 — 需 3.9+"
fi
if command -v node >/dev/null 2>&1; then
  ok "node $(node --version)"
else
  bad "缺 node — 檢索截圖（pubmed_shot/cochrane_search）與圖卡生成需要，請先安裝 Node.js"
fi

say ""
say "[2/5] Python 依賴（kit venv：.venv/）"
if [ "${CHECK_ONLY}" = "1" ]; then
  if [ -x "${VENV_PY}" ] && "${VENV_PY}" -c 'import fitz, pptx, yaml, pytest' 2>/dev/null; then
    ok ".venv 已就緒（pymupdf/python-pptx/pyyaml/pytest 皆可 import）"
  else
    note ".venv 未就緒（去掉 --check-only 重跑即可安裝）"
    REQMISS=1
  fi
else
  if [ ! -x "${VENV_PY}" ]; then
    if python3 -m venv "${KIT_DIR}/.venv"; then ok "建立 .venv"; else bad "建立 .venv 失敗"; fi
  else
    ok ".venv 已存在"
  fi
  if [ -x "${VENV_PIP}" ]; then
    if "${VENV_PIP}" install -q --disable-pip-version-check pymupdf python-pptx pyyaml pytest; then
      ok "pymupdf / python-pptx / pyyaml / pytest 就緒"
    else
      bad "pip install 失敗（看上面錯誤訊息）"
    fi
  fi
fi

say ""
say "[3/5] Node 依賴（Playwright，檢索截圖與圖卡用）"
# chromium 是否真的下載好（只看 node_modules 會漏掉沒跑 playwright install 的情況）
has_chromium() {
  [ -d "${KIT_DIR}/node_modules/playwright" ] || return 1
  (cd "${KIT_DIR}" && node -e \
    'require("fs").accessSync(require("playwright").chromium.executablePath())' 2>/dev/null)
}
if [ "${CHECK_ONLY}" = "1" ]; then
  if has_chromium; then
    ok "node_modules 與 chromium 皆已就緒"
  elif [ -d "${KIT_DIR}/node_modules/playwright" ]; then
    note "node_modules 已裝，但 chromium 尚未下載（去掉 --check-only 重跑，或 npx playwright install chromium）"
    REQMISS=1
  else
    note "尚未 npm install（去掉 --check-only 重跑即可安裝）"
    REQMISS=1
  fi
elif command -v npm >/dev/null 2>&1; then
  if (cd "${KIT_DIR}" && npm install --silent); then
    ok "npm install 完成"
    PW_LOG="$(mktemp)"
    if (cd "${KIT_DIR}" && npx playwright install chromium >"${PW_LOG}" 2>&1) && has_chromium; then
      ok "Playwright chromium 就緒"
    else
      bad "chromium 安裝失敗或找不到執行檔（網路？磁碟空間？）"
      tail -5 "${PW_LOG}" 2>/dev/null | sed 's/^/     /'
    fi
    rm -f "${PW_LOG}"
  else
    bad "npm install 失敗（看上面錯誤訊息）"
  fi
else
  bad "缺 npm — 隨 Node.js 一起安裝"
fi

say ""
say "[4/5] ppt-master 匯出引擎（${PPT_MASTER}）"
if [ -d "${PPT_MASTER}/.git" ]; then
  ok "ppt-master 已存在"
else
  if [ "${CHECK_ONLY}" = "1" ]; then
    note "ppt-master 未安裝（去掉 --check-only 重跑即可自動 clone，約 1.2GB）"
    REQMISS=1
  else
    say "  ⏳ clone ppt-master（資產庫約 1.2GB，--depth 1，需數分鐘）..."
    if git clone --depth 1 https://github.com/hugohe3/ppt-master.git "${PPT_MASTER}"; then
      ok "ppt-master clone 完成"
    else
      bad "ppt-master clone 失敗（網路或磁碟空間？）"
    fi
  fi
fi
if [ -d "${PPT_MASTER}" ] && [ "${CHECK_ONLY}" != "1" ]; then
  # 只看 .venv/bin/python 存在不夠：前次 pip 中途失敗會留下「venv 在但依賴缺」的半成品
  [ -x "${PPT_MASTER}/.venv/bin/python" ] || python3 -m venv "${PPT_MASTER}/.venv"
  if [ -x "${PPT_MASTER}/.venv/bin/pip" ] && \
     "${PPT_MASTER}/.venv/bin/pip" install -q --disable-pip-version-check -r "${PPT_MASTER}/requirements.txt"; then
    ok "ppt-master venv 就緒"
  else
    bad "ppt-master venv 安裝失敗"
  fi
fi

say ""
say "[5/5] Self-check"
# 用 kit venv 的 python 跑（測試需要 pyyaml）；沒有就退回系統 python3
SELFCHECK_PY="python3"
[ -x "${VENV_PY}" ] && SELFCHECK_PY="${VENV_PY}"

PYTEST_LOG="$(mktemp)"
if (cd "${KIT_DIR}" && "${SELFCHECK_PY}" -m pytest tests/ -q >"${PYTEST_LOG}" 2>&1); then
  ok "單元測試通過（$(grep -o '[0-9]* passed' "${PYTEST_LOG}" | tail -1)）"
else
  bad "單元測試失敗 — 詳情：${SELFCHECK_PY} -m pytest tests/ -q"
  tail -5 "${PYTEST_LOG}" 2>/dev/null | sed 's/^/     /'
fi
rm -f "${PYTEST_LOG}"

# 範例專案實跑簡報引擎：張數應等於 content.json 的 slides 數 + 1 張封面
EXAMPLE_JSON="${KIT_DIR}/projects/example-pcv13-covid19/06_slides/content.json"
SELFCHECK_OUT="$(mktemp -d 2>/dev/null || echo /tmp/ebm-bootstrap-$$)"
EXPECT_N="$("${SELFCHECK_PY}" -c "import json,sys; print(len(json.load(open(sys.argv[1]))['slides'])+1)" "${EXAMPLE_JSON}" 2>/dev/null || echo 0)"
if "${SELFCHECK_PY}" "${KIT_DIR}/scripts/gen_journal_svg.py" "${EXAMPLE_JSON}" "${SELFCHECK_OUT}" >/dev/null 2>&1; then
  N="$(ls "${SELFCHECK_OUT}" 2>/dev/null | grep -c '\.svg$')"
  if [ "${N}" -eq "${EXPECT_N}" ] && [ "${N}" -gt 0 ]; then
    ok "簡報引擎正常（範例生成 ${N} 張，與 content.json 相符）"
  elif [ "${N}" -gt 0 ]; then
    bad "簡報引擎張數異常（生成 ${N} 張，預期 ${EXPECT_N} 張）"
  else
    bad "簡報引擎跑完但無產出"
  fi
else
  bad "簡報引擎 self-check 失敗：${SELFCHECK_PY} scripts/gen_journal_svg.py ${EXAMPLE_JSON} <outdir>"
fi
rm -rf "${SELFCHECK_OUT}"

say ""
say "== 結果：✅ ${PASS} ｜ ❌ ${FAIL} ｜ ⚠️ ${SKIP} =="
if [ "${FAIL}" -eq 0 ] && [ "${REQMISS}" -eq 0 ]; then
  say "🎉 就緒。下一步：在本目錄啟動你的 AI CLI（如 claude），輸入："
  say "     /ebm-from-paper 33693636      # 已選好文獻 → 反推整份報告（最常用）"
  say "     /ebm                          # 從臨床問題出發，互動式走完整 6A"
  exit 0
elif [ "${FAIL}" -eq 0 ] && [ "${REQMISS}" -eq 1 ]; then
  say "⚠️  尚未就緒：必裝依賴未備妥（詳見上方 ⚠️ 訊息）—— 跑到簡報匯出會失敗。"
  say "   跑 \`bash bootstrap.sh\`（不加 --check-only）即可自動裝好。"
  exit 1
else
  say "還有 ❌ 項目要處理（見上），修完重跑本腳本即可（冪等）。"
  exit 1
fi
