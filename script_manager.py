import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser
import json

CONFIG_FILE = 'scripts_config.json'

class ScriptManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Script Kütüphanesi")
        self.scripts = []
        self.load_scripts()
        self.create_widgets()

    def create_widgets(self):
        # Script listesinin bulunduğu çerçeve
        self.script_frame = tk.Frame(self.root)
        self.script_frame.pack(side='top', fill='both', expand=True)

        # Kaydırma çubuğu
        self.canvas = tk.Canvas(self.script_frame)
        self.scrollbar = tk.Scrollbar(self.script_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')

        # Script ekleme butonu
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side='bottom', fill='x')

        self.add_button = tk.Button(self.button_frame, text="Script Ekle", command=self.add_script)
        self.add_button.pack(side='left', padx=5, pady=5)

        self.refresh_button = tk.Button(self.button_frame, text="Yenile", command=self.refresh_scripts)
        self.refresh_button.pack(side='left', padx=5, pady=5)

        self.refresh_scripts()

    def load_scripts(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.scripts = json.load(f)
        else:
            self.scripts = []

    def save_scripts(self):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.scripts, f, ensure_ascii=False, indent=4)

    def add_script(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Yeni Script Ekle")

        tk.Label(add_window, text="Script Dosyası:").grid(row=0, column=0, padx=5, pady=5)
        script_entry = tk.Entry(add_window, width=50)
        script_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(add_window, text="Seç", command=lambda: self.browse_file(script_entry, filetypes=[("Python Files", "*.py")])).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(add_window, text="Açıklama:").grid(row=1, column=0, padx=5, pady=5)
        description_entry = tk.Entry(add_window, width=50)
        description_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(add_window, text="Link:").grid(row=2, column=0, padx=5, pady=5)
        link_entry = tk.Entry(add_window, width=50)
        link_entry.grid(row=2, column=1, padx=5, pady=5)

        def save_new_script():
            script_path = script_entry.get()
            description = description_entry.get()
            link = link_entry.get()

            if not os.path.isfile(script_path):
                messagebox.showerror("Hata", "Geçerli bir script dosyası seçmelisiniz.")
                return

            script_info = {
                "path": script_path,
                "description": description,
                "link": link
            }

            self.scripts.append(script_info)
            self.save_scripts()
            self.refresh_scripts()
            add_window.destroy()

        tk.Button(add_window, text="Kaydet", command=save_new_script).grid(row=3, column=1, padx=5, pady=5)

    def browse_file(self, entry_widget, filetypes):
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filename)

    def refresh_scripts(self):
        # Mevcut listeyi temizle
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for index, script_info in enumerate(self.scripts):
            frame = tk.Frame(self.scrollable_frame)
            frame.pack(pady=5, padx=5, fill='x')

            # Script butonu
            script_name = os.path.basename(script_info['path'])
            button = tk.Button(frame, text=script_name, command=lambda idx=index: self.run_script(idx))
            button.pack(side='left')

            # Açıklama etiketi
            description = script_info.get('description', '')
            desc_label = tk.Label(frame, text=description)
            desc_label.pack(side='left', padx=10)

            # Link etiketi (eğer varsa)
            link = script_info.get('link', '')
            if link:
                link_label = tk.Label(frame, text=link, fg="blue", cursor="hand2")
                link_label.pack(side='left', padx=10)
                link_label.bind("<Button-1>", lambda e, url=link: self.open_url(url))

            # Düzenle ve Sil butonları
            edit_button = tk.Button(frame, text="Düzenle", command=lambda idx=index: self.edit_script(idx))
            edit_button.pack(side='right', padx=5)

            remove_button = tk.Button(frame, text="Sil", command=lambda idx=index: self.remove_script(idx))
            remove_button.pack(side='right', padx=5)

    def open_url(self, url):
        webbrowser.open(url)

    def run_script(self, index):
        script_info = self.scripts[index]
        script_path = script_info['path']
        if not os.path.isfile(script_path):
            messagebox.showerror("Hata", f"Script bulunamadı: {script_path}")
            return

        try:
            subprocess.Popen(["python", script_path], cwd=os.path.dirname(script_path))
        except Exception as e:
            messagebox.showerror("Hata", f"Script çalıştırılamadı:\n{e}")

    def edit_script(self, index):
        script_info = self.scripts[index]

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Script Düzenle")

        tk.Label(edit_window, text="Script Dosyası:").grid(row=0, column=0, padx=5, pady=5)
        script_entry = tk.Entry(edit_window, width=50)
        script_entry.insert(0, script_info['path'])
        script_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(edit_window, text="Seç", command=lambda: self.browse_file(script_entry, filetypes=[("Python Files", "*.py")])).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(edit_window, text="Açıklama:").grid(row=1, column=0, padx=5, pady=5)
        description_entry = tk.Entry(edit_window, width=50)
        description_entry.insert(0, script_info.get('description', ''))
        description_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(edit_window, text="Link:").grid(row=2, column=0, padx=5, pady=5)
        link_entry = tk.Entry(edit_window, width=50)
        link_entry.insert(0, script_info.get('link', ''))
        link_entry.grid(row=2, column=1, padx=5, pady=5)

        def save_edited_script():
            script_path = script_entry.get()
            description = description_entry.get()
            link = link_entry.get()

            if not os.path.isfile(script_path):
                messagebox.showerror("Hata", "Geçerli bir script dosyası seçmelisiniz.")
                return

            self.scripts[index] = {
                "path": script_path,
                "description": description,
                "link": link
            }
            self.save_scripts()
            self.refresh_scripts()
            edit_window.destroy()

        tk.Button(edit_window, text="Kaydet", command=save_edited_script).grid(row=3, column=1, padx=5, pady=5)

    def remove_script(self, index):
        confirm = messagebox.askyesno("Sil", "Bu scripti silmek istediğinize emin misiniz?")
        if confirm:
            del self.scripts[index]
            self.save_scripts()
            self.refresh_scripts()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScriptManagerApp(root)
    root.mainloop()
