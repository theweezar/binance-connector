<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Strategy Markdown</title>

    <script defer src="./dist/resources/bootstrap.js"></script>
    <script defer src="./dist/resources/md.js"></script>
    <link rel="stylesheet" href="./dist/resources/chart.css">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Nunito:ital,wght@0,200..1000;1,200..1000&display=swap" rel="stylesheet">

    <style>
        .nunito-normal {
            font-family: "Nunito", sans-serif;
            font-optical-sizing: auto;
            font-weight: normal;
            font-style: normal;
        }

        body.bg-dark {
            background-color: #181a1b !important;
            color: #e0e0e0;
        }

        #strategy table {
            background-color: #23272b;
            color: #e0e0e0;
            border-collapse: collapse;
            width: 100%;
        }

        #strategy th,
        #strategy td {
            border: 1px solid #343a40;
            padding: 8px;
        }

        #strategy th {
            background-color: #212529;
            color: #f8f9fa;
        }

        #strategy tr:nth-child(even) {
            background-color: #24292f;
        }

        #strategy tr:hover {
            background-color: #343a40;
        }

        /* Optional: style links in dark mode */
        #strategy a {
            color: #4da3ff;
        }
    </style>
</head>

<body class="bg-dark main-content">
    <div class="container">
        <div id="strategy" class="mt-4"></div>
    </div>
</body>

</html>