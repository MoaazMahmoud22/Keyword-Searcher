import threading
from queue import Queue

class KeywordSearcher:
    def __init__(self, keyword, file_list):
        self.keyword = keyword
        self.file_list = file_list
        self.results = []
        self.lock = threading.Lock()
        self.task_queue = Queue()

    def search_in_file(self, file_path):
        matches = []
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line_num, line in enumerate(file, start=1):
                    if self.keyword.lower() in line.lower():
                        matches.append((line_num, line.strip()))
        except Exception as e:
            matches.append((0, f"Error reading file: {e}"))
        return matches

    def Thread_Worker(self, thread_id, update_window):
        while not self.task_queue.empty():
            file_path = self.task_queue.get()
            matches = self.search_in_file(file_path)
            with self.lock:
                self.results.append((file_path, matches))
            update_window(thread_id, file_path, matches)
            self.task_queue.task_done()

    def Search_Queue(self, thread_count, update_window):
        for file_path in self.file_list:
            self.task_queue.put(file_path)

        threads = []
        for thread_id in range(1, thread_count + 1):
            thread = threading.Thread(target=self.Thread_Worker, args=(thread_id, update_window))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

