<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lightweight Charts Customization Tutorial</title>

    <script defer src="./dist/js/chart.js"></script>

    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
        }

        .container {
            display: flex;
            flex-direction: row;
            width: 90vw;
            margin: 20px auto;
            background: #fff;
            border: 1px solid #ccc;
            min-height: 600px;
        }

        .sidebar {
            flex: 0 0 25%;
            max-width: 25%;
            border-right: 1px solid #eee;
            padding: 24px 16px;
            background: #fafafa;
            box-sizing: border-box;
        }

        .main-content {
            flex: 0 0 75%;
            max-width: 75%;
            padding: 24px 24px;
            box-sizing: border-box;
        }

        #chart-container {
            width: 100%;
            height: calc(100vh - 200px);
            position: relative;
            background-color: #fff;
            border: 1px solid #ccc;
        }

        #fileInput {
            margin-bottom: 1em;
        }

        .tree-view {
            font-size: 1em;
            margin-top: 1em;
        }

        .tree-view ul {
            list-style: none;
            padding-left: 1em;
        }

        .tree-view li {
            margin: 0.2em 0;
            cursor: pointer;
        }

        .tree-view li:hover {
            background: #e0e0e0;
        }
    </style>

</head>

<body>
    <div class="container">
        <div class="sidebar">
            <h3>Files in <code>/dist/</code></h3>
            <div id="tree-view" class="tree-view">
                <?php
                function listFilesTree($dir, $base = '') {
                    $files = scandir($dir);
                    ?>
                    <ul>
                        <?php foreach ($files as $file):
                            if ($file === '.' || $file === '..') continue;
                            $fullPath = $dir . DIRECTORY_SEPARATOR . $file;
                            $relativePath = ltrim($base . '/' . $file, '/');
                            if (is_dir($fullPath)): ?>
                                <li><strong><?= htmlspecialchars($file) ?></strong>
                                    <?php listFilesTree($fullPath, $relativePath); ?>
                                </li>
                            <?php else: ?>
                                <li>
                                    <a href="?source=<?= htmlspecialchars($relativePath) ?>">
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
                    echo 'No files found or /dist/file directory missing.';
                }
                ?>
            </div>
        </div>
        <div class="main-content">
            <h2>
                Backtest Chart <span id="chart-title"></span>
            </h2>
            <div id="chart-container"></div>
        </div>
    </div>
</body>

</html>