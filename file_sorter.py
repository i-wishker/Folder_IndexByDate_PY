import os
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

IGNORE_FILE = ".file_sorter_ignore.txt"

class FileSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Sorter by Creation Date")
        self.root.geometry("720x480")
        self.root.resizable(False, False)

        self.directory = None
        self.rename_map = []
        self.temp_ignored = set()
        self.perma_ignored = set()

        self.build_ui()

    def build_ui(self):
        tk.Label(
            self.root,
            text="File Sorter (Windows)",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=10)

        # Top buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Choose Folder", command=self.choose_directory)\
            .grid(row=0, column=0, padx=6)

        self.confirm_btn = ttk.Button(
            btn_frame, text="Confirm Rename",
            command=self.confirm_rename, state=tk.DISABLED
        )
        self.confirm_btn.grid(row=0, column=1, padx=6)

        # Ignore buttons
        ttk.Button(
            btn_frame, text="Ignore Temporarily",
            command=self.ignore_temp
        ).grid(row=0, column=2, padx=6)

        ttk.Button(
            btn_frame, text="Ignore Permanently",
            command=self.ignore_permanent
        ).grid(row=0, column=3, padx=6)

        # Preview
        tk.Label(
            self.root,
            text="Preview (select files to ignore)",
            font=("Segoe UI", 11, "bold")
        ).pack(pady=(10, 5))

        preview_frame = tk.Frame(self.root)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=15)

        scrollbar = tk.Scrollbar(preview_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.preview_list = tk.Listbox(
            preview_frame,
            font=("Consolas", 10),
            selectmode=tk.EXTENDED,
            yscrollcommand=scrollbar.set
        )
        self.preview_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.preview_list.yview)

        self.status = tk.Label(
            self.root, text="Select a folder to begin",
            relief=tk.SUNKEN, anchor="w", font=("Segoe UI", 9)
        )
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

    def load_permanent_ignores(self):
        path = os.path.join(self.directory, IGNORE_FILE)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.perma_ignored = set(line.strip() for line in f)

    def save_permanent_ignores(self):
        path = os.path.join(self.directory, IGNORE_FILE)
        with open(path, "w", encoding="utf-8") as f:
            for name in sorted(self.perma_ignored):
                f.write(name + "\n")

    def choose_directory(self):
        self.directory = filedialog.askdirectory()
        if not self.directory:
            return

        self.temp_ignored.clear()
        self.rename_map.clear()
        self.preview_list.delete(0, tk.END)
        self.confirm_btn.config(state=tk.DISABLED)

        self.load_permanent_ignores()

        files = [
            f for f in os.listdir(self.directory)
            if os.path.isfile(os.path.join(self.directory, f))
            and f not in self.perma_ignored
        ]

        if not files:
            messagebox.showinfo("Info", "No files found.")
            return

        files.sort(key=lambda f: os.stat(os.path.join(self.directory, f)).st_ctime)
        used_names = {}

        for file in files:
            if file in self.temp_ignored:
                continue

            ctime = os.stat(os.path.join(self.directory, file)).st_ctime
            date_str = datetime.fromtimestamp(ctime).strftime("%Y-%m-%d")
            _, ext = os.path.splitext(file)

            base = f"{date_str}{ext}"
            count = used_names.get(base, 0)
            new_name = f"{date_str}_{count}{ext}" if count else base
            used_names[base] = count + 1

            if file != new_name:
                self.rename_map.append((file, new_name))
                self.preview_list.insert(tk.END, f"{file} → {new_name}")

        if self.rename_map:
            self.confirm_btn.config(state=tk.NORMAL)
            self.status.config(text=f"Ready to rename {len(self.rename_map)} files")
        else:
            self.status.config(text="No changes needed")

    def get_selected_files(self):
        selected = self.preview_list.curselection()
        files = []
        for i in selected:
            old_name = self.preview_list.get(i).split(" → ")[0]
            files.append(old_name)
        return files

    def ignore_temp(self):
        files = self.get_selected_files()
        if not files:
            return
        self.temp_ignored.update(files)
        self.choose_directory()
        self.status.config(text="Temporarily ignored selected files")

    def ignore_permanent(self):
        files = self.get_selected_files()
        if not files:
            return

        if not messagebox.askyesno(
            "Permanent Ignore",
            "These files will NEVER be renamed again.\nContinue?"
        ):
            return

        self.perma_ignored.update(files)
        self.save_permanent_ignores()
        self.choose_directory()
        self.status.config(text="Permanently ignored selected files")

    def confirm_rename(self):
        if not self.rename_map:
            return

        if not messagebox.askyesno(
            "Confirm Rename",
            f"Rename {len(self.rename_map)} files?"
        ):
            return

        for old, new in self.rename_map:
            os.rename(
                os.path.join(self.directory, old),
                os.path.join(self.directory, new)
            )

        self.preview_list.delete(0, tk.END)
        self.rename_map.clear()
        self.confirm_btn.config(state=tk.DISABLED)
        self.status.config(text="✅ Files renamed successfully")

def main():
    root = tk.Tk()
    FileSorterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
