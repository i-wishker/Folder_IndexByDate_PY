# File Sorter by Creation Date

A Windows-based Python application that automatically organizes and renames files in a directory based on their creation date. This tool provides an interactive GUI to preview changes before committing them, with options to selectively ignore files.

## Features

- **Automatic Renaming**: Renames files based on their creation date in `YYYY-MM-DD` format
- **Preview Mode**: See all proposed changes before they're applied
- **Selective Ignore**:
  - Temporarily ignore specific files for the current session
  - Permanently ignore files (stored in `.file_sorter_ignore.txt`)
- **Duplicate Handling**: Automatically appends counters to files created on the same date
- **User-Friendly GUI**: Built with Tkinter for easy interaction

## How It Works

1. **Select a Folder**: Click "Choose Folder" to select the directory to organize
2. **Review Changes**: The preview pane shows all proposed renames in the format: `OLD_NAME → YYYY-MM-DD_N.EXT`
3. **Selective Ignoring**: 
   - Select files in the preview list
   - Use "Ignore Temporarily" to skip them for this session
   - Use "Ignore Permanently" to add them to the ignore list
4. **Confirm Rename**: Once satisfied with the changes, click "Confirm Rename" to apply them

## Naming Convention

Files are renamed as follows:
- **Single file on a date**: `YYYY-MM-DD.EXT` (e.g., `2026-01-18.txt`)
- **Multiple files on a date**: `YYYY-MM-DD_N.EXT` (e.g., `2026-01-18_1.txt`, `2026-01-18_2.txt`)

## Permanent Ignore List

When you permanently ignore files, they are added to `.file_sorter_ignore.txt` in the target directory. This file persists across sessions, ensuring permanently ignored files are never renamed again.

## Requirements

- Python 3.x
- tkinter (included with Python on Windows)

## Usage

Run the application:

```bash
python file_sorter.py
```

A GUI window will open where you can:
1. Select a folder to organize
2. Preview the proposed changes
3. Ignore specific files if needed
4. Confirm the rename operation

## Notes

- This tool works on **Windows** systems
- Files are sorted by creation date (`st_ctime`)
- The tool preserves file extensions
- All operations can be previewed before committing
- Permanently ignored files are stored in `.file_sorter_ignore.txt` within the target directory

## License

See LICENSE file for details.
