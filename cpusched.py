import tkinter as tk
from tkinter import ttk, messagebox

from algorithms import fcfs, sjf, npp, pp, sjf_preemptive, rr


# ---------------- GUI Functions ---------------- #
def generate_table():
    try:
        count = min(int(entry_count.get()), 8)
        if count <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Input Error", "Enter a valid number of processes.")
        return

    for widget in frame_table_inputs.winfo_children():
        widget.destroy()

    is_priority = algo_var.get() in ["NPP", "PP"]
    headers = ["PID", "Arrival Time", "Burst Time"]
    if is_priority:
        headers.append("Priority")

    for j, header in enumerate(headers):
        tk.Label(frame_table_inputs, text=header, width=15, borderwidth=1, relief="solid").grid(row=0, column=j)

    input_entries.clear()

    for i in range(count):
        row = []
        tk.Label(frame_table_inputs, text=f"P{i+1}", width=15, borderwidth=1, relief="solid").grid(row=i+1, column=0)

        at_entry = tk.Entry(frame_table_inputs, width=15, borderwidth=1, relief="solid")
        at_entry.grid(row=i+1, column=1)
        row.append(at_entry)

        bt_entry = tk.Entry(frame_table_inputs, width=15, borderwidth=1, relief="solid")
        bt_entry.grid(row=i+1, column=2)
        row.append(bt_entry)

        if is_priority:
            pr_entry = tk.Entry(frame_table_inputs, width=15, borderwidth=1, relief="solid")
            pr_entry.grid(row=i+1, column=3)
            row.append(pr_entry)

        input_entries.append(row)

def run_scheduler():
    algo = algo_var.get()
    high_is_high = priority_mode_var.get() == "Higher number = higher priority"
    processes = []

    for i, row in enumerate(input_entries):
        try:
            at = int(row[0].get())
            bt = int(row[1].get())
            pr = int(row[2].get()) if algo in ["NPP", "PP"] and len(row) > 2 else 0
            processes.append({'pid': f"P{i+1}", 'arrival_time': at, 'burst_time': bt, 'priority': pr})
        except ValueError:
            messagebox.showerror("Input Error", f"Invalid input in row {i+1}")
            return

    if algo == "FCFS":
        result, gantt = fcfs(processes)
    elif algo == "SJF":
        result, gantt = sjf(processes)
    elif algo == "NPP":
        result, gantt = npp(processes, high_is_high)
    elif algo == "PP":
        result, gantt = pp(processes, high_is_high)
    elif algo == "SRTF":
        result, gantt = sjf_preemptive(processes)
    elif algo == "RR":
        result, gantt = rr(processes, int(q.get()))
    else:
        messagebox.showerror("Error", "Unknown algorithm selected.")
        return

    update_table(result)
    draw_gantt(gantt)

def update_table(results):
    for i in table.get_children():
        table.delete(i)

    total_wt = 0
    total_tat = 0
    for p in results:
        total_wt += p['waiting_time']
        total_tat += p['turnaround_time']
        table.insert("", tk.END, values=(
            p['pid'], p['arrival_time'], p['burst_time'],
            p['start_time'], p['completion_time'],
            p['waiting_time'], p['turnaround_time']
        ))

    n = len(results)
    avg_wt = total_wt / n if n > 0 else 0
    avg_tat = total_tat / n if n > 0 else 0
    label_avg.config(
        text=f"Average Waiting Time: {avg_wt:.2f}    |    Average Turnaround Time: {avg_tat:.2f}"
    )

def draw_gantt(gantt):
    canvas.delete("all")
    x = 10
    for pid, start, end in gantt:
        color = "gray" if pid == "Idle" else "lightblue"
        canvas.create_rectangle(x, 20, x + (end - start) * 30, 70, fill=color)
        canvas.create_text(x + (end - start) * 15, 45, text=pid)
        canvas.create_text(x, 75, text=str(start), anchor=tk.NW)
        x += (end - start) * 30
    if gantt:
        canvas.create_text(x, 75, text=str(gantt[-1][2]), anchor=tk.NW)


def on_algo_change(event=None):
    if algo_var.get() in ["NPP", "PP"]:
        label_prio_type.pack()
        priority_mode_dropdown.pack()
    else:
        label_prio_type.pack_forget()
        priority_mode_dropdown.pack_forget()

    if algo_var.get() == 'RR':
        q_label.pack(side=tk.LEFT)
        q.pack(side=tk.LEFT, padx=5)
    else:
        q_label.pack_forget()
        q.pack_forget()


    try:
        if int(entry_count.get()) > 0:
            generate_table()
    except ValueError:
        pass

# ---------------- Tkinter UI ---------------- #
root = tk.Tk()
root.title("CPU Scheduling Simulator")
root.geometry("1920x1080")

input_entries = []

# Top input: number of processes
frame_top = tk.Frame(root)
frame_top.pack(pady=10)
tk.Label(frame_top, text="Number of Processes:").pack(side=tk.LEFT)
entry_count = tk.Entry(frame_top, width=5)
entry_count.pack(side=tk.LEFT, padx=5)
tk.Button(frame_top, text="Generate Table", command=generate_table).pack(side=tk.LEFT)

# Algorithm selection
algo_var = tk.StringVar(value="FCFS")
tk.Label(root, text="Select Algorithm:").pack()
algo_dropdown = ttk.Combobox(root, textvariable=algo_var, values=["FCFS", "SJF", "NPP", "PP", "SRTF", "RR"], state="readonly")
algo_dropdown.pack()
algo_dropdown.bind("<<ComboboxSelected>>", on_algo_change)

priority_mode_var = tk.StringVar(value="Lower number = higher priority")
label_prio_type = tk.Label(root, text="Priority Type:")
priority_mode_dropdown = ttk.Combobox(
    root,
    textvariable=priority_mode_var,
    values=["Lower number = higher priority", "Higher number = higher priority"],
    state="readonly"
)

# Run button
tk.Button(root, text="Run Scheduler", command=run_scheduler).pack(pady=10)

frame_top = tk.Frame(root)
frame_top.pack(pady=10)
q_label = tk.Label(frame_top, text="q=")
q_label.pack(side=tk.LEFT)
q = tk.Entry(frame_top, width=5)
q.pack(side=tk.LEFT, padx=5)

# Editable input table
frame_table_inputs = tk.Frame(root)
frame_table_inputs.pack(pady=10)

# Output Table
columns = ("PID", "AT", "BT", "ST", "CT", "WT", "TAT")
table = ttk.Treeview(root, columns=columns, show="headings", height=8)
for col in columns:
    table.heading(col, text=col)
table.pack(pady=10)

# Averages
label_avg = tk.Label(root, text="Average Waiting Time: 0.00ms    |    Average Turnaround Time: 0.00ms", font=("Arial", 12, "bold"))
label_avg.pack(pady=5)

# Gantt Chart
canvas = tk.Canvas(root, height=100, bg="white")
canvas.pack(pady=10, fill="x")

on_algo_change()
root.mainloop()
