from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os
import time
import zipfile
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('reports', exist_ok=True)

# Global variables to simulate state
analysis_state = {
    'uploaded_file': None,
    'is_analyzing': False,
    'analysis_complete': False,
    'analysis_results': None
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file selected'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    if file and file.filename.lower().endswith('.fastq'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Update analysis state
        analysis_state['uploaded_file'] = {
            'name': filename,
            'size': os.path.getsize(file_path)
        }
        analysis_state['analysis_complete'] = False
        
        return jsonify({
            'success': True, 
            'filename': filename,
            'size': analysis_state['uploaded_file']['size']
        })
    
    return jsonify({'success': False, 'error': 'Please upload a valid .fastq file'})

@app.route('/analyze', methods=['POST'])
def analyze_file():
    if not analysis_state['uploaded_file']:
        return jsonify({'success': False, 'error': 'No file uploaded'})
    
    # Get analysis parameters
    clustering_threshold = request.form.get('clustering_threshold', '97')
    min_sequence_length = request.form.get('min_sequence_length', '100')
    
    # Set analyzing state
    analysis_state['is_analyzing'] = True
    analysis_state['analysis_complete'] = False
    
    # Simulate analysis process (replace with actual analysis)
    # In a real application, you would run this in a background task
    import threading
    def run_analysis():
        time.sleep(3)  # Simulate processing time
        
        # Mock analysis results
        analysis_state['analysis_results'] = {
            'total_sequences': 15420,
            'clusters_found': 127,
            'species_identified': 89,
            'parameters': {
                'clustering_threshold': clustering_threshold,
                'min_sequence_length': min_sequence_length
            }
        }
        
        analysis_state['is_analyzing'] = False
        analysis_state['analysis_complete'] = True
    
    thread = threading.Thread(target=run_analysis)
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': 'Analysis started'})

@app.route('/analysis_status')
def analysis_status():
    return jsonify({
        'is_analyzing': analysis_state['is_analyzing'],
        'analysis_complete': analysis_state['analysis_complete'],
        'results': analysis_state['analysis_results']
    })

@app.route('/download/<report_type>')
def download_report(report_type):
    if not analysis_state['analysis_complete']:
        return jsonify({'success': False, 'error': 'No analysis results available'})
    
    # Create mock report files
    report_dir = 'reports'
    
    if report_type == 'raw':
        # Create a mock zip file with raw data
        zip_filename = 'raw_analysis_output.zip'
        zip_path = os.path.join(report_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            # Add mock files
            zipf.writestr('sequences.fasta', 'Mock sequence data...')
            zipf.writestr('clusters.txt', 'Mock clustering results...')
            zipf.writestr('alignments.txt', 'Mock alignment data...')
        
        return send_file(zip_path, as_attachment=True)
    
    elif report_type == 'summary':
        # Create summary report
        summary_content = f"""
eDNA Analysis Summary Report
============================

Analysis Parameters:
- Clustering Threshold: {analysis_state['analysis_results']['parameters']['clustering_threshold']}%
- Min Sequence Length: {analysis_state['analysis_results']['parameters']['min_sequence_length']}

Results:
- Total Sequences: {analysis_state['analysis_results']['total_sequences']}
- Clusters Found: {analysis_state['analysis_results']['clusters_found']}
- Species Identified: {analysis_state['analysis_results']['species_identified']}

Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        report_path = os.path.join(report_dir, 'summary_report.txt')
        with open(report_path, 'w') as f:
            f.write(summary_content)
        
        return send_file(report_path, as_attachment=True)
    
    elif report_type == 'visualizations':
        # Create mock visualization zip
        zip_filename = 'visualizations.zip'
        zip_path = os.path.join(report_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.writestr('cluster_chart.png', 'Mock PNG data...')
            zipf.writestr('taxonomy_tree.svg', 'Mock SVG data...')
            zipf.writestr('heatmap.png', 'Mock heatmap data...')
        
        return send_file(zip_path, as_attachment=True)
    
    return jsonify({'success': False, 'error': 'Invalid report type'})

@app.route('/reset')
def reset_analysis():
    # Reset analysis state
    analysis_state['uploaded_file'] = None
    analysis_state['is_analyzing'] = False
    analysis_state['analysis_complete'] = False
    analysis_state['analysis_results'] = None
    
    # Clean up uploaded files (optional)
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            os.remove(file_path)
        except OSError:
            pass
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)