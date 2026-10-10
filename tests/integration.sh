#!/bin/sh
# End to end test: build a synthetic client, unpack it, compare byte by byte.
set -e

BIN=${BIN:-./unpack-client}
TOOL=${TOOL:-./make_fake_client}
WORK=${WORK:-/tmp/unpack-client-it}

rm -rf "$WORK"
mkdir -p "$WORK"

fail() {
    echo "INTEGRATION FAIL: $1" >&2
    exit 1
}

echo "== 1/5 building a synthetic client (keys in .rdata)"
"$TOOL" "$WORK/client" --files 32 --seed 4242 >"$WORK/gen.log" 2>&1 || fail "generator"
grep -q "index key" "$WORK/gen.log" || fail "generator output"
INDEX_KEY=$(sed -n 's/^  index key        : //p' "$WORK/gen.log")
DATA_KEY=$(sed -n 's/^  data  key        : //p' "$WORK/gen.log")
[ -n "$INDEX_KEY" ] && [ -n "$DATA_KEY" ] || fail "keys not reported"

echo "== 2/5 recovering the keys from metin2client.exe"
"$BIN" keys "$WORK/client/metin2client.exe" \
    --eix "$WORK/client/data/root.eix" \
    --epk "$WORK/client/data/root.epk" >"$WORK/keys.log" 2>&1 || fail "keys command"
grep -q "VERIFIED" "$WORK/keys.log" || { cat "$WORK/keys.log"; fail "nothing verified"; }
grep -q "bytes  : $INDEX_KEY" "$WORK/keys.log" || { cat "$WORK/keys.log"; fail "index key not recovered"; }
grep -q "bytes  : $DATA_KEY" "$WORK/keys.log" || { cat "$WORK/keys.log"; fail "data key not recovered"; }

echo "== 3/5 unpacking data/root"
"$BIN" unpack "$WORK/client" -p root -o "$WORK/out" >"$WORK/unpack.log" 2>&1 ||
    { cat "$WORK/unpack.log"; fail "unpack"; }
grep -q "failed=0" "$WORK/unpack.log" || { cat "$WORK/unpack.log"; fail "some entries failed"; }

echo "== 4/5 comparing every extracted file with the plain originals"
diff -r "$WORK/client/_expected" "$WORK/out" >/dev/null || fail "extracted files differ"
COUNT=$(find "$WORK/out" -type f | wc -l | tr -d ' ')
[ "$COUNT" = "32" ] || fail "expected 32 files, got $COUNT"

echo "== 5/5 unpacking with manually supplied keys (no executable scan)"
"$BIN" unpack "$WORK/client/data/root.eix" -o "$WORK/out2" \
    --no-auto-keys --index-key "$INDEX_KEY" --data-key "$DATA_KEY" >"$WORK/manual.log" 2>&1 ||
    { cat "$WORK/manual.log"; fail "manual keys unpack"; }
diff -r "$WORK/client/_expected" "$WORK/out2" >/dev/null || fail "manual-key output differs"

# A few extra shapes: keys hidden in code, MCSP index, plain index, wide layout.
for variant in "--keys-in-code" "--index-magic MCSP" "--index-magic plain --no-encrypt-index" "--layout wide"; do
    echo "== variant: $variant"
    rm -rf "$WORK/v"
    # shellcheck disable=SC2086
    "$TOOL" "$WORK/v" --files 8 --seed 99 $variant >/dev/null || fail "generator ($variant)"
    "$BIN" unpack "$WORK/v" -p root -o "$WORK/v_out" >/dev/null 2>&1 || fail "unpack ($variant)"
    diff -r "$WORK/v/_expected" "$WORK/v_out" >/dev/null || fail "diff ($variant)"
done

echo "INTEGRATION OK"
