<?php
// Debug file to test CSV access
header('Content-Type: application/json');

$csvFile = '/volume1/BCP-Folder-PHI-Test/BCP Emergency Offline Repository/Offline Patient Chart/offline_patient_chart_redacted.csv';

echo json_encode([
    'file_path' => $csvFile,
    'file_exists' => file_exists($csvFile),
    'is_readable' => is_readable($csvFile),
    'realpath' => realpath($csvFile),
    'ls_test' => exec('ls -la "' . $csvFile . '"')
]);
?>