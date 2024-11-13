    def handleRowDoubleClick(self, item):
        print("inside handle row double clicking method")
        row = None

        if not item:
            print("if not item")
            return


        if item.text():
            print("item.text()")
            if "Album Title: " in item.text():
                print("album title")
                return
            else:
                print("else")
                self.item = item
                self.songTableWidget.song_playing_row = row
                self.lrcPlayer.started_player = True
                if self.get_music_file_from_click(item):
                    self.song_initializing_stuff()
                else:
                    return
        else:
            return

        try:
            row = item.row()
            print("row")
            print(row)
        except AttributeError:
            return

        if self.hidden_rows:
            self.songTableWidget.clearSelection()
            self.restore_table()
            self.songTableWidget.setFocus()
            self.songTableWidget.scroll_to_current_row()
            simulate_keypress(self.songTableWidget, Qt.Key.Key_G)  # only imitation of key press work.
            # Direct calling the method doesn't work. IDk why.
            self.hidden_rows = False

    def handleRowDoubleClick(self, item):
        row = None
        try:
            row = item.row()
        except AttributeError:
            return

        if item:
            if "Album Title: " in item.text():
                return
            else:
                self.item = item
                self.songTableWidget.song_playing_row = row
                self.lrcPlayer.started_player = True
                if self.get_music_file_from_click(item):
                    self.song_initializing_stuff()
                else:
                    return
        else:
            return

        if self.hidden_rows:
            self.songTableWidget.clearSelection()
            self.restore_table()
            self.songTableWidget.setFocus()
            self.songTableWidget.scroll_to_current_row()
            simulate_keypress(self.songTableWidget, Qt.Key.Key_G)  # only imitation of key press work.
            # Direct calling the method doesn't work. IDk why.
            self.hidden_rows = False
