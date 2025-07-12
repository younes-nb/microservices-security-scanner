def build_generic_stereotype_prompt(component_name: str, file_contents: str, stereotype_list: list) -> str:
    stereotypes_with_desc = "\n".join([f"- {s['name']}: {s['description']}" for s in stereotype_list])
    return f"""
            Analyze the service '{component_name}' based on its name and file contents.
            Explain which of the following GENERIC stereotypes it best fits.
            Your task is to provide a brief explanation for which stereotype from the list it best fits.
            Conclude your explanation with your final choice. DO NOT ask any questions.
            Available Generic Stereotypes:
            {stereotypes_with_desc}

            File Contents: {file_contents}
            """

def build_specific_stereotype_prompt(component_name: str, file_contents: str, generic_stereotype: str, generic_explanation: str, specific_stereotype_list: list) -> str:
    stereotypes_with_desc = "\n".join([f"- {s['name']}: {s['description']}" for s in specific_stereotype_list])
    return f"""
            The component '{component_name}' has been classified as a '{generic_stereotype}'.
            Now, refine this by explaining which of the following MORE SPECIFIC stereotypes it best fits.

            Available Specific Stereotypes:
            {stereotypes_with_desc}

            File Contents: {file_contents}
            Initial Analysis: {generic_explanation}
            """

def build_selection_prompt(explanation: str, stereotype_names: list) -> str:
    return f"""
            Based on the explanation, choose EXACTLY ONE stereotype from the list.
            **CRITICAL RULE:** Your response MUST BE ONLY the exact name of the stereotype from the list. It must not contain any other words, punctuation, or explanations.

            Available Stereotypes: {stereotype_names}
            Explanation: {explanation}
            """
            
def build_security_explanation_prompt(component_name: str, stereotype: str, file_contents: str, category_name: str, category_list: list) -> str:
    annotations_with_desc = "\n".join([f"- {item['name']}: {item['description']}" for item in category_list])
    return f"""
            You are analyzing the '{component_name}' component, which has been identified as a '{stereotype}'.
            Focus ONLY on the security category: '{category_name}'.
            Based on the file contents, explain which ONE of the following annotations best applies. If none seem relevant, state that clearly.

            Available Annotations for this category:
            {annotations_with_desc}

            File Contents:
            {file_contents}
            """

def build_single_selection_prompt(explanation: str, item_names: list, category_name: str) -> str:
    return f"""
            Based on the explanation for the '{category_name}' category, choose EXACTLY ONE item from the list below.
            If none from the list apply, respond with the single word "None".
              **CRITICAL RULE:** Your response MUST BE ONLY the exact name of the item or "None". Do not add any other text or explanations.

            Available Items: {item_names}
            Explanation: {explanation}
            """
            
def build_generic_link_prompt(source_component: str, all_components: list, file_contents: str, generic_connector_list: list) -> str:
    stereotypes_with_desc = "\n".join([f"- {s['name']}: {s['description']}" for s in generic_connector_list])
    potential_targets = [c for c in all_components if c != source_component]
    return f"""
            You are a software architect analyzing network connections.
            Your task is to identify all components that the source component '{source_component}' communicates with.

            Based on the file contents of the source component, find connections to any of the potential target components.
            For each link you identify, select one or more generic connector types that describe the connection.

            **CRITICAL RULE:** Respond with ONLY a single valid JSON object.
            This object must have a single key, "links", containing a list of objects.
            Each object in the list must have two keys:
            1. "target_component": The exact name of a component from the potential targets list.
            2. "connector_types": A list of one or more stereotype names from the available generic connectors list.

            If no connections are found, return an empty list: {{"links": []}}

            ---
            **Potential Target Components:**
            {potential_targets}

            **Available Generic Connectors:**
            {stereotypes_with_desc}

            **File Contents for Source Component '{source_component}':**
            {file_contents}
            """
            
def build_link_security_explanation_prompt(source_name: str, target_name: str, connector_types: list, file_contents: str, category_name: str, category_list: list) -> str:
    annotations_with_desc = "\n".join([f"- {item['name']}: {item['description']}" for item in category_list])
    return f"""
            You are analyzing the security of a specific connection between two components:
            - Source: '{source_name}'
            - Target: '{target_name}'
            This connection has been identified with the following connector types: {connector_types}.

            Now, focus ONLY on the security category: '{category_name}'.
            Based on the file contents of the SOURCE component ('{source_name}'), explain which ONE of the following annotations best applies to this specific connection. If none seem relevant, state that clearly.

            Available Annotations for this category:
            {annotations_with_desc}

            File Contents of '{source_name}':
            {file_contents}
            """