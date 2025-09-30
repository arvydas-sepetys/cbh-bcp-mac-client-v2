<?php
// Simple patch to add query parameter routing to existing API

// Read the original file
$original = file_get_contents('/volume1/BCP-Folder-PHI-Test/web/bcp-api.php');

// Find the line with "switch ($path) {"
$search = 'switch ($path) {';
$replacement = '// Fallback for query parameter routing when mod_rewrite not available
    if (empty($path) || $path === "/bcp-api.php") {
        $action = $_GET["action"] ?? "";
        $path = "/bcp-api/" . $action;
    }
    
    switch ($path) {';

// Replace and write back
$modified = str_replace($search, $replacement, $original);
file_put_contents('/volume1/BCP-Folder-PHI-Test/web/bcp-api.php', $modified);

echo "API patched successfully!\n";
?>