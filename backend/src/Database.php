<?php

declare(strict_types=1);

final class Database
{
    private static ?PDO $connection = null;

    public static function connection(): PDO
    {
        if (self::$connection instanceof PDO) {
            return self::$connection;
        }

        $configFile = '/etc/smartfarm/postgres.env';

        if (!is_readable($configFile)) {
            throw new RuntimeException('Database configuration is unavailable.');
        }

        $config = [];

        foreach (file($configFile, FILE_IGNORE_NEW_LINES) as $line) {
            $line = trim($line);

            if ($line === '' || str_starts_with($line, '#')) {
                continue;
            }

            $separator = strpos($line, '=');

            if ($separator === false) {
                throw new RuntimeException('Invalid database configuration.');
            }

            $key = trim(substr($line, 0, $separator));
            $value = trim(substr($line, $separator + 1));

            if (!in_array($key, [
                'DB_HOST',
                'DB_PORT',
                'DB_DATABASE',
                'DB_USERNAME',
                'DB_PASSWORD',
            ], true)) {
                continue;
            }

            $config[$key] = $value;
        }

        foreach ([
            'DB_HOST',
            'DB_PORT',
            'DB_DATABASE',
            'DB_USERNAME',
            'DB_PASSWORD',
        ] as $key) {
            if (!isset($config[$key]) || $config[$key] === '') {
                throw new RuntimeException('Required database configuration is missing.');
            }
        }

        if (!ctype_digit($config['DB_PORT'])
            || (int) $config['DB_PORT'] < 1
            || (int) $config['DB_PORT'] > 65535) {
            throw new RuntimeException('Invalid database port.');
        }

        $dsn = sprintf(
            'pgsql:host=%s;port=%s;dbname=%s',
            $config['DB_HOST'],
            $config['DB_PORT'],
            $config['DB_DATABASE']
        );

        self::$connection = new PDO(
            $dsn,
            $config['DB_USERNAME'],
            $config['DB_PASSWORD'],
            [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES => false,
                PDO::ATTR_TIMEOUT => 5,
            ]
        );

        return self::$connection;
    }
}
