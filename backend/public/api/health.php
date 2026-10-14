<?php

declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

require_once '/opt/smartfarm/backend/src/Database.php';

try {
    Database::connection();

    http_response_code(200);
    $response = [
        'status' => 'ok',
        'service' => 'smart-farm-pro-api',
        'version' => '1.0.0',
        'database' => 'connected',
    ];
} catch (Throwable $exception) {
    $sqlState = $exception instanceof PDOException
        ? ($exception->errorInfo[0] ?? (string) $exception->getCode())
        : (string) $exception->getCode();

    $driverCode = $exception instanceof PDOException
        ? ($exception->errorInfo[1] ?? 'unknown')
        : 'unknown';

    error_log(
        'Smart Farm Pro health check: database connection failed; exception='
        . get_class($exception)
        . ', sqlstate=' . preg_replace('/[^A-Za-z0-9]/', '', (string) $sqlState)
        . ', driver_code=' . preg_replace('/[^0-9]/', '', (string) $driverCode)
    );

    http_response_code(503);
    $response = [
        'status' => 'error',
        'service' => 'smart-farm-pro-api',
        'version' => '1.0.0',
        'database' => 'unavailable',
    ];
}

echo json_encode($response, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
