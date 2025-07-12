import os
from src.run.calculate_metrics import calculate_all_metrics
from src.run.ground_truth import authorization_on_client_service_paths_values, backend_authorization_values, \
    api_gateways_bffs_for_traffic_control_values, sensitive_data_values

calculate_all_metrics()

def generate_csv(models_dict):
    text = ""
    first = True
    header_line = None
    for model_name in models_dict:
        line = model_name
        if first:
            header_line = "model_name"
        metrics_dict = models_dict[model_name]
        for metric in metrics_dict:
            if first:
                header_line += ", " + metric
            value = metrics_dict[metric]
            if value is None:
                line += ", " + "0"
            else:
                line += ", " + str(metrics_dict[metric])
        line += "\n"
        text += line
        if first:
            text = header_line + "\n" + text
            first = False
    return text


def write_csv(models_dict, file_name, directory="output/stats"):
    if not os.path.exists(directory):
        os.makedirs(directory)
    full_path = os.path.join(directory, file_name)
    print(f"INFO: Writing CSV to {full_path}")
    with open(full_path, "w", encoding='utf-8') as file:
        file.write(generate_csv(models_dict))

def write_csv_all():
    write_csv(authorization_on_client_service_paths_values, "authorization_on_client_service_paths.csv")
    write_csv(backend_authorization_values, "backend_authorization.csv")
    write_csv(api_gateways_bffs_for_traffic_control_values, "api_gateways_bffs_for_traffic_control_values.csv")
    write_csv(sensitive_data_values, "sensitive_data_values.csv")

    
