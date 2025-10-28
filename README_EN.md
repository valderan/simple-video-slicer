# SVS — Simple Video Slicer

[Версия на русском языке](README.md)

SVS (Simple Video Slicer) is a cross-platform desktop application with a graphical interface for splitting large video files into smaller fragments. The app supports fast lossless processing and optional conversion to various formats.

![SVS Logo](logo.png)

## Key Features
- 🎬 Slice videos into fragments by time ranges
- ⚡ Fast, lossless processing via stream copy
- 🔄 Optional transcoding with configurable codecs and quality parameters
- 👁️ Preview fragments before processing
- 📊 Video details (duration, resolution, codec)
- 💾 Import/export segment lists (JSON, CSV)
- 📝 Detailed processing log
- 🖥️ Cross-platform support (Linux, Windows, macOS)

## Supported Formats
**Input:** MP4, AVI, MKV, WEBM, MOV, FLV, WMV, MPEG, M4V, 3GP.  
**Output:** MP4 (recommended universal format), MKV (preserves all tracks), AVI, WEBM, MOV.

## Installation
### Requirements
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for dependency management
- FFmpeg available in `PATH`

### Installing FFmpeg
**Linux (Debian/Ubuntu)**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows**
1. Download the archive from the [official FFmpeg website](https://ffmpeg.org/download.html).
2. Extract it and add the `bin` directory to the `PATH` environment variable.

**macOS (Homebrew)**
```bash
brew install ffmpeg
```

### Installing the app with uv and pip
```bash
uv sync
uv pip install -e .[dev]  # optional for development tools
```

## Quick Start
```bash
uv sync
uv run video-slicer
```
1. Select the input video file and output folder.
2. Add one or more segments manually or from a text description.
3. Choose between stream copy and transcoding modes.
4. Press “Start processing” and monitor progress in the log.

## Usage
### Lossless copy (fast processing)
- Keep the video and audio codecs set to `copy`.
- FFmpeg will slice the file without re-encoding, preserving the original quality.

### Transcoding
- Enable the “Convert” option and choose codecs (for example `libx264`/`aac`).
- Adjust `CRF` and extra parameters to balance quality and file size.

### Import/export segment lists
- “File → Save segments…” exports the current table to `segments.json`.
- “File → Load segments…” restores a list from JSON.
- Convert the JSON to CSV with external tools if you need spreadsheet-compatible data.

## User Guide
Detailed instructions covering the interface, text-based lists, the log, and settings are available in [docs/user_guide_EN.md](docs/user_guide_EN.md).

## Development
### Install development dependencies
```bash
uv sync
uv pip install -e .[dev]
```

### Run tests
```bash
uv run pytest
```

### Code formatting
```bash
uv run black src tests
```

### Linting
```bash
uv run ruff check src tests
```

### Project structure
```
src/                 application source code
src/video_slicer/ui/ Qt (PySide6) user interface
src/video_slicer/core/ FFmpeg orchestration and logic
docs/                documentation
tests/               automated tests
```

## FAQ
- **FFmpeg not found?** Ensure the binary is in `PATH` or configure it via the app settings dialog.
- **Need faster processing?** Stick to `copy` mode to avoid re-encoding.
- **Video file will not open?** Verify the file is supported by FFmpeg and accessible with current permissions.
- **How much disk space is required?** Lossless copy requires roughly the total size of the resulting segments; transcoding may need extra temporary space.

## Known Issues
- Preview can be slow for extremely large files on some systems.
- Exotic codecs may not be supported by your FFmpeg build.
- Processing files larger than 50 GB can make the UI less responsive.

## Author
Maintained by the SVS enthusiast team.

## Acknowledgements
- [PySide6](https://doc.qt.io/qtforpython/) — Qt for Python
- [FFmpeg](https://ffmpeg.org/) — multimedia framework
- [uv](https://github.com/astral-sh/uv) — fast Python package manager
- [OpenAI](https://openai.com) — for contributions to the project

## License
Released under the MIT License. See [LICENSE](LICENSE).
