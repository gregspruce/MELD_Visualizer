# MELD Visualizer API Reference

## Overview

The MELD Visualizer API provides a set of endpoints for interacting with the application programmatically.

## Endpoints

- **`POST /_dash-update-component`:** Internal endpoint for Dash component updates.
- **`POST /upload/csv`:** Upload a CSV file containing MELD manufacturing data.
- **`POST /upload/gcode`:** Upload a G-code (.nc) file for toolpath visualization.
- **`GET /config`:** Retrieve the current application configuration.
- **`PUT /config`:** Update application configuration settings.

## API Playground

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MELD Visualizer API Playground</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f8f9fa;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mt-5">MELD Visualizer API Playground</h1>
        <p class="lead">A simple interface for interacting with the MELD Visualizer API.</p>

        <div class="row">
            <div class="col-md-6">
                <h2>Upload CSV</h2>
                <div class="mb-3">
                    <label for="csv-file" class="form-label">CSV File</label>
                    <input type="file" class="form-control" id="csv-file" accept=".csv">
                </div>
                <button class="btn btn-primary" onclick="uploadCSV()">Upload</button>
            </div>
            <div class="col-md-6">
                <h2>Upload G-code</h2>
                <div class="mb-3">
                    <label for="gcode-file" class="form-label">G-code File</label>
                    <input type="file" class="form-control" id="gcode-file" accept=".nc">
                </div>
                <button class="btn btn-primary" onclick="uploadGcode()">Upload</button>
            </div>
        </div>

        <div class="row mt-5">
            <div class="col-md-12">
                <h2>Configuration</h2>
                <button class="btn btn-primary" onclick="getConfig()">Get Configuration</button>
                <div class="mt-3">
                    <textarea class="form-control" id="config-body" rows="8"></textarea>
                </div>
                <button class="btn btn-primary mt-3" onclick="updateConfig()">Update Configuration</button>
            </div>
        </div>

        <div class="row mt-5">
            <div class="col-md-12">
                <h2>Response</h2>
                <pre id="response-area"></pre>
            </div>
        </div>
    </div>

    <script>
        const BASE_URL = 'http://127.0.0.1:8050';

        async function uploadCSV() {
            const fileInput = document.getElementById('csv-file');
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            const response = await fetch(`${BASE_URL}/upload/csv`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            document.getElementById('response-area').textContent = JSON.stringify(data, null, 2);
        }

        async function uploadGcode() {
            const fileInput = document.getElementById('gcode-file');
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            const response = await fetch(`${BASE_URL}/upload/gcode`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            document.getElementById('response-area').textContent = JSON.stringify(data, null, 2);
        }

        async function getConfig() {
            const response = await fetch(`${BASE_URL}/config`);
            const data = await response.json();
            document.getElementById('config-body').value = JSON.stringify(data, null, 2);
        }

        async function updateConfig() {
            const configBody = document.getElementById('config-body').value;
            const response = await fetch(`${BASE_URL}/config`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: configBody
            });

            const data = await response.json();
            document.getElementById('response-area').textContent = JSON.stringify(data, null, 2);
        }
    </script>
</body>
</html>
```
