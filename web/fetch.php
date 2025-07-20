<?php

$symbol = $_GET['symbol'] ?? '';
$interval = $_GET['interval'] ?? '';

$cmd = [
    'cd ..',
    'bash ./sh/backtest.sh ' . escapeshellarg($symbol) . ' ' . escapeshellarg($interval)
];

$cmd_join = implode(' && ', $cmd);
$result = shell_exec($cmd_join);
$result = strtolower(trim($result));

$has_price = str_contains($result, 'successfully fetched ' . strtolower($symbol) . '_' . strtolower($interval));
$has_backtest = str_contains($result, 'successfully processed backtest');

$response = [
    'symbol' => $symbol,
    'interval' => $interval,
    'success' => !!($has_price && $has_backtest)
];

header('Content-Type: application/json');
echo json_encode($response);

?>