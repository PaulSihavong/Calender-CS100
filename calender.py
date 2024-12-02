import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel
from tkinter.ttk import Progressbar
from tkcalendar import Calendar
from datetime import datetime

# Functions
def add_task():
    selected_date = cal.get_date()

    def confirm_task():
        task_name = name_entry.get()
        breakpoints = list(range(0, 101, 100 // scale[0]))
        if task_name:
            if selected_date not in tasks:
                tasks[selected_date] = []
            tasks[selected_date].append({'name': task_name, 'breakpoints': breakpoints, 'progress': 0})
            update_calendar_colors()
            task_window.destroy()
            messagebox.showinfo("Task Added", f"Task '{task_name}' added on {selected_date} with scale: {scale[0]}")
        else:
            messagebox.showwarning("Input Error", "Task name cannot be empty.")

    def update_scale(delta):
        new_scale = scale[0] + delta
        if 1 <= new_scale <= 10:
            scale[0] = new_scale
            scale_label.config(text=f"Scale: {scale[0]}")

    # Task input dialog
    task_window = Toplevel(root)
    task_window.title("Add Task")

    tk.Label(task_window, text="Task Name:").pack(pady=5)
    name_entry = tk.Entry(task_window, width=30)
    name_entry.pack(pady=5)

    tk.Label(task_window, text="Set Scale (1-10):").pack(pady=5)
    scale_frame = tk.Frame(task_window)
    scale_frame.pack(pady=5)
    scale = [5]  # Default scale

    tk.Button(scale_frame, text="-", command=lambda: update_scale(-1)).pack(side="left", padx=5)
    scale_label = tk.Label(scale_frame, text=f"Scale: {scale[0]}")
    scale_label.pack(side="left", padx=5)
    tk.Button(scale_frame, text="+", command=lambda: update_scale(1)).pack(side="left", padx=5)

    tk.Button(task_window, text="Add Task", command=confirm_task).pack(pady=10)

def add_event():
    selected_date = cal.get_date()
    event_name = simpledialog.askstring("Add Event", "Enter event name:")
    if event_name:
        events[selected_date] = {"name": event_name}
        update_calendar_colors()
        messagebox.showinfo("Event Added", f"Event '{event_name}' added on {selected_date}.")

def add_alarm():
    selected_date = cal.get_date()
    alarm_time = simpledialog.askstring("Add Alarm", "Enter alarm time (HH:MM):")
    try:
        alarm_datetime = datetime.strptime(f"{selected_date} {alarm_time}", "%Y-%m-%d %H:%M")
        alarms.append({'time': alarm_datetime})
        update_calendar_colors()
        messagebox.showinfo("Alarm Added", f"Alarm set for {alarm_datetime.strftime('%Y-%m-%d %H:%M')}.")
    except ValueError:
        messagebox.showwarning("Input Error", "Enter a valid time in HH:MM format.")

def view_day_entries():
    selected_date = cal.get_date()
    entries = []

    if selected_date in reminders:
        entries += [{"type": "Reminder", "content": text} for text in reminders[selected_date]]

    if selected_date in events:
        entries.append({"type": "Event", "content": events[selected_date]["name"]})

    for alarm in alarms:
        if alarm['time'].strftime("%Y-%m-%d") == selected_date:
            entries.append({"type": "Alarm", "content": alarm['time'].strftime('%H:%M')})

    if selected_date in tasks:
        for task in tasks[selected_date]:
            entries.append({"type": "Task", "content": task})

    if entries:
        display_entries_window(selected_date, entries)
    else:
        messagebox.showinfo("Entries", f"No entries for {selected_date}.")

def display_entries_window(date, entries):
    window = Toplevel(root)
    window.title(f"Entries for {date}")

    def update_task_progress(task, increase=True):
        current_progress = task['progress']
        breakpoints = task['breakpoints']
        try:
            if increase:
                next_bp = next(bp for bp in breakpoints if bp > current_progress)
                task['progress'] = next_bp
            else:
                prev_bp = max(bp for bp in breakpoints if bp < current_progress)
                task['progress'] = prev_bp
            update_calendar_colors()
            display_entries_window(date, entries)
            window.destroy()
        except (StopIteration, ValueError):
            direction = "maximum" if increase else "minimum"
            messagebox.showinfo("Task Progress", f"Task is already at {direction} progress.")

    def remove_entry(entry):
        if entry["type"] == "Task":
            tasks[date].remove(entry["content"])
            if not tasks[date]:
                del tasks[date]
        elif entry["type"] == "Event":
            del events[date]
        elif entry["type"] == "Alarm":
            alarms.remove({"time": datetime.strptime(f"{date} {entry['content']}", "%Y-%m-%d %H:%M")})
        elif entry["type"] == "Reminder":
            reminders[date].remove(entry["content"])
            if not reminders[date]:
                del reminders[date]
        update_calendar_colors()
        display_entries_window(date, entries)
        window.destroy()

    for entry in entries:
        frame = tk.Frame(window)
        frame.pack(fill="x", pady=5)

        if entry["type"] == "Task":
            tk.Label(frame, text=f"Task: {entry['content']['name']} (Progress: {entry['content']['progress']}%)").pack(side="left", padx=10)
            progress_bar = Progressbar(frame, orient="horizontal", length=200, mode="determinate")
            progress_bar["value"] = entry["content"]["progress"]
            progress_bar.pack(side="left", padx=10)
            tk.Button(frame, text="+", command=lambda e=entry["content"]: update_task_progress(e, increase=True)).pack(side="left", padx=5)
            tk.Button(frame, text="-", command=lambda e=entry["content"]: update_task_progress(e, increase=False)).pack(side="left", padx=5)

        else:
            tk.Label(frame, text=f"{entry['type']}: {entry['content']}").pack(side="left", padx=10)

        tk.Button(frame, text="Remove", command=lambda e=entry: remove_entry(e)).pack(side="right", padx=10)

def update_calendar_colors():
    cal.calevent_remove('all')
    for date in set(list(reminders.keys()) + list(events.keys()) + list(tasks.keys()) + 
                    [alarm['time'].strftime("%Y-%m-%d") for alarm in alarms]):
        day = datetime.strptime(date, "%Y-%m-%d")
        cal.calevent_create(day, f"{day.day}", 'highlight')
    cal.tag_config('highlight', background='yellow')

def export_to_text():
    with open("calendar_data.txt", "w") as f:
        for date in sorted(set(list(reminders.keys()) + list(events.keys()) + list(tasks.keys()) + 
                               [alarm['time'].strftime("%Y-%m-%d") for alarm in alarms])):

            f.write(f"\nDate: {date}\n")
            
            # Write reminders
            if date in reminders:
                f.write("  Reminders:\n")
                for reminder in reminders[date]:
                    f.write(f"    - {reminder}\n")
            
            # Write events
            if date in events:
                f.write(f"  Event: {events[date]['name']}\n")
            
            # Write alarms
            for alarm in alarms:
                if alarm['time'].strftime("%Y-%m-%d") == date:
                    f.write(f"  Alarm: {alarm['time'].strftime('%H:%M')}\n")
            
            # Write tasks
            if date in tasks:
                f.write("  Tasks:\n")
                for task in tasks[date]:
                    f.write(f"    - Task: {task['name']} (Progress: {task['progress']}%)\n")

    messagebox.showinfo("Export Successful", "Data has been exported to 'calendar_data.txt'.")

# Initialize main window
root = tk.Tk()
root.title("CS100 Calender")

# Data storage
reminders = {}
alarms = []
events = {}
tasks = {}

# Calendar widget
cal = Calendar(root, selectmode='day', date_pattern='yyyy-MM-dd')
cal.pack(pady=20)

# Label to show the day number
day_num_label = tk.Label(root, text="Day Number: ", font=("Helvetica", 12))
day_num_label.pack(pady=5)

# Buttons for entries
view_button = tk.Button(root, text="View Day Entries", command=view_day_entries)
view_button.pack(pady=5)

add_task_button = tk.Button(root, text="Add Task", command=add_task)
add_task_button.pack(pady=5)

add_event_button = tk.Button(root, text="Add Event", command=add_event)
add_event_button.pack(pady=5)

add_alarm_button = tk.Button(root, text="Add Alarm", command=add_alarm)
add_alarm_button.pack(pady=5)

export_button = tk.Button(root, text="Export to Text", command=export_to_text)
export_button.pack(pady=5)

update_calendar_colors()
root.mainloop()
