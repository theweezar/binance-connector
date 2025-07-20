<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lightweight Charts Customization Tutorial</title>

    <script defer src="./dist/resources/bootstrap.js"></script>
    <script defer src="./dist/resources/chart.js"></script>
    <link rel="stylesheet" href="./dist/resources/chart.css">
</head>

<body class="bg-light main-content">
    <div class="container-fluid py-4 h-100">
        <div class="row h-100">
            <nav class="col-12 col-md-4 col-lg-3 mb-4 mb-md-0">
                <div class="card shadow-sm h-100">
                    <div class="card-header bg-white">
                        <h5 class="mb-0">Files in <code>/dist/file</code></h5>
                    </div>
                    <div class="card-body p-2" id="tree-view">
                        <?php
                        function listFilesTree($dir, $base = '')
                        {
                            $files = scandir($dir);
                        ?>
                            <ul class="list-unstyled ms-2">
                                <?php foreach ($files as $file):
                                    if ($file === '.' || $file === '..') continue;
                                    $fullPath = $dir . DIRECTORY_SEPARATOR . $file;
                                    $relativePath = ltrim($base . '/' . $file, '/');
                                    $fileExp = explode('_', $file);
                                    $symbol = $fileExp[0] ?? '';
                                    $interval = $fileExp[1] ?? '';
                                    if (is_dir($fullPath)): ?>
                                        <li>
                                            <strong><?= htmlspecialchars($file) ?></strong>
                                            <?php listFilesTree($fullPath, $relativePath); ?>
                                        </li>
                                    <?php else: ?>
                                        <li>
                                            <a
                                                class="link-primary text-decoration-none d-block py-2"
                                                href="?source=<?= htmlspecialchars($relativePath) ?>"
                                                data-symbol="<?= htmlspecialchars($symbol) ?>"
                                                data-interval="<?= htmlspecialchars($interval) ?>">
                                                <?= htmlspecialchars($file) ?>
                                            </a>
                                        </li>
                                <?php endif;
                                endforeach; ?>
                            </ul>
                        <?php
                        }
                        $distPath = __DIR__ . '/dist/file';
                        if (is_dir($distPath)) {
                            listFilesTree($distPath);
                        } else {
                            echo '<div class="text-danger">No files found or /dist/file directory missing.</div>';
                        }
                        ?>
                    </div>
                </div>
            </nav>
            <?php
            $source = $_GET['source'] ?? '';
            $srcExp = explode('_', $source);
            $symbol = $srcExp[0] ?? '';
            $interval = $srcExp[1] ?? '';
            ?>
            <main class="col-12 col-md-8 col-lg-9">
                <div class="card shadow-sm h-100">
                    <div class="card-header bg-white d-flex align-items-center">
                        <h5 class="m-0">
                            <span>Backtest Chart:</span> <span id="chart-title"></span>
                        </h5>
                        <div class="ms-auto">
                            <a
                                id="fetch-button"
                                href="/fetch.php?symbol=<?= htmlspecialchars($symbol) ?>&interval=<?= htmlspecialchars($interval) ?>"
                                class="btn btn-primary btn-sm text-center">
                                <span class="text">Fetch</span>
                            </a>
                        </div>
                    </div>
                    <div class="card-body">
                        <div id="chart-container"></div>
                    </div>
                </div>
            </main>
        </div>
    </div>
</body>

</html>