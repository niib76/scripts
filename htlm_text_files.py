#!/usr/bin/env python3

import os

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
            display: flex;
            margin: 0;
            padding: 0;
            height: 100vh;
        }}
        #left-pane {{
            width: 30%;
            background-color: #f0f0f0;
            padding: 20px;
            overflow-y: auto;
            box-shadow: 2px 0 5px rgba(0,0,0,0.1);
        }}
        #right-pane {{
            width: 70%;
            padding: 20px;
            overflow-y: auto;
        }}
        a {{
            display: block;
            margin: 10px 0;
            text-decoration: none;
            color: #333;
        }}
        a:hover {{
            color: blue;
        }}
        iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}
    </style>
</head>
<body>
    <div id="left-pane">
        {links}
    </div>
    <div id="right-pane">
        <iframe name="right-pane"></iframe>
    </div>
</body>
</html>
"""

# Function to create the file links
def generate_file_links(directory):
    links = ""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.relpath(os.path.join(root, file))
                links += f'<a href="{file_path}" target="right-pane">{file}</a>\n'
    return links

def create_html(directory):
    # Generate file links for .txt files in the directory
    file_links = generate_file_links(directory)
    
    # Create HTML content
    html_content = html_template.format(links=file_links)
    
    # Save to HTML file
    with open("directory_viewer.html", "w") as f:
        f.write(html_content)
    
    print("HTML file generated: directory_viewer.html")

if __name__ == "__main__":
    # You can replace os.getcwd() with the specific directory if needed
    create_html(os.getcwd())
