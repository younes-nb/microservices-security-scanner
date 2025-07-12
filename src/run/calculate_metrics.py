from output.discovered_model import discoverd_model
from src.detectors.component_model_detectors import ComponentModelDetector
from src.run.ground_truth import secure_connections_values, backend_authentication_values, \
    authentication_on_client_service_paths_values, backend_authorization_values, \
    authorization_on_client_service_paths_values, api_gateways_bffs_for_traffic_control_values, observability_values, \
    sensitive_data_values


def calculate_all_metrics():
    model_bundles = [discoverd_model]
    model_names = ["DM"]

    detectors = []

    for model_bundle, name in zip(model_bundles, model_names):
        detectors.append(ComponentModelDetector(model_bundle, name))

    # secure connections

    # SCO = Secure (encrypted or HTTPS) distributed connectors / all distributed connectors
    # SCC = Secure (encrypted or HTTPS) connectors to clients / all client connectors
    # SUC = Secure (encrypted or HTTPS) connectors to UIs / all UI connectors
    # SEC = Secure (encrypted or HTTPS) external connectors (clients + UIs) / all external connectors (clients + UIs)
    # SIC = Secure (encrypted or HTTPS) internal distributed connectors (in the backend, not connected to clients + UIs) /
    #       all internal distributed connectors

    for detector in detectors:
        secure_connections_values[detector.name]["SCO"] = detector.calculate_secure_connector_ratio()
        secure_connections_values[detector.name]["SCC"] = detector.calculate_secure_client_connector_ratio()
        secure_connections_values[detector.name]["SUC"] = detector.calculate_secure_ui_connector_ratio()
        secure_connections_values[detector.name]["SEC"] = detector.calculate_secure_external_client_ui_connector_ratio()
        secure_connections_values[detector.name]["SIC"] = detector.calculate_secure_backend_connector_ratio()

    # system backend authentication

    # AEI = authenticated backend connectors  (w/o in-mem connectors) / backend_connectors  (w/o in-mem connectors)
    # AEI_S = backend connectors (w/o in-mem connectors) securely authenticated (with Protocol-based Secure Authentication
    #         OR Secure Authentication Token)  / backend connectors  (w/o in-mem connectors)
    # AEI_K = backend connectors (w/o in-mem connectors) authenticated with API Keys /
    #         backend connectors (w/o in-mem connectors)
    # AEI_P = backend connectors (w/o in-mem connectors) authenticated with Plaintext Credentials /
    #         backend connectors (w/o in-mem connectors)
    # AEI_C = authenticated backend connectors  (w/o in-mem connectors) that use a secure connection /
    #         backend connectors (w/o in-mem connectors)
    # AEI_A = backend connectors (w/o in-mem connectors) authenticated with a secure
    #         method or API keys or that use a secure connection / backend connectors  (w/o in-mem connectors)

    for detector in detectors:
        backend_authentication_values[detector.name]["AEI"] = \
            detector.calculate_authenticated_backend_connectors_ratio()
        backend_authentication_values[detector.name]["AEI_S"] = \
            detector.calculate_securely_authenticated_backend_connectors_ratio()
        backend_authentication_values[detector.name]["AEI_K"] = \
            detector.calculate_backend_connectors_authenticated_with_api_keys_ratio()
        backend_authentication_values[detector.name]["AEI_P"] = \
            detector.calculate_backend_connectors_authenticated_with_plaintext_ratio()
        backend_authentication_values[detector.name]["AEI_C"] = \
            detector.calculate_secure_connector_and_authenticated_backend_connectors_ratio()
        backend_authentication_values[detector.name]["AEI_A"] = \
            detector.calculate_securely_or_secure_connector_authenticated_backend_connectors_ratio()

    # authentication on paths from clients or uis to system services

    # AEC = authenticated connectors on paths from clients or uis to system services /
    #       connectors on paths from clients or uis to system services
    # AEC_S = securely authenticated connectors on paths from clients or uis to system services /
    #         connectors on paths from clients or uis to system services
    # AEC_K = connectors authenticated with API Keys on paths from clients or uis to system services /
    #         connectors on paths from clients or uis to system services
    # AEC_P = connectors authenticated with Plaintext Credentials on paths from clients or uis to system services /
    #         connectors on paths from clients or uis to system services
    # AEC_C = authenticated connectors that use a secure connection on paths from clients or uis to system services /
    #       connectors on paths from clients or uis to system services
    # AEC_A = connectors  on paths from clients or uis to system services authenticated with a secure method or
    #         API keys or that use a secure connection / connectors on paths from clients or uis to system services

    for detector in detectors:
        authentication_on_client_service_paths_values[detector.name]["AEC"] = \
            detector.calculate_authenticated_connectors_on_client_service_paths_ratio()
        authentication_on_client_service_paths_values[detector.name]["AEC_S"] = \
            detector.calculate_securely_authenticated_connectors_on_client_service_paths_ratio()
        authentication_on_client_service_paths_values[detector.name]["AEC_K"] = \
            detector.calculate_connectors_authenticated_with_api_keys_on_client_service_paths_ratio()
        authentication_on_client_service_paths_values[detector.name]["AEC_P"] = \
            detector.calculate_connectors_authenticated_with_plaintext_on_client_service_paths_ratio()
        authentication_on_client_service_paths_values[detector.name]["AEC_C"] = \
            detector.calculate_secure_connector_and_authenticated_connectors_on_client_service_paths_ratio()
        authentication_on_client_service_paths_values[detector.name]["AEC_A"] = \
            detector.calculate_securely_or_secure_connector_authenticated_connectors_on_client_service_paths_ratio()

    # system backend authorization

    # AUB = authorized backend connectors (w/o in-mem connectors) / backend_connectors (w/o in-mem connectors)
    # AUB_T = backend connectors (w/o in-mem connectors) authorized with authorization tokens / backend connectors (w/o in-mem connectors)
    # AUB_E = backend connectors (w/o in-mem connectors) authorized with encrypted authorization information / backend connectors (w/o in-mem connectors)
    # AUB_P = backend connectors (w/o in-mem connectors) authorized with Plaintext Information /
    #         backend connectors (w/o in-mem connectors)
    # AUB_C = authorized backend connectors (w/o in-mem connectors) that use a secure connection /
    #         backend connectors (w/o in-mem connectors)
    # AEI_A = backend connectors authorized (w/o in-mem connectors) with a secure method or that use a
    #         secure connection / backend connectors (w/o in-mem connectors)

    for detector in detectors:
        backend_authorization_values[detector.name]["AUB"] = \
            detector.calculate_authorized_backend_connectors_ratio()
        backend_authorization_values[detector.name]["AUB_T"] = \
            detector.calculate_backend_connectors_authorized_with_authorization_tokens_ratio()
        backend_authorization_values[detector.name]["AUB_E"] = \
            detector.calculate_backend_connectors_authorized_with_encrypted_information_ratio()
        backend_authorization_values[detector.name]["AUB_P"] = \
            detector.calculate_backend_connectors_authorized_with_plaintext_ratio()
        backend_authorization_values[detector.name]["AUB_C"] = \
            detector.calculate_secure_connector_and_authorized_backend_connectors_ratio()
        backend_authorization_values[detector.name]["AUB_A"] = \
            detector.calculate_securely_or_secure_connector_authorized_backend_connectors_ratio()

    # authorization on paths from clients or uis to system services

    # AUC = authorized connectors on paths from clients or uis to system services /
    #       connectors on paths from clients or uis to system services
    # AUB_T = connectors on paths from clients or uis to system services
    #         authorized with authorization tokens /
    #         connectors on paths from clients or uis to system services
    # AUB_E = connectors on paths from clients or uis to system services authorized with
    #         encrypted authorization information /
    #         connectors on paths from clients or uis to system services
    # AUC_P = connectors on paths from clients or uis to system services authorized with Plaintext Information /
    #         connectors on paths from clients or uis to system services
    # AUC_C = authorized connectors that use a secure connection on paths from clients or uis to system services /
    #         connectors on paths from clients or uis to system services
    # AUC_A = connectors on paths from clients or uis to system services authorized with a secure method
    #         or that use a secure connection / connectors on paths from clients or uis to system services

    for detector in detectors:
        authorization_on_client_service_paths_values[detector.name]["AUC"] = \
            detector.calculate_authorized_connectors_on_client_service_paths_ratio()
        authorization_on_client_service_paths_values[detector.name]["AUC_T"] = \
            detector.calculate_connectors_authorized_with_authorization_tokens_on_client_service_paths_ratio()
        authorization_on_client_service_paths_values[detector.name]["AUC_E"] = \
            detector.calculate_connectors_authorized_with_encrypted_information_on_client_service_path_ratio()
        authorization_on_client_service_paths_values[detector.name]["AUC_P"] = \
            detector.calculate_connectors_authorized_with_plaintext_on_client_service_paths_ratio()
        authorization_on_client_service_paths_values[detector.name]["AUC_C"] = \
            detector.calculate_secure_connector_and_authorized_connectors_on_client_service_paths_ratio()
        authorization_on_client_service_paths_values[detector.name]["AUC_A"] = \
            detector.calculate_securely_or_secure_connector_authorized_connectors_on_client_service_paths_ratio()

    # basic traffic control with API gateways/bffs

    # GWP = client-system service paths that go through API Gateways or BFFs / all client-system service paths
    # FEP = client-system service paths that go through frontend services / all client-system service paths
    # GFP = client-system service paths that go through API Gateways, BFFs, or frontend services / all client-system service paths

    for detector in detectors:
        api_gateways_bffs_for_traffic_control_values[detector.name]["GWP"] = \
            detector.calculate_client_service_paths_with_gateway_or_bff_ratio()
        api_gateways_bffs_for_traffic_control_values[detector.name]["FEP"] = \
            detector.calculate_client_service_paths_with_frontend_service_ratio()
        api_gateways_bffs_for_traffic_control_values[detector.name]["GFP"] = \
            detector.calculate_client_service_paths_with_frontend_service_or_gw_or_bff_ratio()

    # OBSERVABILITY: monitoring & tracing

    # OSS = observed(system services) / all system services
    # OFA = observed(facades) / all facades
    # OSF = observed(system services + facades) / all system services and facade

    for detector in detectors:
        observability_values[detector.name]["OSS"] = \
            detector.calculate_observed_system_services_ratio()
        observability_values[detector.name]["OFA"] = \
            detector.calculate_observed_gws_bffs_and_frontends_ratio()
        observability_values[detector.name]["OSF"] = \
            detector.calculate_observed_services_and_gws_bffs_and_frontends_ratio()

    # SENSITIVE DATA

    # CMP = Component code without plaintext sensitive data / all components
    # CNP = Connector code without plaintext sensitive data / all connectors
    # CCP = Components and connectors code without plaintext sensitive data / all components + all connectors
    for detector in detectors:
        sensitive_data_values[detector.name]["CMP"] = \
            detector.calculate_component_code_without_plaintext_sensitive_data_ratio()
        sensitive_data_values[detector.name]["CNP"] = \
            detector.calculate_connector_code_without_plaintext_sensitive_data_ratio()
        sensitive_data_values[detector.name]["CCP"] = \
            detector.calculate_component_and_connector_code_without_plaintext_sensitive_data_ratio()
