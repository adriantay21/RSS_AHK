import tkinter as tk
from tkinter import ttk
from ahk import AHK
from AHKscript import ahk_script
import threading
from pynput import keyboard

class App:
    def __init__(self):
        self.script_running = False
        self.stop_event = threading.Event()
        self.listener_started = False

        self.root = tk.Tk()
        self.root.title("Input Form")
        self.root.resizable(False, False)

        # Set colors
        self.bg_color = "#e8f5e9"
        self.fg_color = "#1b5e20"
        self.button_bg = "#a5d6a7"
        self.button_fg = "#1b5e20"
        self.entry_bg = "#ffffff"
        self.entry_fg = "#1b5e20"
        self.root.configure(bg=self.bg_color)

        # Validation functions
        def validate_numeric(P):
            return P.isdigit() or P == ""

        # Register validation commands
        validate_numeric_cmd = self.root.register(validate_numeric)

        # "Number of accounts:" label and entry
        tk.Label(self.root, text="Number of accounts:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.number_of_accounts_entry = tk.Entry(self.root, validate='key', validatecommand=(validate_numeric_cmd, '%P'), bg=self.entry_bg, fg=self.entry_fg)
        self.number_of_accounts_entry.grid(row=0, column=1, padx=5, pady=5)

        # "Extended Hours:" toggle (Checkbutton)
        self.extended_hours_var = tk.BooleanVar()
        tk.Label(self.root, text="Extended Hours:", bg=self.bg_color, fg=self.fg_color).grid(row=1, column=0, sticky='e', padx=5, pady=5)
        extended_hours_checkbutton = tk.Checkbutton(self.root, variable=self.extended_hours_var, onvalue=True, offvalue=False, bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color)
        extended_hours_checkbutton.grid(row=1, column=1, sticky='w', padx=5, pady=5)

        # "Market/Limit:" label and dropdown
        tk.Label(self.root, text="Market/Limit:", bg=self.bg_color, fg=self.fg_color).grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.market_limit_dropdown = ttk.Combobox(self.root, values=["Market", "Limit"], state="readonly", width=10)
        self.market_limit_dropdown.grid(row=2, column=1, padx=5, pady=5)
        self.market_limit_dropdown.set("Limit")  # Set default value

        # "Buy/Sell:" label and dropdown
        tk.Label(self.root, text="Buy/Sell:", bg=self.bg_color, fg=self.fg_color).grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.buy_sell_dropdown = ttk.Combobox(self.root, values=["Buy", "Sell"], state="readonly", width=10)
        self.buy_sell_dropdown.grid(row=3, column=1, padx=5, pady=5)
        self.buy_sell_dropdown.set("Buy")  # Set default value

        # "Delay Speed:" label and dropdown
        tk.Label(self.root, text="Delay Speed:", bg=self.bg_color, fg=self.fg_color).grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.delay_speed_dropdown = ttk.Combobox(self.root, values=["Slower","Slow", "Medium", "Fast"], state="readonly", width=10)
        self.delay_speed_dropdown.grid(row=4, column=1, padx=5, pady=5)
        self.delay_speed_dropdown.set("Medium")  # Set default value

        # "Start From (optional):" label and entry
        tk.Label(self.root, text="Start From (optional):", bg=self.bg_color, fg=self.fg_color).grid(row=5, column=0, sticky='e', padx=5, pady=5)
        self.start_from_entry = tk.Entry(self.root, validate='key', validatecommand=(validate_numeric_cmd, '%P'), bg=self.entry_bg, fg=self.entry_fg)
        self.start_from_entry.grid(row=5, column=1, padx=5, pady=5)

        # Start and Stop buttons
        self.start_button = tk.Button(self.root, text="Start", command=self.on_start, bg=self.button_bg, fg=self.button_fg)
        self.start_button.grid(row=6, column=0, columnspan=1, pady=10, padx=5, sticky='e')

        self.stop_button = tk.Button(self.root, text="Stop", command=self.on_stop, bg=self.button_bg, fg=self.button_fg, state='disabled')
        self.stop_button.grid(row=6, column=1, columnspan=1, pady=10, padx=5, sticky='w')

        self.status_label = tk.Label(self.root, text="", fg="green", bg=self.bg_color)
        self.status_label.grid(row=7, column=0, columnspan=2, pady=5)

        # Style configuration
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TCombobox', fieldbackground=self.entry_bg, background=self.button_bg, foreground=self.entry_fg)

    def on_start(self):

        self.number_of_accounts = self.number_of_accounts_entry.get()
        self.extended_hours = bool(self.extended_hours_var.get())
        self.delay_speed = self.delay_speed_dropdown.get()
        self.start_from = self.start_from_entry.get()
        self.market_limit = self.market_limit_dropdown.get()
        self.buy_sell = self.buy_sell_dropdown.get()

        self.start_from = int(self.start_from) if self.start_from.isdigit() else 1

        # Update status label
        self.status_label.config(text='Script ready, press "$" to activate')
        self.root.update()

        if not self.listener_started:
            self.listener_started = True
            self.listener = keyboard.Listener(on_press=self.on_press)
            self.listener.start()

        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')

    def on_stop(self):
        self.stop_event.set()
        self.script_running = False
        self.status_label.config(text='Script stopped')
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.root.update()

    def update_status(self, account_num):

        self.root.after(0, lambda: self.status_label.config(text=f'Script running on account no: {account_num}'))

    def on_press(self, key):
        try:
            if key.char == '$':
                if not self.script_running:
                    # Start the script
                    self.script_running = True
                    self.stop_event.clear()
                    threading.Thread(target=self.run_ahk_script).start()
                    self.root.after(0, lambda: self.status_label.config(text='Script running'))
                else:
                    # Stop the script
                    self.stop_event.set()
                    self.script_running = False
                    self.root.after(0, lambda: self.status_label.config(text='Script stopped'))
        except AttributeError:
            pass  # Ignore special keys

    def run_ahk_script(self):
        try:
            number_of_accounts = int(self.number_of_accounts)
            start_from_value = int(self.start_from)
            ahk_script(number_of_accounts, self.extended_hours, start_from_value, self.stop_event, self.market_limit, self.buy_sell, self.delay_speed, self.update_status)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.script_running = False
            self.root.after(0, lambda: self.status_label.config(text='Script finished'))
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')

    def run(self):
        self.root.mainloop()
