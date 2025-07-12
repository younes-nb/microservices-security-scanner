import tkinter as tk
from tkinter import ttk, messagebox
from src.orchestrator import knowledge_base

class LinkEditorWindow(tk.Toplevel):
    def __init__(self, parent, source_name, component_data, all_components):
        super().__init__(parent)
        self.title(f"Edit Links for: {source_name}")
        self.geometry("800x600")
        self.parent = parent
        self.source_name = source_name
        self.component_data = component_data
        self.all_components = all_components
        self.link_widgets = {}
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        add_frame = ttk.LabelFrame(main_frame, text="Add New Link", padding="10")
        add_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(add_frame, text="Target:").pack(side=tk.LEFT, padx=(0, 5))
        self.new_link_target = ttk.Combobox(add_frame, values=[c for c in self.all_components if c != self.source_name])
        self.new_link_target.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(add_frame, text="Add Link", command=self.add_new_link).pack(side=tk.LEFT)
        self.scroll_canvas = tk.Canvas(main_frame, borderwidth=0)
        self.links_frame = ttk.Frame(self.scroll_canvas)
        self.scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.scroll_canvas.yview)
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        self.canvas_window = self.scroll_canvas.create_window((0, 0), window=self.links_frame, anchor="nw")
        self.links_frame.bind("<Configure>", lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all")))
        self.scroll_canvas.bind("<Configure>", lambda e: self.scroll_canvas.itemconfig(self.canvas_window, width=e.width))
        bottom_bar = ttk.Frame(main_frame)
        bottom_bar.pack(fill=tk.X, pady=(10, 0), side=tk.BOTTOM)
        ttk.Button(bottom_bar, text="Save & Close", command=self.save_and_close).pack(side=tk.RIGHT)
        self.render_links()

    def render_links(self):
        for widget in self.links_frame.winfo_children():
            widget.destroy()
        self.link_widgets = {}
        all_conn_types = sorted([s['name'] for s in knowledge_base.CONNECTOR_GENERIC_STEREOTYPE_LIST] + \
                                [s['name'] for sublist in knowledge_base.CONNECTOR_STEREOTYPE_HIERARCHY_MAP.values() for s in sublist])
        links = self.component_data.get("links", [])
        for i, link_data in enumerate(links):
            target_name = link_data.get("target_name")
            link_frame = ttk.LabelFrame(self.links_frame, text=f"Link to: {target_name}", padding="10")
            link_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)
            link_frame.columnconfigure(1, weight=1)
            ttk.Label(link_frame, text="Connector Types:").grid(row=0, column=0, sticky="nw", padx=(0, 5))
            conn_listbox = tk.Listbox(link_frame, selectmode=tk.MULTIPLE, exportselection=False, height=6)
            for c_type in all_conn_types:
                conn_listbox.insert(tk.END, c_type)
                if c_type in link_data.get("connector_types", []):
                    conn_listbox.selection_set(tk.END)
            conn_listbox.grid(row=0, column=1, sticky="ew")
            ttk.Label(link_frame, text="Security Annotations:").grid(row=1, column=0, sticky="nw", padx=(0, 5))
            sec_frame = ttk.Frame(link_frame)
            sec_frame.grid(row=1, column=1, sticky="ew", pady=(5,0))
            sec_combos = {}
            row = 0
            for cat_name, cat_list in knowledge_base.SECURITY_CONNECTOR_ANNOTATIONS.items():
                cat_label = ttk.Label(sec_frame, text=f"{cat_name.replace('_', ' ').title()}:")
                cat_label.grid(row=row, column=0, sticky="w")
                item_names = ["None"] + [item['name'] for item in cat_list]
                sec_combo = ttk.Combobox(sec_frame, values=item_names)
                sec_combo.grid(row=row, column=1, sticky="ew", pady=2)
                current_selection = "None"
                for sel in link_data.get("security_annotations", []):
                    if sel in [item['name'] for item in cat_list]:
                        current_selection = sel
                        break
                sec_combo.set(current_selection)
                sec_combos[cat_name] = sec_combo
                row += 1
            ttk.Button(link_frame, text="Remove Link", command=lambda idx=i: self.remove_link(idx)).grid(row=2, column=1, sticky="e", pady=(10,0))
            self.link_widgets[i] = {"conn_listbox": conn_listbox, "sec_combos": sec_combos}

    def add_new_link(self):
        target = self.new_link_target.get()
        if not target:
            messagebox.showwarning("Warning", "Please select a target component.")
            return
        if any(link.get("target_name") == target for link in self.component_data.get("links", [])):
            messagebox.showwarning("Warning", f"A link to '{target}' already exists.")
            return
        new_link = {
            "target_name": target,
            "connector_types": [],
            "security_annotations": []
        }
        if "links" not in self.component_data:
            self.component_data["links"] = []
        self.component_data["links"].append(new_link)
        self.render_links()

    def remove_link(self, index):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to remove this link?"):
            if "links" in self.component_data and index < len(self.component_data["links"]):
                del self.component_data["links"][index]
                self.render_links()

    def save_and_close(self):
        new_links_data = []
        for i, widgets in self.link_widgets.items():
            link_data = self.component_data["links"][i]
            listbox = widgets["conn_listbox"]
            selected_indices = listbox.curselection()
            link_data["connector_types"] = [listbox.get(i) for i in selected_indices]
            sec_annots = []
            for combo in widgets["sec_combos"].values():
                selection = combo.get()
                if selection != "None":
                    sec_annots.append(selection)
            link_data["security_annotations"] = sec_annots
            new_links_data.append(link_data)
        self.parent.data[self.source_name]["links"] = new_links_data
        print(f"Updated links for {self.source_name}")
        self.destroy()