<?php

$symbol = $_GET['symbol'] ?? '';
$interval = $_GET['interval'] ?? '';

echo(shell_exec('cd ../sh && npm run backtest:xrp ' . escapeshellarg($symbol) . ' ' . escapeshellarg($interval)));
// echo(shell_exec('pwd'));

?>