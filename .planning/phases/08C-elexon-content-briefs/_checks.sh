#!/bin/bash
# Usage: bash _checks.sh <slug>
# Runs all 12 structural checks; prints PASS/FAIL per check + summary.

SLUG="$1"
FILE="content-briefs/elexon/${SLUG}.md"
VAULT="vault/elexon/${SLUG}.md"
FAILS=0

check() { local name="$1"; local result="$2"; if [ "$result" = "PASS" ]; then echo "  PASS: $name"; else echo "  FAIL: $name"; FAILS=$((FAILS+1)); fi; }

[ -f "$FILE" ] && check "1. file exists" "PASS" || check "1. file exists" "FAIL"

python -c "import yaml; yaml.safe_load(open('${FILE}').read().split('---')[1])" 2>/dev/null && check "2. frontmatter parses" "PASS" || check "2. frontmatter parses" "FAIL"

for key in slug vendor api_code last_verified sources_consulted discrepancies_found ready_for_claude_design checked_at; do
  grep -q "^${key}:" "$FILE" && check "3.${key}" "PASS" || check "3.${key}" "FAIL"
done

sources_count=$(awk '/^sources_consulted:/{flag=1; next} /^[a-z_]+:/{flag=0} flag' "$FILE" | grep -c "^  -")
[ "$sources_count" -ge 3 ] && check "4. sources >= 3 (n=${sources_count})" "PASS" || check "4. sources >= 3 (n=${sources_count})" "FAIL"

for section in "# Editorial layer" "# Hero metadata" "# Stats strip" "# Sidebar siblings" "# Overview" "# Sample chart" "# Schema" "# Sample data" "# API & ingestion" "# Caveats" "# Related datasets"; do
  grep -qF "$section" "$FILE" && check "5.${section}" "PASS" || check "5.${section}" "FAIL"
done

schema_rows=$(awk '/^# Schema/{flag=1; next} /^# /{flag=0} flag && /^\|/' "$FILE" | grep -v '^|--' | grep -v '^| Column' | wc -l)
[ "$schema_rows" -ge 3 ] && check "6. schema rows >= 3 (n=${schema_rows})" "PASS" || check "6. schema rows >= 3 (n=${schema_rows})" "FAIL"

caveat_count=$(grep -cE '^## 0[1-9]' "$FILE")
[ "$caveat_count" -ge 3 ] && check "7. caveats >= 3 (n=${caveat_count})" "PASS" || check "7. caveats >= 3 (n=${caveat_count})" "FAIL"

related_count=$(awk '/^# Related datasets/{flag=1; next} /^# /{flag=0} flag' "$FILE" | grep -cE '^- \*\*')
[ "$related_count" -ge 3 ] && check "8. related >= 3 (n=${related_count})" "PASS" || check "8. related >= 3 (n=${related_count})" "FAIL"

code_count=$(grep -cE '<code|`[a-z_]' "$FILE")
[ "$code_count" -ge 5 ] && check "9. inline code >= 5 (n=${code_count})" "PASS" || check "9. inline code >= 5 (n=${code_count})" "FAIL"

grep -q '^ready_for_claude_design: true' "$FILE" && check "10. ready flag true" "PASS" || check "10. ready flag true" "FAIL"

VAULT_LV=$(grep -E '^last_verified:' "$VAULT" | awk '{print $2}')
BRIEF_LV=$(grep -E '^last_verified:' "$FILE" | head -1 | awk '{print $2}')
[ "$VAULT_LV" = "$BRIEF_LV" ] && check "11. last_verified vault=${VAULT_LV} brief=${BRIEF_LV}" "PASS" || check "11. last_verified vault=${VAULT_LV} brief=${BRIEF_LV}" "FAIL"

grep -qE '^discrepancies_found:\s*(\[\]|$)' "$FILE" && check "12. discrepancies_found format" "PASS" || check "12. discrepancies_found format" "FAIL"

if [ "$FAILS" -eq 0 ]; then
  echo ""
  echo "ALL 12 CHECKS PASS for ${SLUG}"
  exit 0
else
  echo ""
  echo "FAILED ${FAILS} checks for ${SLUG}"
  exit 1
fi
