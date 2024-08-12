# I used to take syllable meaning in obsidian
# The header for title and lists for their meaning. 
# This program migrate data from vocabulary.md to vocabulary.db

import sqlite3
import re

def insert_markdown_into_db(markdown_file, db_file):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Read the markdown file
    with open(markdown_file, 'r', encoding='utf-8') as file:
        content = file.read()

    # Split the content into sections based on headings
    sections = re.split(r'# ', content)[1:]

    for section in sections:
        lines = section.split('\n')
        word = lines[0].strip()
        meanings = [line.strip('- ').strip() for line in lines[1:] if line.strip()]

        for meaning in meanings:
            cursor.execute('INSERT INTO vocabulary (word, meaning) VALUES (?, ?)', (word, meaning))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print(f'Successfully inserted data from {markdown_file} into {db_file}')

# Usage
insert_markdown_into_db('vocabulary.md', 'vocabulary.db')
