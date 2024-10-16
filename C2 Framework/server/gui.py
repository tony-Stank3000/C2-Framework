import requests
import tkinter as tk
from tkinter import messagebox, simpledialog

# Flask server URL
SERVER_URL = "http://127.0.0.1:5000"

# Tkinter GUI application
class C2FrameworkGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("C2 Framework")
        self.root.geometry("400x300")

        # Agent registration
        self.agent_id_label = tk.Label(root, text="Agent ID:")
        self.agent_id_label.pack(pady=5)
        self.agent_id_entry = tk.Entry(root)
        self.agent_id_entry.pack(pady=5)
        self.register_button = tk.Button(root, text="Register Agent", command=self.register_agent)
        self.register_button.pack(pady=5)

        # Command sending
        self.command_label = tk.Label(root, text="Command:")
        self.command_label.pack(pady=5)
        self.command_entry = tk.Entry(root)
        self.command_entry.pack(pady=5)
        self.send_command_button = tk.Button(root, text="Send Command", command=self.send_command)
        self.send_command_button.pack(pady=5)

        # Polling commands
        self.poll_button = tk.Button(root, text="Poll Commands", command=self.poll_commands)
        self.poll_button.pack(pady=5)

        # Reporting output
        self.report_button = tk.Button(root, text="Report Output", command=self.report_output)
        self.report_button.pack(pady=5)

    def register_agent(self):
        agent_id = self.agent_id_entry.get()
        if not agent_id:
            messagebox.showerror("Error", "Agent ID is required")
            return

        response = requests.post(f"{SERVER_URL}/register", json={"agent_id": agent_id})
        if response.status_code == 200:
            messagebox.showinfo("Success", "Agent registered successfully")
        else:
            messagebox.showerror("Error", response.json().get("error", "Failed to register agent"))

    def send_command(self):
        agent_id = self.agent_id_entry.get()
        command = self.command_entry.get()
        if not agent_id or not command:
            messagebox.showerror("Error", "Agent ID and Command are required")
            return

        response = requests.post(f"{SERVER_URL}/command/{agent_id}", json={"command": command})
        if response.status_code == 200:
            messagebox.showinfo("Success", "Command sent successfully")
        else:
            messagebox.showerror("Error", response.json().get("error", "Failed to send command"))

    def poll_commands(self):
        agent_id = self.agent_id_entry.get()
        if not agent_id:
            messagebox.showerror("Error", "Agent ID is required")
            return

        response = requests.get(f"{SERVER_URL}/poll/{agent_id}")
        if response.status_code == 200:
            commands = response.json().get("commands", [])
            if commands:
                command_list = "\n".join([f"ID: {cmd['id']} - Command: {cmd['command']}" for cmd in commands])
                messagebox.showinfo("Pending Commands", command_list)
            else:
                messagebox.showinfo("No Commands", "No pending commands for this agent")
        else:
            messagebox.showerror("Error", response.json().get("error", "Failed to poll commands"))

    def report_output(self):
        command_id = simpledialog.askinteger("Report Output", "Enter Command ID:")
        output = simpledialog.askstring("Report Output", "Enter Command Output:")
        if not command_id or output is None:
            messagebox.showerror("Error", "Command ID and Output are required")
            return

        response = requests.post(f"{SERVER_URL}/report", json={"command_id": command_id, "output": output})
        if response.status_code == 200:
            messagebox.showinfo("Success", "Output reported successfully")
        else:
            messagebox.showerror("Error", response.json().get("error", "Failed to report output"))

# Main function to run the Tkinter GUI
def main():
    root = tk.Tk()
    app = C2FrameworkGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
