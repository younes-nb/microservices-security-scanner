import tkinter as tk
from tkinter import ttk, messagebox
import json
from src.orchestrator import knowledge_base
from .link_editor_window import LinkEditorWindow

class EditorWindow(tk.Toplevel):
    def __init__(self, parent, json_path):
        super().__init__(parent)
        self.title("Analysis Editor")
        self.geometry("900x700")
        self.json_path = json_path
        self.data = self.load_data()
        self.component_widgets = {}
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(toolbar, text="Add New Component", command=self.add_component).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Submit & Close", command=self.submit).pack(side=tk.RIGHT)
        ttk.Button(toolbar, text="Save Changes", command=self.save_data).pack(side=tk.RIGHT, padx=5)
        self.scroll_canvas = tk.Canvas(main_frame, borderwidth=0)
        self.components_frame = ttk.Frame(self.scroll_canvas)
        self.scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.scroll_canvas.yview)
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        self.canvas_window = self.scroll_canvas.create_window((0, 0), window=self.components_frame, anchor="nw")
        self.components_frame.bind("<Configure>", self.on_frame_configure)
        self.scroll_canvas.bind("<Configure>", self.on_canvas_configure)
        self.render_components()

    def on_frame_configure(self, event):
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def on_canvas_configure(self, event):
        self.scroll_canvas.itemconfig(self.canvas_window, width=event.width)

    def load_data(self):
        try:
            with open(self.json_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            messagebox.showerror("Error", f"Could not load or parse JSON file: {e}")
            self.destroy()
            return {}

    def render_components(self):
        for widget in self.components_frame.winfo_children():
            widget.destroy()
        self.component_widgets = {}
        all_comp_types_set = set()
        for s in knowledge_base.COMPONENT_GENERIC_STEREOTYPE_LIST:
            all_comp_types_set.add(s['name'])
        for sublist in knowledge_base.COMPONENT_STEREOTYPE_HIERARCHY_MAP.values():
            for s in sublist:
                all_comp_types_set.add(s['name'])
        all_comp_types = sorted(list(all_comp_types_set))
        all_comp_sec_types = [item['name'] for cat in knowledge_base.SECURITY_COMPONENT_ANNOTATIONS.values() for item in cat]
        for name, component_data in self.data.items():
            comp_frame = ttk.LabelFrame(self.components_frame, text=name, padding="10")
            comp_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)
            comp_frame.columnconfigure(1, weight=1)
            ttk.Label(comp_frame, text="Component Type:").grid(row=0, column=0, sticky="w", pady=2, padx=(0, 5))
            type_selector = ttk.Combobox(comp_frame, values=all_comp_types, width=40)
            type_selector.grid(row=0, column=1, sticky="ew")
            current_type = component_data.get("type")
            if current_type:
                type_selector.set(current_type)
            ttk.Label(comp_frame, text="Security Annotations:").grid(row=1, column=0, sticky="nw", pady=2, padx=(0, 5))
            sec_listbox = tk.Listbox(comp_frame, selectmode=tk.MULTIPLE, exportselection=False, height=5)
            for sec_type in sorted(all_comp_sec_types):
                sec_listbox.insert(tk.END, sec_type)
                if sec_type in component_data.get("security_annotations", []):
                    sec_listbox.selection_set(tk.END)
            sec_listbox.grid(row=1, column=1, sticky="ew")
            button_frame = ttk.Frame(comp_frame)
            button_frame.grid(row=2, column=1, sticky="e", pady=(10, 0))
            ttk.Button(button_frame, text="Edit Links...", command=lambda n=name: self.open_link_editor(n)).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="Delete", command=lambda n=name: self.delete_component(n)).pack(side=tk.LEFT)
            self.component_widgets[name] = {
                "type_selector": type_selector,
                "sec_listbox": sec_listbox
            }

    def _commit_ui_changes_to_data(self):
        for name, widgets in self.component_widgets.items():
            if name in self.data:
                self.data[name]["type"] = widgets["type_selector"].get()
                listbox = widgets["sec_listbox"]
                selected_indices = listbox.curselection()
                selected_values = [listbox.get(i) for i in selected_indices]
                self.data[name]["security_annotations"] = selected_values
        print("UI changes committed to data model.")

    def save_data(self):
        self._commit_ui_changes_to_data()
        try:
            with open(self.json_path, 'w') as f:
                json.dump(self.data, f, indent=4)
            messagebox.showinfo("Success", "Changes saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save JSON file: {e}")

    def add_component(self):
        from tkinter.simpledialog import askstring
        new_name = askstring("New Component", "Enter the name for the new component:")
        if new_name and new_name not in self.data:
            self.data[new_name] = {"type": None, "security_annotations": [], "links": []}
            self.render_components()
        elif new_name:
            messagebox.showwarning("Warning", "A component with that name already exists.")
            
    def delete_component(self, component_name_to_delete):
        """Deletes a component after user confirmation."""
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete the component '{component_name_to_delete}'?"):
            return
        if component_name_to_delete in self.data:
            del self.data[component_name_to_delete]
        for component_data in self.data.items():
            if "links" in component_data:
                component_data["links"] = [
                    link for link in component_data["links"]
                    if link.get("target_name") != component_name_to_delete
                ]
        self.render_components()
        print(f"Deleted component: {component_name_to_delete}")


    def open_link_editor(self, source_name):
        component_data = self.data.get(source_name)
        if component_data is None:
            return
        LinkEditorWindow(
            parent=self,
            source_name=source_name,
            component_data=component_data,
            all_components=list(self.data.keys())
        )
        
    def validate_data(self):
        missing_types = []
        for name, component_data in self.data.items():
            if not component_data.get("type"):
                missing_types.append(name)
        if missing_types:
            messagebox.showerror("Validation Error", "The following components are missing a type:\n\n" + "\n".join(missing_types))
            return False
        for name, component_data in self.data.items():
            for link in component_data.get("links", []):
                if not link.get("connector_types"):
                    messagebox.showerror("Validation Error", f"The link from '{name}' to '{link.get('target_name')}' is missing a connector type.")
                    return False
        return True

    def submit(self):
        self._commit_ui_changes_to_data()
        if not self.validate_data():
            return
        try:
            with open(self.json_path, 'w') as f:
                json.dump(self.data, f, indent=4)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Could not save JSON file: {e}")