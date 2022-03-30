import sys
import threading
import time

import py_cui
import requests

from typing import List, Optional


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

    def register_user(self, private_key: Optional[str] = None):
        data = None
        if private_key is not None:
            data = {"key": private_key}

        response = requests.post(url=self.url + "register_user", json=data)
        response.raise_for_status()

    def get_public_key(self) -> Optional[str]:
        response = requests.get(url=self.url + "public_key")
        if response.status_code != 200:
            return None
        return response.json()["key"]

    def get_chats(self) -> Optional[List[str]]:
        response = requests.get(url=self.url + "chats")
        if response.status_code != 200:
            return None
        return response.json()["chats"]


class Application:
    def __init__(self, cui: py_cui.PyCUI, client: ClientWrapper):
        self.cui: py_cui.PyCUI = cui
        self.client: ClientWrapper = client
        self.nickname: str = "Vasya"  # TODO
        self.chats: List[str] = []

        self.chats_list_cell = self.cui.add_scroll_menu("Chats", 0, 0, 5, 1)
        self.chat_cell = self.cui.add_scroll_menu("Chat", 0, 1, 5, 7)
        self.input_cell = self.cui.add_text_box("Message:", 5, 0, 1, 8)
        self.add_chat_cell = self.cui.add_text_box("New chat (enter name and public key):", 6, 0, 1, 8)
        self.registration_cell = self.cui.add_text_box(
            "Login (enter private key if already registered, leave empty otherwise):", 7, 0, 1, 8
        )

        self.input_cell.add_key_command(py_cui.keys.KEY_ENTER, self.send_message)
        self.add_chat_cell.add_key_command(py_cui.keys.KEY_ENTER, self.add_chat)
        self.registration_cell.add_key_command(py_cui.keys.KEY_ENTER, self.registration)

        self.init_chats_list()
        self.cui.move_focus(self.registration_cell)
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
        try:
            name = self.chats_list_cell.get()
        except:
            self.chat_cell.clear()
            return

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
        try:
            name, key = self.add_chat_cell.get().split(" ", 1)
        except ValueError:
            print("Unexpected input format: {}".format(self.add_chat_cell.get()), file=sys.stderr)
            return

        if not name or not key:
            return

        try:
            self.client.add_chat(name, key)
        except requests.HTTPError:
            return

        self.add_chat_cell.clear()
        self.chats.append(name)
        self.refresh_chats_list()

    def init_chats_list(self):
        chats = self.client.get_chats()
        for c in chats:
            self.chats.append(c)
        self.refresh_chats_list()

    def registration(self):
        private_key = self.registration_cell.get()
        if private_key:
            self.client.register_user(private_key)
        else:
            self.client.register_user(None)

        public_key = self.client.get_public_key()
        if public_key is None:
            return

        self.registration_cell.set_text("Public key: {}".format(public_key))

    def start_background_updating(self):
        operation_thread = threading.Thread(target=self.refresh, daemon=True)
        operation_thread.start()

    def refresh(self):
        while True:
            self.refresh_chats_list()
            time.sleep(1)


def main():
    root = py_cui.PyCUI(10, 8, auto_focus_buttons=False)
    root.set_refresh_timeout(1)
    root.set_title("Mock")

    Application(root, ClientWrapper("localhost", "8000"))
    root.start()


if __name__ == "__main__":
    main()
