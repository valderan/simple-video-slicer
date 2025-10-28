# SVS — Simple Video Slicer

SVS is a desktop Python application for splitting large video files into fragments without quality loss. The UI is built with PySide6 and relies on FFmpeg for media processing.

## Features
- Create any number of segments with custom time ranges
- Lossless copy mode or conversion using popular codecs
- Support for numerous input and output containers
- Thumbnail generation and preview of selected intervals
- Localised interface (Russian / English)
- Logging of processing operations

## Requirements
- Python 3.12+
- FFmpeg available in the `PATH`
- Linux, Windows, or macOS

## Installing FFmpeg
### Linux (Debian/Ubuntu)
```bash
sudo apt update
sudo apt install ffmpeg
```

### Windows
1. Download the archive from the [official FFmpeg website](https://ffmpeg.org/download.html)
2. Extract it and add the `bin` directory to the `PATH`

### macOS
```bash
brew install ffmpeg
```

## Install dependencies with uv
```bash
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e .[dev]
```

## Quick start
```bash
uv run python -m video_slicer.main
```

1. Select an input video file
2. Choose the output directory
3. Add one or more segments
4. Configure codecs and optional extra parameters
5. Click “Process” to run FFmpeg

## FAQ
**FFmpeg not found** — ensure the FFmpeg binaries are accessible from the `PATH`.

**Can I process huge files?** — yes, the application handles files tens of gigabytes in size. Performance depends on the selected mode (copy vs transcoding).

## Known issues
- Preview requires an installed FFmpeg binary
- On macOS, the first run may require permission to execute external processes

## License
The project is distributed under the MIT License. See [LICENSE](LICENSE).
