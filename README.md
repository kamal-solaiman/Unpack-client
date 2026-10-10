# Unpack-client

أداة **C++** لفك تشفير واستخراج ملفات `data/root` (وحزم EterPack عموماً: `.eix` + `.epk`)
من عميل Metin2، مع **استخراج مفاتيح التشفير XTEA تلقائياً من `metin2client.exe`** —
بدون أي مكتبات خارجية، وتعمل على Windows و Linux و macOS.

```
unpack-client unpack D:\Metin2 -p root
```

```
=== root ===
[*] scanning D:/Metin2/metin2client.exe (7.41 MB) for XTEA keys...
[+] index key found  [0x02B09EB9, 0x0581696F, 0x289B9863, 0x001A1879]
[+] data  key found  [0x04B4B822, 0x1F6EB264, 0x0018EAAE, 0x1CFBF6A6]
[*] root: 4812 entries, layout classic-192, version 2

---------------- summary ----------------
root             entries=4812   extracted=4812   failed=0    skipped=0    OK
                 -> unpacked/root (146.20 MB)

keys recovered from D:/Metin2/metin2client.exe
  index: bytes: b9 9e b0 02 6f 69 81 05 63 98 9b 28 79 18 1a 00 | offset 0x5A2140 | via .rdata
  data : bytes: 22 b8 b4 04 64 b2 6e 1f ae ea 18 00 a6 f6 fb 1c | offset 0x5A2150 | via .rdata
```

---

## لماذا هذه الأداة؟

عميل Metin2 يخزّن ملفاته داخل أرشيفات `EterPack`:

| الملف | المحتوى |
|---|---|
| `data/root.eix` | الفهرس: أسماء الملفات، الأحجام، الإزاحات، نوع الضغط/التشفير — **مشفّر بـ XTEA** داخل حاوية `MCOZ`/`MCSP` |
| `data/root.epk` | البيانات نفسها، ملف تلو الآخر، وكل ملف مضغوط (LZO/Snappy) وقد يكون مشفراً بـ XTEA |

المفتاحان (مفتاح الفهرس ومفتاح المحتوى) موجودان داخل `metin2client.exe` — إما كمصفوفة
`DWORD[4]` ثابتة في قسم `.rdata`، أو كقيم فورية (`push imm32` / `mov …, imm32`) داخل الكود.
الأداة تبحث عنهما وتتأكد من صحتهما **بفك ترويسة ملف حقيقي**، أي أن النتيجة إثبات وليست تخميناً.

---

## البناء

### Windows

أسهل طريقة: شغّل `build_windows.bat` (يجرّب MSVC ثم MinGW ثم CMake).

يدوياً:

```bat
:: MSVC (من x64 Native Tools Command Prompt)
cl /nologo /EHsc /std:c++17 /O2 /Isrc /Itests /D_CRT_SECURE_NO_WARNINGS ^
   src\*.cpp tests\testsupport.cpp /Fe:unpack-client.exe

:: MinGW-w64
g++ -std=c++17 -O2 -Isrc -Itests -static -o unpack-client.exe src\*.cpp tests\testsupport.cpp
```

أو CMake:

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
```

### Linux / macOS

```bash
make            # ينتج ./unpack-client
make tools      # ينتج أيضاً ./make_fake_client (أداة الاختبارات)
```

لا توجد أي تبعيات: فك ضغط LZO1X و Snappy و XTEA و CRC32 و قارئ ملفات PE كلها مكتوبة
داخل المشروع.

---

## الاستخدام

### 1) فك حزمة `data/root`

```bash
# كل الحزم داخل مجلد العميل (data/ و pack/)
unpack-client unpack D:\Metin2

# حزمة root فقط
unpack-client unpack D:\Metin2 -p root

# ملف eix مباشرة + مجلد إخراج محدد
unpack-client unpack D:\Metin2\data\root.eix -o D:\out\root

# عرض الملفات بدون استخراج
unpack-client unpack D:\Metin2\data\root.eix --list
```

الأداة تبحث تلقائياً عن `metin2client.exe` في مجلد العميل، تستخرج المفتاحين، تفك الفهرس،
ثم تستخرج كل ملف إلى مساره الافتراضي (`d:/ymir art/...` تُحفظ كـ `ymir art/...`).

### 2) استخراج المفاتيح فقط

```bash
unpack-client keys metin2client.exe --eix data/root.eix --epk data/root.epk
unpack-client keys metin2client.exe --eix data/root.eix --json
unpack-client keys metin2client.exe --eix data/root.eix --deep   # فحص شامل أبطأ
```

المخرجات: المفتاح كـ 16 بايت (hex) وكأربعة `DWORD`، مع عنوانه داخل الملف وطريقة إيجاده،
وإن كان المفتاح الافتراضي الرسمي موجوداً داخل الـ exe أيضاً.

### 3) معلومات عن الفهرس

```bash
unpack-client info data/root.eix --exe metin2client.exe
```

يعرض: نوع الحاوية، هل هي مشفرة، عدد الملفات، توزيع الأنواع (0/1/2/6)، المجلدات،
وأول الملفات.

### 4) مفاتيح يدوية

```bash
unpack-client unpack data/root.eix --no-auto-keys ^
  --index-key "b9 9e b0 02 6f 69 81 05 63 98 9b 28 79 18 1a 00" ^
  --data-key  "22 b8 b4 04 64 b2 6e 1f ae ea 18 00 a6 f6 fb 1c"

# أو كأربعة أرقام
unpack-client unpack data/root.eix --index-key "[45129401, 92367215, 681285731, 1710201]"
```

### كل الخيارات

| الخيار | الوصف |
|---|---|
| `-o, --out DIR` | مجلد الإخراج (الافتراضي `./unpacked/<اسم الحزمة>`) |
| `-e, --exe FILE` | ملف التنفيذ الذي تُستخرج منه المفاتيح |
| `-p, --pack NAME` | حزمة محددة (يمكن تكرارها): `root`, `locale_europe`, ... |
| `--index-key K` | مفتاح الفهرس (16 بايت hex أو 4 DWORDs) |
| `--data-key K` | مفتاح محتوى الـ epk |
| `--eix FILE` / `--epk FILE` | ملفات تُستخدم للتحقق من المفاتيح (مع أمر `keys`) |
| `--no-auto-keys` | عدم فحص الـ exe، استخدام المفاتيح المعطاة فقط |
| `--strict-types` | الثقة في بايت النوع بدل الاكتشاف التلقائي |
| `--deep` | فحص شامل: كل إزاحة بايت + كل ترتيبات القيم الفورية (أبطأ ~5x) |
| `--list` | عرض القائمة فقط دون كتابة ملفات |
| `--json` | تقرير JSON (مناسب للسكربتات) |
| `--no-crc` | تجاهل تحقق CRC32 |
| `-v, --verbose` / `--debug` / `-q, --quiet` | مستوى الرسائل |
| `test` | تشغيل الاختبارات الذاتية المدمجة |

---

## ماذا تدعم الأداة

| نوع الملف داخل الـ epk | المعنى | الدعم |
|---|---|---|
| `0` | خام بدون ضغط أو تشفير | ✅ |
| `1` | LZO داخل حاوية `MCOZ` | ✅ |
| `2` | XTEA(LZO) — `MCOZ` مشفّر | ✅ (وهو الأكثر شيوعاً في `data/root`) |
| `6` | XTEA(Snappy) — `MCSP` مشفّر | ✅ |
| `3` | Panama | ❌ يحتاج مفتاح من السيرفر (`.iv`) |
| `4` / `5` | HybridCrypt | ❌ يحتاج ملف مفتاح من السيرفر |

كما تدعم الأداة:

* فهرس `EPKD` غير مشفّر، أو `MCOZ`/`MCSP` غير مشفّر (مضغوط فقط).
* سيرفرات تشفّر ملف `.eix` بالكامل بـ XTEA (بدون حاوية) — تُكتشف وتُفكّ تلقائياً.
* CRC غير مطابق أو قديم: يُعتمد الناتج الصحيح بالحجم مع تحذير بدل فشل الملف.
* **الاكتشاف التلقائي**: إذا كان بايت النوع في الفهرس خاطئاً أو غير مدعوم، تجرّب الأداة كل
  الحاويات والمفاتيح الممكنة وتعتمد النتيجة التي يتطابق حجمها و CRC32 الخاص بها.
* **تخطيطات فهرس مختلفة**: `192` بايت (الرسمي)، `200` (إزاحة 64-bit)، وأسماء 256 بايت،
  وتُختار تلقائياً حسب بيانات الفهرس.
* ملفات `.epk` ضخمة (تُقرأ بـ memory mapping، لا تُحمَّل في الذاكرة).

---

## كيف يعمل استخراج المفاتيح

1. **قراءة PE**: تحليل ترويسة `MZ/PE` وأقسامها (`.text`, `.rdata`, `.data`) — بدون Windows API.
2. **توليد المرشّحات** بالترتيب:
   1. المفاتيح الرسمية المعروفة (index / content / item_proto / mob_proto).
   2. كل 4 `DWORD` متتالية بمحاذاة 4 بايت داخل أقسام البيانات (`.rdata` أولاً).
   3. سلاسل ASCII بطول 16/32 (بعض السيرفرات تضع المفتاح كنص hex).
   4. القيم الفورية في الكود: `push imm32`, `mov r32, imm32`, `mov [mem], imm32` —
      كل 4 قيم متتالية داخل نافذة 96 بايت تُعتبر مرشّحاً.
   5. كل 4 `DWORD` متتالية داخل `.text`.
   6. `--deep`: كل إزاحة بايت في الملف + كل ترتيبات (permutations) القيم الفورية.
3. **التحقق** (وليس التخمين): لكل مرشّح يُفكّ بلوك XTEA واحد (8 بايت) من ترويسة الـ `.eix`
   ويقارن الناتج بـ `MCOZ`/`MCSP`. احتمال الخطأ ≈ 1 من 4 مليار.
4. **التأكيد**: بعد نجاح الفهرس، يُفكّ الملف بالكامل ويُتحقق من `EPKD` + الإصدار + عدد
   الملفات. ولمفتاح المحتوى يُفكّ ملف حقيقي من الـ `.epk` ويُقارن الحجم و **CRC32** —
   وأحياناً بملفين مختلفين.
5. إذا فشل كل شيء (مثلاً الـ exe محمي بـ Themida/VMProtect أو المفاتيح تُفكّ وقت التشغيل)،
   تعرض الأداة قائمة مرشّحين مرتّبة حسب الاحتمالية مع عناوينها لتجربتها يدوياً.

الأداء المرجعي (exe بحجم 5 MB + حزمة 38 MB فيها 2000 ملف): استخراج المفاتيح ≈ 1.3 ثانية،
الفك الكامل ≈ 1.8 ثانية، والفحص الشامل `--deep` ≈ 7 ثوانٍ.

---

## الاختبارات

```bash
./unpack-client test --verbose    # 467 فحصاً: XTEA، LZO1X، Snappy، الحاويات، الفهرس، PE، المفاتيح
make integration                  # يبني عميلاً صناعياً كاملاً ثم يفكّه ويقارن الملفات بـ diff
```

`tests/README.md` يشرح كيف تُعاد توليد بيانات الاختبار المرجعية.

---

## بنية المشروع

```
src/
  main.cpp            سطر الأوامر
  unpacker.cpp        اكتشاف مجلد العميل + فك الحزم + التقارير (JSON/نص)
  key_finder.cpp      استخراج والتحقق من مفاتيح XTEA من الـ exe
  pe.cpp              قارئ PE (الأقسام والخصائص)
  eterpack.cpp        فهرس EPKD + تخطيطات المدخلات + استخراج الملفات
  crypted_object.cpp  حاوية MCOZ/MCSP (ترويسة 16 بايت + تحقق + فك)
  xtea.cpp            XTEA (32 جولة، delta 0x9E3779B9)
  lzo.cpp             فك LZO1X (+ ترميز "stored" للاختبارات)
  snappy.cpp          فك Snappy الخام والمؤطَّر
  crc32.cpp           CRC32 بكل صيغه للتحقق
  selftest.cpp        الاختبارات الذاتية المدمجة
tests/                دعم الاختبارات + سكربت التكامل + مولّد البيانات المرجعية
tools/                make_fake_client: يبني عميلاً صناعياً للاختبار الشامل
docs/format.md        تفاصيل الصيغ التي تعالجها الأداة
```

---

## تشخيص الأعطال

| الرسالة | السبب | الحل |
|---|---|---|
| `no metin2client.exe found` | الأداة تبحث في مجلد الإدخال والمجلد الأب فقط | `--exe "D:\Metin2\metin2client.exe"` |
| `wrong XTEA key` / `no key could be verified` | المفاتيح ليست قيماً ثابتة داخل الـ exe (حماية Themida/VMProtect، أو تُشتق وقت التشغيل) | جرّب `--deep`، ثم قائمة المرشّحين المرتّبة، أو مرّر المفاتيح يدوياً |
| `unknown magic ... (first bytes: ...)` | صيغة فهرس غير معتادة أو ملف تالف | شغّل `unpack-client info root.eix --exe ...` وأرسل المخرجات |
| `unsupported pack type 3/4/5` | Panama أو HybridCrypt | يحتاج ملف المفتاح من جهة السيرفر (`panama/*.iv` أو `package/*.dat`) |
| `CRC mismatch` (تحذير) | الفهرس يحتوي CRC قديم/مختلف | لا شيء — الملف يُستخرج ويُعتمد بحجمه الصحيح |
| `the .epk looks truncated` | التحميل ناقص | أعد تحميل ملف الـ `.epk` |

للتشخيص الكامل:

```bash
unpack-client info  data/root.eix --exe metin2client.exe --json
unpack-client keys  metin2client.exe --eix data/root.eix --epk data/root.epk --deep --json
unpack-client unpack data/root.eix --list -v
```

---

## ملاحظات وحدود

* الأداة **للقراءة فقط**: لا تعدّل ملفات العميل ولا تعيد التغليف (repack).
* الأنواع `3/4/5` (Panama / HybridCrypt) تحتاج مواد مفتاح من جهة السيرفر ولا يمكن استخراجها
  من الـ exe وحده؛ تُسجَّل كـ `skipped` في التقرير.
* إذا كان الـ exe مضغوطاً/محمياً (packer/protector) فلن توجد المفاتيح كنص ثابت — جرّب
  `--deep`، أو استخرج المفاتيح من نسخة غير محمية، أو مرّرها يدوياً بـ `--index-key/--data-key`.
* بعض السيرفرات تستخدم امتدادات أو أسماء مختلفة (`pack/` بدل `data/`) — الأداة تبحث في
  المجلد حتى عمق 3 عن أي `*.eix`.
* الاستخدام على مسؤوليتك: فك ملفات عميل تملكه أو تملك إذن التعديل عليه.

---

## English summary

`unpack-client` is a dependency-free C++17 tool that decrypts and extracts Metin2
`EterPack` archives (`.eix` + `.epk`, e.g. `data/root`). It recovers the XTEA index and
content keys directly from `metin2client.exe` by enumerating candidate dword quadruples
(static arrays in `.rdata`, code immediates, ASCII strings) and **verifying** them against
the real index header and against a real entry (size + CRC32), so a reported key is a proof,
not a guess. Supported entry types: 0 (raw), 1 (LZO), 2 (XTEA+LZO), 6 (XTEA+Snappy), plus
automatic type/layout detection, memory-mapped multi-GB `.epk` files, `--list`, `--json` and
a built-in test suite (`unpack-client test`).

## License

MIT — see the SPDX header of every source file.
