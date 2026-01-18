import os
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ===================== CONFIG =====================
IGNORE_STORAGE_DIR = r"DirNameHere" #writer your IgnoreStorage here
IGNORE_FILE_PATH = os.path.join(IGNORE_STORAGE_DIR, "ignored_files.py")

ALWAYS_IGNORE = {".ignored_files.txt"}
# ==================================================


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

        os.makedirs(IGNORE_STORAGE_DIR, exist_ok=True)
        self.load_permanent_ignores()
        self.build_ui()

    # ---------------- UI ----------------
    def build_ui(self):
        tk.Label(
            self.root,
            text="File Sorter (Windows)",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=10)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Choose Folder", command=self.choose_directory)\
            .grid(row=0, column=0, padx=6)

        self.confirm_btn = ttk.Button(
            btn_frame, text="Confirm Rename",
            command=self.confirm_rename, state=tk.DISABLED
        )
        self.confirm_btn.grid(row=0, column=1, padx=6)

        ttk.Button(
            btn_frame, text="Ignore Temporarily",
            command=self.ignore_temp
        ).grid(row=0, column=2, padx=6)

        ttk.Button(
            btn_frame, text="Ignore Permanently",
            command=self.ignore_permanent
        ).grid(row=0, column=3, padx=6)

        tk.Label(
            self.root,
            text="Preview (old → new)",
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
            self.root,
            text="Select a folder to begin",
            anchor="w",
            relief=tk.SUNKEN,
            font=("Segoe UI", 9)
        )
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

    # ---------------- Ignore handling ----------------
    def load_permanent_ignores(self):
        if os.path.exists(IGNORE_FILE_PATH):
            with open(IGNORE_FILE_PATH, "r", encoding="utf-8") as f:
                self.perma_ignored = set(
                    line.strip() for line in f if line.strip()
                )

    def save_permanent_ignores(self):
        with open(IGNORE_FILE_PATH, "w", encoding="utf-8") as f:
            for name in sorted(self.perma_ignored):
                f.write(name + "\n")

    # ---------------- Core logic ----------------
    def choose_directory(self):
        self.directory = filedialog.askdirectory()
        if not self.directory:
            return

        self.preview_list.delete(0, tk.END)
        self.rename_map.clear()
        self.confirm_btn.config(state=tk.DISABLED)

        files = [
            f for f in os.listdir(self.directory)
            if os.path.isfile(os.path.join(self.directory, f))
            and f not in ALWAYS_IGNORE
            and f not in self.perma_ignored
            and f not in self.temp_ignored
        ]

        if not files:
            self.status.config(text="No eligible files found")
            return

        files.sort(key=lambda f: os.stat(os.path.join(self.directory, f)).st_ctime)
        used_names = {}

        for file in files:
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
        return [
            self.preview_list.get(i).split(" → ")[0]
            for i in self.preview_list.curselection()
        ]

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
            "These files will be ignored globally.\nContinue?"
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
