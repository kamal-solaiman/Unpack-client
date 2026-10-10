# الاختبارات

## 1) الاختبارات الذاتية المدمجة

```bash
./unpack-client test            # ملخص
./unpack-client test --verbose  # يعرض كل قسم ورسائل الأخطاء
```

تشمل 437 فحصاً:

| القسم | ما يتحقق منه |
|---|---|
| `crc32 / xtea` | قيمة CRC32 القياسية، تطابق كل صيغ CRC، دوران تشفير/فك XTEA، تحليل المفاتيح من hex ومن DWORDs |
| `lzo1x` | فك 4 تدفقات مرجعية أنتجها ضاغط LZO الحقيقي، وفك تدفقات `lzo1xStore`، ورفض المدخلات التالفة |
| `snappy` | فك 4 تدفقات مرجعية من Snappy الحقيقي + ترميز "stored" |
| `crypted object` | بناء/فك `MCOZ` و `MCSP` بمفتاح صحيح وخاطئ، والحالة غير المشفرة |
| `path sanitizer` | إزالة `d:/`، ومنع `../`، واستبدال المحارف الممنوعة |
| `pe parser` | قراءة صورة PE صناعية: الأقسام والخصائص و image base |
| `pack round trip` | بناء حزمة كاملة (أنواع 0/1/2/6) وفكّها، مع فهرس `MCOZ`/`MCSP`/غير مشفر |
| `index layout detection` | كل التخطيطات المدعومة (192/200/288/296/96) |
| `unsupported types` | الأنواع 3/4/5 تُرفض في الوضع الصارم وتُسترجع بالاكتشاف التلقائي |
| `key finder` | إيجاد المفتاحين في `.rdata`، وكقيم فورية في الكود، والمفاتيح الرسمية، وحالة الفشل (بدون مفتاح) |

## 2) اختبار التكامل (end to end)

```bash
make integration
```

يبني `tools/make_fake_client` عميلاً صناعياً كاملاً على القرص:

```
fake_client/
  metin2client.exe      صورة PE صناعية تحتوي المفتاحين
  data/root.eix         فهرس مشفر (MCOZ + XTEA)
  data/root.epk         ملفات بأنواع 0 و 1 و 2 و 6
  _expected/...         نفس الملفات بصيحتها الأصلية للمقارنة
  keys.txt              المفاتيح المستخدمة
```

ثم يقوم السكربت بـ:

1. استخراج المفتاحين والتحقق من تطابقهما مع `keys.txt`.
2. فك `data/root` والتأكد من `failed=0`.
3. `diff -r` بين `_expected/` والمخرجات (مقارنة بايت ببايت).
4. إعادة الفك بمفاتيح يدوية مع `--no-auto-keys`.
5. تكرار كل ذلك مع أربعة أشكال مختلفة: المفاتيح مخفية في الكود، فهرس `MCSP`، فهرس غير
   مشفر، وتخطيط `wide-offset-200`.

خيارات المولّد:

```bash
./make_fake_client OUT [--files N] [--seed N] [--layout classic|wide|name256]
                     [--index-magic MCOZ|MCSP|plain] [--no-encrypt-index]
                     [--keys-in-code] [--text-kb N] [--rdata-kb N]
```

`--text-kb/--rdata-kb` تكبّر صورة الـ exe لقياس زمن الفحص على أحجام واقعية.

## 3) إعادة توليد `src/testdata.h`

الملف `src/testdata.h` يحتوي تدفقات LZO و Snappy **حقيقية** (أنتجتها مكتبات مرجعية) مع
نسخها الأصلية، ويُستخدم للتحقق من صحة فك الضغط في `lzo.cpp` و `snappy.cpp`.

لتوليد من جديد تحتاج أداتين خارجيتين (لا تُستخدمان في وقت التشغيل ولا تُشحن مع الأداة):

```bash
# 1) مرجع LZO (minilzo من مرآة LZO)
git clone --depth 1 https://github.com/nemequ/lzo /tmp/lzo
mkdir -p /tmp/oracle/include/lzo
cp /tmp/lzo/minilzo/minilzo.c /tmp/lzo/minilzo/minilzo.h /tmp/oracle/
cp /tmp/lzo/include/lzo/{lzoconf.h,lzodefs.h} /tmp/oracle/
cp /tmp/lzo/include/lzo/lzo1x.h /tmp/oracle/include/lzo/
cat > /tmp/oracle/lzo_oracle.c <<'EOF'
#include <stdio.h>
#include <stdlib.h>
#include "minilzo.h"
int main(int argc, char **argv) {
    static char wrk[LZO1X_1_MEM_COMPRESS];
    lzo_init();
    FILE *f = fopen(argv[2], "rb"); fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *in = malloc(n + 16); fread(in, 1, n, f); fclose(f);
    size_t cap = n + n / 16 + 4096; unsigned char *out = malloc(cap); lzo_uint outlen = cap;
    if (argv[1][0] == 'c') { if (lzo1x_1_compress(in, n, out, &outlen, wrk)) return 1; }
    else { lzo_uint dl = cap; if (lzo1x_decompress_safe(in, n, out, &dl, NULL)) return 1; outlen = dl; }
    f = fopen(argv[3], "wb"); fwrite(out, 1, outlen, f); fclose(f);
    return 0;
}
EOF
gcc -O2 -I/tmp/oracle -I/tmp/oracle/include -o /tmp/oracle/lzo_oracle \
    /tmp/oracle/lzo_oracle.c /tmp/oracle/minilzo.c

# 2) مرجع Snappy
python3 -m venv /tmp/venv && /tmp/venv/bin/pip install cramjam

# 3) التوليد
/tmp/venv/bin/python tests/gen_testdata.py /tmp/oracle/lzo_oracle > src/testdata.h
make test
```

الأداة تُبنى وتُختبر بدون هذه الخطوات: `src/testdata.h` موجود في المستودع.

> ملاحظة ترخيص: minilzo/LZO برخصة GPL وcramjam برخصة Apache-2، وتُستخدمان **فقط** لتوليد
> بيانات الاختبار؛ لا يُترجَم أي جزء منهما داخل `unpack-client` ولا يُشحن معه.
