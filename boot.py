import tkinter as tk

def show_boot_screen(master, on_complete):
    master.configure(bg="black")
    label = tk.Label(master, text="Fugi_fugi OS\nЗагрузка...", font=("Arial", 36, "bold"),
                     fg="white", bg="black")
    label.pack(expand=True)
    master.after(2000, lambda: [label.destroy(), on_complete(master)])