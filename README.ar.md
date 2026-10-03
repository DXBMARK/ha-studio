<div align="center">

# HA Studio

**صمّم وولّد لوحات تحكّم احترافية للشركات متوافقة مع Home Assistant — مؤشرات الأداء، استهلاك الطاقة لكل جهاز، الكاميرات، البنية التحتية، النسخ الاحتياطي والصوت — من مهارة ذكاء اصطناعي واحدة قابلة للنقل.**

[English](README.md) · [Claude Code](#claude-code) · [Claude.ai](#claudeai) · [Codex](#codex-openai) · [ChatGPT](#chatgpt) · [Gemini](#gemini) · [Antigravity](#antigravity)

[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue?style=flat-square)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-open%20format-8A2BE2?style=flat-square)](https://agentskills.io)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![Tests](https://img.shields.io/github/actions/workflow/status/DXBMARK/ha-studio/ci.yml?branch=main&label=tests&style=flat-square)](https://github.com/DXBMARK/ha-studio/actions/workflows/ci.yml)
[![Security scan: CodeQL](https://img.shields.io/github/actions/workflow/status/DXBMARK/ha-studio/codeql.yml?branch=main&label=CodeQL&style=flat-square)](https://github.com/DXBMARK/ha-studio/actions/workflows/codeql.yml)
[![Release](https://img.shields.io/github/v/release/DXBMARK/ha-studio?style=flat-square&color=f97e1a)](https://github.com/DXBMARK/ha-studio/releases)
[![GitHub stars](https://img.shields.io/github/stars/DXBMARK/ha-studio?style=flat-square&color=f97e1a)](https://github.com/DXBMARK/ha-studio/stargazers)

by **DXBMARK LLC**

![Aurora overview](docs/screenshots/aurora-overview.webp)

</div>

<div dir="rtl">

> مشروع مستقل. غير تابع لـ Home Assistant أو Open Home Foundation أو أي مزوّد ذكاء اصطناعي مذكور هنا، ولا تعتمده أو تصادق عليه. يُستخدم اسم "Home Assistant" وصفياً فقط ("متوافق مع Home Assistant"). انظر [TRADEMARKS.md](TRADEMARKS.md).

---

## لماذا هذا المشروع

أغلب لوحات Home Assistant (HA) تصميمات هواة. الشركة تحتاج إجابات من نظرة واحدة: *هل الطاقة طبيعية؟ أي جهاز يهدر الطاقة؟ هل الكاميرات تعمل؟ هل مواقعنا وشهاداتنا ونسخنا الاحتياطية سليمة؟* يمنح HA Studio مساعد الذكاء الاصطناعي طريقة كاملة قابلة للتكرار — مع الأدوات — لتحقيق ذلك بأمان.

| تقول | ينفّذ |
|---|---|
| "صمّم لوحة لآيباد المكتب" | استقبال المتطلبات ← جرد ← خطة مؤشرات ← YAML لـ Lovelace + ثيم + معاينة |
| "اعرض الطاقة لكل جهاز" | تدقيق الطاقة (حسّاسات kWh الناقصة، `state_class` الخاطئ، الحمل غير المتتبَّع) + عرض Energy |
| "أضف الكاميرات والمكيّفات الجديدة" | إعادة الجرد، مقارنة، تصنيف، إعادة التوليد |
| "راقب Proxmox وDokploy ودومينات الشركة والنسخ الاحتياطي" | وصفات أصلية لـ HA (تكاملات رسمية، حسّاسات REST/template، تنبيهات) |
| "عرض لكل غرفة، موظفون مقابل مدراء" | عرض الغرف من خريطة المناطق التي تقدّمها؛ تبويبات المدراء فقط عبر خيار العرض `visible` |
| "اجعلها بهوية شركتنا" | ثلاثة تصاميم زجاجية مفحوصة لسهولة القراءة؛ من الـ tokens إلى ثيم HA |

## ما الذي تحصل عليه

- **مهارة** (`skills/ha-studio/`): سير عمل، 10 أدلة مرجعية، 7 ملفات أنشطة (مكتب، متجر، مقهى، عيادة، فندق، مستودع، DevOps).
- **أدوات** (Python، المكتبة القياسية + PyYAML): جرد للقراءة فقط، تدقيق الطاقة، مولّد Lovelace، مولّد الثيم، فاحص تباين WCAG، مدقّق اللوحات، بانٍ لمعاينة HTML، أدوات لقطات الشاشة، فاحص المهارة.
- **ثلاثة تصاميم زجاجية معتمدة** — Aurora وMidnight وFrost — مع tokens وثيمات HA ومعاينات.
  ملاحظة: يوثّق Home Assistant رسمياً عدداً قليلاً فقط من متغيّرات الثيم (مثل `primary-color` و`accent-color`)؛ المظهر الزجاجي يستخدم أيضاً `ha-card-*` و`card-background-color` وهي غير موثّقة رسمياً وقد تتغيّر بين الإصدارات. أعد فحص المظهر بعد تحديثات Home Assistant.
- **أدوات الإصدار**: ZIP لـ claude.ai، حزمة ChatGPT، نص Gemini Gem، مثبّت آمن، CI.
- **اختبارات**: مجموعة `pytest` تغطي التوليد والتحقق والتباين والتغليف والترخيص ونظافة الأسرار.

## لقطات الشاشة

كل اللقطات مولَّدة من بيانات تجريبية (مستخدمون وهميون، مضيفون `example.com`) بواسطة `tools/make_screenshots.py` — لا بيانات عملاء حقيقية. معاينات HTML تحمّل الخطوط من Google Fonts وقت العرض (وهذا يرسل عنوان IP للمشاهد إلى Google)؛ استضف خطوط OFL محلياً إن كان ذلك يهمّك.

*الأيقونات: Font Awesome Free من Fonticons, Inc.، ترخيص CC BY 4.0.*

</div>

| Aurora — dark / orange | Midnight — navy / sky | Frost — light |
|---|---|---|
| ![](docs/screenshots/aurora-energy.webp) | ![](docs/screenshots/midnight-energy.webp) | ![](docs/screenshots/frost-energy.webp) |
| ![](docs/screenshots/aurora-infra.webp) | ![](docs/screenshots/midnight-infra.webp) | ![](docs/screenshots/frost-infra.webp) |
| ![](docs/screenshots/aurora-backups.webp) | ![](docs/screenshots/midnight-voice.webp) | ![](docs/screenshots/frost-overview.webp) |

**Components, palette and measured contrast**

![Aurora components](docs/screenshots/aurora-components.webp)
![Midnight components](docs/screenshots/midnight-components.webp)
![Frost components](docs/screenshots/frost-components.webp)

**Icon set** (55 preview glyphs; HA dashboards use `mdi:` names)

![Icons](docs/screenshots/icons.webp)

<div dir="rtl">

## التثبيت

اختر منصتك. المهارة مجلد واحد بصيغة [Agent Skills](https://agentskills.io) المفتوحة؛ المحوّلات تقوم بالتغليف فقط.

### Claude Code

```text
/plugin marketplace add DXBMARK/ha-studio
/plugin install ha-studio@dxbmark
```
بديل يدوي:
```bash
git clone https://github.com/DXBMARK/ha-studio && cd ha-studio
python3 tools/install.py --target claude-code-user          # dry run
python3 tools/install.py --target claude-code-user --yes    # installs to ~/.claude/skills
```
ثم اطلب: *"Use ha-studio to design a dashboard for my office."*

### Claude.ai
1. نزّل `ha-studio-<version>.zip` من **Releases** في المستودع (أو شغّل `python3 tools/build_release.py`).
2. في Claude: **Settings ← Capabilities ← Skills ← Upload skill** (قد تختلف أسماء القوائم)، واختر ملف ZIP.
3. يتطلب خطة تدعم المهارات وتنفيذ الشيفرة مفعّلين. ابدأ محادثة تصف مهمة لوحة Home Assistant.

Claude API: ارفع المجلد نفسه عبر Skills API وأرفقه بـ `container.skills` (الحاوية بلا شبكة، فاستخدم ملفات التصدير `--states-file`).

### Codex (OpenAI)
```bash
python3 tools/install.py --target codex-repo --dest /path/to/your/project --yes   # → .agents/skills/
python3 tools/install.py --target codex-user --yes                                 # → ~/.agents/skills/
```
استدعِ بـ `$ha-studio` أو صف المهمة فقط. ملف [AGENTS.md](AGENTS.md) المرفق يوجّه Codex إلى المهارة.

### ChatGPT
لا يوجد في ChatGPT تثبيت من GitHub. اختر أحد المسارات:
- **Skills** (Business / Enterprise / Edu، إن فعّلها المسؤول): ارفع ZIP المهارة. *صيغة الرفع لم يتحقق منها DXBMARK.*
- **Project** (Plus/Pro): أنشئ Project والصق `chatgpt/instructions.md` (≈3.6 ألف حرف) كتعليمات وارفع الملفات من `chatgpt-pack-<version>.zip ← knowledge/`.
- **Free/Go أو التعليمات المخصصة**: الصق `chatgpt/instructions-lite.md` (≈0.7 ألف حرف).

### Gemini
- **Gemini CLI** (تراخيص المؤسسات — انتهى وصول CLI للمستهلكين في 18 يونيو 2026): `gemini skills install https://github.com/DXBMARK/ha-studio --consent`، أو التثبيت كإضافة عبر `gemini-extension.json` (يحمّل `GEMINI.md`).
- **تطبيق Gemini**: أنشئ **Gem** والصق `gem-instructions.md` (من ملفات الإصدار). الـ Gems لا تشغّل السكربتات؛ تحصل على المنهج وكتابة YAML.

### Antigravity
```bash
python3 tools/install.py --target antigravity-project --dest /path/to/project --yes   # → .agents/skills/
python3 tools/install.py --target antigravity-user --yes                              # global skills folder
```
تختلف المسارات العامة بين إصدارات Antigravity — تأكد من وثائقه الحالية. التثبيت من رابط GitHub لم يُتحقَّق منه.

> المثبّت **لا يستبدل** تثبيتاً موجوداً ولا يفعل شيئاً دون `--yes`.

## بداية سريعة (بدون ذكاء اصطناعي)

```bash
pip install PyYAML
S=skills/ha-studio/scripts

# 1) Inventory (read-only). Token stays in the environment.
HA_URL=https://homeassistant.local:8123 HA_TOKEN=... python3 $S/ha_inventory.py --out inventory.json   # use https (or a trusted LAN); redirects are refused so the token never leaves your host
#    …or offline from an export, e.g. the bundled demo:
python3 $S/ha_inventory.py --states-file skills/ha-studio/assets/examples/demo_states.json --out inventory.json

# 2) Energy audit
python3 $S/energy_audit.py inventory.json --tariff 0.15

# 3) Generate theme + dashboard, then validate
python3 $S/gen_theme.py aurora --out themes/dxbmark_aurora.yaml
python3 $S/generate_lovelace.py inventory.json --profile office --theme dxbmark_aurora --title "My Office" --out dashboard.yaml
#    Optional: --areas areas.yaml adds a Rooms view; --admin-user <HA user id> hides Energy/Security/Infra/Backups from other users
python3 $S/validate_dashboard.py dashboard.yaml --inventory inventory.json

# 4) Optional: iPad HTML previews and screenshots (needs Playwright)
python3 $S/build_design.py --out preview/ --brand "My Company"
```
لا تستبدل السكربتات ملف إخراج موجوداً إلا مع `--force`. للتطبيق، الصق `dashboard.yaml` في محرّر الإعداد الخام للوحة، أو اربطه من لوحة بوضع YAML. استخدم `assets/examples/packages/dxbmark_infra.yaml` نقطة بداية لمؤشرات Proxmox/Dokploy/الشهادات/النسخ الاحتياطي.

## جرّبه محلياً (أمر واحد)

```bash
pip install -r requirements-test.txt
python3 tools/serve_demo.py            # يبني كل شيء على بيانات العرض المرفقة ثم يخدمه على http://127.0.0.1:8099/
```
يشغّل خط العمل كاملاً (جرد ← تدقيق الطاقة ← ثيم ← لوحة Lovelace بعرض الغرف وتبويبات المدراء ← تحقق ← تقرير التباين ← ثلاث معاينات آيباد تفاعلية ← صفحات المكوّنات والأيقونات) ويفتح صفحة فهرس بكل النتائج. لا شيء يغادر جهازك. استخدم `--states-file my_states.json` لتصدير Home Assistant الخاص بك، و`--port` لتغيير المنفذ، و`--no-serve` للبناء فقط.

### لماذا صورة Docker؟
اختيارية. المهارة نفسها لا تحتاج Docker. الصورة `ghcr.io/dxbmark/ha-studio` ([GitHub Packages](https://github.com/orgs/DXBMARK/packages?repo_name=ha-studio)) تضم Python وPyYAML لتشغيل أدوات سطر الأوامر على خادم أو CI دون تثبيت أي شيء:
```bash
docker run --rm -v "$PWD":/work ghcr.io/dxbmark/ha-studio:1.1.0 generate_lovelace inventory.json --profile office --out dashboard.yaml
docker run --rm ghcr.io/dxbmark/ha-studio:1.1.0 --help      # قائمة الأدوات
```
تعمل بمستخدم غير جذري ولا تجري اتصالات شبكة من تلقاء نفسها. لا يوجد فهرس Python في GitHub Packages، فالحاوية هي طريقة هذا المستودع للنشر كحزمة.

## كيف تعمل المهارة

```
Intake → Inventory → Classify & KPI plan → Energy audit → Design → Generate → Preview → Validate → Deliver
```
- **للقراءة فقط افتراضياً.** لا تستدعي خدمات HA ولا تعدّل إعداداتك؛ التطبيق يحتاج موافقتك الصريحة.
- **لا تخترع كيانات.** المؤشرات الناقصة تُبلَّغ كفجوات مع التكامل/المساعد الذي ينشئها.
- **الأسرار خارج المخرجات.** الرموز عبر البيئة أو `!secret`؛ المدقّقات ترفض النصوص الشبيهة بالأسرار.
- **الكاميرات حسّاسة للخصوصية.** بلاطات معتمة، لقطات أولاً، عروض مقيّدة، الصوت مغلق.
- **صريحة بشأن الحدود.** [verification-checklist.md](skills/ha-studio/references/verification-checklist.md) يسرد ما *لم* يُختبر على نسخة حيّة.

## نظام التصميم

زجاج يبقى مقروءاً: النص ≥ 4.5:1 وعناصر الواجهة ≥ 3:1 مقيسة على البطاقة المركّبة (`contrast_check.py`)، بدائل معتمة لـ `prefers-reduced-transparency` و`prefers-contrast` و`forced-colors`، أهداف لمس 48 بكسل، ومصفوفة حالات لكل عنصر. التفاصيل: [design-system.md](skills/ha-studio/references/design-system.md).

## هيكل المستودع

```
skills/ha-studio/   the skill (SKILL.md, scripts/, references/, assets/)
.claude-plugin/             Claude Code plugin + marketplace manifests
chatgpt/                    ChatGPT instructions (full + lite)
tools/                      build_release.py, install.py, make_screenshots.py, serve_demo.py
tests/                      pytest suite          docs/screenshots/  README images
AGENTS.md  GEMINI.md  gemini-extension.json      platform adapters
README.ar.md                                      Arabic
LICENSE  NOTICE  THIRD_PARTY_NOTICES.md  TRADEMARKS.md  SECURITY.md  CONTRIBUTING.md  VERSIONING.md  CHANGELOG.md
```

## التطوير

```bash
pip install -r requirements-dev.txt
pytest -q
python3 skills/ha-studio/scripts/lint_skill.py
python3 skills/ha-studio/scripts/contrast_check.py
python3 tools/build_release.py        # → dist/
python3 tools/make_screenshots.py     # regenerate docs/screenshots (needs Playwright + Chromium)
```

## الملكية والترخيص وحقوق الأطراف الثالثة

- **المالك:** DXBMARK LLC. كل المحتوى الأصلي — المهارة والشيفرة والـ tokens والقوالب والنصوص ولقطات نماذج DXBMARK — © 2026 DXBMARK LLC، ومرخّص بموجب **Apache License 2.0** ([LICENSE](LICENSE)، [NOTICE](NOTICE)). اسم DXBMARK علامة تجارية لـ DXBMARK LLC وغير مرخّص للاستخدام.
- **الأطراف الثالثة تحتفظ بحقوقها.** Font Awesome Free (CC BY 4.0) والخطوط (OFL 1.1) وMaterial Design Icons (Apache-2.0) وغيرها مذكورة في [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). وثائق Home Assistant (CC BY-NC-SA 4.0) **لا تُنسخ**؛ الحقائق معاد صياغتها بكلماتنا. لا يُستخدم شعار Home Assistant. n8n اختياري ولا يُعاد توزيعه.
- **ليست استشارة قانونية.** ملاحظات الكاميرات/الخصوصية إرشاد هندسي؛ راجع القوانين المطبّقة في مكان النشر قبل تركيب الكاميرات.

## مكوّنات الأطراف الثالثة

كل ما يلي ملك لأصحابه ويحتفظ بترخيصه الخاص؛ النص الكامل وطريقة الاستخدام في [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

| المكوّن | الترخيص | الاستخدام |
|---|---|---|
| [Font Awesome Free](https://fontawesome.com/license/free) | CC BY 4.0 (الأيقونات) | 55 أيقونة صلبة كمسارات SVG، للمعاينة فقط |
| [ui-ux-pro-max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | MIT | مضمّن دون تعديل في `vendor/` مع ملف ترخيصه |
| Inter وSource Serif 4 وJetBrains Mono | SIL OFL 1.1 | خطوط المعاينة (تُحمَّل من Google Fonts) |
| Material Design Icons | Apache-2.0 | أسماء `mdi:` فقط |
| Home Assistant | Apache-2.0 (الشيفرة) | المنصة المستهدفة، إشارة فقط؛ لا تُنسخ وثائقها (CC BY-NC-SA) |
| PyYAML وpytest وPlaywright | MIT / Apache-2.0 | يثبّتها المستخدم، ولا نعيد توزيعها |
| shields.io وGitHub Actions وصورة Docker `python:3.12-slim` | شروطها | شارات README والـ CI وصورة الحاوية |

## المساهمة والأمان

انظر [CONTRIBUTING.md](CONTRIBUTING.md) (توقيع DCO، صياغة أصلية فقط) و[SECURITY.md](SECURITY.md).

---

</div>

<div align="center">

### تواصل معنا

[![زيارة الموقع](https://img.shields.io/badge/Visit%20Website-www.dxbmark.com-f97e1a?style=for-the-badge&logo=googlechrome&logoColor=white)](https://www.dxbmark.com)
[![راسلنا](https://img.shields.io/badge/Contact%20Us-info%40dxbmark.com-0b1220?style=for-the-badge&logo=gmail&logoColor=f97e1a)](mailto:info@dxbmark.com)
[![تابعنا على لينكدإن](https://img.shields.io/badge/Follow%20on-LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/company/dxbmark)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-%2B971%2050%20512%201583-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://wa.me/971505121583)

<sub>© 2026 DXBMARK LLC · Apache-2.0 · دبي، الإمارات &nbsp;|&nbsp; ⭐ ضع نجمة للمستودع إن أفادك HA Studio</sub>

</div>
