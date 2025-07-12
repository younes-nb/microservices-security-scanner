import os
import yaml
from . import knowledge_base
from . import prompt_builder
from . import output_generator
from src.agent.agent import (
    get_explanation,
    select_stereotype_from_explanation,
    get_structured_annotations
)
from src.agent.tools import read_multiple_files

class ScannerOrchestrator:
    def __init__(self, project_path, log_callback):
        self.project_path = project_path
        self.log = log_callback
        self.components_data = {}

    def run_scan(self):
        try:
            self.log("\n--- STAGE 1: Analyzing Components ---")
            docker_compose_path = os.path.join(self.project_path, 'docker-compose.yaml')
            with open(docker_compose_path, 'r') as f:
                docker_compose_data = yaml.safe_load(f)
            component_list = list(docker_compose_data.get('services', {}).keys())
            self._analyze_components(component_list, docker_compose_data)
            self.log("--- STAGE 1 COMPLETE ---")
            self.log("\n--- STAGE 2: Analyzing Links Between Components ---")
            self._analyze_and_create_links(component_list, docker_compose_data)
            self.log("--- STAGE 2 COMPLETE ---")
            output_generator.generate_json_output(self.components_data, self.log)
            self.log("\n✅ SCAN COMPLETE: Process finished successfully.")
        except Exception as e:
            self.log(f"\n❌ FATAL ERROR: The orchestration failed: {e}")

    def _get_file_contents(self, component_name, service_info):
        """Helper to read source files for a given component."""
        build_context = service_info.get('build', {}).get('context')
        if build_context == '.':
            dockerfile_path = service_info.get('build', {}).get('dockerfile')
            if dockerfile_path and '/' in dockerfile_path:
                build_context = os.path.dirname(dockerfile_path)
            else:
                build_context = component_name
        elif build_context is None and 'image' in service_info:
            build_context = component_name
        full_component_path = os.path.abspath(os.path.join(self.project_path, build_context))
        if not os.path.isdir(full_component_path):
            return f"This is an image-based service named '{component_name}'. No local files."
        try:
            files_to_read = [os.path.join(full_component_path, f) for f in os.listdir(full_component_path) if os.path.isfile(os.path.join(full_component_path, f)) and not f.endswith(('.lock', '.ico', '.png'))][:10]
            return read_multiple_files.invoke({"file_paths": files_to_read}) if files_to_read else f"Directory for service '{component_name}' is empty."
        except Exception as e:
            return f"Error reading files for service '{component_name}': {e}"


    def _analyze_components(self, component_list, docker_compose_data):
        generic_stereotype_names = [s['name'] for s in knowledge_base.COMPONENT_GENERIC_STEREOTYPE_LIST]
        for component_name in component_list:
            self.log(f"\n--- Running Analysis on '{component_name}' ---")
            service_info = docker_compose_data.get('services', {}).get(component_name, {})
            file_contents = self._get_file_contents(component_name, service_info)
            final_stereotype = None
            type_hint = None
            prompt = prompt_builder.build_generic_stereotype_prompt(component_name, file_contents, knowledge_base.COMPONENT_GENERIC_STEREOTYPE_LIST)
            generic_explanation = get_explanation(prompt)
            self.log(f"INFO: AI Explanation (Generic): {generic_explanation}")
            prompt = prompt_builder.build_selection_prompt(generic_explanation, generic_stereotype_names)
            generic_stereotype = select_stereotype_from_explanation(prompt, choices=generic_stereotype_names)
            if generic_stereotype in generic_stereotype_names:
                final_stereotype = generic_stereotype
                self.log(f"INFO: Selected Generic Stereotype: '{generic_stereotype}'")
                if generic_stereotype in knowledge_base.COMPONENT_STEREOTYPE_HIERARCHY_MAP:
                    specific_list = knowledge_base.COMPONENT_STEREOTYPE_HIERARCHY_MAP[generic_stereotype]
                    specific_names = [s['name'] for s in specific_list]
                    prompt = prompt_builder.build_specific_stereotype_prompt(component_name, file_contents, generic_stereotype, generic_explanation, specific_list)
                    specific_explanation = get_explanation(prompt)
                    self.log(f"INFO: AI Explanation (Specific): {specific_explanation}")
                    prompt = prompt_builder.build_selection_prompt(specific_explanation, specific_names)
                    specific_stereotype = select_stereotype_from_explanation(prompt, choices=specific_names)
                    if specific_stereotype in specific_names:
                        final_stereotype = specific_stereotype
                        self.log(f"SUCCESS: Refined to specific stereotype: '{final_stereotype}'")
                    else:
                        type_hint = specific_stereotype
                        self.log(f"INFO: No valid specific type chosen. Using generic '{final_stereotype}'.")
            else:
                type_hint = generic_stereotype
                self.log(f"WARNING: Invalid generic stereotype '{generic_stereotype}'. Type will be null.")
            self.log(f"INFO: Final Stereotype for '{component_name}': '{final_stereotype}'")
            self.log(f"\n--- Analyzing Security Annotations for '{component_name}' ---")
            collected_security_annotations = []
            security_annotation_hints = []
            for category_name, category_list in knowledge_base.SECURITY_COMPONENT_ANNOTATIONS.items():
                self.log(f"--- Analyzing Category: {category_name} ---")
                prompt = prompt_builder.build_security_explanation_prompt(component_name, final_stereotype, file_contents, category_name, category_list)
                security_explanation = get_explanation(prompt)
                self.log(f"INFO: AI Explanation ({category_name}): {security_explanation}")
                item_names = [item['name'] for item in category_list]
                prompt = prompt_builder.build_single_selection_prompt(security_explanation, item_names, category_name)
                selected_annotation = select_stereotype_from_explanation(prompt, choices=item_names) # Reusing the agent function
                if selected_annotation in item_names:
                    self.log(f"SUCCESS: Selected annotation '{selected_annotation}' for category '{category_name}'.")
                    collected_security_annotations.append(selected_annotation)
                elif selected_annotation and selected_annotation.lower() != 'none':
                    self.log(f"INFO: Invalid annotation '{selected_annotation}' for category '{category_name}'. Storing as hint.")
                    security_annotation_hints.append(selected_annotation)
                else:
                    self.log(f"INFO: No specific annotation selected for category '{category_name}'.")
            component_output = {
                "type": final_stereotype,
                "security_annotations": collected_security_annotations
            }
            if type_hint:
                component_output["type_hint"] = type_hint
            if security_annotation_hints:
                component_output["security_annotation_hints"] = security_annotation_hints
            self.components_data[component_name] = component_output
            self.log(f"SUCCESS: Analysis complete for '{component_name}'. Found {len(collected_security_annotations)} security annotations.")
    
    def _analyze_and_create_links(self, component_list, docker_compose_data):
        """Analyzes and refines connections between all identified components."""
        for source_name in component_list:
            self.log(f"\n--- Analyzing outgoing links for '{source_name}' ---")
            service_info = docker_compose_data.get('services', {}).get(source_name, {})
            file_contents = self._get_file_contents(source_name, service_info)
            self.log(f"INFO: Discovering all potential links from '{source_name}'...")
            prompt = prompt_builder.build_generic_link_prompt(
                source_component=source_name,
                all_components=component_list,
                file_contents=file_contents,
                generic_connector_list=knowledge_base.CONNECTOR_GENERIC_STEREOTYPE_LIST
            )
            link_results = get_structured_annotations(prompt)
            if not link_results or "links" not in link_results:
                self.log(f"INFO: No outgoing links were found for '{source_name}'.")
                continue
            discovered_links = link_results.get("links", [])
            final_links = []
            links_hint = []
            for link in discovered_links:
                target_name = link.get("target_component")
                generic_types = link.get("connector_types", [])
                if not target_name or not generic_types:
                    links_hint.append(f"Malformed link object from AI: {link}")
                    continue
                self.log(f"INFO: Refining link from '{source_name}' to '{target_name}'...")
                final_connector_types = []
                for g_type in generic_types:
                    if g_type in knowledge_base.CONNECTOR_STEREOTYPE_HIERARCHY_MAP:
                        specific_list = knowledge_base.CONNECTOR_STEREOTYPE_HIERARCHY_MAP[g_type]
                        specific_names = [s['name'] for s in specific_list]
                        expl_prompt = prompt_builder.build_specific_stereotype_prompt(
                            f"{source_name} -> {target_name}", file_contents, g_type, f"This link is a '{g_type}'.", specific_list
                        )
                        specific_explanation = get_explanation(expl_prompt)
                        sel_prompt = prompt_builder.build_single_selection_prompt(specific_explanation, specific_names, f"Specific type for {g_type}")
                        specific_type = select_stereotype_from_explanation(sel_prompt, choices=specific_names)
                        if specific_type and specific_type in specific_names:
                            self.log(f"SUCCESS: Refined '{g_type}' to '{specific_type}'.")
                            final_connector_types.append(specific_type)
                        else:
                            self.log(f"INFO: Could not refine '{g_type}', keeping the generic type.")
                            final_connector_types.append(g_type) # Keep the generic one
                            if specific_type and specific_type.lower() != 'none':
                                links_hint.append(f"Invalid specific connector '{specific_type}' for generic '{g_type}'.")
                    else:
                        final_connector_types.append(g_type)
                self.log(f"--- Analyzing Security for link '{source_name}' -> '{target_name}' ---")
                collected_security_annotations = []
                security_annotation_hints = []
                for category_name, category_list in knowledge_base.SECURITY_CONNECTOR_ANNOTATIONS.items():
                    item_names = [item['name'] for item in category_list]
                    prompt = prompt_builder.build_link_security_explanation_prompt(
                        source_name, target_name, final_connector_types, file_contents, category_name, category_list
                    )
                    security_explanation = get_explanation(prompt)
                    self.log(f"INFO: AI Explanation (Link Security - {category_name}): {security_explanation}")
                    prompt = prompt_builder.build_single_selection_prompt(security_explanation, item_names, category_name)
                    selected_annotation = select_stereotype_from_explanation(prompt, choices=item_names)
                    if selected_annotation in item_names:
                        collected_security_annotations.append(selected_annotation)
                    elif selected_annotation and selected_annotation.lower() != 'none':
                        security_annotation_hints.append(selected_annotation)
                link_object = {
                    "target_name": target_name,
                    "connector_types": final_connector_types,
                    "security_annotations": collected_security_annotations
                }
                if security_annotation_hints:
                    link_object["security_annotation_hints"] = security_annotation_hints

                final_links.append(link_object)
            if final_links:
                self.components_data[source_name]["links"] = final_links
            if links_hint:
                self.components_data[source_name]["links_hint"] = links_hint

            self.log(f"SUCCESS: Link analysis complete for '{source_name}'.")