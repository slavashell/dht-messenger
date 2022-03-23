import threading
import time

import py_cui
import requests


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

    def read_messages(self, name: str):
        params = {
            "name": name,
        }
        response = requests.get(url=self.url + "read_messages", params=params)
        return response.json()


class Application:
    def __init__(self, cui: py_cui.PyCUI, client: ClientWrapper):
        self.cui = cui
        self.client = client
        self.nickname = "Vasya"  # TODO

        self.chats_list_cell = self.cui.add_scroll_menu("Chats", 0, 0, row_span=5, column_span=1)
        self.chat_cell = self.cui.add_scroll_menu("Chat", 0, 1, 5, 5)
        self.input_cell = self.cui.add_text_box("Message:", 5, 1, 1, 5)
        self.input_cell.add_key_command(py_cui.keys.KEY_ENTER, self.send_message)
        self.cui.move_focus(self.input_cell)
        # self.chats_list_cell.set_on_selection_change_event(self.refresh)
        # self.cui.set_on_draw_update_func(self.refresh)
        self.start_background_updating()

    def send_message(self):
        message = self.input_cell.get()
        companion = self.chats_list_cell.get()
        if not companion:
            return

        self.client.send_message(companion, message)
        self.input_cell.clear()
        self.refresh_chat()

    def refresh_chats_list(self):
        self.refresh_chat()
        companions = ["Alice"]
        if not companions:
            self.chats_list_cell.clear()
            return

        shown_chats = self.chats_list_cell.get_item_list()
        current_chats = ["Alice"]
        if shown_chats == current_chats:
            return

        chat = self.chats_list_cell.get()
        self.chats_list_cell.clear()
        for c in companions:
            self.chats_list_cell.add_item(c)
        self.chats_list_cell.set_selected(chat)

    def refresh_chat(self):
        companion = self.chats_list_cell.get()
        if not companion:
            self.chat_cell.clear()
            return

        self.chat_cell.set_title("Chat with {}".format(companion))
        shown_count = len(self.chat_cell.get_item_list())

        messages = self.client.read_messages(companion)

        if shown_count == len(messages):
            return

        self.chat_cell.clear()
        for message in messages:
            self.chat_cell.add_item(message)

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
