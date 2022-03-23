import threading
import time

import py_cui
import requests

from typing import List


class ClientWrapper:
    def __init__(self, host: str, port: str):
        self.url = "http://{}:{}/".format(host, port)

    def send_message(self, name: str, text: str):
        data = {
            "name": name,
            "text": text,
        }
        response = requests.post(url=self.url + "send_message", json=data)
        response.raise_for_status()

    def read_messages(self, name: str) -> List[str]:
        params = {
            "name": name,
        }
        response = requests.get(url=self.url + "read_messages", params=params)
        if response.status_code != 200:
            return []
        return response.json()

    def add_chat(self, name: str, key: str):
        data = {
            "name": name,
            "key": key,
        }
        response = requests.post(url=self.url + "add_chat", json=data)
        response.raise_for_status()


class Application:
    def __init__(self, cui: py_cui.PyCUI, client: ClientWrapper):
        self.cui: py_cui.PyCUI = cui
        self.client: ClientWrapper = client
        self.nickname: str = "Vasya"  # TODO
        self.chats: List[str] = []

        self.chats_list_cell = self.cui.add_scroll_menu("Chats", 0, 0, row_span=5, column_span=1)
        self.chat_cell = self.cui.add_scroll_menu("Chat", 0, 1, 5, 5)
        self.input_cell = self.cui.add_text_box("Message:", 5, 1, 1, 5)
        self.add_chat_cell = self.cui.add_text_box("New chat:", 7, 1, 1, 5)
        self.input_cell.add_key_command(py_cui.keys.KEY_ENTER, self.send_message)
        self.add_chat_cell.add_key_command(py_cui.keys.KEY_ENTER, self.add_chat)
        self.cui.move_focus(self.input_cell)
        # self.chats_list_cell.set_on_selection_change_event(self.refresh)
        # self.cui.set_on_draw_update_func(self.refresh)
        self.start_background_updating()

    def send_message(self):
        message = self.input_cell.get()
        if not message:
            return

        name = self.chats_list_cell.get()
        if not name:
            return

        self.client.send_message(name, message)
        self.input_cell.clear()
        self.refresh_chat()

    def refresh_chats_list(self):
        self.refresh_chat()
        if not self.chats:
            self.chats_list_cell.clear()
            return

        shown_chats = self.chats_list_cell.get_item_list()
        if shown_chats == self.chats:
            return

        chat = self.chats_list_cell.get()
        self.chats_list_cell.clear()
        for c in self.chats:
            self.chats_list_cell.add_item(c)
        self.chats_list_cell.set_selected(chat)

    def refresh_chat(self):
        name = self.chats_list_cell.get()
        if not name:
            self.chat_cell.clear()
            return

        self.chat_cell.set_title("Chat with {}".format(name))
        shown_count = len(self.chat_cell.get_item_list())

        messages = self.client.read_messages(name)

        if messages is None:
            return

        if shown_count == len(messages):
            return

        self.chat_cell.clear()
        for message in messages:
            self.chat_cell.add_item(message)

    def add_chat(self):
        name, key = self.add_chat_cell.get().split(" ", 1)
        if not name or not key:
            return

        self.client.add_chat(name, key)  # TODO: try/except
        self.add_chat_cell.clear()
        self.chats.append(name)
        self.refresh_chats_list()

    def start_background_updating(self):
        operation_thread = threading.Thread(target=self.refresh, daemon=True)
        operation_thread.start()

    def update_chats_list(self):
        pass

    def refresh(self):
        while True:
            self.refresh_chats_list()
            time.sleep(1)


def main():
    root = py_cui.PyCUI(8, 6)
    root.set_refresh_timeout(1)
    root.set_title("Mock")

    Application(root, ClientWrapper("localhost", "8000"))
    root.start()


if __name__ == "__main__":
    main()
