import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from calculator_logic import Calculator

calc = Calculator()

# --- App Setup ---
app = ttk.Window(title="iOS Calculator", themename="litera", resizable=(False, False))
app.geometry("360x520")

display_var = tk.StringVar(value="")

# ---------- Helper Functions ----------
def animate(button):
    try:
        original = getattr(button, "original_style", "light")
        button.config(bootstyle="info")
        button.after(110, lambda: button.config(bootstyle=original))
    except Exception:
        pass

def update_display(text=None):
    display_var.set(text if text is not None else calc.expression)

def btn_press(v):
    calc.add(str(v))
    update_display()

def btn_clear():
    calc.clear()
    update_display()

def btn_backspace():
    calc.backspace()
    update_display()

def btn_evaluate():
    result = calc.evaluate()
    update_display(result)
    refresh_history_list()

def create_bordered_button(parent, text, style, command, grid_opts=None):
    border_frame = ttk.Frame(parent, bootstyle="secondary")
    btn = ttk.Button(border_frame, text=text, **style)
    btn.original_style = style["bootstyle"]
    btn.config(command=lambda: (animate(btn), command()))
    btn.pack(padx=2, pady=2)
    if grid_opts:
        border_frame.grid(**grid_opts)
    return btn

# ---------- History Toggle ----------
history_visible = False

def toggle_history():
    global history_visible
    if history_visible:
        history_frame.pack_forget()
        main_frame.pack(fill="both", expand=True)
        history_visible = False
    else:
        main_frame.pack_forget()
        refresh_history_list()
        history_frame.pack(fill="both", expand=True)
        history_visible = True

# ---------- Keyboard Bindings ----------
def on_key(event):
    key = event.keysym
    char = event.char

    if key in ("Return", "KP_Enter"):
        btn_evaluate()
        return "break"
    if key == "Escape":
        btn_clear()
        return "break"
    if key == "BackSpace":
        btn_backspace()
        return "break"
    if char and (char.isdigit() or char == "."):
        btn_press(char)
        return "break"
    if char in "+-*/%":
        btn_press(char)
        return "break"
    if char.lower() == "h":
        toggle_history()
        return "break"

app.bind_all("<Key>", on_key)

# ---------- Main Frames ----------
main_frame = ttk.Frame(app)
main_frame.pack(fill="both", expand=True)

history_frame = ttk.Frame(app)

# ---------- Display Area ----------
top_area = ttk.Frame(main_frame)
top_area.pack(fill="x", padx=12, pady=10)

display = ttk.Entry(
    top_area,
    textvariable=display_var,
    font=("SF Pro Display", 36),
    justify="right",
    bootstyle="in",
)
display.pack(fill="x", padx=2, pady=2)
display.configure(state="readonly")

# ---------- Control Row ----------
ctrl_frame = ttk.Frame(main_frame)
ctrl_frame.pack(pady=8)

create_bordered_button(ctrl_frame, "C", {"bootstyle": "secondary", "width": 6, "padding": 8}, btn_clear, {"row": 0, "column": 0, "padx": 8})
create_bordered_button(ctrl_frame, "+", {"bootstyle": "warning", "width": 6, "padding": 8}, lambda: btn_press("+"), {"row": 0, "column": 1, "padx": 8})
create_bordered_button(ctrl_frame, "History", {"bootstyle": "light", "width": 8, "padding": 8}, toggle_history, {"row": 0, "column": 2, "padx": 8})

# ---------- Keypad ----------
pad_frame = ttk.Frame(main_frame)
pad_frame.pack(pady=6)

button_style = {"bootstyle": "light", "width": 6, "padding": 12}
op_style = {"bootstyle": "warning", "width": 6, "padding": 12}
zero_style = {"bootstyle": "light", "width": 14, "padding": 12}

buttons = [
    ("7", lambda: btn_press("7")), ("8", lambda: btn_press("8")), ("9", lambda: btn_press("9")), ("/", lambda: btn_press("/")),
    ("4", lambda: btn_press("4")), ("5", lambda: btn_press("5")), ("6", lambda: btn_press("6")), ("*", lambda: btn_press("*")),
    ("1", lambda: btn_press("1")), ("2", lambda: btn_press("2")), ("3", lambda: btn_press("3")), ("-", lambda: btn_press("-")),
]

i = 0
for r in range(3):
    for c in range(4):
        text, cmd = buttons[i]
        style = op_style if text in "/*-" else button_style
        create_bordered_button(pad_frame, text, style, cmd, {"row": r, "column": c, "padx": 8, "pady": 8})
        i += 1

create_bordered_button(pad_frame, "0", zero_style, lambda: btn_press("0"), {"row": 3, "column": 0, "columnspan": 2, "padx": 8, "pady": 8})
create_bordered_button(pad_frame, ".", button_style, lambda: btn_press("."), {"row": 3, "column": 2, "padx": 8, "pady": 8})
create_bordered_button(pad_frame, "=", op_style, btn_evaluate, {"row": 3, "column": 3, "padx": 8, "pady": 8})

back_btn = create_bordered_button(main_frame, "⌫", {"bootstyle": "light", "width": 6, "padding": 8}, btn_backspace)
back_btn.master.pack(pady=4)

# ---------- History Panel ----------
def refresh_history_list():
    history_listbox.delete(0, tk.END)
    for expr, res in calc.get_history():
        history_listbox.insert(tk.END, f"{expr} = {res}")

history_header = ttk.Frame(history_frame)
history_header.pack(fill="x", pady=6, padx=6)

back_button = create_bordered_button(history_header, "← Back", {"bootstyle": "secondary", "width": 8, "padding": 6}, toggle_history)
back_button.master.pack(side="left")

clear_hist_btn = create_bordered_button(history_header, "Clear History", {"bootstyle": "light", "width": 12, "padding": 6}, lambda: (calc.clear_history(), refresh_history_list()))
clear_hist_btn.master.pack(side="right")

history_listbox = tk.Listbox(history_frame, font=("SF Pro Display", 12))
history_listbox.pack(fill="both", expand=True, padx=8, pady=8)

def on_history_double_click(evt):
    sel = history_listbox.curselection()
    if not sel:
        return
    value = history_listbox.get(sel[0])
    if "=" in value:
        _, res = value.split("=", 1)
        calc.expression = res.strip()
        update_display()
        toggle_history()

history_listbox.bind("<Double-Button-1>", on_history_double_click)

# ---------- Start ----------
update_display()
app.mainloop()
