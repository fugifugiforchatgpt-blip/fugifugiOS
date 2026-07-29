# clipboard.py
_clipboard_text = ""

def copy(text):
    global _clipboard_text
    _clipboard_text = text

def paste():
    return _clipboard_text

def has_text():
    return bool(_clipboard_text)