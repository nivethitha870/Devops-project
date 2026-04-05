import os
import re
import glob
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import heapq
from collections import defaultdict
from langdetect import detect
from translate import Translator as OfflineTranslator
from matplotlib import pyplot as plt
from PyPDF2 import PdfReader


class Graph:
    def __init__(self):
        self.graph = {}

    def add_edge(self, u, v):
        if u not in self.graph:
            self.graph[u] = []
        if v not in self.graph:
            self.graph[v] = []
        self.graph[u].append(v)
        self.graph[v].append(u)

    def dfs(self, start):
        visited = set()
        result = []

        def dfs_recursive(vertex):
            visited.add(vertex)
            result.append(vertex)
            for neighbor in self.graph.get(vertex, []):
                if neighbor not in visited:
                    dfs_recursive(neighbor)

        dfs_recursive(start)
        return result

class ResumeShortlister:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 AI Resume Shortlister")
        self.root.geometry("1150x780")
        self.root.configure(bg="#f0f8ff")

        self.keyword_hash = defaultdict(int)
        self.skill_graph = Graph()
        self.candidates = []
        self.resume_texts = {}

        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TLabel", background="#f0f8ff", font=("Segoe UI", 11))
        style.configure("Header.TLabel", font=("Segoe UI", 20, "bold"), background="#f0f8ff", foreground="#0a9396")
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6, background="#0a9396", foreground="#ffffff")
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10))

        ttk.Label(self.root, text="AI‑Powered Resume Shortlisting", style="Header.TLabel").pack(pady=10)

        ctrl_frame = ttk.Frame(self.root)
        ctrl_frame.pack(fill='x', pady=10)

        ttk.Label(ctrl_frame, text="Required Skills (comma-separated):").grid(row=0, column=0, sticky='w', padx=10)
        self.search_entry = ttk.Entry(ctrl_frame, width=60)
        self.search_entry.grid(row=1, column=0, padx=10, pady=5, sticky='w')

        btn_frame = ttk.Frame(ctrl_frame)
        btn_frame.grid(row=1, column=1, sticky='e', padx=10)
        ttk.Button(btn_frame, text="Load Resumes", command=self.load_resumes_from_folder).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Show Graph", command=self.show_bar_graph).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Summary Dashboard", command=self.show_summary_dashboard).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Clear", command=self.clear_results).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Exit", command=self.root.destroy).pack(side='left', padx=5)

        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=10)

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10)

        self.tree = ttk.Treeview(main_frame, columns=("#1", "#2", "#3"), show='headings', selectmode='browse')
        self.tree.heading("#1", text="Rank")
        self.tree.heading("#2", text="Name")
        self.tree.heading("#3", text="Score")
        self.tree.column("#1", width=60, anchor='center')
        self.tree.column("#2", width=300)
        self.tree.column("#3", width=80, anchor='center')
        self.tree.bind("<<TreeviewSelect>>", self.show_resume_preview)
        self.tree.pack(side='left', fill='both', expand=True)

        scroll = ttk.Scrollbar(main_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side='left', fill='y')

        self.preview = scrolledtext.ScrolledText(self.root, height=15, wrap='word', font=("Consolas", 11), bg="#ffffff", fg="#333333")
        self.preview.pack(fill='both', expand=True, padx=10, pady=10)

    def clear_results(self):
        self.tree.delete(*self.tree.get_children())
        self.preview.delete("1.0", tk.END)
        self.candidates.clear()
        self.keyword_hash.clear()
        self.skill_graph = Graph()
        self.resume_texts.clear()

    def read_text_from_file(self, filepath):
        ext = os.path.splitext(filepath)[1].lower()
        try:
            if ext == ".txt":
                with open(filepath, "r", encoding='utf-8') as f:
                    return f.read()
            elif ext == ".pdf":
                reader = PdfReader(filepath)
                return " ".join(page.extract_text() or "" for page in reader.pages)
            elif ext == ".docx":
                doc = Document(filepath)
                return "\n".join(p.text for p in doc.paragraphs)
        except Exception as e:
            return f"[Error reading file {filepath}]: {e}"
        return ""

    def process_resume(self, text, required_skills):
        try:
            lang = detect(text)
            if lang != 'en':
                translator = OfflineTranslator(from_lang=lang, to_lang="en")
                text = translator.translate(text)
        except Exception:
            pass

        keywords = re.findall(r'\b\w+\b', text.lower())
        for word in keywords:
            self.keyword_hash[word] += 1

        for skill in required_skills:
            for related in required_skills:
                if skill != related:
                    self.skill_graph.add_edge(skill, related)

        matched = set(keywords) & set(required_skills)
        root = next(iter(matched), '')
        related_skills = self.skill_graph.dfs(root) if root else []
        related_score = sum(1 for s in related_skills if s in matched)
        return len(matched) * 2 + related_score

    def load_resumes_from_folder(self):
        folder = filedialog.askdirectory(title="Select Resume Folder")
        if not folder:
            return

        self.clear_results()
        req_skills = [s.strip().lower() for s in self.search_entry.get().split(',') if s.strip()]
        if not req_skills:
            messagebox.showwarning("No Skills", "Enter at least one required skill.")
            return

        files = glob.glob(os.path.join(folder, '*'))
        supported_exts = ('.txt', '.pdf', '.docx')
        files = [f for f in files if f.lower().endswith(supported_exts)]

        if not files:
            messagebox.showinfo("No Files", "No supported resume files found.")
            return

        for file in files:
            text = self.read_text_from_file(file)
            score = self.process_resume(text, req_skills)
            name_match = re.search(r'^Name:\s*(.+)', text, re.MULTILINE)
            name = name_match.group(1).strip() if name_match else os.path.basename(file)
            self.candidates.append((-score, name))
            self.resume_texts[name] = text

        sorted_cands = sorted(self.candidates)
        for rank, (neg_score, name) in enumerate(sorted_cands, 1):
            self.tree.insert('', 'end', values=(rank, name, -neg_score))

    def show_resume_preview(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        name = item['values'][1]
        text = self.resume_texts.get(name, "[No Preview Available]")
        self.preview.delete("1.0", tk.END)
        self.preview.insert(tk.END, text)

    def show_bar_graph(self):
        if not self.candidates:
            messagebox.showinfo("No Data", "Load resumes first.")
            return
        names = [name for _, name in sorted(self.candidates)]
        scores = [-score for score, _ in sorted(self.candidates)]

        plt.figure(figsize=(10, 5))
        bars = plt.bar(names, scores, color="#0a9396")
        plt.xticks(rotation=45, ha="right")
        plt.title("Skill Match Scores", fontsize=14)
        plt.ylabel("Score")
        plt.tight_layout()

        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.5, int(yval), ha='center', va='bottom', fontsize=9)

        plt.show()

    def show_summary_dashboard(self):
        if not self.candidates:
            messagebox.showinfo("No Data", "Please load resumes first.")
            return

        top_candidates = sorted(self.candidates)[:3]
        avg_score = sum(-score for score, _ in self.candidates) / len(self.candidates)
        top_name = top_candidates[0][1]
        top_score = -top_candidates[0][0]

        dash = tk.Toplevel(self.root)
        dash.title("📋 Final Summary Dashboard")
        dash.geometry("500x400")
        dash.configure(bg="#ffe5ec")

        tk.Label(dash, text="🏆 Resume Summary Dashboard", font=("Segoe UI", 18, "bold"), bg="#ffe5ec", fg="#d6336c").pack(pady=10)

        tk.Label(dash, text=f"Top Scorer: {top_name}", font=("Segoe UI", 14), bg="#ffe5ec", fg="#800f2f").pack(pady=10)
        tk.Label(dash, text=f"Top Score: {top_score}", font=("Segoe UI", 14), bg="#ffe5ec", fg="#800f2f").pack()

        tk.Label(dash, text=f"Average Score: {avg_score:.2f}", font=("Segoe UI", 13), bg="#ffe5ec", fg="#6a040f").pack(pady=10)

        tk.Label(dash, text="Top 3 Candidates", font=("Segoe UI", 14, "bold"), bg="#ffe5ec", fg="#9d0208").pack(pady=5)
        for i, (_, name) in enumerate(top_candidates, 1):
            tk.Label(dash, text=f"{i}. {name}", font=("Segoe UI", 12), bg="#ffe5ec").pack()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ResumeShortlister()
    app.run()
