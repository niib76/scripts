#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2023 Niels Bijleveld

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import re
import html
from flask import Flask, request, jsonify

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Directory Explorer</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            height: 100vh;
            background-color: #121212;
            color: #e0e0e0;
            display: flex;
            flex-direction: column;
        }}
        header {{
            width: 100%;
            background-color: #1e1e1e;
            padding: 10px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.5);
            border-bottom: 1px solid #333;
            display: flex;
            justify-content: space-between;
        }}
        #left-pane {{
            width: 30%;
            background-color: #1e1e1e;
            padding: 20px;
            overflow-y: auto;
            box-shadow: 2px 0 5px rgba(0,0,0,0.5);
            border-right: 1px solid #333;
        }}
        #right-pane {{
            width: 70%;
            padding: 20px;
            overflow-y: auto;
            white-space: pre-wrap;
            font-family: monospace;
            background-color: #121212;
            color: #4caf50;
            border-left: 1px solid #333;
            position: relative;
        }}
        .container {{
            display: flex;
            height: calc(100vh - 50px); /* Adjust height to include the top bar */
        }}
        a {{
            display: inline-block;
            margin: 5px 0;
            text-decoration: none;
            color: #8ab4f8;
            margin-right: 10px;
        }}
        a:hover {{
            color: #bb86fc;
        }}
        .delete {{
            color: red;
            cursor: pointer;
            margin-left: 10px;
        }}
        .delete:hover {{
            color: darkred;
        }}
        .directory {{
            font-weight: bold;
            margin-top: 10px;
            cursor: pointer;
            color: #e0e0e0;
        }}
        .file-list {{
            display: none;
            margin-left: 15px;
        }}
        .directory.collapsed + .file-list {{
            display: none;
        }}
        .directory.expanded + .file-list {{
            display: block;
        }}
        .file-row {{
            display: block;
            margin-bottom: 5px;
        }}
        button {{
            background-color: #4caf50;
            border: none;
            color: white;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 4px;
        }}
        button:hover {{
            background-color: #45a049;
        }}
        #search-bar {{
            width: 50%;
            padding: 5px;
            border-radius: 4px;
            border: 1px solid #333;
            background-color: #1e1e1e;
            color: #e0e0e0;
            margin-right: 10px;
        }}
        #search-bar::placeholder {{
            color: #aaa;
        }}
        #highlighted {{
            background-color: yellow;
            color: black;
        }}
    </style>
    <script>
        function toggleDirectory(element) {{
            element.classList.toggle('expanded');
            element.classList.toggle('collapsed');
        }}

        function showFileContent(content) {{
            document.getElementById('right-pane').innerHTML = content;
            clearSearch();  // Clear previous search highlights
        }}

        function confirmDelete(filePath) {{
            if (confirm("Are you sure you want to delete " + filePath + "?")) {{
                fetch('/delete', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{ file_path: filePath }})
                }}).then(response => {{
                    if (response.ok) {{
                        alert("File deleted successfully!");
                        location.reload();
                    }} else {{
                        alert("Failed to delete the file.");
                    }}
                }}).catch(error => {{
                    alert("Error: " + error);
                }});
            }}
        }}

        function refreshFiles() {{
            fetch('/refresh')
                .then(response => response.text())
                .then(html => {{
                    document.getElementById('left-pane').innerHTML = html;
                    document.getElementById('right-pane').innerHTML = "<p>File list refreshed.</p>";
                }})
                .catch(error => {{
                    alert("Error refreshing files: " + error);
                }});
        }}

        function searchInFile() {{
            let searchTerm = document.getElementById('search-bar').value;
            let contentPane = document.getElementById('right-pane');
            let content = contentPane.innerHTML;

            clearSearch();  // Clear previous search highlights

            if (searchTerm) {{
                let regex = new RegExp(searchTerm, 'gi');
                let highlightedContent = content.replace(regex, match => `<span id="highlighted">${{match}}</span>`);
                contentPane.innerHTML = highlightedContent;
            }}
        }}

        function clearSearch() {{
            let contentPane = document.getElementById('right-pane');
            let content = contentPane.innerHTML;
            contentPane.innerHTML = content.replace(/<span id="highlighted">(.*?)<\/span>/g, '$1');
        }}
    </script>
</head>
<body>
    <header>
        <button onclick="refreshFiles()">Refresh</button>
        <input type="text" id="search-bar" placeholder="Search in file...">
        <button onclick="searchInFile()">Search</button>
    </header>
    <div class="container">
        <div id="left-pane">
            {links}
        </div>
        <div id="right-pane">
            <!-- File content will appear here -->
        </div>
    </div>
</body>
</html>
"""

ansi_to_html = {
    "\033[0m": "</span>",                          # Reset
    "\033[1m": "<span style='font-weight: bold;'>",# Bold
    "\033[22m": "</span>",                         # Reset bold/dim
    "\033[31m": "<span style='color: #ff5555;'>",  # Red
    "\033[32m": "<span style='color: #4caf50;'>",  # Softer Green (Matching the default green text color)
    "\033[33m": "<span style='color: #f1fa8c;'>",  # Yellow
    "\033[34m": "<span style='color: #bd93f9;'>",  # Blue
    "\033[35m": "<span style='color: #ff79c6;'>",  # Magenta
    "\033[36m": "<span style='color: #8be9fd;'>",  # Cyan
}

def ansi_to_html_conversion(text):
    for ansi_code, html_code in ansi_to_html.items():
        text = text.replace(ansi_code, html_code)
    return text

def read_and_convert_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""
    
    content = ansi_to_html_conversion(content)
    content = html.escape(content).replace("\n", "<br>")
    return content

def generate_file_links(directory):
    links = ""
    directories_with_files = set()
    directory_contents = []

    for root, dirs, files in os.walk(directory):
        has_txt_files = any(file.endswith(".txt") for file in files)
        if has_txt_files or any(os.path.join(root, d) in directories_with_files for d in dirs):
            rel_dir = os.path.relpath(root, directory)
            if rel_dir != '.':
                directory_contents.append((rel_dir, sorted([f for f in files if f.endswith(".txt")])))

            for d in dirs:
                directories_with_files.add(os.path.join(root, d))
    
    # Sort directories and files
    directory_contents.sort(key=lambda x: x[0])
    
    for rel_dir, files in directory_contents:
        links += f'<div class="directory collapsed" onclick="toggleDirectory(this)">{html.escape(rel_dir)}</div>\n'
        
        if files:
            links += '<div class="file-list">\n'
            for file in sorted(files):
                file_path = os.path.join(directory, rel_dir, file)
                file_content = read_and_convert_file(file_path)
                # Each file is on its own row
                links += f'<div class="file-row">'
                links += f'<a href="#" onclick="showFileContent(`{file_content}`)">{html.escape(file)}</a>'
                links += f'<span class="delete" onclick="confirmDelete(`{file_path}`)">&#x2716;</span>'
                links += '</div>\n'  # Close file row div
            links += '</div>\n'

    return links

def create_html(directory):
    file_links = generate_file_links(directory)
    return html_template.format(links=file_links)

def delete_file(file_path):
    try:
        os.remove(file_path)
        return True
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
        return False

if __name__ == "__main__":
    app = Flask(__name__)

    @app.route("/")
    def index():
        html_content = create_html(os.getcwd())
        return html_content

    @app.route("/refresh")
    def refresh():
        html_content = generate_file_links(os.getcwd())
        return html_content

    @app.route("/delete", methods=["POST"])
    def delete():
        data = request.get_json()
        file_path = data.get('file_path')
        if delete_file(file_path):
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error"}), 500

    # Change the port to 9999
    app.run(port=9999, debug=True)
