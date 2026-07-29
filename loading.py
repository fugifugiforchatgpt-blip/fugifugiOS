import tkinter as tk


class LoadingScreen:
    def __init__(self, master, on_complete):
        self.master = master
        self.on_complete = on_complete
        self.frame = tk.Frame(master, bg="black")
        self.frame.pack(fill="both", expand=True)

        self.message_label = tk.Label(self.frame, text="Загрузка", font=("Arial", 24), fg="white", bg="black")
        self.message_label.pack(expand=True)

        self.msg = "Загрузка"
        self.animate_dots()
        self.master.after(2000, self.finish)

    def animate_dots(self, count=0):
        if not self.message_label.winfo_exists():
            return
        dots = '.' * (count % 4)
        self.message_label.config(text=f"{self.msg}{dots}")
        self.master.after(500, lambda: self.animate_dots(count + 1))

    def finish(self):
        self.frame.destroy()
        self.on_complete(self.master)