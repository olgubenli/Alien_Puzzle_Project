import json
import os

def create_notebook(notebook_name, file_list):
    cells = []
    
    # Notebook Title
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [f"# Source Code Reference: {notebook_name}"]
    })

    file_directory = r"c:\Users\olgub\OneDrive\Masaüstü\Alien_Puzzle_Project\src"

    for filename in file_list:
        filepath = os.path.join(file_directory, filename)
        
        # Handle potential typo for histogram file if needed, but strict filename usage is best
        if not os.path.exists(filepath):
            print(f"Warning: {filepath} not found. Skipping.")
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Add a markdown cell for the filename
        cells.append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [f"## {filename}"]
        })
        
        # Add the code cell with the content
        # The content is separate lines for better JSON formatting
        cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {
                "collapsed": True  # Optional: start collapsed if possible, though standard NB doesn't always respect this
            },
            "outputs": [],
            "source": content.splitlines(keepends=True)
        })

    notebook_content = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.5"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    output_path = os.path.join(r"c:\Users\olgub\OneDrive\Masaüstü\Alien_Puzzle_Project\notebooks", notebook_name)
    # Ensure notebooks directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(notebook_content, f, indent=1)
    print(f"Created {output_path}")

if __name__ == "__main__":
    # Notebook 2
    create_notebook("Notebook_2.ipynb", [
        "yenimatrisgunceldb.py", 
        "anayolyanyoltop10.py", 
        "icbaglantilarladuraklar.py", 
        "equjmesafeler.py", 
        "k7top5icin.py", 
        "kontrol56top20icin.py"
    ])

    # Notebook 3
    create_notebook("Notebook_3.ipynb", [
        "yenigrafik49.py", 
        "yenigrafik50.py",
        "piegrafik18.py", 
        "bigpie20590grafik6.py", 
        "violingrafik.py", 
        "historgram1bucuk.py"
    ])

    # Notebook 4
    create_notebook("Notebook_4.ipynb", [
        "3dgrafik31.py", 
        "networkgrafikhat5.py", 
        "dunyadanmesafe.py", 
        "sonuckontrol.py", 
        "strestestison6.py"
    ])
