#! /usr/bin/env python
# windows version will be late in developement since my daily driver is archlinux. 
# the database(vocabulary.db) is saved in vmanager folder under local folder of %appdata%
# I used to migrate from my vocabulary.md to the database

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMessageBox
import sys
import sqlite3
import os

class VocabularyManager(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initDB()

    def initUI(self):
        self.setWindowTitle('Vocabulary Manager')

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        form_layout = QtWidgets.QFormLayout()

        # Widgets
        self.word_input = QtWidgets.QLineEdit()
        self.meaning_input = QtWidgets.QLineEdit()
        self.add_button = QtWidgets.QPushButton('Add Entry')
        # self.edit_button = QtWidgets.QPushButton('Edit Entry')
        self.delete_button = QtWidgets.QPushButton('Delete Entry')
        self.search_button = QtWidgets.QPushButton('Search Entry')
        self.view_button = QtWidgets.QPushButton('View All Entries')
        self.result_text = QtWidgets.QTextEdit()
        self.result_text.setReadOnly(True)

        # Layouts
        form_layout.addRow('Word:', self.word_input)
        form_layout.addRow('Meaning:', self.meaning_input)
        layout.addLayout(form_layout)
        layout.addWidget(self.add_button)
        # layout.addWidget(self.edit_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.search_button)
        layout.addWidget(self.view_button)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

        # Connect buttons
        self.add_button.clicked.connect(self.add_entry)
        # self.edit_button.clicked.connect(self.edit_entry)
        self.delete_button.clicked.connect(self.delete_entry)
        self.search_button.clicked.connect(self.search_entry)
        self.view_button.clicked.connect(self.view_all_entries)

        # Connect returnPressed signal to the search_entry method
        self.word_input.returnPressed.connect(self.search_entry)
        self.meaning_input.returnPressed.connect(self.add_entry)

    def initDB(self):
        # Adjust the path to your Windows system
        db_dir = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'vmanager')
        os.makedirs(db_dir, exist_ok=True)
        db_path = os.path.join(db_dir, 'vocabulary.db')

        self.conn = sqlite3.connect(db_path)
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
        if word != "" and meaning != "":
            self.cursor.execute('INSERT INTO vocabulary (word, meaning) VALUES (?, ?)', (word, meaning))
            self.conn.commit()
            self.result_text.setText(f'Added: {word} - {meaning}')
        else:
            self.result_text.setText('Please provide both word and meaning.')

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
        self.cursor.execute('SELECT meaning FROM vocabulary WHERE word = ?', (word,))
        results = self.cursor.fetchall()
        if results:
            display_text = '\n'.join([f'{meaning[0]}' for meaning in results])
            self.result_text.setText(display_text)
        else:
            self.result_text.setText('No entry found.')
        self.meaning_input.clear() #clearing the meaning input box

    def view_all_entries(self):
        self.cursor.execute('SELECT word, meaning FROM vocabulary')
        entries = self.cursor.fetchall()
        display_text = '\n'.join([f'{word}: {meaning}' for word, meaning in entries])
        self.result_text.setText(display_text)

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = VocabularyManager()
    ex.show()
    sys.exit(app.exec_())
