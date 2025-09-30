<?php
/**
 * Simple API wrapper for query parameter routing
 * This fixes the URL rewriting issue in Web Station port-based config
 */

// Set headers
header('Content-Type: application/json');
header('Cache-Control: no-cache, no-store, must-revalidate');
header('Pragma: no-cache');
header('Expires: 0');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle preflight requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Get the action from query parameter
$action = $_GET['action'] ?? '';
$method = $_SERVER['REQUEST_METHOD'] ?? 'GET';

// Route based on action
switch ($action) {
    case 'health':
        if ($method === 'GET') {
            echo json_encode([
                'status' => 'healthy',
                'timestamp' => date('c'),
                'message' => 'BCP NAS API is operational',
                'csv_file_exists' => is_readable('/volume1/BCP-Folder-PHI-Test/web/data.csv')
            ]);
        } else {
            http_response_code(405);
            echo json_encode(['error' => 'Method not allowed']);
        }
        break;
        
    case 'search':
        if ($method === 'POST') {
            // Get POST data
            $input = json_decode(file_get_contents('php://input'), true);
            $patientId = $input['patientId'] ?? '';
            
            if (empty($patientId)) {
                http_response_code(400);
                echo json_encode(['error' => 'Patient ID is required']);
                exit();
            }
            
            // Search in CSV file  
            $csvFile = '/volume1/BCP-Folder-PHI-Test/web/data.csv';
            if (!is_readable($csvFile)) {
                http_response_code(500);
                echo json_encode(['error' => 'CSV file not found']);
                exit();
            }
            
            $results = [];
            if (($handle = fopen($csvFile, 'r')) !== FALSE) {
                $headers = fgetcsv($handle); // Get header row: [enterprise_member_id,commons_patient_id,section,content]
                
                while (($data = fgetcsv($handle)) !== FALSE) {
                    // Check if this row matches our patient ID (column 1 = commons_patient_id)
                    if (count($data) >= 4 && $data[1] === $patientId) {
                        $section = $data[2]; // section name
                        $content = $data[3]; // content
                        
                        // Organize by sections
                        if (!isset($results[$section])) {
                            $results[$section] = [];
                        }
                        $results[$section][] = $content;
                    }
                }
                fclose($handle);
            }
            
            if (empty($results)) {
                http_response_code(404);
                echo json_encode(['error' => 'Patient not found']);
            } else {
                echo json_encode($results);
            }
        } else {
            http_response_code(405);
            echo json_encode(['error' => 'Method not allowed']);
        }
        break;
        
    default:
        http_response_code(404);
        echo json_encode(['error' => 'Endpoint not found']);
        break;
}
?>