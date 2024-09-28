#! /usr/bin/env python

import sys, os, platform
import sqlite3

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import Qt  # for shortcuts
from PyQt6.QtWidgets import QMessageBox


class VocabularyManager(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setup()
        self.initUI()
        self.initDB()

    def setup(self):
        self.os_name = platform.system()
        current_directory = os.path.dirname(os.path.abspath(__file__))

        self.icon_path = os.path.join(current_directory, "resources", "icon.png")

        if (self.os_name == "Linux"):
            db_dir = os.path.join(os.environ['HOME'], '.config', 'sqlite_personal_dictionary')
            os.makedirs(db_dir, exist_ok=True)

        elif (self.os_name == "Windows"):
            db_dir = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'sqlite-personal-dictionary')
            os.makedirs(db_dir, exist_ok=True)

        self.db_path = os.path.join(db_dir, 'vocabulary.db')

    def initUI(self):
        self.setWindowTitle('Personal Dictionary')

        # The icon
        self.setWindowIcon(QtGui.QIcon(self.icon_path))

        # Make the window always on top
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.WindowStaysOnTopHint)

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        form_layout = QtWidgets.QFormLayout()

        # Widgets
        self.word_input = QtWidgets.QLineEdit()
        self.meaning_input = QtWidgets.QLineEdit()
        self.add_button = QtWidgets.QPushButton('Add Entry')
        self.search_button = QtWidgets.QPushButton('Search Entry')
        self.delete_button = QtWidgets.QPushButton('Delete Entry')
        self.view_button = QtWidgets.QPushButton('View All Entries')
        self.result_text = QtWidgets.QTextEdit()
        self.result_text.setReadOnly(True)

        # Layouts
        form_layout.addRow('Word:', self.word_input)
        form_layout.addRow('Meaning:', self.meaning_input)
        layout.addLayout(form_layout)
        layout.addWidget(self.add_button)
        layout.addWidget(self.search_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.view_button)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

        # Connect buttons
        self.add_button.clicked.connect(self.add_entry)
        self.search_button.clicked.connect(self.search_entry)
        self.delete_button.clicked.connect(self.delete_entry)
        self.view_button.clicked.connect(self.view_all_entries)

        # Connect returnPressed signal to the search_entry method
        self.word_input.returnPressed.connect(self.search_entry)
        self.meaning_input.returnPressed.connect(self.add_entry)

    def initDB(self):
        self.conn = sqlite3.connect(self.db_path)
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
        word = self.word_input.text().strip()
        meaning = self.meaning_input.text().strip()
        if word != "" and meaning != "":
            self.cursor.execute('INSERT INTO vocabulary (word, meaning) VALUES (?, ?)', (word, meaning))
            self.conn.commit()
            self.result_text.setText(f'Added: {word} - {meaning}')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_S and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.search_entry()
        elif event.key() == Qt.Key.Key_Q and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.delete_entry()
        else:
            super().keyPressEvent(event)

    def delete_entry(self):
        word = self.word_input.text().strip()
        meaning = self.meaning_input.text().strip()
        if word and meaning:
            reply = QMessageBox.question(
                self,
                'Delete Entry',
                f'Are you sure you want to delete the meaning "{meaning}" from the word "{word}"?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.cursor.execute('DELETE FROM vocabulary WHERE word = ? AND meaning = ?', (word, meaning))
                if self.cursor.rowcount > 0:
                    self.conn.commit()
                    self.result_text.setText(f'Deleted meaning "{meaning}" from word "{word}"')
                else:
                    self.result_text.setText('No matching meaning found for deletion.')
        else:
            self.result_text.setText('Please provide both word and meaning.')

    def search_entry(self):
        word = self.word_input.text().strip()

        self.cursor.execute('SELECT meaning FROM vocabulary WHERE word = ?', (word,))
        base_results = self.cursor.fetchall()

        syllables = [word[i:i+1] for i in range(len(word))]  # Each character as a syllable
        related_results = {syllable: [] for syllable in syllables}

        combinations = []
        if len(syllables) > 2:
            for i in range(1, len(syllables)):
                combination = ''.join(syllables[:i+1])
                combinations.append(combination)

        remove_list = [" ", "하", "다", "하다", "를", "을"]

        for syllable in syllables + combinations:
            for remove in remove_list:
                syllable = syllable.replace(remove, "")

            if syllable:
                self.cursor.execute('SELECT word, meaning FROM vocabulary WHERE word LIKE ?', (f'%{syllable}%',))
                results = self.cursor.fetchall()

                filtered_results = [(w, m) for w, m in results if w != word]
                related_results[syllable] = filtered_results

        display_text = ""

        if base_results:
            display_text += f"Base Meaning for '{word}':\n"
            display_text += '\n'.join([f'- {meaning[0]}' for meaning in base_results])
            display_text += "\n\n"
        else:
            display_text += f"No exact match found for '{word}'.\n\n"

        if any(related_results.values()):
            display_text += "Related Meanings:"
            for syllable, results in related_results.items():
                if results:
                    display_text += f"\nSyllable/Combination '{syllable}':\n"
                    display_text += '\n'.join([f'{w}: {m}' for w, m in results])
                    display_text += "\n"
        else:
            display_text += "No related meanings found."

        self.result_text.setText(display_text)
        self.meaning_input.clear()

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
    sys.exit(app.exec())
