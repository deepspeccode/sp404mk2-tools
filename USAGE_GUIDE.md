# SP-404 MK2 Toolkit Usage Guide

## 🚀 Quick Start

### 1. Setup
```bash
# Run the setup script
./setup.sh

# Or install dependencies manually
pip3 install flask werkzeug
```

### 2. Choose Your Interface

#### A. Command Line Interface (Recommended)
The main toolkit provides comprehensive CLI functionality:

```bash
# Get help
./sp404_toolkit.py --help

# Pad configuration examples
./sp404_toolkit.py padconf info padconf/PADCONF001.BIN --pad 1
./sp404_toolkit.py padconf set-bpm padconf/PADCONF001.BIN --pad 1 --bpm 120.0
./sp404_toolkit.py padconf list padconf/PADCONF001.BIN

# Pattern analysis examples
./sp404_toolkit.py pattern info pattern/PTN00001-01.BIN
./sp404_toolkit.py pattern to-hex pattern/PTN00001-01.BIN
```

#### B. Advanced Pattern Editor
For detailed pattern analysis:

```bash
# Analyze a pattern file
./pattern_editor.py pattern/PTN00001-01.BIN --summary

# Show timeline of events
./pattern_editor.py pattern/PTN00001-01.BIN --timeline

# Export to JSON for further analysis
./pattern_editor.py pattern/PTN00001-01.BIN --export-json pattern_data.json
```

#### C. Web Interface
For a user-friendly browser interface:

```bash
# Start the web server
./web_interface.py

# Open http://localhost:5000 in your browser
```

#### D. Interactive Notebook
For data science and exploration:

```bash
# Install Jupyter if not already installed
pip3 install jupyter matplotlib pandas numpy

# Start Jupyter
jupyter notebook SP404_MK2_Explorer.ipynb
```

## 📚 Detailed Usage Examples

### Working with Pad Configurations

#### Reading Pad Information
```python
from sp404_toolkit import PadConfig

# Load a PADCONF file
padconf = PadConfig('padconf/PADCONF001.BIN')

# Get info for a specific pad
info = padconf.get_pad_info(1)
print(f"Pad 1 BPM: {info['bpm']}")
print(f"Pad 1 Volume: {info['volume']}")

# Get info for all pads
all_pads = padconf.list_all_pads()
```

#### Modifying Pad Settings
```python
# Change pad BPM
padconf.set_pad_bpm(1, 140.0)  # Set pad 1 to 140 BPM

# Change pad volume  
padconf.set_pad_volume(1, 100)  # Set pad 1 volume to 100
```

### Working with Pattern Files

#### Basic Pattern Operations
```python
from pattern_editor import AdvancedPatternParser

# Load and analyze a pattern
parser = AdvancedPatternParser('pattern/PTN00001-01.BIN')
summary = parser.get_pattern_summary()

print(f"Pattern has {summary['num_events']} events")
print(f"Pattern length: {summary['metadata']['num_bars']} bars")

# Get timeline view
timeline = parser.get_timeline()
for event in timeline[:5]:  # First 5 events
    print(f"Bar {event['time_bars']:.3f}: {event['pad']} (vel={event['velocity']})")
```

#### Converting Pattern Formats
```python
from sp404_toolkit import PatternFile

# Convert binary to hex dump
pattern = PatternFile('pattern/PTN00001-01.BIN')
hex_file = pattern.to_hex_dump()  # Creates PTN00001-01.TXT

# Convert hex dump back to binary
pattern.from_hex_dump('pattern/PTN00001-01.TXT')
```

### Backup and Restore Operations

```bash
# Create a backup of your project
./sp404_toolkit.py backup create my_project.sp404backup padconf/PADCONF001.BIN pattern/

# Restore a backup
./sp404_toolkit.py backup restore my_project.sp404backup ./restored_project/
```

## 🔧 Advanced Usage

### Batch Processing Multiple Files

```python
from pathlib import Path
from sp404_toolkit import PadConfig

# Process all PADCONF files
for padconf_file in Path('padconf').glob('PADCONF*.BIN'):
    padconf = PadConfig(str(padconf_file))
    
    # Set all pads to 120 BPM
    for pad in range(1, 161):
        try:
            padconf.set_pad_bpm(pad, 120.0)
        except Exception as e:
            print(f"Error setting pad {pad}: {e}")
    
    print(f"Updated {padconf_file}")
```

### Custom Analysis Scripts

```python
import struct

def analyze_unknown_bytes(padconf_file, pad_number):
    """Analyze unknown byte regions in PADCONF files"""
    padconf = PadConfig(padconf_file)
    
    # Read raw pad data
    pad_offset = padconf._get_pad_offset(pad_number)
    raw_data = padconf._read_bytes(pad_offset, 172)
    
    # Analyze unknown regions
    unknown_regions = [
        (0x14, 4),  # bytes 0x14-0x17
        (0x20, 2),  # bytes 0x20-0x21  
        (0x2C, 4),  # bytes 0x2C-0x2F
    ]
    
    for offset, length in unknown_regions:
        data = raw_data[offset:offset+length]
        print(f"Unknown region 0x{offset:02X}-0x{offset+length-1:02X}: {data.hex()}")

# Example usage
# analyze_unknown_bytes('padconf/PADCONF001.BIN', 1)
```

## 🌐 Web Interface Features

The web interface (`./web_interface.py`) provides:

1. **File Upload**: Drag and drop PADCONF.BIN and pattern files
2. **Pad Analysis**: View and edit individual pad settings
3. **Pattern Visualization**: Analyze pattern events and timeline
4. **File Conversion**: Convert between BIN and TXT formats
5. **Batch Operations**: Process multiple files at once

### Web Interface Screenshots

- **Dashboard**: Main interface with file upload areas
- **Pad Editor**: Modify BPM, volume, and other pad settings
- **Pattern Analyzer**: View pattern events and timeline
- **File Converter**: Convert between binary and text formats

## 🐛 Troubleshooting

### Common Issues

1. **File not found errors**
   - Ensure file paths are correct
   - Check that files exist in the expected directories

2. **Permission errors**
   - Run `chmod +x *.py` to make scripts executable
   - Ensure you have write permissions for file modifications

3. **Import errors**
   - Make sure all required packages are installed: `pip3 install -r requirements.txt`
   - Verify Python 3 is being used

4. **Web interface not loading**
   - Check that Flask is installed: `pip3 install flask`
   - Ensure port 5000 is available
   - Try accessing via `http://127.0.0.1:5000` instead of `localhost`

### Getting Help

- Check the inline help: `./sp404_toolkit.py --help`
- Review the source code comments
- Examine the original notes files in `pattern/pattern_notes.txt` and `padconf/mk2_notes.txt`

## 🎯 Use Cases

### 1. **Project Backup and Management**
```bash
# Create timestamped backups
./sp404_toolkit.py backup create "backup_$(date +%Y%m%d_%H%M%S).sp404backup" padconf/PADCONF001.BIN pattern/
```

### 2. **Batch BPM Changes**
```python
# Set all pads in a bank to the same BPM
padconf = PadConfig('padconf/PADCONF001.BIN')
for pad in range(1, 17):  # Bank A (pads 1-16)
    padconf.set_pad_bpm(pad, 128.0)
```

### 3. **Pattern Analysis and Comparison**
```bash
# Compare multiple patterns
for file in pattern/PTN00001-*.BIN; do
    echo "=== $file ==="
    ./pattern_editor.py "$file" --summary
done
```

### 4. **Data Export for External Tools**
```bash
# Export pattern data to JSON for use in other DAWs
./pattern_editor.py pattern/PTN00001-01.BIN --export-json pattern_for_daw.json
```

## 🔬 Research and Development

This toolkit is designed for reverse engineering research. Key areas for further development:

1. **Unknown byte regions**: Many byte positions in PADCONF files are not yet understood
2. **Effects data**: EFX settings are not saved in PADCONF files
3. **Sample data**: Understanding how sample files are referenced and managed
4. **Pattern events**: More detailed understanding of event encoding
5. **Firmware analysis**: Using the firmware search tools to understand internal operations

### Contributing to Research

If you discover new byte meanings or file format details:

1. Document your findings in the notes files
2. Add test cases to verify your discoveries
3. Update the parsing classes with new functionality
4. Share your findings with the community

## 📝 File Format Reference

### PADCONF.BIN Structure (52,000 bytes)
- **Header** (0x00-0xA4): Project settings, bank BPMs, volumes
- **Pad Metadata** (0xA5+): 172 bytes × 160 pads
- **Sample Names**: 24 bytes × 160 pads  
- **Mark Positions**: 60 bytes × 160 pads

### Pattern File Structure
- **Event Records**: 8-byte aligned pad trigger data
- **End Marker**: `008c 0000 0000 0000`
- **Pattern Metadata**: Bars, loop points after end marker

### Key Data Types
- **BPM**: Integer × 100 (120.00 BPM = 12000)
- **Timing**: 1440 ticks = 1 bar (4/4 time)
- **Volume**: 0-127 range
- **Pan**: 0x40 = center, ±63 range