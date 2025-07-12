import json
import os

def _sanitize_name(name):
    return name.replace('-', '_').replace(' ', '_')

def generate_python_model(json_path: str, output_path: str, project_path: str, log_callback):
    log_callback(f"--- STAGE 3: Generating Python Model ---")
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        log_callback(f"ERROR: Could not load or parse JSON file for model generation: {e}")
        return
    sanitized_component_names = []
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    try:
        with open(output_path, 'w') as f:
            f.write("from src.codeable_models import CClass, CBundle, add_links\n")
            f.write("from src.metamodels.component_metamodel import component\n")
            f.write("from src.metamodels.microservice_components_metamodel import *\n")
            f.write("from src.metamodels.security_annotations_metamodel import *\n\n")
            f.write("# --- 1. Component Definitions ---\n")
            for name, details in data.items():
                class_name = _sanitize_name(name)
                sanitized_component_names.append(class_name)
                string_name = name.replace('-', ' ').title()
                stereotypes = []
                comp_type = details.get("type")
                if comp_type:
                    stereotypes.append(comp_type)
                stereotypes.extend(details.get("security_annotations", []))
                valid_stereotypes = [s for s in stereotypes if s]
                stereotype_str = ", ".join(f'{s}' for s in valid_stereotypes)
                f.write(f'{class_name} = CClass(component, "{string_name}", stereotype_instances=[{stereotype_str}])\n')
            f.write("\n# --- 2. Link Definitions ---\n")
            for source_name, details in data.items():
                if "links" in details and details["links"]:
                    source_class_name = _sanitize_name(source_name)
                    for link in details["links"]:
                        target_name = link.get("target_name")
                        if not target_name or target_name not in data:
                            log_callback(f"WARNING: Skipping link from '{source_name}' to non-existent target '{target_name}'.")
                            continue
                        target_class_name = _sanitize_name(target_name)
                        link_stereotypes = []
                        link_stereotypes.extend(link.get("connector_types", []))
                        link_stereotypes.extend(link.get("security_annotations", []))
                        valid_link_stereotypes = [s for s in link_stereotypes if s]
                        stereotype_str = ", ".join(f'{s}' for s in valid_link_stereotypes)
                        f.write(f'add_links({{{source_class_name}: {target_class_name}}}, role_name="target", stereotype_instances=[{stereotype_str}])\n')
            f.write("\n\n# --- 3. Bundle Definition ---\n")
            project_folder_name = os.path.basename(os.path.normpath(project_path))
            bundle_name = _sanitize_name(project_folder_name)
            elements_list_str = ", ".join(sanitized_component_names)
            f.write(f'discoverd_model = CBundle("{bundle_name}",\n'
                    f'                      elements=[o.class_object for o in [{elements_list_str}]])\n')
        log_callback(f"SUCCESS: Python model generated at '{output_path}'")
    except Exception as e:
        log_callback(f"ERROR: Failed to generate Python model file: {e}")