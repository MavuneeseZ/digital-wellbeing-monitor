"""
Timetable Conflict Detector
A mini project for college - detects scheduling conflicts in class timetables
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, timedelta
import json
import os

class TimetableConflictDetector:
    def __init__(self, root):
        self.root = root
        self.root.title("Timetable Conflict Detector")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Data storage
        self.timetable = []
        self.filename = "timetable_data.json"
        
        # Days and time slots
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        self.time_slots = self.generate_time_slots()
        
        # Load existing data
        self.load_data()
        
        # Setup UI
        self.setup_ui()
        
    def generate_time_slots(self):
        """Generate time slots from 8:00 AM to 6:00 PM"""
        slots = []
        start_time = datetime.strptime("08:00", "%H:%M")
        end_time = datetime.strptime("18:00", "%H:%M")
        
        current = start_time
        while current <= end_time:
            slots.append(current.strftime("%H:%M"))
            current += timedelta(minutes=30)
        
        return slots
    
    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title_label = tk.Label(
            self.root,
            text="📅 Timetable Conflict Detector",
            font=("Arial", 18, "bold"),
            bg="#4CAF50",
            fg="white",
            pady=10
        )
        title_label.pack(fill=tk.X)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left frame - Input
        left_frame = ttk.LabelFrame(main_frame, text="Add Class", padding="10")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Subject Name
        ttk.Label(left_frame, text="Subject Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.subject_entry = ttk.Entry(left_frame, width=30)
        self.subject_entry.grid(row=0, column=1, pady=5)
        
        # Day
        ttk.Label(left_frame, text="Day:").grid(row=1, column=0, sticky="w", pady=5)
        self.day_combo = ttk.Combobox(left_frame, values=self.days, state="readonly", width=28)
        self.day_combo.grid(row=1, column=1, pady=5)
        self.day_combo.current(0)
        
        # Start Time
        ttk.Label(left_frame, text="Start Time:").grid(row=2, column=0, sticky="w", pady=5)
        self.start_time_combo = ttk.Combobox(left_frame, values=self.time_slots, state="readonly", width=28)
        self.start_time_combo.grid(row=2, column=1, pady=5)
        self.start_time_combo.current(0)
        
        # End Time
        ttk.Label(left_frame, text="End Time:").grid(row=3, column=0, sticky="w", pady=5)
        self.end_time_combo = ttk.Combobox(left_frame, values=self.time_slots, state="readonly", width=28)
        self.end_time_combo.grid(row=3, column=1, pady=5)
        self.end_time_combo.current(2)
        
        # Room Number
        ttk.Label(left_frame, text="Room Number:").grid(row=4, column=0, sticky="w", pady=5)
        self.room_entry = ttk.Entry(left_frame, width=30)
        self.room_entry.grid(row=4, column=1, pady=5)
        
        # Teacher Name
        ttk.Label(left_frame, text="Teacher Name:").grid(row=5, column=0, sticky="w", pady=5)
        self.teacher_entry = ttk.Entry(left_frame, width=30)
        self.teacher_entry.grid(row=5, column=1, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Add Class", command=self.add_class).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Fields", command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Check Conflicts", command=self.check_all_conflicts).pack(side=tk.LEFT, padx=5)
        
        # Right frame - Display
        right_frame = ttk.LabelFrame(main_frame, text="Timetable", padding="10")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Treeview for displaying classes
        columns = ("Subject", "Day", "Time", "Room", "Teacher")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="tree headings", height=15)
        
        # Column headings
        self.tree.heading("#0", text="ID")
        self.tree.heading("Subject", text="Subject")
        self.tree.heading("Day", text="Day")
        self.tree.heading("Time", text="Time")
        self.tree.heading("Room", text="Room")
        self.tree.heading("Teacher", text="Teacher")
        
        # Column widths
        self.tree.column("#0", width=40)
        self.tree.column("Subject", width=120)
        self.tree.column("Day", width=100)
        self.tree.column("Time", width=120)
        self.tree.column("Room", width=80)
        self.tree.column("Teacher", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Delete button
        ttk.Button(right_frame, text="Delete Selected", command=self.delete_class).pack(pady=5)
        
        # Bottom frame - Conflict display
        bottom_frame = ttk.LabelFrame(main_frame, text="Conflict Report", padding="10")
        bottom_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        self.conflict_text = scrolledtext.ScrolledText(bottom_frame, height=10, wrap=tk.WORD)
        self.conflict_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=3)
        main_frame.rowconfigure(1, weight=1)
        
        # Populate treeview
        self.refresh_treeview()
    
    def add_class(self):
        """Add a new class to the timetable"""
        subject = self.subject_entry.get().strip()
        day = self.day_combo.get()
        start_time = self.start_time_combo.get()
        end_time = self.end_time_combo.get()
        room = self.room_entry.get().strip()
        teacher = self.teacher_entry.get().strip()
        
        # Validation
        if not subject:
            messagebox.showerror("Error", "Please enter a subject name!")
            return
        
        if not day:
            messagebox.showerror("Error", "Please select a day!")
            return
        
        # Check if end time is after start time
        start_dt = datetime.strptime(start_time, "%H:%M")
        end_dt = datetime.strptime(end_time, "%H:%M")
        
        if end_dt <= start_dt:
            messagebox.showerror("Error", "End time must be after start time!")
            return
        
        # Create class entry
        class_entry = {
            "subject": subject,
            "day": day,
            "start_time": start_time,
            "end_time": end_time,
            "room": room,
            "teacher": teacher
        }
        
        # Check for conflicts before adding
        conflicts = self.detect_conflicts(class_entry)
        
        if conflicts:
            conflict_msg = "⚠️ Conflict detected!\n\n"
            for conflict in conflicts:
                conflict_msg += f"• {conflict}\n"
            conflict_msg += "\nDo you still want to add this class?"
            
            if not messagebox.askyesno("Conflict Warning", conflict_msg):
                return
        
        # Add to timetable
        self.timetable.append(class_entry)
        self.save_data()
        self.refresh_treeview()
        self.clear_fields()
        
        messagebox.showinfo("Success", "Class added successfully!")
    
    def detect_conflicts(self, new_class):
        """Detect conflicts with existing classes"""
        conflicts = []
        
        new_start = datetime.strptime(new_class["start_time"], "%H:%M")
        new_end = datetime.strptime(new_class["end_time"], "%H:%M")
        
        for i, existing_class in enumerate(self.timetable):
            # Check if same day
            if existing_class["day"] != new_class["day"]:
                continue
            
            exist_start = datetime.strptime(existing_class["start_time"], "%H:%M")
            exist_end = datetime.strptime(existing_class["end_time"], "%H:%M")
            
            # Check time overlap
            if (new_start < exist_end and new_end > exist_start):
                # Same room conflict
                if existing_class["room"] and new_class["room"] and \
                   existing_class["room"].lower() == new_class["room"].lower():
                    conflicts.append(
                        f"Room conflict with '{existing_class['subject']}' on {existing_class['day']} "
                        f"({existing_class['start_time']}-{existing_class['end_time']}) in room {existing_class['room']}"
                    )
                
                # Same teacher conflict
                if existing_class["teacher"] and new_class["teacher"] and \
                   existing_class["teacher"].lower() == new_class["teacher"].lower():
                    conflicts.append(
                        f"Teacher conflict: {existing_class['teacher']} is teaching '{existing_class['subject']}' "
                        f"on {existing_class['day']} ({existing_class['start_time']}-{existing_class['end_time']})"
                    )
        
        return conflicts
    
    def check_all_conflicts(self):
        """Check for all conflicts in the timetable"""
        self.conflict_text.delete(1.0, tk.END)
        
        if len(self.timetable) < 2:
            self.conflict_text.insert(tk.END, "✓ Not enough classes to check for conflicts.\n")
            return
        
        all_conflicts = []
        
        for i in range(len(self.timetable)):
            for j in range(i + 1, len(self.timetable)):
                class1 = self.timetable[i]
                class2 = self.timetable[j]
                
                # Check if same day
                if class1["day"] != class2["day"]:
                    continue
                
                start1 = datetime.strptime(class1["start_time"], "%H:%M")
                end1 = datetime.strptime(class1["end_time"], "%H:%M")
                start2 = datetime.strptime(class2["start_time"], "%H:%M")
                end2 = datetime.strptime(class2["end_time"], "%H:%M")
                
                # Check time overlap
                if (start1 < end2 and end1 > start2):
                    # Room conflict
                    if class1["room"] and class2["room"] and \
                       class1["room"].lower() == class2["room"].lower():
                        all_conflicts.append(
                            f"🔴 Room Conflict:\n"
                            f"   '{class1['subject']}' ({class1['start_time']}-{class1['end_time']})\n"
                            f"   and '{class2['subject']}' ({class2['start_time']}-{class2['end_time']})\n"
                            f"   both scheduled in room {class1['room']} on {class1['day']}\n"
                        )
                    
                    # Teacher conflict
                    if class1["teacher"] and class2["teacher"] and \
                       class1["teacher"].lower() == class2["teacher"].lower():
                        all_conflicts.append(
                            f"🔴 Teacher Conflict:\n"
                            f"   {class1['teacher']} is assigned to both:\n"
                            f"   '{class1['subject']}' ({class1['start_time']}-{class1['end_time']})\n"
                            f"   and '{class2['subject']}' ({class2['start_time']}-{class2['end_time']})\n"
                            f"   on {class1['day']}\n"
                        )
        
        if all_conflicts:
            self.conflict_text.insert(tk.END, f"Found {len(all_conflicts)} conflict(s):\n\n")
            for conflict in all_conflicts:
                self.conflict_text.insert(tk.END, conflict + "\n")
        else:
            self.conflict_text.insert(tk.END, "✓ No conflicts found! Your timetable is valid.\n")
    
    def delete_class(self):
        """Delete selected class from timetable"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a class to delete!")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this class?"):
            item_id = int(self.tree.item(selected[0])["text"])
            del self.timetable[item_id]
            self.save_data()
            self.refresh_treeview()
            messagebox.showinfo("Success", "Class deleted successfully!")
    
    def refresh_treeview(self):
        """Refresh the treeview with current timetable data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add all classes
        for i, class_entry in enumerate(self.timetable):
            time_str = f"{class_entry['start_time']} - {class_entry['end_time']}"
            self.tree.insert(
                "",
                tk.END,
                text=str(i),
                values=(
                    class_entry["subject"],
                    class_entry["day"],
                    time_str,
                    class_entry["room"] or "N/A",
                    class_entry["teacher"] or "N/A"
                )
            )
    
    def clear_fields(self):
        """Clear all input fields"""
        self.subject_entry.delete(0, tk.END)
        self.day_combo.current(0)
        self.start_time_combo.current(0)
        self.end_time_combo.current(2)
        self.room_entry.delete(0, tk.END)
        self.teacher_entry.delete(0, tk.END)
    
    def save_data(self):
        """Save timetable data to JSON file"""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.timetable, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")
    
    def load_data(self):
        """Load timetable data from JSON file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    self.timetable = json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {str(e)}")
                self.timetable = []
        else:
            self.timetable = []


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = TimetableConflictDetector(root)
    root.mainloop()


if __name__ == "__main__":
    main()