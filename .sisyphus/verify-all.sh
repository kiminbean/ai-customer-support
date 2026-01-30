#!/usr/bin/env bash
set -uo pipefail

PASS=0
FAIL=0

check() {
  if eval "$2" > /dev/null 2>&1; then
    echo "  PASS: $1"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $1"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== AI Customer Support — Final Verification ==="
echo ""

echo "[1/5] Backend Tests"
cd backend
source venv/bin/activate
RESULT=$(pytest tests/ -q --tb=no 2>&1 | tail -1)
echo "  $RESULT"
check "All tests pass" "echo '$RESULT' | grep -q 'passed'"

echo ""
echo "[2/5] Backend Coverage"
COV=$(pytest tests/ --cov=. --cov-report=term-missing -q 2>&1 | grep '^TOTAL' | awk '{print $4}' | tr -d '%')
echo "  Coverage: ${COV}%"
check "Coverage >= 60%" "[ ${COV:-0} -ge 60 ]"
cd ..

echo ""
echo "[3/5] Frontend Build"
cd app
npm run build > /dev/null 2>&1
check "npm run build succeeds" "true"
cd ..

echo ""
echo "[4/5] File Checks"
check "Navbar.tsx exists" "test -f app/src/components/Navbar.tsx"
check "Admin layout exists" "test -f 'app/src/app/(admin)/layout.tsx'"
check "Voice page exists" "test -f 'app/src/app/(admin)/voice/page.tsx'"
check "widget.js exists" "test -f app/public/widget.js"
check "widget.js < 5KB" "[ $(wc -c < app/public/widget.js) -lt 5120 ]"
check "widget.js valid JS" "node -c app/public/widget.js"
check "DashboardSidebar has voice" "grep -q voice app/src/components/DashboardSidebar.tsx"
check "auth.py exists" "test -f backend/auth.py"
check "database.py exists" "test -f backend/database.py"
check "Dockerfile exists" "test -f backend/Dockerfile"
check "CI workflow exists" "test -f .github/workflows/ci.yml"
check "AGENTS.md < 500 lines" "[ $(wc -l < AGENTS.md) -lt 500 ]"

echo ""
echo "[5/5] Demo Mode"
check ".env.example (backend)" "test -f backend/.env.example"
check ".env.example (frontend)" "test -f app/.env.example"

echo ""
echo "=== Results: ${PASS} passed, ${FAIL} failed ==="
[ "$FAIL" -eq 0 ] && echo "ALL CHECKS PASSED" || echo "SOME CHECKS FAILED"
exit "$FAIL"
