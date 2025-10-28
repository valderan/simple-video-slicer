# SVS User Guide

## Installation and Launch
- Install Python 3.12 or newer and ensure the [uv](https://github.com/astral-sh/uv) tool is available on your system.
- Make sure FFmpeg is installed and visible in your `PATH` (see the "Installing FFmpeg" section below).
- From the project root, synchronise dependencies:
  ```bash
  uv sync
  ```
- Start the application with:
  ```bash
  uv run video-slicer
  ```

## Importing Video and Creating Segments Manually
1. Click “Browse…” in the “Input video file” block and choose the source clip.
2. Select the “Output directory” where the processed segments will be written.
3. Add a segment with “Add segment” and specify start/end times. You can enter values in `HH:MM:SS`, `MM:SS`, or seconds.
4. Configure processing: keep codecs on `copy` for fast lossless slicing or enable conversion and choose codecs plus CRF.
5. Click “Start processing” to generate segment files.

## Creating Segments from Text Descriptions
- Click “Create list” above the segment table to open the bulk creation dialog.
- Paste a description such as:
  ```
  00:00 Intro
  02:15 Main topic
  05:30 Outro
  ```
- Each line must start with a timestamp (same formats as manual input) followed by an optional title.
- The dialog validates ascending order automatically and highlights formatting issues.
- Enable “Add numbering” to prepend incremental numbers to file names and table entries.
- “Keep description in filename” appends the text label to generated file names; adjust the separator in the “Separator” field.
- After confirmation, the application builds segments from the list and asks whether to merge them with existing entries.

## Text List Interface Details
- The editor supports multiline input and displays a formatting hint.
- Separators `-`, `–`, and `—` between time and description are recognised. If no description is given, file names fall back to automatic numbering.
- When both “Numbering” and “Description” are enabled, you may set a custom separator (default `_`). Characters `<>:"/\|?*` are disallowed.
- Before segments are created, the dialog previews the parsed list and requests confirmation with the final count.

## Segment Preview
- Each segment row features a “Preview” button (▶ icon).
- The preview dialog uses FFmpeg to generate a thumbnail and shows the exact start time in `HH:MM:SS` format.
- Use preview to verify segment boundaries before launching processing.

## Metadata Display
- The “Metadata” column indicates whether information about the rendered file is available.
- After processing, open the metadata dialog to inspect container, codecs, and the resulting file path.
- The “Metadata” button above the table reveals detailed properties of the source video: duration, resolution, and available streams.

## Saving and Loading Segment Lists
- “File → Save segments…” stores the current list as JSON (`segments.json`). Each record contains `start_time`, `end_time`, `filename`, `format`, `convert`, `video_codec`, `audio_codec`, `crf`, and `extra_params`.
- “File → Load segments…” restores segments from a JSON file. Time values are accepted in `HH:MM:SS`, `MM:SS`, or seconds.
- The resulting JSON can be converted to CSV with external tools when you need to share the list outside the application.

## Settings Menu
- **Interface language** — switch between Russian and English UI texts.
- **Theme** — choose light or dark widgets.
- **FFmpeg path** — select the `ffmpeg` binary manually; the “Detect automatically” button searches common locations.
- **Enable logging** — “Save detailed log to file” mirrors console messages to disk.
- **Log file** — select where the `.log` file should be stored (defaults to the user home directory).
- **Strip segment metadata** — remove embedded tags from produced files.
- **Embed SVS metadata** — add generator information to exported segments.
- **Use icon buttons** — replace text buttons in the table with compact icons.

## Processing Log
- The “Log” panel at the bottom captures every step: segment start, FFmpeg output, and completion messages.
- Entries are timestamped automatically for easier troubleshooting.
- “Copy log” sends the visible text to the clipboard. When file logging is enabled, the same content is saved to the chosen `.log` file.

## Transcoding Segments or the Entire File
- Leave video and audio codecs on `copy` for lossless slicing — FFmpeg simply copies streams to segment files.
- To transcode, tick “Convert”, choose codecs (e.g., `libx264`/`aac`), adjust `CRF`, and add extra FFmpeg parameters if required.
- To re-encode the whole file, create a single segment starting at `00:00:00` and keep the end blank; the chosen codecs apply to the full duration.

## Installing FFmpeg
### Linux (Debian/Ubuntu)
```bash
sudo apt update
sudo apt install ffmpeg
```

### Windows
1. Download the archive from the [official FFmpeg website](https://ffmpeg.org/download.html).
2. Extract it and add the `bin` directory to the `PATH` environment variable.

### macOS (Homebrew)
```bash
brew install ffmpeg
```

## Saving and Migrating Application Profiles
- Interface preferences, language, file locations, and logging choices are saved automatically when the app closes.
- Copy the configuration file to another machine to transfer your preferred environment.

## Additional Tips
- Preview segments before processing to avoid unnecessary reruns.
- Check the log after completion — FFmpeg messages help diagnose codec issues.
- Export segment lists regularly for large projects so that you always have a backup configuration.
