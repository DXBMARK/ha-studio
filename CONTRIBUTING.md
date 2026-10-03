# Contributing

Thanks for helping. This project is owned by DXBMARK LLC and licensed under Apache-2.0.

1. **Sign off every commit** (`git commit -s`) to certify the Developer Certificate of Origin (https://developercertificate.org/):
   you wrote the change or have the right to submit it under Apache-2.0.
2. **Original wording only.** Do not paste Home Assistant documentation text or examples, or any third-party content
   whose licence is incompatible with Apache-2.0 (CC BY-NC-SA, source-available, GPL).
3. **No secrets, no real customer data** in code, tests, screenshots or examples. Use the demo inventory.
4. **Run the checks**: `pip install -r requirements-dev.txt && pytest -q && python3 skills/ha-studio/scripts/lint_skill.py`.
5. Keep `SKILL.md` under 500 lines; put detail in `references/`. Use only the open-format frontmatter keys.
6. After editing design tokens run `python3 skills/ha-studio/scripts/contrast_check.py`.
7. Mark anything you could not test on a live Home Assistant as *unverified* in `references/verification-checklist.md`.

By contributing you agree your contribution is licensed under Apache-2.0 and may be distributed by DXBMARK LLC.
