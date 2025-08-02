import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import csv
import os

CSV_FILE = 'contacts.csv'

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['name', 'phone', 'group'])

def load_contacts():
    contacts = []
    with open(CSV_FILE, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            contacts.append(row)
    return contacts

def refresh_table():
    for row in tree.get_children():
        tree.delete(row)
    for i, contact in enumerate(load_contacts()):
        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
        tree.insert('', 'end', values=(contact['name'], contact['phone']), tags=(tag,))

def search_contacts(event=None):
    query = entry_search.get().strip().lower()

    # Clear all existing rows in the Treeview
    for row in tree.get_children():
        tree.delete(row)

    contacts = load_contacts()

    # If the search box is empty or contains the placeholder text
    if not query or query == "search by name or number":
        for i, contact in enumerate(contacts):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.insert('', 'end', values=(contact['name'], contact['phone']), tags=(tag,))
        return

    # Split the search query into words
    words = query.split()
    matches = []

    # Search for matching contacts
    for contact in contacts:
        name = contact['name'].lower()
        phone = contact['phone']
        group = contact['group'].lower()

        # If any word matches the beginning or is contained in name, phone, or group
        if any(name.startswith(word) or phone.startswith(word) or group.startswith(word) for word in words):
            matches.append(contact)
        elif any(word in name or word in phone or word in group for word in words):
            matches.append(contact)

    # Display matching contacts with alternating highlight colors
    if matches:
        for idx, contact in enumerate(matches):
            tag = 'highlight_even' if idx % 2 == 0 else 'highlight_odd'
            tree.insert('', 'end', values=(contact['name'], contact['phone']), tags=(tag,))
    else:
        # If no match found, show a "no contact found" message
        tree.insert('', 'end', values=("❌ No contacts found", ""), tags=('notfound',))


def filter_by_group(keyword):
    for row in tree.get_children():
        tree.delete(row)
    contacts = load_contacts()
    filtered = [c for c in contacts if keyword.lower() in c['group'].lower()]
    for i, contact in enumerate(filtered):
        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
        tree.insert('', 'end', values=(contact['name'], contact['phone']), tags=(tag,))

def prompt_password():
    pwd = simpledialog.askstring("🔐 Password Required", "Enter password:", show='*')
    return pwd == "1234"

def add_contact():
    name = entry_name.get().strip()
    phone = entry_phone.get().strip()

    if not name or not phone or name.lower() == "name" or phone.lower() == "phone number":
        messagebox.showwarning("Error", "Please enter both name and phone number.")
        return

    contacts = load_contacts()
    for contact in contacts:
        if contact['name'].lower() == name.lower():
            messagebox.showerror("Duplicate", "This name already exists.")
            return

    # Step 1: Pop-up for group selection
    popup = tk.Toplevel(root)
    popup.title("Select Group")
    popup.geometry("300x160")

    # for window show in middel
    popup.update_idletasks()
    popup_width = popup.winfo_width()
    popup_height = popup.winfo_height()
    x = (popup.winfo_screenwidth() // 2) - (popup_width // 2)
    y = (popup.winfo_screenheight() // 2) - (popup_height // 2)
    popup.geometry(f"+{x}+{y}")

    popup.grab_set()

    tk.Label(popup, text="📂 Select Contact Group:", font=("Segoe UI", 12, "bold")).pack(pady=10)

    group_var = tk.StringVar()
    group_var.set("Select Group")

    group_options = [
        "Management", "HR & Admin", "BOE & IT", "Desk", "Production",
        "Edit Panel", "Accounts_Marketing", "Transport", "Bureau Office", "Fm"
    ]

    dropdown = tk.OptionMenu(popup, group_var, *group_options)
    dropdown.config(font=("Segoe UI", 11), width=20)
    dropdown.pack(pady=5)

    def save_with_password():
        selected_group = group_var.get()
        if selected_group == "Select Group":
            messagebox.showwarning("Error", "Please select a group.")
            return

        if not prompt_password():
            messagebox.showerror("Denied", "Wrong password!")
            return

        with open(CSV_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([name, phone, selected_group])

        popup.destroy()
        messagebox.showinfo("Success", "Contact added successfully!")
        entry_name.delete(0, tk.END)
        entry_phone.delete(0, tk.END)
        reset_placeholders()
        refresh_table()
        search_contacts()

    tk.Button(popup, text="Save", command=save_with_password, bg="#2ecc71", fg="white", font=("Segoe UI", 11, "bold")).pack(pady=10)

def update_contact():
    if not prompt_password():
        messagebox.showerror("Denied", "Wrong password!")
        return

    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Select", "Please select a contact to update.")
        return
    old_name = tree.item(selected[0])['values'][0]
    new_name = entry_name.get().strip()
    new_phone = entry_phone.get().strip()
    if not new_name or not new_phone or new_name.lower() == "name" or new_phone.lower() == "phone number":
        messagebox.showwarning("Error", "Please enter both name and phone number.")
        return
    contacts = load_contacts()
    for contact in contacts:
        if contact['name'] == old_name:
            contact['name'] = new_name
            contact['phone'] = new_phone
            break
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'phone', 'group'])
        writer.writeheader()
        writer.writerows(contacts)
    messagebox.showinfo("Success", "Contact updated successfully!")
    refresh_table()
    search_contacts()

def on_tree_select(event):
    selected = tree.selection()
    if selected:
        values = tree.item(selected[0])['values']
        entry_name.delete(0, tk.END)
        entry_name.insert(0, values[0])
        entry_phone.delete(0, tk.END)
        entry_phone.insert(0, values[1])

def on_focus_in(entry, placeholder):
    if entry.get().lower() == placeholder.lower():
        entry.delete(0, tk.END)
        entry.config(fg='black')

def on_focus_out(entry, placeholder):
    if not entry.get():
        entry.insert(0, placeholder)
        entry.config(fg='grey')

def reset_placeholders():
    if not entry_name.get() or entry_name.get().strip() == "":
        entry_name.insert(0, "Name")
        entry_name.config(fg='grey')
    if not entry_phone.get() or entry_phone.get().strip() == "":
        entry_phone.insert(0, "Phone Number")
        entry_phone.config(fg='grey')


# GUI Start..........
root = tk.Tk()
root.title("📞 Contact Manager For Ekhon Tv")

window_width, window_height = 720, 650
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.configure(bg="#f5f5f5")

# Logo Image loader
logo_img = tk.PhotoImage(file="logo.png")

top_frame = tk.Frame(root, bg="#f5f5f5")
top_frame.pack(fill=tk.X, pady=2, padx=5)

logo_label = tk.Label(top_frame, image=logo_img, bg="#f5f5f5")
logo_label.pack(side=tk.LEFT)


style = ttk.Style()
style.theme_use("default")

style.configure("Treeview",
    background="white",
    foreground="black",
    rowheight=30,
    fieldbackground="white",
    font=("Segoe UI", 14, "bold"),
    bordercolor="#d9d9d9",
    borderwidth=1,
    highlightbackground="#c0c0c0",
    relief="solid"
)

style.configure("Treeview.Heading",
    font=("Segoe UI", 15, "bold"),
    background="#e6e6e6",
    foreground="black",
    relief="raised",
    borderwidth=1
)

style.map("Treeview", background=[("selected", "#a0c4ff")])

# Main Frame with Group Buttons and Right Section

main_frame = tk.Frame(root, bg="#f5f5f5")
main_frame.pack(pady=(5, 10), padx=(0,20))

group_btn_frame = tk.Frame(main_frame, bg="#f5f5f5")
group_btn_frame.pack(side=tk.LEFT, padx=(10, 10))

tk.Label(group_btn_frame, text="📂 Groups", bg="#f5f5f5", font=("Segoe UI", 14, "bold")).pack(pady=(10))

button_data = [
    ("Management", "Management"),
    ("HR & Admin", "HR & Admin"),
    ("BOE & IT", "BOE & IT"),
    ("Desk", "Desk"),
    ("Production", "Production"),
    ("Edit Panel", "Edit Panel"),
    ("Accounts_Marketing", "Accounts"),
    ("Transport", "Transport"),
    ("Bureau Office", "Bureau Office")
]


for text, keyword in button_data:
    tk.Button(group_btn_frame, text=text, command=lambda k=keyword: filter_by_group(k), width=16, font=("Segoe UI", 11,"bold")).pack(pady=(2,5))

tk.Button(group_btn_frame, text="Show All", command=refresh_table, width=16, font=("Segoe UI", 11, "bold")).pack(pady=2)

# Right side frame for Search label, Search entry and Treeview
right_frame = tk.Frame(main_frame, bg="#f5f5f5")
right_frame.pack(side=tk.LEFT, padx=10)

# Search Label upper
tk.Label(right_frame, text="🔍 Search by Name or Number:", bg="#f5f5f5", font=("Segoe UI", 14, "bold")).pack(anchor='w', pady=(0, 5))

# Search Entry down
entry_search = tk.Entry(right_frame, width=35, font=("Segoe UI", 14, "bold"))
entry_search.pack(pady=(0, 10))
entry_search.insert(0,"Search")
entry_search.config(fg='grey')
entry_search.bind("<FocusIn>", lambda e: on_focus_in(entry_search, "Search"))
entry_search.bind("<FocusOut>", lambda e: on_focus_out(entry_search, "Search"))
entry_search.bind("<KeyRelease>", search_contacts)

# Treeview Frame
tree_frame = tk.Frame(right_frame, bd=1, relief="solid")
tree_frame.pack()

tree_scroll = tk.Scrollbar(tree_frame)
tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

tree = ttk.Treeview(tree_frame, columns=('name', 'phone'), show='headings', height=12, yscrollcommand=tree_scroll.set)
tree.pack(side=tk.LEFT)
tree_scroll.config(command=tree.yview)

tree.heading('name', text='👤 Name')
tree.heading('phone', text='📞 Phone Number')
tree.column('name', anchor='center', width=280)
tree.column('phone', anchor='center', width=200)
tree.bind("<<TreeviewSelect>>", on_tree_select)

# Input and buttons below the treeview
frame_input = tk.Frame(root, bg="#f5f5f5")
frame_input.pack(pady=10)

entry_name = tk.Entry(frame_input, width=25, font=("Segoe UI", 14))
entry_name.grid(row=0, column=0, padx=10)
entry_name.insert(0, "Name")
entry_name.config(fg='grey')
entry_name.bind("<FocusIn>", lambda e: on_focus_in(entry_name, "Name"))
entry_name.bind("<FocusOut>", lambda e: on_focus_out(entry_name, "Name"))

entry_phone = tk.Entry(frame_input, width=25, font=("Segoe UI", 14))
entry_phone.grid(row=0, column=1, padx=10)
entry_phone.insert(0, "Phone Number")
entry_phone.config(fg='grey')
entry_phone.bind("<FocusIn>", lambda e: on_focus_in(entry_phone, "Phone Number"))
entry_phone.bind("<FocusOut>", lambda e: on_focus_out(entry_phone, "Phone Number"))

frame_btn = tk.Frame(root, bg="#f5f5f5")
frame_btn.pack()

tk.Button(frame_btn, text="➕ Add", command=add_contact, bg="#2ecc71", fg="white", width=12, font=("Segoe UI", 13, "bold")).grid(row=0, column=0, padx=5)
tk.Button(frame_btn, text="✏️ Update", command=update_contact, bg="#f1c40f", fg="black", width=12, font=("Segoe UI", 13, "bold")).grid(row=0, column=1, padx=5)

# Tag Colors
tree.tag_configure('highlight_odd', background='#ffe4b9')
tree.tag_configure('highlight_even', background='#fbb11a')
#tree.tag_configure('normal', background='white', font=("Segoe UI", 14,'bold'))
tree.tag_configure('evenrow', background='white')
tree.tag_configure('oddrow', background='#EEEEEE')
tree.tag_configure('notfound', font=('Segoe UI', 14, 'bold'), foreground='red')


# Footer
copyright_text = "© 2025 Shahriyar Rahman Antor. All rights reserved."
footer_label = tk.Label(root, text=copyright_text, bg="#f5f5f5", fg="gray40", font=("Segoe UI", 10))
footer_label.pack(side=tk.BOTTOM, pady=5)

reset_placeholders()
refresh_table()
root.mainloop()
