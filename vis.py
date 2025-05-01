import os
import json
from bs4 import BeautifulSoup
from pyvis.network import Network

# Set directory to scan
DIRECTORY = "./"

# Collect all files in the directory
files = [f for f in os.listdir(DIRECTORY) if os.path.isfile(os.path.join(DIRECTORY, f))]

# Store relationships and node metadata
relationships = []
file_contents = {}

# Step 1: Read text-based files (skip binary like .png)
for filename in files:
    path = os.path.join(DIRECTORY, filename)
    ext = filename.split(".")[-1].lower()

    # Read only if it's likely a text file
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            file_contents[filename] = content
    except:
        file_contents[filename] = None  # For PNGs etc.

# Step 2: Scan for file references
for filename, content in file_contents.items():
    if content is None:
        continue  # skip binary files

    linked_files = set()

    # Obsidian-style [[filename]]
    if "[[" in content:
        linked_files.update(
            [link.split("]]")[0] for link in content.split("[[")[1:] if "]]" in link]
        )

    # HTML-style <img src="file"> or <script src="file">
    if filename.endswith(".html"):
        try:
            soup = BeautifulSoup(content, "html.parser")
            for tag in soup.find_all(["img", "script", "link"]):
                ref = tag.get("src") or tag.get("href")
                if ref and os.path.basename(ref) in files:
                    linked_files.add(os.path.basename(ref))
        except:
            pass

    # JSON-style string references
    if filename.endswith(".json"):
        try:
            data = json.loads(content)
            for other_file in files:
                if other_file in str(data):
                    linked_files.add(other_file)
        except:
            pass

    # Raw mentions of file names
    for other_file in files:
        if other_file != filename and other_file in content:
            linked_files.add(other_file)

    # Add relationships
    for target in linked_files:
        if target in files and target != filename:
            relationships.append((filename, target))

# Step 3: Remove duplicate edges
relationships = list(set(relationships))

# Step 4: Visualize using PyVis
net = Network(height="850px", width="100%", directed=True)

# Add nodes with color coding
def get_color(file):
    if file.endswith(".json"):
        return "#FFD700"
    elif file.endswith(".html"):
        return "#ADD8E6"
    elif file.endswith(".png") or file.endswith(".jpg"):
        return "#90EE90"
    elif file.endswith(".md") or file.endswith(".txt"):
        return "#FFA07A"
    else:
        return "#D3D3D3"

for f in files:
    net.add_node(f, label=f, color=get_color(f))

# Add edges
for src, dst in relationships:
    net.add_edge(src, dst)

# Show the graph
net.show("obsidian_style_graph.html", notebook=False)

import webbrowser
webbrowser.open("obsidian_style_graph.html")
