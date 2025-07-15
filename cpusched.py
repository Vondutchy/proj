import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque

# ---------------- Scheduling Logic ---------------- #
def fcfs(processes):
    processes.sort(key=lambda x: x['arrival_time'])
    time = 0
    gantt_chart = []
    for process in processes:
        if time < process['arrival_time']:
            time = process['arrival_time']
        start = time
        finish = time + process['burst_time']
        time = finish

        process['start_time'] = start
        process['completion_time'] = finish
        process['turnaround_time'] = finish - process['arrival_time']
        process['waiting_time'] = process['turnaround_time'] - process['burst_time']
        gantt_chart.append((process['pid'], start, finish))
    return processes, gantt_chart

def sjf(processes):
    n = len(processes)
    completed = 0
    time = 0
    gantt_chart = []
    processes = sorted(processes, key=lambda x: x['arrival_time'])
    is_completed = [False] * n

    while completed < n:
        ready_queue = [p for i, p in enumerate(processes)
                       if p['arrival_time'] <= time and not is_completed[i]]

        if ready_queue:
            current = min(ready_queue, key=lambda x: x['burst_time'])
            idx = processes.index(current)

            start = time
            finish = time + current['burst_time']
            time = finish

            processes[idx]['start_time'] = start
            processes[idx]['completion_time'] = finish
            processes[idx]['turnaround_time'] = finish - current['arrival_time']
            processes[idx]['waiting_time'] = processes[idx]['turnaround_time'] - current['burst_time']

            is_completed[idx] = True
            completed += 1
            gantt_chart.append((current['pid'], start, finish))
        else:
            time += 1

    return processes, gantt_chart

def npp(processes, higher_number_is_higher):
    n = len(processes)
    completed = 0
    time = 0
    gantt_chart = []
    processes = sorted(processes, key=lambda x: x['arrival_time'])
    is_completed = [False] * n

    while completed < n:
        ready_queue = [p for i, p in enumerate(processes)
                       if p['arrival_time'] <= time and not is_completed[i]]

        if ready_queue:
            current = min(
                ready_queue,
                key=lambda x: -x['priority'] if higher_number_is_higher else x['priority']
            )
            idx = processes.index(current)

            start = time
            finish = time + current['burst_time']
            time = finish

            processes[idx]['start_time'] = start
            processes[idx]['completion_time'] = finish
            processes[idx]['turnaround_time'] = finish - current['arrival_time']
            processes[idx]['waiting_time'] = processes[idx]['turnaround_time'] - current['burst_time']

            is_completed[idx] = True
            completed += 1
            gantt_chart.append((current['pid'], start, finish))
        else:
            time += 1

    return processes, gantt_chart

def pp(processes, higher_number_is_higher):
    n = len(processes)
    time = 0
    completed = 0
    gantt_chart = []
    remaining_bt = [p['burst_time'] for p in processes]
    is_completed = [False] * n

    for p in processes:
        p['start_time'] = None

    while completed < n:
        ready_queue = [i for i in range(n) if processes[i]['arrival_time'] <= time and not is_completed[i]]
        if ready_queue:
            if higher_number_is_higher:
                current = max(ready_queue, key=lambda i: processes[i]['priority'])
            else:
                current = min(ready_queue, key=lambda i: processes[i]['priority'])

            if processes[current]['start_time'] is None:
                processes[current]['start_time'] = time

            remaining_bt[current] -= 1

            if not gantt_chart or gantt_chart[-1][0] != processes[current]['pid']:
                gantt_chart.append((processes[current]['pid'], time, time + 1))
            else:
                gantt_chart[-1] = (gantt_chart[-1][0], gantt_chart[-1][1], time + 1)

            if remaining_bt[current] == 0:
                is_completed[current] = True
                completed += 1
                processes[current]['completion_time'] = time + 1
                processes[current]['turnaround_time'] = processes[current]['completion_time'] - processes[current]['arrival_time']
                processes[current]['waiting_time'] = processes[current]['turnaround_time'] - processes[current]['burst_time']
            time += 1
        else:
            time += 1

    return processes, gantt_chart


def rr(processes, q=2):
    processes = sorted(processes, key=lambda x: x['arrival_time'])
    n = len(processes)
    ready_queue = deque()
    gantt_chart = []
    time = 0
    remaining_bt = {p['pid']: p['burst_time'] for p in processes}
    completion = {}
    visited = set()

    i = 0  # track process arrival

    while i < n or ready_queue:
        # Add newly arrived processes to ready queue
        while i < n and processes[i]['arrival_time'] <= time:
            ready_queue.append(processes[i]['pid'])
            visited.add(processes[i]['pid'])
            i += 1

        if not ready_queue:
            # No process is ready, advance time
            time = processes[i]['arrival_time']
            continue

        pid = ready_queue.popleft()
        exec_time = min(q, remaining_bt[pid])
        start = time
        time += exec_time
        finish = time
        gantt_chart.append((pid, start, finish))
        remaining_bt[pid] -= exec_time

        # Check for new arrivals during execution
        while i < n and processes[i]['arrival_time'] <= time:
            if processes[i]['pid'] not in visited:
                ready_queue.append(processes[i]['pid'])
                visited.add(processes[i]['pid'])
            i += 1

        # If not finished, requeue
        if remaining_bt[pid] > 0:
            ready_queue.append(pid)
        else:
            completion[pid] = finish

    # Compute metrics
    for p in processes:
        pid = p['pid']
        p['completion_time'] = completion[pid]
        p['turnaround_time'] = p['completion_time'] - p['arrival_time']
        p['waiting_time'] = p['turnaround_time'] - p['burst_time']
        # Optional: Get first time it was seen in Gantt chart
        p['start_time'] = next(start for p_id, start, _ in gantt_chart if p_id == pid)

    return processes, gantt_chart

def sjf_preemptive(processes):
    n = len(processes)
    processes = sorted(processes, key=lambda x: x['arrival_time'])

    remaining_bt = {p['pid']: p['burst_time'] for p in processes}
    arrival_dict = {p['pid']: p['arrival_time'] for p in processes}
    process_info = {p['pid']: p for p in processes}

    complete = 0
    time = 0
    shortest = None
    gantt_chart = []
    current_pid = None
    start_time = {}

    while complete < n:
        ready_queue = [pid for pid in remaining_bt if arrival_dict[pid] <= time and remaining_bt[pid] > 0]
        if ready_queue:
            shortest = min(ready_queue, key=lambda pid: remaining_bt[pid])

            if current_pid != shortest:
                if current_pid is not None and gantt_chart and gantt_chart[-1][0] == current_pid:
                    gantt_chart[-1] = (current_pid, gantt_chart[-1][1], time)
                gantt_chart.append((shortest, time, None))
                if shortest not in start_time:
                    start_time[shortest] = time
                current_pid = shortest

            remaining_bt[shortest] -= 1

            if remaining_bt[shortest] == 0:
                complete += 1
                process_info[shortest]['completion_time'] = time + 1
                process_info[shortest]['turnaround_time'] = process_info[shortest]['completion_time'] - arrival_dict[shortest]
                process_info[shortest]['waiting_time'] = process_info[shortest]['turnaround_time'] - process_info[shortest]['burst_time']
        else:
            current_pid = None
        time += 1

    for i in range(len(gantt_chart)):
        pid, start, end = gantt_chart[i]
        if end is None:
            gantt_chart[i] = (pid, start, time)

    for pid in process_info:
        process_info[pid]['start_time'] = start_time[pid]

    return list(process_info.values()), gantt_chart

# ---------------- GUI Functions ---------------- #
def generate_table():
    try:
        count = int(entry_count.get())
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
        canvas.create_rectangle(x, 20, x + (end - start) * 30, 70, fill="lightblue")
        canvas.create_text(x + (end - start) * 15, 45, text=pid)
        canvas.create_text(x, 75, text=str(start), anchor=tk.NW)
        x += (end - start) * 30
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
