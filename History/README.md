# فك حزمة History — `workplace.d2`

أداة Python تفك حزمة `History/pack/workplace.d2` **دون تشغيل** `History2.exe` أو ملفات Python المستخرجة، ودون تعديل المدخلات. النتائج تخص نسخة العميل والحزمة المرفقتين؛ ليست دعمًا عامًا لكل ملفات `.d2`.

## التثبيت والتشغيل

Python 3.10+، من جذر المستودع:

```bash
# Linux / macOS
python3 -m venv .venv
.venv/bin/python -m pip install -r History/requirements.txt
.venv/bin/python History/unpack.py key
.venv/bin/python History/unpack.py list
.venv/bin/python History/unpack.py verify
.venv/bin/python History/unpack.py extract
```

```powershell
# Windows PowerShell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r History/requirements.txt
.venv\Scripts\python.exe History/unpack.py key
.venv\Scripts\python.exe History/unpack.py verify
.venv\Scripts\python.exe History/unpack.py extract
```

الحزمة الافتراضية هي `History/pack/workplace.d2`؛ النتيجة الافتراضية `History/unpacked/workplace/` (مستبعدة من Git). يمكن تمرير مسار حزمة مختلف وتحديد مجلد إخراج جديد، مثل:

```bash
.venv/bin/python History/unpack.py extract History/pack/workplace.d2 -o History/unpacked/workplace-2
```

مجلد النتائج **لا يجوز أن يكون موجودًا مسبقًا**؛ لا تكتب الأداة فوق الملفات السابقة. `verify` يتحقق من كل الملفات بلا إنشاء نتائج. `list` يعرض الفهرس فقط ولا يفك المحتوى. يمكن ضبط حدود الأمان بالبايت باستخدام `--max-file-size` و`--max-total-size` عند التعامل مع مدخلات موثوقة كبيرة.

## أين يوجد المفتاح؟

التحليل الثابت لـ `History2.exe` يبيّن أن العميل يقرأ أول `0x44` بايت من الحزمة: توقيع `0xF00FED5C`، ثم **مفتاح AES-256 بطول 32 بايت**، ثم **32 بايت من مادة IV**. يستخدم AES-CFB أول 16 بايت من مادة IV؛ ويمكن لعميل History تطبيق قناع XOR إضافي مرتبط باسم الحزمة، لكن `workplace.d2` المرفقة تُفك بنجاح **من دون قناع إضافي**. ولذلك، **المفتاح الفعّال لهذه الحزمة مستخرج من رأس `.d2`، وليس سرًا ثابتًا مستخرجًا من ملف EXE**. يُستخدم `History2.exe` لمعرفة خوارزمية القراءة والتشفير، ويطابق أمر `key` بصمته مع النسخة التي تم تحليلها؛ لن يدّعي العثور على مفتاح داخل EXE خلافًا للواقع.

المفتاح لهذه العينة (hex):

```text
4d2f40854e9df31cb095c62702992a0f0e35f6416a5456b94e3d9fefad1de7b8
```

الفك: AES-256-CFB مع مقطع تغذية راجعة 128 بت وإعادة التهيئة لكل ملف، ثم raw LZ4 عند الحاجة، ثم التحقق من الحجم وXXH32 ببذرة `0xF00FED5C`. التفاصيل والإزاحات في [FORMAT.md](FORMAT.md).

## النتائج وحدود الأسماء

نجح التحقق من **813 / 813** ملفًا: **16,929,395** بايت بعد الفك، من حزمة طولها **6,126,018** بايت. لا يحتوي الفهرس أسماء الملفات الأصلية، بل قيم `name_hash` فقط؛ تُحفظ الملفات بأسماء مؤقتة مثل `0000_75a4d836.py` و`0001_c976ee2e.pyc` مع `manifest.json` يحوي لكل ملف الفهرس والإزاحات والبصمة والحجم وSHA-256 للمحتوى. الامتدادات تقديرية من محتوى الملف؛ لا تعني استعادة الاسم الأصلي. بعض المحتوى **Python 2.7 bytecode** محفوظ كما هو بصيغة `.pyc`، وليس مصدر Python مفكوكًا أو برنامجًا يتم تشغيله.

المدخلات غير الموثوقة تُفحص من حيث توقيع الحزمة، وحدود الرؤوس والحمولات، والحدود القصوى للأحجام، والطول وبصمة XXH32 لكل ملف. يكتب `extract` إلى مجلد مؤقت ولا ينشر النتائج إلا بعد نجاح الجميع؛ ويحذف المجلد المؤقت عند الفشل. لا تفتح أو تشغل الملفات المستخرجة إلا بعد فحصها بنفسك.

## الاختبارات

```bash
.venv/bin/python -m unittest discover -s History/tests -v
HISTORY_FULL_TEST=1 .venv/bin/python -m unittest discover -s History/tests -v
```

الاختبار الأخير يتحقق من كل ملفات العينة وبصمة العميل المرفق. لا يُشغَّل الملف التنفيذي في أي خطوة.
