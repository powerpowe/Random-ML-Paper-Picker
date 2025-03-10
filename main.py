import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import random

# 학회 목록 가져오기
conf_root = './paperlist'
conf_dirs = [d for d in os.listdir(conf_root) if os.path.isdir(os.path.join(conf_root, d))]

def load_years(conf):
    """ 선택한 학회의 연도 리스트 반환 """
    conf_path = os.path.join(conf_root, conf)
    conf_files = [f for f in os.listdir(conf_path) if f.endswith('.json')]
    years = sorted([file.replace(conf, '').replace('.json', '') for file in conf_files])
    return years

def load_papers(selected_confs, selected_years):
    """ 선택한 학회 및 연도에서 논문을 로드 """
    papers = []
    for conf in selected_confs:
        for year in selected_years:
            conf_path = os.path.join(conf_root, conf, f"{conf}{year}.json")
            try:
                with open(conf_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    for paper in json_data:
                        papers.append({
                            "title": paper.get("title", "N/A"),
                            "author": paper.get("author", "N/A"),
                            "conference": conf,
                            "year": year,
                            "status": paper.get("status", "N/A")
                        })
            except Exception:
                continue
    return papers

# GUI 설정
root = tk.Tk()
root.title("Top-tier ML Conference Papers Viewer / Random Picker")
root.geometry("1000x600")

# 학회 선택 체크박스
frame_conf = tk.LabelFrame(root, text="Select Conferences")
frame_conf.pack(fill=tk.X, padx=10, pady=5)

conf_vars = {conf: tk.BooleanVar() for conf in conf_dirs}
for conf, var in conf_vars.items():
    ttk.Checkbutton(frame_conf, text=conf, variable=var).pack(side=tk.LEFT)

def toggle_all_confs(state):
    for var in conf_vars.values():
        var.set(state)
    update_years()

ttk.Button(frame_conf, text="Select All", command=lambda: toggle_all_confs(True)).pack(side=tk.LEFT, padx=5)
ttk.Button(frame_conf, text="Deselect All", command=lambda: toggle_all_confs(False)).pack(side=tk.LEFT, padx=5)

# 연도 선택 체크박스
frame_year = tk.LabelFrame(root, text="Select Years")
frame_year.pack(fill=tk.X, padx=10, pady=5)

year_vars = {}
button_frame_year = tk.Frame(frame_year)
button_frame_year.pack(fill=tk.X, padx=5, pady=5)

def update_years():
    """ 선택한 학회에 따라 연도 목록 갱신 """
    selected_confs = [conf for conf, var in conf_vars.items() if var.get()]
    all_years = sorted(set(sum([load_years(conf) for conf in selected_confs], [])))
    
    # 기존 체크박스 삭제 (버튼은 유지)
    for widget in frame_year.winfo_children():
        if widget != button_frame_year:
            widget.destroy()
    
    global year_vars
    year_vars = {year: tk.BooleanVar() for year in all_years}
    for year, var in year_vars.items():
        ttk.Checkbutton(frame_year, text=year, variable=var).pack(side=tk.LEFT)

def toggle_all_years(state):
    for var in year_vars.values():
        var.set(state)
    
# 논문 리스트 갱신 함수
def update_paper_list():
    selected_confs = [conf for conf, var in conf_vars.items() if var.get()]
    selected_years = [year for year, var in year_vars.items() if var.get()]
    
    if not selected_confs or not selected_years:
        messagebox.showwarning("Warning", "Please select at least one conference and one year.")
        return
    
    papers = load_papers(selected_confs, selected_years)
    listbox.delete(0, tk.END)
    for paper in papers:
        listbox.insert(tk.END, f"[{paper['conference']} {paper['year']}] {paper['title']}")
    listbox.papers = papers

def pick_random_paper():
    selected_confs = [conf for conf, var in conf_vars.items() if var.get()]
    selected_years = [year for year, var in year_vars.items() if var.get()]
    
    if not selected_confs or not selected_years:
        messagebox.showwarning("Warning", "Please select at least one conference and one year.")
        return
    
    papers = load_papers(selected_confs, selected_years)
    if not papers:
        messagebox.showinfo("Random Paper", "No paper.")
        return
    
    for i in range(100000):
        paper = random.choice(papers)
        if paper['status'].lower() in ['reject', 'withdraw']:
            print(i, paper['title'], paper['status'])
            continue
        else:
            break

    title_text.delete("1.0", tk.END)
    title_text.insert(tk.END, paper["title"])
    authors_text.delete("1.0", tk.END)
    authors_text.insert(tk.END, paper["author"])
    conf_year_text.delete("1.0", tk.END)
    conf_year_text.insert(tk.END, f"{paper['conference']} {paper['year']}")

def show_details(event):
    selection = listbox.curselection()
    if selection:
        index = selection[0]
        paper = listbox.papers[index]
        title_text.delete("1.0", tk.END)
        title_text.insert(tk.END, paper["title"])
        authors_text.delete("1.0", tk.END)
        authors_text.insert(tk.END, paper["author"])
        conf_year_text.delete("1.0", tk.END)
        conf_year_text.insert(tk.END, f"{paper['conference']} {paper['year']}")
    paper = random.choice(papers)
    title_text.delete("1.0", tk.END)
    title_text.insert(tk.END, paper["title"])
    authors_text.delete("1.0", tk.END)
    authors_text.insert(tk.END, paper["author"])
    conf_year_text.delete("1.0", tk.END)
    conf_year_text.insert(tk.END, f"{paper['conference']} {paper['year']}")

ttk.Button(button_frame_year, text="Select All", command=lambda: toggle_all_years(True)).pack(side=tk.LEFT, padx=5)
ttk.Button(button_frame_year, text="Deselect All", command=lambda: toggle_all_years(False)).pack(side=tk.LEFT, padx=5)

# 버튼 추가
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)

ttk.Button(frame_buttons, text="Update Years", command=update_years).pack(side=tk.LEFT, padx=5)
ttk.Button(frame_buttons, text="Load Papers", command=update_paper_list).pack(side=tk.LEFT, padx=5)
ttk.Button(frame_buttons, text="Pick Random Paper", command=pick_random_paper).pack(side=tk.LEFT, padx=5)

# 논문 표시 영역
frame_list = tk.Frame(root)
frame_list.pack(side=tk.LEFT, fill=tk.Y)

listbox = tk.Listbox(frame_list, width=50, height=30)
listbox.pack(side=tk.LEFT, fill=tk.Y)

scrollbar = tk.Scrollbar(frame_list, orient=tk.VERTICAL)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)

# 논문 상세 정보
frame_details = tk.Frame(root)
frame_details.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

title_label = ttk.Label(frame_details, text="Title:", font=("Arial", 12, "bold"))
title_label.pack(anchor="w", padx=10, pady=5)
title_text = tk.Text(frame_details, height=3, wrap=tk.WORD)
title_text.pack(fill=tk.X, padx=10)

authors_label = ttk.Label(frame_details, text="Authors:", font=("Arial", 12, "bold"))
authors_label.pack(anchor="w", padx=10, pady=5)
authors_text = tk.Text(frame_details, height=3, wrap=tk.WORD)
authors_text.pack(fill=tk.X, padx=10)

conf_year_label = ttk.Label(frame_details, text="Conference & Year:", font=("Arial", 12, "bold"))
conf_year_label.pack(anchor="w", padx=10, pady=5)
conf_year_text = tk.Text(frame_details, height=2, wrap=tk.WORD)
conf_year_text.pack(fill=tk.X, padx=10)



listbox.bind("<<ListboxSelect>>", show_details)

root.mainloop()