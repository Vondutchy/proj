from collections import deque

def fcfs(processes):
    processes.sort(key=lambda x: x['arrival_time'])
    time = 0
    gantt_chart = []
    for process in processes:
        if time < process['arrival_time']:
            gantt_chart.append(("Idle", time, process['arrival_time']))
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
            if not gantt_chart or gantt_chart[-1][0] != "Idle":
                gantt_chart.append(("Idle", time, time + 1))
            else:
                gantt_chart[-1] = ("Idle", gantt_chart[-1][1], time + 1)
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
            if not gantt_chart or gantt_chart[-1][0] != "Idle":
                gantt_chart.append(("Idle", time, time + 1))
            else:
                gantt_chart[-1] = ("Idle", gantt_chart[-1][1], time + 1)
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
            if not gantt_chart or gantt_chart[-1][0] != "Idle":
                gantt_chart.append(("Idle", time, time + 1))
            else:
                gantt_chart[-1] = ("Idle", gantt_chart[-1][1], time + 1)
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
        # enqueue processes which arrived
        while i < n and processes[i]['arrival_time'] <= time:
            ready_queue.append(processes[i]['pid'])
            visited.add(processes[i]['pid'])
            i += 1

        # handle idle
        if not ready_queue:
            next_arrival = processes[i]['arrival_time']
            if not gantt_chart or gantt_chart[-1][0] != "Idle":
                gantt_chart.append(("Idle", time, next_arrival))
            else:
                gantt_chart[-1] = ("Idle", gantt_chart[-1][1], next_arrival)
            time = next_arrival
            continue

        # process next in queue
        pid = ready_queue.popleft()
        exec_time = min(q, remaining_bt[pid])
        start = time
        time += exec_time
        finish = time
        gantt_chart.append((pid, start, finish))
        remaining_bt[pid] -= exec_time

        # enqueue processes which arrived during execution
        while i < n and processes[i]['arrival_time'] <= time:
            if processes[i]['pid'] not in visited:
                ready_queue.append(processes[i]['pid'])
                visited.add(processes[i]['pid'])
            i += 1

        if remaining_bt[pid] > 0:  # add back to queue
            ready_queue.append(pid)
        else:
            completion[pid] = finish

    for p in processes:
        pid = p['pid']
        p['completion_time'] = completion[pid]
        p['turnaround_time'] = p['completion_time'] - p['arrival_time']
        p['waiting_time'] = p['turnaround_time'] - p['burst_time']
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
            if not gantt_chart or gantt_chart[-1][0] != "Idle":
                gantt_chart.append(("Idle", time, time + 1))
            else:
                gantt_chart[-1] = ("Idle", gantt_chart[-1][1], time + 1)
            current_pid = None
        time += 1

    for i in range(len(gantt_chart)):
        pid, start, end = gantt_chart[i]
        if end is None:
            gantt_chart[i] = (pid, start, time)

    for pid in process_info:
        process_info[pid]['start_time'] = start_time[pid]

    return list(process_info.values()), gantt_chart
