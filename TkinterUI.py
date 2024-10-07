import tkinter as tk
from tkinter import ttk
from ahk import AHK
from AHKscript import ahk_script
import threading
from pynput import keyboard

# Global variables
script_running = False
stop_event = threading.Event()
listener_started = False

def main():
    root = tk.Tk()
    root.title("Input Form")
    root.resizable(False, False) 

    # Set colors
    bg_color = "#e8f5e9" 
    fg_color = "#1b5e20"  
    button_bg = "#a5d6a7"  
    button_fg = "#1b5e20"  
    entry_bg = "#ffffff"   
    entry_fg = "#1b5e20"   
    root.configure(bg=bg_color)

    #validation functions
    def validate_numeric(P):
        return P.isdigit() or P == ""

    # Register validation commands
    validate_numeric_cmd = root.register(validate_numeric)


    # "Number of accounts:" label and entry
    tk.Label(root, text="Number of accounts:", bg=bg_color, fg=fg_color).grid(row=0, column=0, sticky='e', padx=5, pady=5)
    number_of_accounts_entry = tk.Entry(root, validate='key', validatecommand=(validate_numeric_cmd, '%P'), bg=entry_bg, fg=entry_fg)
    number_of_accounts_entry.grid(row=0, column=1, padx=5, pady=5)

    # "Extended Hours:" toggle (Checkbutton)
    extended_hours_var = tk.BooleanVar()
    tk.Label(root, text="Extended Hours:", bg=bg_color, fg=fg_color).grid(row=1, column=0, sticky='e', padx=5, pady=5)
    extended_hours_checkbutton = tk.Checkbutton(root, variable=extended_hours_var, onvalue=True, offvalue=False, bg=bg_color, fg=fg_color, selectcolor=bg_color)
    extended_hours_checkbutton.grid(row=1, column=1, sticky='w', padx=5, pady=5)

    # "Market/Limit:" label and dropdown
    tk.Label(root, text="Market/Limit:", bg=bg_color, fg=fg_color).grid(row=2, column=0, sticky='e', padx=5, pady=5)
    market_limit_dropdown = ttk.Combobox(root, values=["Market","Limit"], state="readonly", width=10)
    market_limit_dropdown.grid(row=2, column=1, padx=5, pady=5)
    market_limit_dropdown.set("Limit")  # Set default value

    # "Buy/Sell:" label and dropdown
    tk.Label(root, text="Buy/Sell:", bg=bg_color, fg=fg_color).grid(row=3, column=0, sticky='e', padx=5, pady=5)
    buy_sell_dropdown = ttk.Combobox(root, values=["Buy", "Sell"], state="readonly", width=10)
    buy_sell_dropdown.grid(row=3, column=1, padx=5, pady=5)
    buy_sell_dropdown.set("Buy")  # Set default value

    # "Delay Speed:" label and dropdown
    tk.Label(root, text="Delay Speed:", bg=bg_color, fg=fg_color).grid(row=4, column=0, sticky='e', padx=5, pady=5)
    delay_speed_dropdown = ttk.Combobox(root, values=["Slow", "Medium", "Fast"], state="readonly", width=10)
    delay_speed_dropdown.grid(row=4, column=1, padx=5, pady=5)
    delay_speed_dropdown.set("Medium")  # Set default value

    # "Start From (optional):" label and entry
    tk.Label(root, text="Start From (optional):", bg=bg_color, fg=fg_color).grid(row=5, column=0, sticky='e', padx=5, pady=5)
    start_from_entry = tk.Entry(root, validate='key', validatecommand=(validate_numeric_cmd, '%P'), bg=entry_bg, fg=entry_fg)
    start_from_entry.grid(row=5, column=1, padx=5, pady=5)

    # Start and Stop buttons
    start_button = tk.Button(root, text="Start", command=lambda: on_start(), bg=button_bg, fg=button_fg)
    start_button.grid(row=6, column=0, columnspan=1, pady=10, padx=5, sticky='e')

    stop_button = tk.Button(root, text="Stop", command=lambda: on_stop(), bg=button_bg, fg=button_fg)
    stop_button.grid(row=6, column=1, columnspan=1, pady=10, padx=5, sticky='w')

    status_label = tk.Label(root, text="", fg="green", bg=bg_color)
    status_label.grid(row=7, column=0, columnspan=2, pady=5)


    def on_start():
        global listener_started, number_of_accounts, extended_hours, delay_speed, start_from, market_limit, buy_sell, listener

        # Get parameters from GUI inputs
        number_of_accounts = number_of_accounts_entry.get()
        extended_hours = bool(extended_hours_var.get())
        delay_speed = delay_speed_dropdown.get()
        start_from = start_from_entry.get()
        market_limit = market_limit_dropdown.get()
        buy_sell = buy_sell_dropdown.get()

        start_from = int(start_from) if start_from.isdigit() else 0

        # Update status label
        status_label.config(text='Script ready, press "$" to activate')
        root.update()

        if not listener_started:
            listener_started = True
            listener = keyboard.Listener(on_press=on_press)
            listener.start()

        start_button.config(state='disabled')
        stop_button.config(state='normal')

    def on_stop():
        global script_running, stop_event
        stop_event.set()
        script_running = False
        status_label.config(text='Script stopped')
        start_button.config(state='normal')
        root.update()

    def update_status(account_num):
        # Use 'root.after' to safely update the GUI from a separate thread
        root.after(0, lambda: status_label.config(text=f'Script running on account no: {account_num}'))

    def on_press(key):
        global script_running, stop_event

        try:
            if key.char == '$':
                if not script_running:
                    # Start the script
                    script_running = True
                    stop_event.clear()
                    threading.Thread(target=run_ahk_script).start()
                    root.after(0, lambda: status_label.config(text='Script running'))
                else:
                    # Stop the script
                    stop_event.set()
                    script_running = False
                    root.after(0, lambda: status_label.config(text='Script stopped'))
        except AttributeError:
            pass

    def run_ahk_script():
        try:
            global number_of_accounts, extended_hours, start_from, market_limit, buy_sell, listener_started, listener, delay_speed
            number_of_accounts = int(number_of_accounts)
            start_from_value = int(start_from)
            ahk_script(number_of_accounts, extended_hours, start_from_value, stop_event, market_limit,buy_sell, delay_speed, update_status)
        except Exception as e:
            print(e)
        finally:
            global script_running
            script_running = False
            root.after(0, lambda: status_label.config(text='Script finished'))

    style = ttk.Style()
    style.theme_use('default')
    style.configure('TCombobox', fieldbackground=entry_bg, background=button_bg, foreground=entry_fg)

    root.mainloop()

if __name__ == "__main__":
    main()
