# Сборка бинарных файлов / Building standalone binaries

## Русская версия

### Требования
- Python 3.12+
- Установленные зависимости проекта: `uv sync`
- Установленный PyInstaller: `uv pip install pyinstaller`
- Установленный FFmpeg и доступный в `PATH`
- Для каждой целевой платформы сборка должна выполняться на соответствующей ОС и архитектуре.

### Быстрая сборка
```bash
uv sync                   # устанавливаем зависимости проекта
uv pip install pyinstaller  # добавляем PyInstaller (однократно)
python utils/build.py linux_86_64
```
Готовый бинарный файл будет сохранён в `./dist/svs_0_1_linux_86_64`.

### Доступные цели сборки
| Идентификатор | Операционная система | Архитектура | Имя бинарника |
|---------------|----------------------|-------------|---------------|
| `linux_86_64` | Linux                | x86_64      | `svs_0_1_linux_86_64` |
| `linux_arm`   | Linux                | ARM64       | `svs_0_1_linux_arm`   |
| `windows_86_64` | Windows           | x86_64      | `svs_0_1_windows_86_64` |
| `windows_arm` | Windows             | ARM64       | `svs_0_1_windows_arm`   |
| `macos_86_64` | macOS               | x86_64      | `svs_0_1_macos_86_64` |
| `macos_arm`   | macOS               | ARM64       | `svs_0_1_macos_arm`   |

### Полезные флаги
- `--clean` — удалить предыдущие артефакты перед сборкой.
- `--force` — пропустить проверку платформы (используется только в особых случаях, успешность не гарантирована).

### Проверка результата
1. Запустите бинарный файл из каталога `dist`.
2. Убедитесь, что открывается главное окно приложения.
3. При необходимости используйте `FFMPEG_PATH` в настройках для указания пути к FFmpeg.

### Частые проблемы
- **PyInstaller не найден** — установите его командой `uv pip install pyinstaller`.
- **Сборка для другой платформы** — скрипт нужно запускать на целевой ОС (например, Windows ARM для `windows_arm`).
- **Отсутствуют системные библиотеки Qt** — установите системные пакеты Qt, используя менеджер пакетов вашей ОС.

---

## English version

### Requirements
- Python 3.12+
- Project dependencies installed via `uv sync`
- PyInstaller installed (`uv pip install pyinstaller`)
- FFmpeg available on `PATH`
- Each target must be built on a host that matches the desired operating system and CPU architecture.

### Quick build
```bash
uv sync                    # install project dependencies
uv pip install pyinstaller # add PyInstaller (one time)
python utils/build.py linux_86_64
```
The resulting binary will be stored at `./dist/svs_0_1_linux_86_64`.

### Available build targets
| Target ID | Operating system | Architecture | Binary name |
|-----------|------------------|--------------|-------------|
| `linux_86_64` | Linux   | x86_64 | `svs_0_1_linux_86_64` |
| `linux_arm`   | Linux   | ARM64  | `svs_0_1_linux_arm`   |
| `windows_86_64` | Windows | x86_64 | `svs_0_1_windows_86_64` |
| `windows_arm` | Windows | ARM64  | `svs_0_1_windows_arm`   |
| `macos_86_64` | macOS   | x86_64 | `svs_0_1_macos_86_64` |
| `macos_arm`   | macOS   | ARM64  | `svs_0_1_macos_arm`   |

### Useful flags
- `--clean` removes previous artifacts before the build.
- `--force` skips the host platform check (use only if you understand the risks).

### Validating the binary
1. Run the generated executable from the `dist` directory.
2. Confirm that the main application window opens.
3. Configure the FFmpeg path inside the app if it is not detected automatically.

### Common issues
- **PyInstaller not found** — install it with `uv pip install pyinstaller`.
- **Cross-building** — run the script on the target OS (e.g. Windows ARM for `windows_arm`).
- **Missing Qt libraries** — install the required Qt runtime packages provided by your operating system.
