# Lightroom Mobile XMP Dumper

This project is designed to extract XMP sidecar files from the Ad0be Lightroom Mobile app.

Ad0be does not provide a way to save XMP sidecar files from the app. The only official way to get the data is to export as DNG files *one by one* from the app and then extract the XMP files from those huge DNG files. This is just *stupid*.

## Requirements

- Python 3.x with a few dependencies specified in requirements.txt
- [`ifuse`](https://github.com/libimobiledevice/ifuse) for mounting iOS devices

## Usage

> **Note:** Ensure that you have properly configured `ifuse` and have access to the iOS device’s file system before running this script.

1. **Install dependencies**:
  ```bash
  pip install -r requirements.txt
  ```

2. **Run the script**:
   ```bash
   python dump_xmp.py /path/to/output_dir --no-copy-source-file
   ```
   - `output_dir`: The directory where XMP files will be saved.
   - `--no-copy-source-file`: Optional flag to skip copying original source files.


## Output Structure

The output directory will be populated with subdirectories based on the capture date of each photo (`YYYY-MM-DD`). Each directory contains:

- Original image files (optional)
- Corresponding `.xmp` sidecar files

## Example

```bash
python dump_xmp.py ./xmp_output
```

This command will extract all XMP files from Lightroom Mobile and store them under `./xmp_output`, organized by date.
