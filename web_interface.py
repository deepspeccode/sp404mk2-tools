#!/usr/bin/env python3
"""
Web Interface for SP-404 MK2 Toolkit
Provides a browser-based interface for working with SP-404 MK2 files
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os
import json
import tempfile
from werkzeug.utils import secure_filename
from pathlib import Path
import sys

# Add current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from sp404_toolkit import PadConfig, PatternFile, SP404MK2Error
    from pattern_editor import AdvancedPatternParser
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure sp404_toolkit.py and pattern_editor.py are in the same directory")
    sys.exit(1)

app = Flask(__name__)
app.secret_key = 'sp404mk2_dev_key'  # Change in production
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'bin', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/api/padconf/info/<int:pad_number>', methods=['POST'])
def get_pad_info(pad_number):
    """Get information about a specific pad"""
    try:
        file = request.files['padconf_file']
        if file and allowed_file(file.filename):
            # Save temporarily
            temp_path = os.path.join(tempfile.gettempdir(), secure_filename(file.filename))
            file.save(temp_path)
            
            padconf = PadConfig(temp_path)
            info = padconf.get_pad_info(pad_number)
            
            # Clean up
            os.unlink(temp_path)
            
            return jsonify({'success': True, 'data': info})
        else:
            return jsonify({'success': False, 'error': 'Invalid file'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/padconf/list', methods=['POST'])
def list_all_pads():
    """Get information about all pads"""
    try:
        file = request.files['padconf_file']
        if file and allowed_file(file.filename):
            temp_path = os.path.join(tempfile.gettempdir(), secure_filename(file.filename))
            file.save(temp_path)
            
            padconf = PadConfig(temp_path)
            all_pads = padconf.list_all_pads()
            
            os.unlink(temp_path)
            
            return jsonify({'success': True, 'data': all_pads})
        else:
            return jsonify({'success': False, 'error': 'Invalid file'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/padconf/update', methods=['POST'])
def update_pad_config():
    """Update pad configuration"""
    try:
        file = request.files['padconf_file']
        pad_number = int(request.form['pad_number'])
        
        if file and allowed_file(file.filename):
            temp_path = os.path.join(tempfile.gettempdir(), secure_filename(file.filename))
            file.save(temp_path)
            
            padconf = PadConfig(temp_path)
            
            # Update BPM if provided
            if 'bpm' in request.form:
                bpm = float(request.form['bpm'])
                padconf.set_pad_bpm(pad_number, bpm)
            
            # Update volume if provided
            if 'volume' in request.form:
                volume = int(request.form['volume'])
                padconf.set_pad_volume(pad_number, volume)
            
            # Return updated file
            return send_file(temp_path, as_attachment=True, 
                           download_name=f"modified_{file.filename}")
        else:
            return jsonify({'success': False, 'error': 'Invalid file'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/pattern/info', methods=['POST'])
def get_pattern_info():
    """Get pattern file information"""
    try:
        file = request.files['pattern_file']
        if file and allowed_file(file.filename):
            temp_path = os.path.join(tempfile.gettempdir(), secure_filename(file.filename))
            file.save(temp_path)
            
            parser = AdvancedPatternParser(temp_path)
            summary = parser.get_pattern_summary()
            timeline = parser.get_timeline()
            
            os.unlink(temp_path)
            
            return jsonify({
                'success': True, 
                'data': {
                    'summary': summary,
                    'timeline': timeline
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid file'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/pattern/convert', methods=['POST'])
def convert_pattern():
    """Convert pattern between BIN and TXT formats"""
    try:
        file = request.files['pattern_file']
        convert_to = request.form.get('convert_to', 'txt')
        
        if file and allowed_file(file.filename):
            temp_path = os.path.join(tempfile.gettempdir(), secure_filename(file.filename))
            file.save(temp_path)
            
            pattern = PatternFile(temp_path)
            
            if convert_to == 'txt':
                output_path = pattern.to_hex_dump()
                download_name = file.filename.replace('.BIN', '.TXT')
            else:  # convert to bin
                output_path = temp_path.replace('.TXT', '.BIN')
                pattern.from_hex_dump(temp_path)
                download_name = file.filename.replace('.TXT', '.BIN')
            
            return send_file(output_path, as_attachment=True, download_name=download_name)
        else:
            return jsonify({'success': False, 'error': 'Invalid file'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Create templates directory and HTML template
def create_templates():
    """Create the HTML template for the web interface"""
    os.makedirs('templates', exist_ok=True)
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SP-404 MK2 Toolkit</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #1a1a1a;
            color: #ffffff;
        }
        .container {
            background: #2d2d2d;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        h1, h2 {
            color: #ff6b35;
            border-bottom: 2px solid #ff6b35;
            padding-bottom: 10px;
        }
        .section {
            margin-bottom: 30px;
        }
        .file-input {
            background: #3d3d3d;
            border: 2px dashed #666;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin: 15px 0;
            cursor: pointer;
            transition: border-color 0.3s;
        }
        .file-input:hover {
            border-color: #ff6b35;
        }
        input[type="file"] {
            display: none;
        }
        button {
            background: #ff6b35;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            margin: 5px;
            transition: background-color 0.3s;
        }
        button:hover {
            background: #e55a2b;
        }
        button:disabled {
            background: #666;
            cursor: not-allowed;
        }
        input[type="number"], input[type="text"] {
            background: #3d3d3d;
            border: 1px solid #666;
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            margin: 5px;
        }
        .results {
            background: #1e1e1e;
            border-radius: 6px;
            padding: 15px;
            margin-top: 15px;
            border-left: 4px solid #ff6b35;
        }
        .error {
            background: #4a1a1a;
            border-left-color: #ff4444;
            color: #ffaaaa;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th, td {
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #444;
        }
        th {
            background: #3d3d3d;
            color: #ff6b35;
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎛️ SP-404 MK2 Toolkit</h1>
        <p>Web interface for analyzing and editing SP-404 MK2 files</p>
    </div>

    <div class="grid">
        <!-- Pad Configuration Section -->
        <div class="container">
            <h2>🎚️ Pad Configuration</h2>
            
            <div class="section">
                <h3>Upload PADCONF.BIN</h3>
                <div class="file-input" onclick="document.getElementById('padconf-file').click()">
                    <input type="file" id="padconf-file" accept=".bin" onchange="handlePadconfUpload(this)">
                    <p>Click to select PADCONF.BIN file</p>
                </div>
                <div id="padconf-filename"></div>
            </div>

            <div class="section">
                <h3>Pad Operations</h3>
                <div>
                    <input type="number" id="pad-number" placeholder="Pad Number (1-160)" min="1" max="160">
                    <button onclick="getPadInfo()" id="get-pad-info-btn" disabled>Get Pad Info</button>
                    <button onclick="listAllPads()" id="list-pads-btn" disabled>List All Pads</button>
                </div>
                
                <div style="margin-top: 15px;">
                    <h4>Edit Pad Settings</h4>
                    <input type="number" id="new-bpm" placeholder="BPM (e.g., 120.0)" step="0.01" min="1" max="999.99">
                    <input type="number" id="new-volume" placeholder="Volume (0-127)" min="0" max="127">
                    <button onclick="updatePadSettings()" id="update-pad-btn" disabled>Update Pad</button>
                </div>
            </div>

            <div id="padconf-results" class="results" style="display: none;"></div>
        </div>

        <!-- Pattern Analysis Section -->
        <div class="container">
            <h2>🎵 Pattern Analysis</h2>
            
            <div class="section">
                <h3>Upload Pattern File</h3>
                <div class="file-input" onclick="document.getElementById('pattern-file').click()">
                    <input type="file" id="pattern-file" accept=".bin,.txt" onchange="handlePatternUpload(this)">
                    <p>Click to select Pattern .BIN or .TXT file</p>
                </div>
                <div id="pattern-filename"></div>
            </div>

            <div class="section">
                <h3>Pattern Operations</h3>
                <button onclick="analyzePattern()" id="analyze-pattern-btn" disabled>Analyze Pattern</button>
                <button onclick="convertPattern('txt')" id="convert-to-txt-btn" disabled>Convert to TXT</button>
                <button onclick="convertPattern('bin')" id="convert-to-bin-btn" disabled>Convert to BIN</button>
            </div>

            <div id="pattern-results" class="results" style="display: none;"></div>
        </div>
    </div>

    <!-- Tools Section -->
    <div class="container">
        <h2>🛠️ Additional Tools</h2>
        <div class="section">
            <h3>Quick Actions</h3>
            <button onclick="downloadSampleFiles()">Download Sample Files</button>
            <button onclick="showDocumentation()">View Documentation</button>
            <button onclick="exportProject()">Export Project Data</button>
        </div>
    </div>

    <script>
        let currentPadconfFile = null;
        let currentPatternFile = null;

        function handlePadconfUpload(input) {
            const file = input.files[0];
            if (file) {
                currentPadconfFile = file;
                document.getElementById('padconf-filename').innerHTML = `<strong>Selected:</strong> ${file.name}`;
                
                // Enable buttons
                document.getElementById('get-pad-info-btn').disabled = false;
                document.getElementById('list-pads-btn').disabled = false;
                document.getElementById('update-pad-btn').disabled = false;
            }
        }

        function handlePatternUpload(input) {
            const file = input.files[0];
            if (file) {
                currentPatternFile = file;
                document.getElementById('pattern-filename').innerHTML = `<strong>Selected:</strong> ${file.name}`;
                
                // Enable buttons
                document.getElementById('analyze-pattern-btn').disabled = false;
                document.getElementById('convert-to-txt-btn').disabled = false;
                document.getElementById('convert-to-bin-btn').disabled = false;
            }
        }

        function getPadInfo() {
            const padNumber = document.getElementById('pad-number').value;
            if (!padNumber || !currentPadconfFile) {
                alert('Please select a PADCONF file and enter a pad number');
                return;
            }

            const formData = new FormData();
            formData.append('padconf_file', currentPadconfFile);

            fetch(`/api/padconf/info/${padNumber}`, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                const resultsDiv = document.getElementById('padconf-results');
                if (data.success) {
                    const info = data.data;
                    resultsDiv.innerHTML = `
                        <h4>Pad ${info.pad_number} Information</h4>
                        <table>
                            <tr><td><strong>BPM:</strong></td><td>${info.bpm.toFixed(2)}</td></tr>
                            <tr><td><strong>Volume:</strong></td><td>${info.volume}</td></tr>
                            <tr><td><strong>Gate:</strong></td><td>${info.gate ? 'On' : 'Off'}</td></tr>
                            <tr><td><strong>Loop:</strong></td><td>${info.loop_enabled ? 'On' : 'Off'}</td></tr>
                            <tr><td><strong>Pitch:</strong></td><td>${info.pitch_semitones} semitones</td></tr>
                            <tr><td><strong>Pan:</strong></td><td>${info.pan} (0=center)</td></tr>
                        </table>
                    `;
                    resultsDiv.className = 'results';
                } else {
                    resultsDiv.innerHTML = `<strong>Error:</strong> ${data.error}`;
                    resultsDiv.className = 'results error';
                }
                resultsDiv.style.display = 'block';
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while getting pad info');
            });
        }

        function listAllPads() {
            if (!currentPadconfFile) {
                alert('Please select a PADCONF file');
                return;
            }

            const formData = new FormData();
            formData.append('padconf_file', currentPadconfFile);

            fetch('/api/padconf/list', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                const resultsDiv = document.getElementById('padconf-results');
                if (data.success) {
                    let html = '<h4>All Pad Configurations</h4>';
                    html += '<table><tr><th>Pad</th><th>BPM</th><th>Vol</th><th>Gate</th><th>Loop</th><th>Pitch</th><th>Pan</th></tr>';
                    
                    data.data.forEach(pad => {
                        html += `<tr>
                            <td>${pad.pad_number}</td>
                            <td>${pad.bpm.toFixed(2)}</td>
                            <td>${pad.volume}</td>
                            <td>${pad.gate ? 'On' : 'Off'}</td>
                            <td>${pad.loop_enabled ? 'On' : 'Off'}</td>
                            <td>${pad.pitch_semitones}</td>
                            <td>${pad.pan}</td>
                        </tr>`;
                    });
                    html += '</table>';
                    
                    resultsDiv.innerHTML = html;
                    resultsDiv.className = 'results';
                } else {
                    resultsDiv.innerHTML = `<strong>Error:</strong> ${data.error}`;
                    resultsDiv.className = 'results error';
                }
                resultsDiv.style.display = 'block';
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while listing pads');
            });
        }

        function updatePadSettings() {
            const padNumber = document.getElementById('pad-number').value;
            const newBpm = document.getElementById('new-bpm').value;
            const newVolume = document.getElementById('new-volume').value;
            
            if (!padNumber || !currentPadconfFile) {
                alert('Please select a PADCONF file and enter a pad number');
                return;
            }

            if (!newBpm && !newVolume) {
                alert('Please enter at least one value to update (BPM or Volume)');
                return;
            }

            const formData = new FormData();
            formData.append('padconf_file', currentPadconfFile);
            formData.append('pad_number', padNumber);
            if (newBpm) formData.append('bpm', newBpm);
            if (newVolume) formData.append('volume', newVolume);

            fetch('/api/padconf/update', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    return response.blob();
                }
                throw new Error('Update failed');
            })
            .then(blob => {
                // Download the modified file
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `modified_${currentPadconfFile.name}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                alert('Pad settings updated! Modified file downloaded.');
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while updating pad settings');
            });
        }

        function analyzePattern() {
            if (!currentPatternFile) {
                alert('Please select a pattern file');
                return;
            }

            const formData = new FormData();
            formData.append('pattern_file', currentPatternFile);

            fetch('/api/pattern/info', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                const resultsDiv = document.getElementById('pattern-results');
                if (data.success) {
                    const summary = data.data.summary;
                    const timeline = data.data.timeline;
                    
                    let html = '<h4>Pattern Analysis</h4>';
                    html += `<p><strong>File Size:</strong> ${summary.file_size} bytes</p>`;
                    html += `<p><strong>Events:</strong> ${summary.num_events}</p>`;
                    html += `<p><strong>Bars:</strong> ${summary.metadata.num_bars}</p>`;
                    html += `<p><strong>Loop:</strong> ${summary.metadata.loop_start} - ${summary.metadata.loop_end}</p>`;
                    
                    if (timeline.length > 0) {
                        html += '<h5>Event Timeline</h5>';
                        html += '<table><tr><th>Time (bars)</th><th>Pad</th><th>Velocity</th><th>Pitch</th></tr>';
                        timeline.forEach(event => {
                            html += `<tr>
                                <td>${event.time_bars.toFixed(3)}</td>
                                <td>${event.pad}</td>
                                <td>${event.velocity}</td>
                                <td>${event.pitch}</td>
                            </tr>`;
                        });
                        html += '</table>';
                    }
                    
                    resultsDiv.innerHTML = html;
                    resultsDiv.className = 'results';
                } else {
                    resultsDiv.innerHTML = `<strong>Error:</strong> ${data.error}`;
                    resultsDiv.className = 'results error';
                }
                resultsDiv.style.display = 'block';
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while analyzing pattern');
            });
        }

        function convertPattern(format) {
            if (!currentPatternFile) {
                alert('Please select a pattern file');
                return;
            }

            const formData = new FormData();
            formData.append('pattern_file', currentPatternFile);
            formData.append('convert_to', format);

            fetch('/api/pattern/convert', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    return response.blob();
                }
                throw new Error('Conversion failed');
            })
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = currentPatternFile.name.replace(format === 'txt' ? '.BIN' : '.TXT', format === 'txt' ? '.TXT' : '.BIN');
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                alert(`Pattern converted to ${format.toUpperCase()} format!`);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred during conversion');
            });
        }

        function downloadSampleFiles() {
            alert('Sample files feature coming soon!');
        }

        function showDocumentation() {
            window.open('https://github.com/yourusername/sp404mk2-toolkit', '_blank');
        }

        function exportProject() {
            alert('Project export feature coming soon!');
        }
    </script>
</body>
</html>'''
    
    with open('templates/index.html', 'w') as f:
        f.write(html_content)

if __name__ == "__main__":
    create_templates()
    print("🎛️ SP-404 MK2 Toolkit Web Interface")
    print("📁 Creating templates...")
    print("🚀 Starting web server on http://localhost:5000")
    print("📖 Open your browser and navigate to the URL above")
    print("\nPress Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)