# SVS User Guide

## Installation
1. Install Python 3.12 or newer.
2. Make sure FFmpeg is available in your `PATH`.
3. Create a virtual environment and install the dependencies via `uv pip install -e .`.

## Launch
```bash
uv run python -m video_slicer.main
```

## Workflow
1. Click “Browse...” in the “Input video file” section and select the source clip.
2. Choose the “Output directory” where the segments will be stored.
3. Add a segment and enter start/end timestamps.
4. Configure codecs and CRF value or keep `copy` for lossless processing.
5. Press “Process” and wait for the completion message.

## Tips
- Use the preview dialog to verify the selected frame.
- When no filename is provided, segments are named automatically.
- Create several segments in a row to process a file in batches.
