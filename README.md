# SP-404 MK2 Reverse Engineering Project

This repository contains tools and documentation for reverse engineering the Roland SP-404 MK2 sampler/drum machine's internal file formats. The project focuses on understanding and manipulating pattern files and pad configuration data.

## 🎛️ Overview

The SP-404 MK2 stores its data in proprietary binary formats. This project provides:

- **Pattern file analysis**: Understanding how drum sequences and pad triggers are stored
- **Pad configuration analysis**: Decoding settings like BPM, volume, effects, and sample assignments
- **Firmware analysis tools**: Scripts to examine the device's firmware
- **Conversion utilities**: Tools to convert between binary and human-readable formats

## 📁 Repository Structure

```
├── pattern/          # Pattern files and analysis
├── padconf/          # Pad configuration files and tools
├── firmware/         # Firmware analysis tools
├── bin/              # Utility scripts
└── README.md         # This file
```

### Pattern Files (`/pattern/`)

Contains pattern data in both binary (`.BIN`) and hex dump (`.TXT`) formats:

- `PTN00001-XX.BIN/TXT`: Pattern data files
- `pattern_notes.txt`: Documentation of pattern file format
- `PTN00001-LIST.TXT`: Comparison of different pattern variations
- `Project16.zip`: Collection of pattern files

**Key Features:**
- 8-byte aligned data structure
- Tick-based timing system (1440 ticks = 1 bar at 4/4 time)
- Stores pad triggers, velocity, chromatic pitch, and timing information

### Pad Configuration (`/padconf/`)

Binary files containing pad settings and a Python tool for editing:

- `PADCONFXXX.BIN`: Binary pad configuration files (52KB each)
- `mk2_bpm_edit.py`: Python script to modify pad BPM values
- `mk2_notes.txt`: Detailed documentation of PADCONF.BIN format
- `PADCONF_LIST.TXT`: Log of changes between configurations

**Configuration Data Includes:**
- BPM settings (stored as integers: 90.00 BPM = 9000)
- Volume levels, pan settings
- Loop points, sample start/end positions
- Effects routing, mute groups
- Pad linking, one-shot modes
- Sample filenames (23 character limit)

### Firmware Analysis (`/firmware/`)

Tools for downloading and analyzing SP-404 MK2 firmware:

- `get_firmware.sh`: Downloads official firmware
- `*_search.sh`: Various search utilities for finding specific file types
- Search scripts for: BMP images, C source, WAV files, shell scripts, etc.

### Utilities (`/bin/`)

- `hex_diff.sh`: Compare binary files and display differences in hex format

## 🛠️ Getting Started

### Prerequisites

- Python 3.x (for all toolkit tools)
- `xxd` (for hex dump conversion)
- `wget` and `unzip` (for firmware download)
- Standard Unix tools (`bash`, `perl`, `gawk`)

### Quick Setup

1. Clone this repository
2. Run the setup script:
   ```bash
   ./setup.sh
   ```
3. (Optional) Download firmware for analysis:
   ```bash
   cd firmware && ./get_firmware.sh
   ```

### Manual Setup

If you prefer manual setup:
```bash
pip3 install flask werkzeug pandas matplotlib numpy
chmod +x *.py bin/*.sh firmware/*.sh
```

## 🚀 New Toolkit Features

This repository now includes a comprehensive toolkit with multiple interfaces:

### 1. **Unified CLI Tool** (`sp404_toolkit.py`)
```bash
# Get pad information
./sp404_toolkit.py padconf info padconf/PADCONF001.BIN --pad 1

# Set pad BPM
./sp404_toolkit.py padconf set-bpm padconf/PADCONF001.BIN --pad 1 --bpm 120.0

# List all pad configurations
./sp404_toolkit.py padconf list padconf/PADCONF001.BIN

# Analyze patterns
./sp404_toolkit.py pattern info pattern/PTN00001-01.BIN

# Create backups
./sp404_toolkit.py backup create my_project.sp404backup padconf/PADCONF001.BIN pattern/
```

### 2. **Advanced Pattern Editor** (`pattern_editor.py`)
```bash
# Detailed pattern analysis
./pattern_editor.py pattern/PTN00001-01.BIN --summary

# Show event timeline
./pattern_editor.py pattern/PTN00001-01.BIN --timeline

# Export to JSON
./pattern_editor.py pattern/PTN00001-01.BIN --export-json pattern_data.json
```

### 3. **Web Interface** (`web_interface.py`)
```bash
# Start browser-based interface
./web_interface.py
# Then open http://localhost:5000
```

### 4. **Interactive Notebook** (`SP404_MK2_Explorer.ipynb`)
```bash
# For data science and exploration
jupyter notebook SP404_MK2_Explorer.ipynb
```

## 📖 Legacy Usage Examples

### Working with Pattern Files (Original Methods)

Convert binary pattern to readable hex dump:
```bash
xxd -c 8 pattern/PTN00001-01.BIN > pattern/PTN00001-01.TXT
```

Convert hex dump back to binary:
```bash
xxd -r pattern/PTN00001-01.TXT pattern/PTN00001-01.BIN
```

### Editing Pad Configurations (Original Method)

Modify pad BPM using the original Python script:
```bash
python3 padconf/mk2_bpm_edit.py padconf/PADCONF001.BIN 1 12000
# Sets pad 1 to 120.00 BPM (12000 = 120.00)
```

### File Analysis

Compare two binary files:
```bash
bin/hex_diff.sh file1.bin file2.bin
```

Search firmware for specific content:
```bash
firmware/bmp_search.sh      # Find bitmap files
firmware/c_source_search.sh # Find C source files
firmware/wav_search.sh      # Find WAV audio files
```

## 📊 File Format Details

### Pattern File Structure
- **8-byte aligned records**
- **Event records**: Store pad hits with timing, velocity, and pitch
- **End markers**: `008c 0000 0000 0000` indicates pattern end
- **Loop data**: Bar count and loop points stored after pattern data

### PADCONF File Structure (52,000 bytes total)
- **Header**: Project settings, bank BPM values, volumes
- **Pad metadata**: 172 bytes × 160 pads
  - Sample start/end positions
  - BPM, volume, pitch, speed settings
  - Loop mode, gate settings, effects routing
  - Pad linking, mute groups
- **Sample names**: 24 bytes × 160 pads
- **Mark positions**: 60 bytes × 160 pads (15 marks per pad)

### Important Byte Positions (PADCONF)
- `0x0012`: Bank/Project tempo setting
- `0x0013-0x0014`: Project BPM
- `0x0041-0x0068`: Bank BPM values
- `0x0081-0x00A0`: Project name
- `0x00A5+`: Pad metadata (172-byte structures)

## ⚠️ Important Notes

- **Firmware compatibility**: Documentation based on SP-404 MK2 firmware v5.01
- **Backup first**: Always backup original files before modification
- **BPM format**: BPM values stored as integers (multiply display value by 100)
- **Sample limits**: Sample names limited to 23 characters
- **Effects limitation**: Saving EFX (SHIFT+MARK) does not save effects in PADCONF files

## 🎯 Use Cases

This reverse engineering work enables:

- **Custom backup tools**: Create your own project backup utilities
- **Batch editing**: Modify multiple pad settings programmatically  
- **Data analysis**: Understand how the SP-404 MK2 organizes data
- **Alternative interfaces**: Develop custom software for device interaction
- **Format conversion**: Convert between SP-404 MK2 and other formats

## 🤝 Contributing

This is a research project documenting the SP-404 MK2's file formats. Contributions welcome:

- Additional file format documentation
- New analysis tools
- Bug fixes and improvements
- Test cases with different firmware versions

## ⚖️ Legal Notice

This project is for educational and research purposes. All reverse engineering is performed on legally owned hardware and software. Respect Roland's intellectual property and terms of service.

## 📄 File Format Version

Current documentation covers **SP-404 MK2 firmware v5.01**. Other firmware versions may have different formats or byte positions.