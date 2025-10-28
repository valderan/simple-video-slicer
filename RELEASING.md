# Release and versioning guide / Руководство по релизам и версионированию

## English
1. Ensure the main branch is clean and tests pass: `uv run pytest`.
2. Decide on the new semantic version (`MAJOR.MINOR.PATCH`).
3. Update the code version with `python utils/bump_version.py <new_version>`.
4. Document the changes in `CHANGELOG.md` under the new version heading.
5. Commit the changes and create a tag:
   ```bash
   git commit -am "Release <new_version>"
   git tag v<new_version>
   ```
6. Build binaries for the required platforms following [utils/BUILDING.md](utils/BUILDING.md) and upload them to the release page.
7. Push commits and tags: `git push && git push --tags`.

## Русский
1. Убедитесь, что основная ветка чистая и тесты проходят: `uv run pytest`.
2. Определите новую семантическую версию (`MAJOR.MINOR.PATCH`).
3. Обновите номер версии командой `python utils/bump_version.py <new_version>`.
4. Опишите изменения в файле `CHANGELOG.md` в разделе новой версии.
5. Зафиксируйте изменения и создайте тег:
   ```bash
   git commit -am "Release <new_version>"
   git tag v<new_version>
   ```
6. Соберите бинарные файлы для нужных платформ согласно [utils/BUILDING.md](utils/BUILDING.md) и загрузите их на страницу релиза.
7. Отправьте коммиты и теги: `git push && git push --tags`.
