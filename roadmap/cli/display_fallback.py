"""Fallback display utilities when rich is unavailable."""

class Console:
    def print(self, *args, **kwargs):
        text = " ".join(str(a) for a in args)
        print(text)

class Table:
    def __init__(self, title=None):
        self.title = title
        self.columns = []
        self.rows = []
    def add_column(self, name, **kwargs):
        self.columns.append(name)
    def add_row(self, *values):
        self.rows.append(values)

class Panel:
    def __init__(self, content, title=None, border_style=None):
        self.content = content
        self.title = title
        self.border_style = border_style
