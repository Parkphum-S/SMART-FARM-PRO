<?php

declare(strict_types=1);

date_default_timezone_set('Asia/Bangkok');

header('Content-Type: application/json; charset=utf-8');

$response = [
    'application' => 'SMART FARM IoT CONTROL & AI PLATFORM',
    'service' => 'smartfarm-web',
    'status' => 'ok',
    'server_time' => date('c'),
    'timezone' => date_default_timezone_get(),
    'environment' => 'baseline',
];

echo json_encode(
    $response,
    JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE
);
