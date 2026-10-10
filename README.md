# Unpack-client

## ALT2

أداة Python لفك حزم `alt2/data/root` واستخراج مفتاحها من `alt2/metin2client.exe` دون تشغيل العميل أو تعديل الملفات الأصلية.

- [تعليمات التشغيل والنتائج](alt2/README.md)
- [الأداة](alt2/unpack.py)
- [توثيق بنية الحزمة والتحليل](alt2/FORMAT.md)

تتطلب Python 3.10 أو أحدث، وحزمتي `lz4` و`xxhash`. الأداة مخصصة للصيغة الموجودة في عينة ALT2 المرفقة، وليست أداة عامة لجميع عملاء Metin2.

## History

أداة منفصلة لفك حزمة `History/pack/workplace.d2` والتحقق من محتوياتها دون تشغيل العميل:

- [التعليمات والنتائج](History/README.md)
- [الأداة](History/unpack.py)
- [توثيق الصيغة وتحليل العميل](History/FORMAT.md)

مفتاح هذه العينة موجود في رأس الحزمة نفسها؛ يُستخدم `History2.exe` لتحديد طريقة استخدامه والتحقق من نسخة العميل، لا لادعاء استخراج مفتاح ثابت غير موجود فيه. تتطلب الأداة `pycryptodome` و`lz4` و`xxhash` وفق [History/requirements.txt](History/requirements.txt).
