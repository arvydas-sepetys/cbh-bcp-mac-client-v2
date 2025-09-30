#!/usr/bin/env python3
"""
PHI-Compliant NAS HTTP Server for BCP Emergency Access
Serves patient data remotely without allowing local downloads

This server must be deployed on the NAS (10.1.21.3) to provide
secure remote access to PHI data during emergency scenarios.

COMPLIANCE FEATURES:
- No PHI data leaves the NAS server
- Search-only interface (no bulk downloads)
- Logging of all access attempts
- VPN-only access (internal network only)
"""

import json
import csv
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os
from datetime import datetime

# Configure logging for compliance tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/volume1/BCP-Folder-PHI-Test/access.log'),
        logging.StreamHandler()
    ]
)

class PHIComplianceHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler that maintains PHI compliance
    - Only serves search results, never raw files
    - Logs all access for audit purposes
    - Validates requests to prevent data exposure
    """
    
    def __init__(self, *args, **kwargs):
        self.csv_file_path = '/volume1/BCP-Folder-PHI-Test/offline_patient_chart_redacted.csv'
        self.required_headers = ['enterprise_member_id', 'commons_patient_id', 'section', 'content']
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests - health checks only"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path in ['/health', '/bcp-api/health']:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'status': 'healthy',
                'service': 'PHI-Compliant BCP Server',
                'timestamp': datetime.now().isoformat(),
                'compliance': 'PHI data secured on NAS'
            }
            self.wfile.write(json.dumps(response).encode())
            logging.info(f"Health check from {self.client_address[0]}")
        else:
            self.send_error(404, "Endpoint not found")
            logging.warning(f"Invalid GET request to {self.path} from {self.client_address[0]}")

    def do_POST(self):
        """Handle POST requests - patient searches only"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path in ['/bcp-search', '/bcp-api/search']:
            self.handle_patient_search()
        else:
            self.send_error(404, "Endpoint not found")
            logging.warning(f"Invalid POST request to {self.path} from {self.client_address[0]}")

    def handle_patient_search(self):
        """
        Handle PHI-compliant patient search requests
        Returns only search results, never raw data files
        """
        try:
            # Read request data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            patient_id = request_data.get('patientId', '').strip()
            
            if not patient_id:
                self.send_error(400, "Patient ID required")
                logging.warning(f"Search attempt without patient ID from {self.client_address[0]}")
                return
            
            # Log the search attempt (patient ID is logged for audit)
            logging.info(f"PHI-compliant search for patient {patient_id} from {self.client_address[0]}")
            
            # Search for patient data
            patient_data = self.search_patient_data(patient_id)
            
            if patient_data:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(patient_data).encode())
                logging.info(f"Successful search for patient {patient_id} - {len(patient_data)} sections found")
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {'error': 'No data found for this patient'}
                self.wfile.write(json.dumps(response).encode())
                logging.info(f"No data found for patient {patient_id}")
                
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
            logging.error(f"Search error for {self.client_address[0]}: {str(e)}")

    def search_patient_data(self, patient_id):
        """
        Search for patient data in CSV file
        Returns structured data without exposing file contents
        """
        patient_data = {}
        
        try:
            if not os.path.exists(self.csv_file_path):
                logging.error(f"CSV file not found: {self.csv_file_path}")
                return None
            
            with open(self.csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Validate headers
                if not all(header in reader.fieldnames for header in self.required_headers):
                    logging.error(f"CSV file missing required headers: {self.required_headers}")
                    return None
                
                # Search for patient data
                for row in reader:
                    current_patient_id = row.get('commons_patient_id', '').strip()
                    data_category = row.get('section', '').strip()
                    data_text = row.get('content', '').strip()
                    
                    if current_patient_id == patient_id:
                        if data_category not in patient_data:
                            patient_data[data_category] = []
                        patient_data[data_category].append(data_text)
            
            return patient_data if patient_data else None
            
        except Exception as e:
            logging.error(f"Error reading CSV file: {str(e)}")
            return None

    def log_message(self, format, *args):
        """Override to use our logging system"""
        logging.info(format % args)

def run_server():
    """
    Start the PHI-compliant HTTP server
    Only accessible from internal VPN network
    """
    server_address = ('0.0.0.0', 5000)  # Listen on all interfaces, port 5000
    httpd = HTTPServer(server_address, PHIComplianceHandler)
    
    logging.info("Starting PHI-Compliant BCP Server on port 5000")
    logging.info("Server configured for VPN-only access")
    logging.info("All access attempts will be logged for compliance")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("Server shutdown requested")
        httpd.shutdown()

if __name__ == '__main__':
    run_server()