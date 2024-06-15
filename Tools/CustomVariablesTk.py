import tkinter as tk


class ListVar(tk.Variable):
    def __init__(self, master=None, value=None, name=None):
        super().__init__(master, value, name)
        self._list = []
        if value:
            self.set(value)

    def set(self, value):
        if not isinstance(value, list):
            raise ValueError("ListVar solo acepta listas")
        self._list = value
        self._tk.call("set", self._name, *self._list)

    def get(self):
        return self._list
