#!/usr/bin/env python3
"""
SP-404 MK2 Toolkit
A comprehensive tool for working with SP-404 MK2 files (patterns, pad configurations, etc.)
"""

import argparse
import struct
import os
import sys
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class SP404MK2Error(Exception):
    """Base exception for SP-404 MK2 toolkit errors"""
    pass

class PadConfig:
    """Class to handle PADCONF.BIN file operations"""
    
    # Byte positions based on mk2_notes.txt
    HEADER_SIZE = 0xA5
    PAD_METADATA_SIZE = 172
    PAD_NAME_SIZE = 24
    MARKS_PER_PAD = 15
    MARKS_SIZE_PER_PAD = 60
    
    # Pad metadata offsets (relative to pad start)
    OFFSETS = {
        'sample_start': 0x00,
        'sample_end': 0x04, 
        'volume': 0x08,
        'gate': 0x0C,
        'loop_enabled': 0x10,
        'mute_group': 0x18,
        'bpm_sync': 0x1C,
        'bpm': 0x22,  # 2 bytes
        'one_shot_mode': 0x24,
        'loop_point': 0x28,
        'pitch': 0x30,
        'fine': 0x34,
        'loop_mode': 0x38,
        'speed': 0x3C,
        'vinyl': 0x40,
        'pan': 0x44,
        'pad_link': 0x48,
        'bus_route': 0x4C,
        'attack': 0x54,
        'hold': 0x58,
        'release': 0x5C
    }
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        if not os.path.exists(file_path):
            raise SP404MK2Error(f"File not found: {file_path}")
    
    def _get_pad_offset(self, pad_number: int) -> int:
        """Get the byte offset for a specific pad (1-160)"""
        if not 1 <= pad_number <= 160:
            raise SP404MK2Error("Pad number must be between 1 and 160")
        return self.HEADER_SIZE + ((pad_number - 1) * self.PAD_METADATA_SIZE)
    
    def _read_bytes(self, offset: int, length: int) -> bytes:
        """Read bytes from the file at specified offset"""
        with open(self.file_path, 'rb') as f:
            f.seek(offset)
            return f.read(length)
    
    def _write_bytes(self, offset: int, data: bytes):
        """Write bytes to the file at specified offset"""
        with open(self.file_path, 'r+b') as f:
            f.seek(offset)
            f.write(data)
    
    def get_pad_bpm(self, pad_number: int) -> float:
        """Get the BPM for a specific pad"""
        pad_offset = self._get_pad_offset(pad_number)
        bpm_offset = pad_offset + self.OFFSETS['bpm']
        bpm_bytes = self._read_bytes(bpm_offset, 2)
        bpm_int = struct.unpack('>H', bpm_bytes)[0]  # Big endian 16-bit
        return bpm_int / 100.0
    
    def set_pad_bpm(self, pad_number: int, bpm: float):
        """Set the BPM for a specific pad"""
        if not 1.0 <= bpm <= 999.99:
            raise SP404MK2Error("BPM must be between 1.00 and 999.99")
        
        pad_offset = self._get_pad_offset(pad_number)
        bpm_offset = pad_offset + self.OFFSETS['bpm']
        bpm_int = int(bpm * 100)
        bpm_bytes = struct.pack('>H', bpm_int)
        self._write_bytes(bpm_offset, bpm_bytes)
    
    def get_pad_volume(self, pad_number: int) -> int:
        """Get the volume for a specific pad (0-127)"""
        pad_offset = self._get_pad_offset(pad_number)
        volume_offset = pad_offset + self.OFFSETS['volume']
        volume_bytes = self._read_bytes(volume_offset, 4)
        return struct.unpack('>I', volume_bytes)[0] & 0x7F
    
    def set_pad_volume(self, pad_number: int, volume: int):
        """Set the volume for a specific pad (0-127)"""
        if not 0 <= volume <= 127:
            raise SP404MK2Error("Volume must be between 0 and 127")
        
        pad_offset = self._get_pad_offset(pad_number)
        volume_offset = pad_offset + self.OFFSETS['volume']
        volume_bytes = struct.pack('>I', volume)
        self._write_bytes(volume_offset, volume_bytes)
    
    def get_pad_info(self, pad_number: int) -> Dict:
        """Get comprehensive information about a pad"""
        pad_offset = self._get_pad_offset(pad_number)
        
        info = {
            'pad_number': pad_number,
            'bpm': self.get_pad_bpm(pad_number),
            'volume': self.get_pad_volume(pad_number)
        }
        
        # Get additional properties
        gate_bytes = self._read_bytes(pad_offset + self.OFFSETS['gate'], 4)
        info['gate'] = struct.unpack('>I', gate_bytes)[0] == 1
        
        loop_bytes = self._read_bytes(pad_offset + self.OFFSETS['loop_enabled'], 4)
        info['loop_enabled'] = struct.unpack('>I', loop_bytes)[0] == 0x7FFFFFFF
        
        pitch_bytes = self._read_bytes(pad_offset + self.OFFSETS['pitch'], 4)
        info['pitch_semitones'] = struct.unpack('>I', pitch_bytes)[0]
        
        pan_bytes = self._read_bytes(pad_offset + self.OFFSETS['pan'], 4)
        pan_value = struct.unpack('>I', pan_bytes)[0]
        info['pan'] = pan_value - 0x40  # Center is 0x40
        
        return info
    
    def list_all_pads(self) -> List[Dict]:
        """Get information for all 160 pads"""
        return [self.get_pad_info(i) for i in range(1, 161)]

class PatternFile:
    """Class to handle pattern file operations"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        if not os.path.exists(file_path):
            raise SP404MK2Error(f"File not found: {file_path}")
    
    def to_hex_dump(self, output_path: Optional[str] = None) -> str:
        """Convert pattern file to hex dump format"""
        if output_path is None:
            output_path = self.file_path.replace('.BIN', '.TXT')
        
        os.system(f'xxd -c 8 "{self.file_path}" > "{output_path}"')
        return output_path
    
    def from_hex_dump(self, hex_file_path: str):
        """Convert hex dump back to binary pattern file"""
        os.system(f'xxd -r "{hex_file_path}" "{self.file_path}"')
    
    def get_pattern_info(self) -> Dict:
        """Extract basic pattern information"""
        with open(self.file_path, 'rb') as f:
            data = f.read()
        
        # Look for end marker
        end_marker = b'\x00\x8c\x00\x00\x00\x00\x00\x00'
        end_pos = data.find(end_marker)
        
        info = {
            'file_size': len(data),
            'end_marker_position': end_pos if end_pos != -1 else None,
            'has_valid_end_marker': end_pos != -1
        }
        
        if end_pos != -1 and len(data) > end_pos + 8:
            # Read pattern metadata after end marker
            post_end = data[end_pos + 8:end_pos + 16]
            if len(post_end) >= 8:
                info['num_bars'] = post_end[0]
                info['loop_start'] = post_end[5] 
                info['loop_end'] = post_end[6]
        
        return info

def main():
    parser = argparse.ArgumentParser(
        description="SP-404 MK2 Toolkit - Tools for working with SP-404 MK2 files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Pad configuration operations
  %(prog)s padconf info padconf/PADCONF001.BIN --pad 1
  %(prog)s padconf set-bpm padconf/PADCONF001.BIN --pad 1 --bpm 120.0
  %(prog)s padconf set-volume padconf/PADCONF001.BIN --pad 1 --volume 100
  %(prog)s padconf list padconf/PADCONF001.BIN
  
  # Pattern operations  
  %(prog)s pattern info pattern/PTN00001-01.BIN
  %(prog)s pattern to-hex pattern/PTN00001-01.BIN
  %(prog)s pattern from-hex pattern/PTN00001-01.TXT
  
  # Backup operations
  %(prog)s backup create my_project.sp404backup padconf/PADCONF001.BIN pattern/
  %(prog)s backup restore my_project.sp404backup ./restored/
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Pad configuration commands
    padconf_parser = subparsers.add_parser('padconf', help='Pad configuration operations')
    padconf_subparsers = padconf_parser.add_subparsers(dest='padconf_action')
    
    # padconf info
    info_parser = padconf_subparsers.add_parser('info', help='Get pad information')
    info_parser.add_argument('file', help='PADCONF.BIN file path')
    info_parser.add_argument('--pad', type=int, help='Specific pad number (1-160)')
    
    # padconf set-bpm
    bpm_parser = padconf_subparsers.add_parser('set-bpm', help='Set pad BPM')
    bpm_parser.add_argument('file', help='PADCONF.BIN file path')
    bpm_parser.add_argument('--pad', type=int, required=True, help='Pad number (1-160)')
    bpm_parser.add_argument('--bpm', type=float, required=True, help='BPM value (e.g., 120.0)')
    
    # padconf set-volume
    vol_parser = padconf_subparsers.add_parser('set-volume', help='Set pad volume')
    vol_parser.add_argument('file', help='PADCONF.BIN file path')
    vol_parser.add_argument('--pad', type=int, required=True, help='Pad number (1-160)')
    vol_parser.add_argument('--volume', type=int, required=True, help='Volume (0-127)')
    
    # padconf list
    list_parser = padconf_subparsers.add_parser('list', help='List all pad configurations')
    list_parser.add_argument('file', help='PADCONF.BIN file path')
    list_parser.add_argument('--format', choices=['table', 'json'], default='table', help='Output format')
    
    # Pattern commands
    pattern_parser = subparsers.add_parser('pattern', help='Pattern file operations')
    pattern_subparsers = pattern_parser.add_subparsers(dest='pattern_action')
    
    # pattern info
    pinfo_parser = pattern_subparsers.add_parser('info', help='Get pattern information')
    pinfo_parser.add_argument('file', help='Pattern file path')
    
    # pattern to-hex
    tohex_parser = pattern_subparsers.add_parser('to-hex', help='Convert pattern to hex dump')
    tohex_parser.add_argument('file', help='Pattern .BIN file path')
    tohex_parser.add_argument('--output', help='Output .TXT file path')
    
    # pattern from-hex
    fromhex_parser = pattern_subparsers.add_parser('from-hex', help='Convert hex dump to pattern')
    fromhex_parser.add_argument('file', help='Hex dump .TXT file path')
    fromhex_parser.add_argument('--output', help='Output .BIN file path')
    
    # Backup commands
    backup_parser = subparsers.add_parser('backup', help='Backup and restore operations')
    backup_subparsers = backup_parser.add_subparsers(dest='backup_action')
    
    # backup create
    create_parser = backup_subparsers.add_parser('create', help='Create backup')
    create_parser.add_argument('output', help='Backup file path')
    create_parser.add_argument('padconf', help='PADCONF.BIN file path')
    create_parser.add_argument('pattern_dir', help='Pattern directory path')
    
    # backup restore
    restore_parser = backup_subparsers.add_parser('restore', help='Restore backup')
    restore_parser.add_argument('backup_file', help='Backup file path')
    restore_parser.add_argument('output_dir', help='Output directory')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'padconf':
            handle_padconf_command(args)
        elif args.command == 'pattern':
            handle_pattern_command(args)
        elif args.command == 'backup':
            handle_backup_command(args)
    except SP404MK2Error as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

def handle_padconf_command(args):
    """Handle pad configuration commands"""
    padconf = PadConfig(args.file)
    
    if args.padconf_action == 'info':
        if args.pad:
            info = padconf.get_pad_info(args.pad)
            print(f"Pad {args.pad} Information:")
            print(f"  BPM: {info['bpm']:.2f}")
            print(f"  Volume: {info['volume']}")
            print(f"  Gate: {'On' if info['gate'] else 'Off'}")
            print(f"  Loop: {'On' if info['loop_enabled'] else 'Off'}")
            print(f"  Pitch: {info['pitch_semitones']} semitones")
            print(f"  Pan: {info['pan']} (0=center)")
        else:
            print("Please specify --pad number for detailed info")
    
    elif args.padconf_action == 'set-bpm':
        old_bpm = padconf.get_pad_bpm(args.pad)
        padconf.set_pad_bpm(args.pad, args.bpm)
        print(f"Pad {args.pad} BPM changed from {old_bpm:.2f} to {args.bpm:.2f}")
    
    elif args.padconf_action == 'set-volume':
        old_volume = padconf.get_pad_volume(args.pad)
        padconf.set_pad_volume(args.pad, args.volume)
        print(f"Pad {args.pad} volume changed from {old_volume} to {args.volume}")
    
    elif args.padconf_action == 'list':
        all_pads = padconf.list_all_pads()
        if args.format == 'json':
            import json
            print(json.dumps(all_pads, indent=2))
        else:
            print(f"{'Pad':<4} {'BPM':<8} {'Vol':<4} {'Gate':<5} {'Loop':<5} {'Pitch':<6} {'Pan':<4}")
            print("-" * 50)
            for pad in all_pads:
                print(f"{pad['pad_number']:<4} {pad['bpm']:<8.2f} {pad['volume']:<4} "
                      f"{'On' if pad['gate'] else 'Off':<5} "
                      f"{'On' if pad['loop_enabled'] else 'Off':<5} "
                      f"{pad['pitch_semitones']:<6} {pad['pan']:<4}")

def handle_pattern_command(args):
    """Handle pattern file commands"""
    pattern = PatternFile(args.file)
    
    if args.pattern_action == 'info':
        info = pattern.get_pattern_info()
        print(f"Pattern File: {args.file}")
        print(f"  File Size: {info['file_size']} bytes")
        print(f"  Has End Marker: {info['has_valid_end_marker']}")
        if info['end_marker_position']:
            print(f"  End Marker Position: 0x{info['end_marker_position']:08X}")
        if 'num_bars' in info:
            print(f"  Number of Bars: {info['num_bars']}")
            print(f"  Loop Start: {info['loop_start']}")
            print(f"  Loop End: {info['loop_end']}")
    
    elif args.pattern_action == 'to-hex':
        output_path = pattern.to_hex_dump(args.output)
        print(f"Converted to hex dump: {output_path}")
    
    elif args.pattern_action == 'from-hex':
        output_path = args.output or args.file.replace('.TXT', '.BIN')
        pattern_out = PatternFile(output_path)
        pattern_out.from_hex_dump(args.file)
        print(f"Converted from hex dump: {output_path}")

def handle_backup_command(args):
    """Handle backup and restore commands"""
    import tarfile
    import json
    from datetime import datetime
    
    if args.backup_action == 'create':
        # Create backup archive
        backup_info = {
            'created': datetime.now().isoformat(),
            'toolkit_version': '1.0',
            'files': {}
        }
        
        with tarfile.open(args.output, 'w:gz') as tar:
            # Add PADCONF file
            if os.path.exists(args.padconf):
                tar.add(args.padconf, arcname='PADCONF.BIN')
                backup_info['files']['padconf'] = 'PADCONF.BIN'
                print(f"Added pad configuration: {args.padconf}")
            
            # Add pattern files
            pattern_path = Path(args.pattern_dir)
            if pattern_path.exists():
                pattern_files = []
                for pattern_file in pattern_path.glob('*.BIN'):
                    arcname = f"patterns/{pattern_file.name}"
                    tar.add(str(pattern_file), arcname=arcname)
                    pattern_files.append(arcname)
                backup_info['files']['patterns'] = pattern_files
                print(f"Added {len(pattern_files)} pattern files")
            
            # Add backup metadata
            metadata = json.dumps(backup_info, indent=2).encode()
            import io
            metadata_file = io.BytesIO(metadata)
            tarinfo = tarfile.TarInfo(name='backup_info.json')
            tarinfo.size = len(metadata)
            tar.addfile(tarinfo, metadata_file)
        
        print(f"Backup created: {args.output}")
    
    elif args.backup_action == 'restore':
        # Extract backup archive
        os.makedirs(args.output_dir, exist_ok=True)
        
        with tarfile.open(args.backup_file, 'r:gz') as tar:
            tar.extractall(args.output_dir)
        
        print(f"Backup restored to: {args.output_dir}")

if __name__ == "__main__":
    main()