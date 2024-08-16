#! /usr/bin/env python

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox
import sys
import sqlite3

class VocabularyManager(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initDB()

    def initUI(self):
        self.setWindowTitle('Personal Dictionary')

        # The icon
        self.setWindowIcon(QtGui.QIcon('/home/adam178/.local/share/vmanager/korean_icon.png'))

        # Make the window always on top
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        form_layout = QtWidgets.QFormLayout()

        # Widgets
        self.word_input = QtWidgets.QLineEdit()
        self.meaning_input = QtWidgets.QLineEdit()
        # self.add_button = QtWidgets.QPushButton('Add Entry')
        # self.edit_button = QtWidgets.QPushButton('Edit Entry')
        self.delete_button = QtWidgets.QPushButton('Delete Entry')
        # self.search_button = QtWidgets.QPushButton('Search Entry')
        self.view_button = QtWidgets.QPushButton('View All Entries')
        self.result_text = QtWidgets.QTextEdit()
        self.result_text.setReadOnly(True)

        # Layouts
        form_layout.addRow('Word:', self.word_input)
        form_layout.addRow('Meaning:', self.meaning_input)
        layout.addLayout(form_layout)
        # layout.addWidget(self.add_button)
        # layout.addWidget(self.edit_button)
        layout.addWidget(self.delete_button)
        # layout.addWidget(self.search_button)
        layout.addWidget(self.view_button)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

        # Connect buttons
        # self.add_button.clicked.connect(self.add_entry)
        # self.edit_button.clicked.connect(self.edit_entry)
        self.delete_button.clicked.connect(self.delete_entry)
        # self.search_button.clicked.connect(self.search_entry)
        self.view_button.clicked.connect(self.view_all_entries)

        # Connect returnPressed signal to the search_entry method
        self.word_input.returnPressed.connect(self.search_entry)
        self.meaning_input.returnPressed.connect(self.add_entry)

    def initDB(self):
        self.conn = sqlite3.connect('/home/adam178/.local/share/vmanager/vocabulary.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS vocabulary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            meaning TEXT
        )
        ''')
        self.conn.commit()

    def add_entry(self):
        word = self.word_input.text()
        meaning = self.meaning_input.text()
        if (word != "" and meaning != ""):
            self.cursor.execute('INSERT INTO vocabulary (word, meaning) VALUES (?, ?)', (word, meaning))
            self.conn.commit()
            self.result_text.setText(f'Added: {word} - {meaning}')

    # def edit_entry(self):
    #     word = self.word_input.text()
    #     new_meaning = self.meaning_input.text()
    #     if (new_meaning != ""):
    #         self.cursor.execute('UPDATE vocabulary SET meaning = ? WHERE word = ?', (new_meaning, word))
    #         if self.cursor.rowcount > 0:
    #             self.conn.commit()
    #             self.result_text.setText(f'Updated: {word} - {new_meaning}')
    #         else:
    #             self.result_text.setText('No entry found to update.')


    def delete_entry(self):
        word = self.word_input.text()
        meaning = self.meaning_input.text()
        if word and meaning:
            # Show confirmation dialog
            reply = QMessageBox.question(
                self,
                'Delete Entry',
                f'Are you sure you want to delete the meaning "{meaning}" from the word "{word}"?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            # Proceed with deletion if the user confirms
            if reply == QMessageBox.Yes:
                self.cursor.execute('DELETE FROM vocabulary WHERE word = ? AND meaning = ?', (word, meaning))
                if self.cursor.rowcount > 0:
                    self.conn.commit()
                    self.result_text.setText(f'Deleted meaning "{meaning}" from word "{word}"')
                else:
                    self.result_text.setText('No matching meaning found for deletion.')
        else:
            self.result_text.setText('Please provide both word and meaning.')

    def search_entry(self):
        word = self.word_input.text()

        # Base meaning: exact match for the word
        self.cursor.execute('SELECT meaning FROM vocabulary WHERE word = ?', (word,))
        base_results = self.cursor.fetchall()

        # Syllables: split the word into syllables
        syllables = [word[i:i+1] for i in range(len(word))]  # Each character as a syllable
        related_results = {syllable: [] for syllable in syllables}

        # Define a list of characters/syllables to remove
        remove_list = [" ", "하", "해", "다", "하다", "를", "을"]

        # Iterate over the syllables
        for syllable in syllables:
            # Remove the unwanted characters/syllables
            for remove in remove_list:
                syllable = syllable.replace(remove, "")
            
            # Only proceed if the syllable is not empty after removing characters
            if syllable:
                self.cursor.execute('SELECT word, meaning FROM vocabulary WHERE word LIKE ?', (f'%{syllable}%',))
                results = self.cursor.fetchall()
                
                # Filter out the original word from the results
                filtered_results = [(w, m) for w, m in results if w != word]
                related_results[syllable] = filtered_results

        # Display results
        display_text = ""

        if base_results:
            display_text += f"Base Meaning for '{word}':\n"
            display_text += '\n'.join([f'- {meaning[0]}' for meaning in base_results])
            display_text += "\n\n"
        else:
            display_text += f"No exact match found for '{word}'.\n\n"

        if any(related_results.values()):
            display_text += "Related Meanings:\n"
            for syllable, results in related_results.items():
                if results:
                    display_text += f"\nSyllable '{syllable}':\n"
                    display_text += '\n'.join([f'{w}: {m}' for w, m in results])
                    display_text += "\n"
        else:
            display_text += "No related meanings found."

        self.result_text.setText(display_text)
        self.meaning_input.clear()  # Clearing the meaning input box

    def view_all_entries(self):
        self.cursor.execute('SELECT word, meaning FROM vocabulary')
        entries = self.cursor.fetchall()
        display_text = '\n'.join([f'{i+1}. {word}: {meaning}' for i, (word, meaning) in enumerate(entries)])
        self.result_text.setText(display_text)

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = VocabularyManager()
    ex.show()
    sys.exit(app.exec_())
