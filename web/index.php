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
                <div class="card cart-tree-view shadow-sm">
                    <!-- <div class="card-header bg-white">
                        <h5 class="mb-0">Files in <code>/dist/file</code></h5>
                    </div> -->
                    <div class="card-body p-2" id="tree-view">
                        <?php
                        function listFilesTree($dir, $base = '')
                        {
                            $files = scandir($dir);
                            $source = $_GET['source'] ?? '';
                        ?>
                            <ul class="list-unstyled data-list">
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
                                                class="data-link text-decoration-none d-block p-2 <?= ($source === $relativePath ? 'selected bg-dark text-white' : '') ?>"
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
                        <div class="dropdown chart-settings">
                            <button class="btn btn-secondary dropdown-toggle" type="button" id="chartSettings" data-bs-toggle="dropdown" aria-expanded="false">
                                <span>Backtest Chart:</span> <span id="chartTitle"></span>
                            </button>
                            <ul class="dropdown-menu w-100 px-2" aria-labelledby="chartSettings">
                                <li>
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" id="trendLineSeries" checked>
                                        <label class="form-check-label" for="trendLineSeries">Trend Line</label>
                                    </div>
                                </li>
                            </ul>
                        </div>
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