# ================================
# WhatsApp Auto Sender - Modern UI
# ================================

from twilio.rest import Client
from datetime import datetime
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# ================================
# TWILIO CREDENTIALS
# ================================

accountSID = ''
token = ''

client = Client(accountSID, token)

# ================================
# SEND FUNCTION
# ================================

def send(recipient_number, message_body):

    try:
        message = client.messages.create(
            from_='whatsapp:+14155238886',
            body=message_body,
            to=f'whatsapp:{recipient_number}'
        )

        status_label.config(
            text=f"✅ Message Sent Successfully!\nSID: {message.sid}",
            foreground="green"
        )

    except Exception as e:
        status_label.config(
            text=f"❌ Error:\n{str(e)}",
            foreground="red"
        )


# ================================
# SCHEDULER FUNCTION
# ================================

def schedule_message():

    name = name_entry.get()
    number = number_entry.get()
    message_body = message_text.get("1.0", tk.END).strip()
    date_str = date_entry.get()
    time_str = time_entry.get()

    if not name or not number or not message_body:
        messagebox.showerror(
            "Missing Information",
            "Please fill all the fields."
        )
        return

    try:
        sch_datetime = datetime.strptime(
            f'{date_str} {time_str}',
            "%Y-%m-%d %H:%M"
        )

        current = datetime.now()
        timedif = sch_datetime - current
        delay = timedif.total_seconds()

        if delay <= 0:
            messagebox.showerror(
                "Invalid Time",
                "Please select a future date and time."
            )
            return

        status_label.config(
            text=f"⏳ Message Scheduled for {sch_datetime}",
            foreground="#ff9800"
        )

        # Run scheduler in separate thread
        threading.Thread(
            target=wait_and_send,
            args=(delay, number, message_body),
            daemon=True
        ).start()

    except ValueError:
        messagebox.showerror(
            "Format Error",
            "Use correct date/time format."
        )


def wait_and_send(delay, number, message_body):

    time.sleep(delay)
    send(number, message_body)


# ================================
# MAIN WINDOW
# ================================

root = tk.Tk()
root.title("WhatsApp Auto Sender")
root.geometry("650x700")
root.configure(bg="#0f172a")

# ================================
# STYLE
# ================================

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "TLabel",
    background="#0f172a",
    foreground="white",
    font=("Segoe UI", 11)
)

style.configure(
    "TButton",
    font=("Segoe UI", 11, "bold"),
    padding=10
)

style.configure(
    "TEntry",
    padding=8,
    font=("Segoe UI", 10)
)

# ================================
# HEADER
# ================================

title = tk.Label(
    root,
    text="📱 WhatsApp Auto Scheduler",
    bg="#0f172a",
    fg="white",
    font=("Segoe UI", 24, "bold")
)

title.pack(pady=20)

subtitle = tk.Label(
    root,
    text="Schedule WhatsApp messages beautifully 🚀",
    bg="#0f172a",
    fg="#94a3b8",
    font=("Segoe UI", 11)
)

subtitle.pack(pady=5)

# ================================
# MAIN CARD FRAME
# ================================

card = tk.Frame(
    root,
    bg="#1e293b",
    bd=0,
    relief="ridge"
)

card.pack(padx=30, pady=20, fill="both", expand=True)

# ================================
# NAME
# ================================

ttk.Label(card, text="Recipient Name").pack(
    anchor="w",
    padx=20,
    pady=(20, 5)
)

name_entry = ttk.Entry(card, width=50)
name_entry.pack(padx=20, pady=5)

# ================================
# NUMBER
# ================================

ttk.Label(
    card,
    text="WhatsApp Number (+91xxxxxxxxxx)"
).pack(
    anchor="w",
    padx=20,
    pady=(15, 5)
)

number_entry = ttk.Entry(card, width=50)
number_entry.pack(padx=20, pady=5)

# ================================
# MESSAGE
# ================================

ttk.Label(card, text="Message").pack(
    anchor="w",
    padx=20,
    pady=(15, 5)
)

message_text = tk.Text(
    card,
    height=8,
    width=50,
    font=("Segoe UI", 10),
    bg="#334155",
    fg="white",
    insertbackground="white",
    relief="flat",
    padx=10,
    pady=10
)

message_text.pack(padx=20, pady=5)

# ================================
# DATE
# ================================

ttk.Label(
    card,
    text="Date (YYYY-MM-DD)"
).pack(
    anchor="w",
    padx=20,
    pady=(15, 5)
)

date_entry = ttk.Entry(card, width=50)
date_entry.pack(padx=20, pady=5)

# ================================
# TIME
# ================================

ttk.Label(
    card,
    text="Time (HH:MM - 24 Hour)"
).pack(
    anchor="w",
    padx=20,
    pady=(15, 5)
)

time_entry = ttk.Entry(card, width=50)
time_entry.pack(padx=20, pady=5)

# ================================
# BUTTON
# ================================

schedule_btn = tk.Button(
    card,
    text="🚀 Schedule Message",
    bg="#22c55e",
    fg="white",
    font=("Segoe UI", 13, "bold"),
    relief="flat",
    padx=20,
    pady=12,
    cursor="hand2",
    command=schedule_message
)

schedule_btn.pack(pady=30)

# Hover effect
def on_enter(e):
    schedule_btn['bg'] = "#16a34a"

def on_leave(e):
    schedule_btn['bg'] = "#22c55e"

schedule_btn.bind("<Enter>", on_enter)
schedule_btn.bind("<Leave>", on_leave)

# ================================
# STATUS LABEL
# ================================

status_label = tk.Label(
    card,
    text="Waiting for scheduling...",
    bg="#1e293b",
    fg="#cbd5e1",
    font=("Segoe UI", 11)
)

status_label.pack(pady=20)

# ================================
# FOOTER
# ================================

footer = tk.Label(
    root,
    text="Built with Python + Twilio 💚",
    bg="#0f172a",
    fg="#64748b",
    font=("Segoe UI", 10)
)

footer.pack(pady=10)

# ================================
# RUN APP
# ================================

root.mainloop()
