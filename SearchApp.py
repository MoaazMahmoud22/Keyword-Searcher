import threading
import KeywordSearcher
from tkinter import Tk, Label, Entry, Button, filedialog, Text, Spinbox, messagebox, Toplevel
from tkinter.scrolledtext import ScrolledText

class SearchApp:
    def __init__(self):
        self.root = Tk()
        self.root.title("Step-by-Step File Search Tool")
        self.file_list = []
        self.keyword = ""
        self.thread_count = 1
        self.thread_windows = {}
        self.root.geometry("700x500")
        self.build_file_selection_ui()

    def build_file_selection_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        Label(self.root, text="Step 1: Select Files to Search", font=("Arial", 14)).pack(pady=10)
        Button(self.root, text="Select Files", command=self.select_files).pack(pady=10)
        Button(self.root, text="Next", command=self.build_thread_selection_ui).pack(pady=10)

    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Text Files", "*.txt")])
        if files:
            self.file_list = files
            messagebox.showinfo("Files Selected", f"{len(files)} files selected.")

    def build_thread_selection_ui(self):
        if not self.file_list:
            messagebox.showerror("Error", "Please select files before proceeding.")
            return

        for widget in self.root.winfo_children():
            widget.destroy()

        Label(self.root, text="Step 2: Select Number of Threads", font=("Arial", 14)).pack(pady=10)
        self.thread_spinbox = Spinbox(self.root, from_=1, to=10, width=5)
        self.thread_spinbox.pack(pady=10)
        Button(self.root, text="Back", command=self.build_file_selection_ui).pack(pady=5)
        Button(self.root, text="Next", command=self.build_keyword_entry_ui).pack(pady=10)

    def build_keyword_entry_ui(self):
        self.thread_count = int(self.thread_spinbox.get())

        for widget in self.root.winfo_children():
            widget.destroy()

        Label(self.root, text="Step 3: Enter Keyword to Search", font=("Arial", 14)).pack(pady=10)
        self.keyword_entry = Entry(self.root, width=40)
        self.keyword_entry.pack(pady=10)
        Button(self.root, text="Back", command=self.build_thread_selection_ui).pack(pady=5)
        Button(self.root, text="Start Search", command=self.Search_Queue).pack(pady=10)

    def create_thread_window(self, thread_id):
        window = Toplevel(self.root)
        window.title(f"Thread {thread_id} Progress")
        window.geometry("500x400")
        text_widget = ScrolledText(window, wrap="word")
        text_widget.pack(fill="both", expand=True)
        self.thread_windows[thread_id] = text_widget

    def highlight_matches(self, text_widget, keyword):
        start_idx = "1.0"
        while True:
            start_idx = text_widget.search(keyword, start_idx, nocase=1, stopindex="end")
            if not start_idx:
                break
            end_idx = f"{start_idx}+{len(keyword)}c"
            text_widget.tag_add("highlight", start_idx, end_idx)
            text_widget.tag_config("highlight", background="yellow", foreground="red")
            start_idx = end_idx

    def update_thread_window(self, thread_id, file_path, matches):
        text_widget = self.thread_windows.get(thread_id)
        if text_widget:
            text_widget.insert("end", f"File: {file_path}\n", "bold")
            for line_num, line in matches:
                text_widget.insert("end", f"  Line {line_num}: {line}\n")
            text_widget.insert("end", "\n")
            self.highlight_matches(text_widget, self.keyword)

    def Search_Queue(self):
        self.keyword = self.keyword_entry.get().strip()
        if not self.keyword:
            messagebox.showerror("Error", "Please enter a keyword.")
            return

        if not self.file_list:
            messagebox.showerror("Error", "No files selected.")
            return

        for thread_id in range(1, self.thread_count + 1):
            self.create_thread_window(thread_id)

        searcher = KeywordSearcher(self.keyword, self.file_list)
        threading.Thread(
            target=searcher.Search_Queue,
            args=(self.thread_count, self.update_thread_window),
            daemon=True,
        ).start()