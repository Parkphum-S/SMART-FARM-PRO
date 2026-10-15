<?php

declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

require_once dirname(__DIR__, 2) . '/src/Database.php';

try {
    $sql = <<<'SQL'
        SELECT
            s.id,
            s.farm_id,
            s.zone_id,
            s.device_id,
            s.sensor_code,
            s.sensor_type,
            s.name,
            s.is_active,
            r.recorded_at,
            r.temperature_c,
            r.humidity_pct,
            r.value
        FROM app.sensors AS s
        LEFT JOIN LATERAL (
            SELECT
                recorded_at,
                temperature_c,
                humidity_pct,
                value
            FROM app.sensor_readings
            WHERE sensor_id = s.id
            ORDER BY recorded_at DESC, id DESC
            LIMIT 1
        ) AS r ON TRUE
        ORDER BY s.id
        SQL;

    $sensors = Database::connection()->query($sql)->fetchAll();

    http_response_code(200);
    $response = [
        'status' => 'ok',
        'service' => 'smart-farm-pro-api',
        'count' => count($sensors),
        'data' => $sensors,
    ];
} catch (Throwable $exception) {
    $sqlState = $exception instanceof PDOException
        ? ($exception->errorInfo[0] ?? (string) $exception->getCode())
        : (string) $exception->getCode();

    error_log(
        'Smart Farm Pro sensors API failed; exception='
        . get_class($exception)
        . ', sqlstate='
        . preg_replace('/[^A-Za-z0-9]/', '', $sqlState)
    );

    http_response_code(503);
    $response = [
        'status' => 'error',
        'service' => 'smart-farm-pro-api',
        'message' => 'Sensor data is temporarily unavailable.',
    ];
}

echo json_encode(
    $response,
    JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE
);
