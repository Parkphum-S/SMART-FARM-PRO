<?php

declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

http_response_code(200);

echo json_encode([
    'status' => 'ok',
    'service' => 'smart-farm-pro-api',
    'version' => '1.0.0',
    'database' => 'not_configured',
], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
