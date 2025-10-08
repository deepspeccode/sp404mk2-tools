#!/usr/bin/env python3
"""
Advanced Pattern Editor for SP-404 MK2
Provides detailed pattern analysis and editing capabilities
"""

import struct
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class PatternEvent:
    """Represents a single pattern event (pad hit)"""
    ticks: int
    pad: int
    chromatic_pitch: int
    velocity: int
    tick_length: int
    
    def to_dict(self) -> Dict:
        return {
            'ticks': self.ticks,
            'pad': self.pad,
            'pad_name': self._pad_to_name(self.pad),
            'chromatic_pitch': self.chromatic_pitch,
            'velocity': self.velocity,
            'tick_length': self.tick_length
        }
    
    def _pad_to_name(self, pad_value: int) -> str:
        """Convert pad hex value to human readable name"""
        # Based on notes: x2F (Pad A1) -> xCE (Pad J16?)
        # This is a simplified mapping - would need more research for complete accuracy
        if 0x2F <= pad_value <= 0x3E:  # Bank A
            return f"A{pad_value - 0x2E}"
        elif 0x3F <= pad_value <= 0x4E:  # Bank B
            return f"B{pad_value - 0x3E}"
        # Add more banks as needed
        else:
            return f"Pad_0x{pad_value:02X}"

class AdvancedPatternParser:
    """Advanced pattern file parser with editing capabilities"""
    
    END_MARKER = b'\x00\x8c\x00\x00\x00\x00\x00\x00'
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        with open(file_path, 'rb') as f:
            self.data = f.read()
        self.events = []
        self.metadata = {}
        self._parse()
    
    def _parse(self):
        """Parse the pattern file"""
        # Find end marker
        end_pos = self.data.find(self.END_MARKER)
        if end_pos == -1:
            raise ValueError("Invalid pattern file: no end marker found")
        
        # Parse events before end marker
        self._parse_events(end_pos)
        
        # Parse metadata after end marker
        self._parse_metadata(end_pos)
    
    def _parse_events(self, end_pos: int):
        """Parse pattern events from the data"""
        pos = 0
        while pos < end_pos:
            # Read 8-byte aligned record
            if pos + 8 > len(self.data):
                break
            
            record = self.data[pos:pos + 8]
            
            # Check if this looks like an event record
            if len(record) == 8 and record[0] != 0xFF:
                ticks = record[0]
                pad = record[1]
                chromatic_pitch = record[3]
                velocity = record[4]
                
                # Tick length from bytes 6-7 (reverse order)
                tick_length = struct.unpack('>H', record[6:8])[0]
                
                if ticks > 0:  # Valid event
                    event = PatternEvent(ticks, pad, chromatic_pitch, velocity, tick_length)
                    self.events.append(event)
            
            pos += 8
    
    def _parse_metadata(self, end_pos: int):
        """Parse pattern metadata after end marker"""
        if end_pos + 16 <= len(self.data):
            post_end = self.data[end_pos + 8:end_pos + 16]
            self.metadata = {
                'num_bars': post_end[0] if len(post_end) > 0 else 0,
                'loop_start': post_end[5] if len(post_end) > 5 else 0,
                'loop_end': post_end[6] if len(post_end) > 6 else 0,
                'end_marker_position': end_pos
            }
    
    def get_pattern_summary(self) -> Dict:
        """Get a summary of the pattern"""
        return {
            'file_path': self.file_path,
            'file_size': len(self.data),
            'num_events': len(self.events),
            'metadata': self.metadata,
            'events': [event.to_dict() for event in self.events]
        }
    
    def export_to_json(self, output_path: str):
        """Export pattern to JSON format"""
        summary = self.get_pattern_summary()
        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def get_timeline(self) -> List[Dict]:
        """Get a timeline view of events"""
        timeline = []
        for event in sorted(self.events, key=lambda e: e.tick_length):
            timeline.append({
                'time_ticks': event.tick_length,
                'time_bars': event.tick_length / 1440,  # 1440 ticks per bar
                'pad': event._pad_to_name(event.pad),
                'velocity': event.velocity,
                'pitch': event.chromatic_pitch
            })
        return timeline

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced Pattern Editor for SP-404 MK2")
    parser.add_argument('pattern_file', help='Pattern .BIN file to analyze')
    parser.add_argument('--export-json', help='Export to JSON file')
    parser.add_argument('--timeline', action='store_true', help='Show timeline view')
    parser.add_argument('--summary', action='store_true', help='Show pattern summary')
    
    args = parser.parse_args()
    
    try:
        parser_obj = AdvancedPatternParser(args.pattern_file)
        
        if args.export_json:
            parser_obj.export_to_json(args.export_json)
            print(f"Pattern exported to JSON: {args.export_json}")
        
        if args.timeline:
            timeline = parser_obj.get_timeline()
            print("\nPattern Timeline:")
            print(f"{'Time (bars)':<12} {'Pad':<8} {'Velocity':<9} {'Pitch':<5}")
            print("-" * 40)
            for event in timeline:
                print(f"{event['time_bars']:<12.3f} {event['pad']:<8} {event['velocity']:<9} {event['pitch']:<5}")
        
        if args.summary or not any([args.export_json, args.timeline]):
            summary = parser_obj.get_pattern_summary()
            print(f"\nPattern Summary:")
            print(f"File: {summary['file_path']}")
            print(f"Size: {summary['file_size']} bytes")
            print(f"Events: {summary['num_events']}")
            print(f"Bars: {summary['metadata']['num_bars']}")
            print(f"Loop: {summary['metadata']['loop_start']} - {summary['metadata']['loop_end']}")
    
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    main()