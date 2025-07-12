from src.metamodels.component_metamodel import connectors_relation
from src.metamodels.microservice_components_metamodel import client, http, https, restful_http, service, facade, \
    in_memory_connector, ui, middleware_service, external_component, api_gateway, backends_for_frontends_gateway, \
    monitoring_component, tracing_component
from src.metamodels.security_annotations_metamodel import encrypted_communication, unencrypted_communication, \
    authentication_connector_type, no_authentication, \
    authentication_scope_none, protocol_based_secure_authentication, secure_authentication_token, \
    authentication_with_api_keys, \
    authentication_with_plaintext_credentials, authentication_scope_some_requests, authorization_connector_type, \
    authorization_scope_none, authorization_scope_some_requests, no_authorization, token_based_authorization, \
    authorization_with_plaintext_information, encrypted_authorization_information, authentication_not_required, \
    authorization_not_required, component_code_plaintext_sensitive_data, connector_code_plaintext_sensitive_data


def contains_stereotype_of_type(object, the_type):
    if len([s for s in object.stereotype_instances if s.is_classifier_of_type(the_type)]) > 0:
        return True
    return False


class DetectorResult(object):
    def __init__(self, reason, model_elements):
        self.reason = reason
        # TODO: model elements should deliver traceability to the source code from where they are extracted
        self.model_elements = model_elements

    def __str__(self):
        element_string = "[" + ", ".join([str(e) for e in self.model_elements]) + "]"
        return "Model Elements: " + element_string + ", Reason: " + str(self.reason)


class DetectorResults(object):
    def __init__(self):
        self.successful = []
        self.failed = []
        self.undefined = []

    def add_successful(self, reason, detected_on_model_elements):
        self.successful.append(DetectorResult(reason, detected_on_model_elements))

    def add_failed(self, reason, detected_on_model_elements):
        self.failed.append(DetectorResult(reason, detected_on_model_elements))

    def add_undefined(self, reason, detected_on_model_elements):
        self.undefined.append(DetectorResult(reason, detected_on_model_elements))

    def add_all(self, detector_results):
        self.successful.extend(detector_results.successful)
        self.failed.extend(detector_results.failed)
        self.undefined.extend(detector_results.undefined)

    @staticmethod
    def _get_result_strings(prepend, results):
        result_strings = ""
        for result in results:
            result_strings += prepend + ": " + str(result) + "\n"
        return result_strings

    def __str__(self):
        result_strings = self._get_result_strings("Successful", self.successful)
        if result_strings != "":
            result_strings += "\n"
        failed = self._get_result_strings("Failed", self.failed)
        result_strings += failed
        if failed != "":
            result_strings += "\n"
        undefined = self._get_result_strings("Undefined", self.undefined)
        result_strings += undefined
        if undefined != "":
            result_strings += "\n"
        return result_strings

    def is_model_element_in_successful(self, model_element):
        for e in self.successful:
            if model_element in e.model_elements:
                return True
        return False

    def is_model_element_in_undefined(self, model_element):
        for e in self.undefined:
            if model_element in e.model_elements:
                return True
        return False

    def is_model_element_in_failed(self, model_element):
        for e in self.failed:
            if model_element in e.model_elements:
                return True
        return False


class ComponentModelDetector(object):
    def __init__(self, model_bundle, name=None):
        self.name = name
        self._model_bundle = model_bundle
        self._all_connectors = None
        self._all_distributed_connectors = None
        self._compute_all_connectors_on_elements()
        self._client_connectors = None
        self._compute_all_client_connectors()
        self._ui_connectors = None
        self._compute_all_ui_connectors()
        self._backend_connectors = [ic for ic in self._all_connectors if
                                    (ic not in self._client_connectors and ic not in self._ui_connectors)]
        self._distributed_backend_connectors = \
            self._get_connectors_without_in_mem_connectors(self._backend_connectors)
        self._secure_connectors = None
        self._secure_client_connectors = None
        self._secure_ui_connectors = None
        self._secure_backend_connectors = None
        self._paths_from_services_to_clients = None
        self._csrf_protected_paths_from_services_to_clients = None
        self._non_authenticated_client_to_service_connections = None
        self._non_securely_authenticated_client_to_service_connections = None

        self._all_paths_from_clients_or_uis_to_system_services = None
        self._connectors_on_client_service_paths = None
        self._paths_from_clients_or_uis_to_system_services_without_facade = None

        self._client_service_paths_with_gateway_or_bff = None
        self._client_service_paths_with_frontend_service_or_gw_or_bff = None
        self._client_service_paths_with_frontend_service = None

        self._authenticated_backend_connectors = None
        self._backend_connectors_securely_authenticated = None
        self._backend_connectors_authenticated_with_api_keys = None
        self._backend_connectors_authenticated_with_plaintext = None
        self._secure_connector_and_authenticated_backend_connectors = None
        self._securely_or_secure_connector_authenticated_backend_connectors = None

        self._authenticated_connectors_on_client_service_paths = None
        self._securely_authenticated_connectors_on_client_service_paths = None
        self._connectors_authenticated_with_api_keys_on_client_service_paths = None
        self._connectors_authenticated_with_plaintext_on_client_service_paths = None
        self._secure_connector_and_authenticated_connectors_on_client_service_paths = None
        self._securely_or_secure_connector_authenticated_connectors_on_client_service_paths = None

        self._authorized_backend_connectors = None
        self._backend_connectors_authorized_with_authorization_tokens = None
        self._backend_connectors_authorized_with_encrypted_information = None
        self._backend_connectors_authorized_with_plaintext = None
        self._secure_connector_and_authorized_backend_connectors = None
        self._securely_or_secure_connector_authorized_backend_connectors = None

        self._authorized_connectors_on_client_service_paths = None
        self._connectors_authorized_with_authorization_tokens_on_client_service_paths = None
        self._connectors_authorized_with_encrypted_information_on_client_service_paths = None
        self._connectors_authorized_with_plaintext_on_client_service_paths = None
        self._secure_connector_and_authorized_connectors_on_client_service_paths = None
        self._securely_or_secure_connector_authorized_connectors_on_client_service_paths = None

        self._monitoring_and_tracing_components = None
        self._all_system_services = None
        self._all_gws_bffs_and_frontends = None

        self._observed_system_services = None
        self._observed_gws_bffs_and_frontends = None
        self._observed_services_gws_bffs_and_frontends = None

        self._component_code_without_plaintext_sensitive_data = None
        self._connector_code_without_plaintext_sensitive_data = None
        self._component_or_connector_code_without_plaintext_sensitive_data = None

    # SECURE CONNECTIONS

    def _compute_all_connectors_on_elements(self):
        if self._all_connectors is None:
            self._all_connectors = []
            for element in self._model_bundle.elements:
                for connector in element.get_links_for_association(connectors_relation):
                    if connector not in self._all_connectors:
                        self._all_connectors.append(connector)
        self._all_distributed_connectors = self._get_connectors_without_in_mem_connectors(self._all_connectors)

    def _compute_all_client_connectors(self):
        if self._all_distributed_connectors is None:
            self._compute_all_connectors_on_elements(self)
        if self._client_connectors is None:
            self._client_connectors = []
            for c in self._all_distributed_connectors:
                if contains_stereotype_of_type(c.source, client):
                    self._client_connectors.append(c)
                # if links are coming in from a UI into the system, they are also clients in the UI, but not if they
                # connect to another UI
                elif contains_stereotype_of_type(c.source, ui) and not contains_stereotype_of_type(c.target, ui):
                    self._client_connectors.append(c)

    def _compute_all_ui_connectors(self):
        if self._all_distributed_connectors is None:
            self._compute_all_connectors_on_elements(self)
        if self._ui_connectors is None:
            self._ui_connectors = []
            for c in self._all_distributed_connectors:
                if contains_stereotype_of_type(c.target, ui):
                    self._ui_connectors.append(c)

    @staticmethod
    def _get_connectors_without_in_mem_connectors(connectors):
        result = []
        for c in connectors:
            if not contains_stereotype_of_type(c, in_memory_connector):
                result.append(c)
        return result

    @staticmethod
    def _get_connectors_without_in_connectors_with_external_targets(connectors):
        result = []
        for c in connectors:
            if not contains_stereotype_of_type(c.target, external_component):
                result.append(c)
        return result

    def _detect_secure_connectors(self, connectors):
        # in memory connectors do not need to be encrypted/secured
        connectors_without_in_mem_connectors = self._get_connectors_without_in_mem_connectors(connectors)

        results = DetectorResults()
        for connector in connectors_without_in_mem_connectors:
            if (contains_stereotype_of_type(connector, http) or contains_stereotype_of_type(connector, https) or
                    contains_stereotype_of_type(connector, restful_http)):
                if contains_stereotype_of_type(connector, http):
                    results.add_failed("HTTP-based connector uses unencrypted HTTP", [connector])
                elif contains_stereotype_of_type(connector, https):
                    results.add_successful("HTTP-based connector uses encrypted HTTPS", [connector])
                else:
                    results.add_undefined("HTTP-based connector not designated as either encrypted or unencrypted HTTP",
                                          [connector])
            elif contains_stereotype_of_type(connector, encrypted_communication):
                results.add_successful("Encrypted connector used", [connector])
            elif contains_stereotype_of_type(connector, unencrypted_communication):
                results.add_failed("Unencrypted connector used", [connector])
            else:
                results.add_undefined("Connector encryption status unclear", [connector])
        return results

    def detect_all_secure_connectors(self):
        if self._secure_connectors is None:
            self._secure_connectors = self._detect_secure_connectors(self._all_distributed_connectors)
        return self._secure_connectors

    def calculate_secure_connector_ratio(self):
        if len(self._all_distributed_connectors) == 0:
            return None
        return len(self.detect_all_secure_connectors().successful) / len(self._all_distributed_connectors)

    def detect_secure_client_connectors(self):
        if self._secure_client_connectors is None:
            self._secure_client_connectors = self._detect_secure_connectors(self._client_connectors)
        return self._secure_client_connectors

    def calculate_secure_client_connector_ratio(self):
        if len(self._client_connectors) == 0:
            return None
        return len(self.detect_secure_client_connectors().successful) / len(self._client_connectors)

    def detect_secure_ui_connectors(self):
        if self._secure_ui_connectors is None:
            self._secure_ui_connectors = self._detect_secure_connectors(self._ui_connectors)
        return self._secure_ui_connectors

    def calculate_secure_ui_connector_ratio(self):
        if len(self._ui_connectors) == 0:
            return None
        return len(self.detect_secure_ui_connectors().successful) / len(self._ui_connectors)

    def detect_secure_backend_connectors(self):
        if self._secure_backend_connectors is None:
            self._secure_backend_connectors = self._detect_secure_connectors(self._distributed_backend_connectors)
        return self._secure_backend_connectors

    def calculate_secure_backend_connector_ratio(self):
        if len(self._distributed_backend_connectors) == 0:
            return None
        return len(self.detect_secure_backend_connectors().successful) / len(self._distributed_backend_connectors)

    def detect_secure_external_client_ui_connectors(self):
        result = DetectorResults()
        result.add_all(self.detect_secure_client_connectors())
        result.add_all(self.detect_secure_ui_connectors())
        return result

    def calculate_secure_external_client_ui_connector_ratio(self):
        external_connectors = self._client_connectors + self._ui_connectors
        if len(external_connectors) == 0:
            return None
        return len(self.detect_secure_external_client_ui_connectors().successful) / len(external_connectors)

    # Client / UI - Service Paths

    def _get_all_paths_between_nodes_recursive(self, source, target, visited, path):
        paths = []
        visited = visited.copy()
        visited.append(source)
        for connector in source.get_links_for_association(connectors_relation):
            next_node = connector.get_opposite_object(source)
            if next_node not in visited:
                if next_node == target:
                    paths.append(path + [next_node])
                else:
                    paths.extend(
                        self._get_all_paths_between_nodes_recursive(next_node, target, visited, path + [next_node]))
        return paths

    def _get_all_paths_between_nodes(self, source, target):
        visited = list()
        paths = self._get_all_paths_between_nodes_recursive(source, target, visited, [source])
        return paths

    @staticmethod
    def _is_system_service(component):
        return (contains_stereotype_of_type(component, service) and
                not contains_stereotype_of_type(component, external_component) and
                not contains_stereotype_of_type(component, middleware_service) and
                not contains_stereotype_of_type(component, facade))

    @staticmethod
    def _is_client_or_ui(component):
        return contains_stereotype_of_type(component, client) or contains_stereotype_of_type(component, ui)

    # checks that the paths are well-formed in the sense that paths first contain clients, then maybe facades,
    # and then services, but not e.g. client-facade-client-facade-service, or client-service-facade-service
    def _is_path_order_well_formed(self, path):
        facade_found = False
        service_found = False
        for c in path:
            if service_found and contains_stereotype_of_type(c.class_object_class, facade):
                return False
            if (facade_found or service_found) and self._is_client_or_ui(c.class_object_class):
                return False
            if contains_stereotype_of_type(c.class_object_class, facade):
                facade_found = True
            if self._is_system_service(c.class_object_class):
                service_found = True
        return True

    def _is_client_or_ui_located_only_before_services_facades(self, path):
        client_or_ui_found = False
        for c in path:
            if self._is_system_service(c.class_object_class):
                client_or_ui_found = True
                continue
            if client_or_ui_found and contains_stereotype_of_type(c.class_object_class, facade):
                return False
        return True

    def _get_all_paths_from_clients_or_uis_to_system_services(self):
        if self._all_paths_from_clients_or_uis_to_system_services is None:
            clients = []
            services = []
            for element in self._model_bundle.elements:
                element_class = element.class_object_class
                if self._is_client_or_ui(element_class):
                    clients.append(element)
                if self._is_system_service(element_class):
                    services.append(element)
            paths = []
            for s in services:
                for c in clients:
                    for new_path in self._get_all_paths_between_nodes(c, s):
                        # we only want the paths from clients directly to services (maybe via other services or facades)
                        if len([c for c in new_path if not (
                                self._is_client_or_ui(c.class_object_class) or
                                contains_stereotype_of_type(c.class_object_class, facade) or
                                self._is_system_service(c.class_object_class))]) == 0:
                            # but we do not want to add paths in which clients are placed after facades or services,
                            # or facades after services
                            if self._is_path_order_well_formed(new_path):
                                paths.append(new_path)
            self._all_paths_from_clients_or_uis_to_system_services = paths
        return self._all_paths_from_clients_or_uis_to_system_services

    def _get_all_paths_from_services_to_clients_without_facade(self):
        if self._paths_from_clients_or_uis_to_system_services_without_facade is None:
            paths_without_facade = []
            for path in self._get_all_paths_from_clients_or_uis_to_system_services():
                if len([c for c in path if facade in c.class_object_class.stereotype_instances]) == 0:
                    paths_without_facade.append(path)
            self._paths_from_clients_or_uis_to_system_services_without_facade = paths_without_facade
        return self._paths_from_clients_or_uis_to_system_services_without_facade

    def _get_connectors_on_client_service_paths(self):
        if self._connectors_on_client_service_paths is None:
            connectors = set()
            for path in self._get_all_paths_from_clients_or_uis_to_system_services():
                i = 0
                while i < len(path) - 1:
                    links = path[i].get_links_for_association(connectors_relation)
                    for link in links:
                        # select the component / connector links that are connecting the elements on the path only
                        if ((link.source == path[i].class_object_class and
                             link.target == path[i + 1].class_object_class) or
                                (link.source == path[i + 1].class_object_class and
                                 link.target == path[i].class_object_class)):
                            if contains_stereotype_of_type(link.target, service) and \
                                    not contains_stereotype_of_type(link.target, facade):
                                connectors.add(link)
                    i += 1
            self._connectors_on_client_service_paths = self._get_connectors_without_in_connectors_with_external_targets(
                self._get_connectors_without_in_mem_connectors(list(connectors)))
        return self._connectors_on_client_service_paths

    # BACKEND AUTHENTICATION

    @staticmethod
    def _is_authentication_not_required(connector):
        return contains_stereotype_of_type(connector, authentication_not_required)

    def _get_connectors_that_require_authentication(self, connectors):
        return [c for c in connectors if not self._is_authentication_not_required(c)]

    def _detect_authenticated_connectors(self, connectors):
        # in memory connectors do not need to be authenticated
        connectors_without_in_mem_connectors = self._get_connectors_without_in_mem_connectors(connectors)

        results = DetectorResults()
        for connector in connectors_without_in_mem_connectors:
            if contains_stereotype_of_type(connector, authentication_connector_type):
                if self._is_authentication_not_required(connector):
                    # we treat connectors that do not require authentication as though they are not part of the model
                    # (neither positive nor negative impact)
                    pass
                elif contains_stereotype_of_type(connector, authentication_scope_none):
                    results.add_failed("Authenticated connector used, but authentication scope 'none' is used",
                                       [connector])
                elif contains_stereotype_of_type(connector, authentication_scope_some_requests):
                    results.add_failed("Authenticated connector used, but authentication scope 'some' is used",
                                       [connector])
                else:
                    results.add_successful("Fully authenticated connector used", [connector])
            elif contains_stereotype_of_type(connector, no_authentication):
                results.add_failed("No Authentication connector used", [connector])
            else:
                results.add_undefined("Authentication status unclear", [connector])
        return results

    def detect_authenticated_backend_connectors(self):
        if self._authenticated_backend_connectors is None:
            self._authenticated_backend_connectors = self._detect_authenticated_connectors(
                self._distributed_backend_connectors)
        return self._authenticated_backend_connectors

    def calculate_authenticated_backend_connectors_ratio(self):
        if len(self._distributed_backend_connectors) == 0:
            return None
        return len(self.detect_authenticated_backend_connectors().successful) / len(
            self._get_connectors_that_require_authentication(self._distributed_backend_connectors))

    def _detect_connector_detector_results_with_property(self, detector_results, desired_property_function,
                                                         property_description):
        new_detector_results = DetectorResults()
        new_detector_results.failed.extend(detector_results.failed)
        new_detector_results.undefined.extend(detector_results.undefined)
        for detector_result in detector_results.successful:
            connector = detector_result.model_elements[0]
            reason = detector_result.reason
            if desired_property_function(connector):
                new_detector_results.add_successful(reason + " and is " + property_description, [connector])
            else:
                new_detector_results.add_failed(reason + " but is not " + property_description, [connector])
        return new_detector_results

    @staticmethod
    def _is_securely_authenticated(connector):
        return (contains_stereotype_of_type(connector, protocol_based_secure_authentication) or
                contains_stereotype_of_type(connector, secure_authentication_token))

    def detect_securely_authenticated_backend_connectors(self):
        if self._backend_connectors_securely_authenticated is None:
            detector_results = self.detect_authenticated_backend_connectors()
            self._backend_connectors_securely_authenticated = \
                self._detect_connector_detector_results_with_property(detector_results,
                                                                      self._is_securely_authenticated,
                                                                      "securely authenticated")
        return self._backend_connectors_securely_authenticated

    def calculate_securely_authenticated_backend_connectors_ratio(self):
        if len(self._distributed_backend_connectors) == 0:
            return None
        return (len(self.detect_securely_authenticated_backend_connectors().successful) /
                len(self._get_connectors_that_require_authentication(self._distributed_backend_connectors)))

    @staticmethod
    def _is_authenticated_with_api_keys(connector):
        return contains_stereotype_of_type(connector, authentication_with_api_keys)

    def detect_backend_connectors_authenticated_with_api_keys(self):
        if self._backend_connectors_authenticated_with_api_keys is None:
            detector_results = self.detect_authenticated_backend_connectors()
            self._backend_connectors_authenticated_with_api_keys = \
                self._detect_connector_detector_results_with_property(detector_results,
                                                                      self._is_authenticated_with_api_keys,
                                                                      "authenticated with API keys")
        return self._backend_connectors_authenticated_with_api_keys

    def calculate_backend_connectors_authenticated_with_api_keys_ratio(self):
        if len(self._distributed_backend_connectors) == 0:
            return None
        return (len(self.detect_backend_connectors_authenticated_with_api_keys().successful) /
                len(self._get_connectors_that_require_authentication(self._distributed_backend_connectors)))

    @staticmethod
    def _is_authenticated_with_plaintext(connector):
        return contains_stereotype_of_type(connector, authentication_with_plaintext_credentials)

    def detect_backend_connectors_authenticated_with_plaintext(self):
        if self._backend_connectors_authenticated_with_plaintext is None:
            detector_results = self.detect_authenticated_backend_connectors()
            self._backend_connectors_authenticated_with_plaintext = \
                self._detect_connector_detector_results_with_property(detector_results,
                                                                      self._is_authenticated_with_plaintext,
                                                                      "authenticated with plaintext credentials")
        return self._backend_connectors_authenticated_with_plaintext

    def calculate_backend_connectors_authenticated_with_plaintext_ratio(self):
        if len(self._distributed_backend_connectors) == 0:
            return None
        return (len(self.detect_backend_connectors_authenticated_with_plaintext().successful) /
                len(self._get_connectors_that_require_authentication(self._distributed_backend_connectors)))

    def detect_secure_connector_and_authenticated_backend_connectors(self):
        if self._secure_connector_and_authenticated_backend_connectors is None:
            authenticated_connectors = self.detect_authenticated_backend_connectors()
            secure_connectors = self.detect_secure_backend_connectors()
            distributed_backend_connectors = self._distributed_backend_connectors

            results = self._secure_connector_and_authenticated_backend_connectors = DetectorResults()

            for c in distributed_backend_connectors:
                if self._is_authentication_not_required(c):
                    pass
                elif (secure_connectors.is_model_element_in_successful(c) and
                      authenticated_connectors.is_model_element_in_successful(c)):
                    results.add_successful("is authenticated and has secure connection", [c])
                elif (secure_connectors.is_model_element_in_undefined(c) and
                      authenticated_connectors.is_model_element_in_undefined(c)):
                    results.add_undefined("undefined secure connection and authentication status", [c])
                else:
                    results.add_failed("either is not fully authenticated and has no secure connection", [c])
        return self._secure_connector_and_authenticated_backend_connectors

    def calculate_secure_connector_and_authenticated_backend_connectors_ratio(self):
        if len(self._distributed_backend_connectors) == 0:
            return None
        return (len(self.detect_secure_connector_and_authenticated_backend_connectors().successful) /
                len(self._get_connectors_that_require_authentication(self._distributed_backend_connectors)))

    def detect_securely_or_secure_connector_authenticated_backend_connectors(self):
        if self._securely_or_secure_connector_authenticated_backend_connectors is None:
            securely_authenticated = self.detect_securely_authenticated_backend_connectors()
            # api_key_authenticated = self.detect_backend_connectors_authenticated_with_api_keys()
            secure_connector_authenticated = self.detect_secure_connector_and_authenticated_backend_connectors()
            distributed_backend_connectors = self._distributed_backend_connectors

            results = self._securely_or_secure_connector_authenticated_backend_connectors = DetectorResults()

            for c in distributed_backend_connectors:
                if self._is_authentication_not_required(c):
                    pass
                elif (securely_authenticated.is_model_element_in_successful(c) or
                      # api_key_authenticated.is_model_element_in_successful(c) or
                      secure_connector_authenticated.is_model_element_in_successful(c)):
                    results.add_successful("is securely authenticated or " +
                                           # with API key, or " +
                                           "is authenticated and has secure connection", [c])
                elif (securely_authenticated.is_model_element_in_undefined(c) and
                      # api_key_authenticated.is_model_element_in_undefined(c) and
                      secure_connector_authenticated.is_model_element_in_undefined(c)):
                    results.add_undefined("undefined secure connection and authentication status", [c])
                else:
                    results.add_failed("either is not authenticated securely or " +
                                       # with API key, or " +
                                       "has no secure connection", [c])
        return self._securely_or_secure_connector_authenticated_backend_connectors

    def calculate_securely_or_secure_connector_authenticated_backend_connectors_ratio(self):
        if len(self._distributed_backend_connectors) == 0:
            return None
        return (len(self.detect_securely_or_secure_connector_authenticated_backend_connectors().successful) /
                len(self._get_connectors_that_require_authentication(self._distributed_backend_connectors)))

    # AUTHENTICATION ON CLIENT (OR UI) to SERVICE PATHS

    def detect_authenticated_connectors_on_client_service_paths(self):
        if self._authenticated_connectors_on_client_service_paths is None:
            self._authenticated_connectors_on_client_service_paths = \
                self._detect_authenticated_connectors(
                    self._get_connectors_on_client_service_paths())
        return self._authenticated_connectors_on_client_service_paths

    def calculate_authenticated_connectors_on_client_service_paths_ratio(self):
        detector_results = self.detect_authenticated_connectors_on_client_service_paths()
        if len(self._get_connectors_on_client_service_paths()) == 0:
            return None
        return (len(detector_results.successful) /
                len(self._get_connectors_that_require_authentication(self._get_connectors_on_client_service_paths())))

    def detect_securely_authenticated_connectors_on_client_service_paths(self):
        if self._securely_authenticated_connectors_on_client_service_paths is None:
            detector_results = self.detect_authenticated_connectors_on_client_service_paths()
            self._securely_authenticated_connectors_on_client_service_paths = \
                self._detect_connector_detector_results_with_property(detector_results,
                                                                      self._is_securely_authenticated,
                                                                      "securely authenticated")
        return self._securely_authenticated_connectors_on_client_service_paths

    def calculate_securely_authenticated_connectors_on_client_service_paths_ratio(self):
        detector_results = self.detect_securely_authenticated_connectors_on_client_service_paths()
        if len(self._get_connectors_on_client_service_paths()) == 0:
            return None
        return (len(detector_results.successful) /
                len(self._get_connectors_that_require_authentication(self._get_connectors_on_client_service_paths())))

    def detect_connectors_authenticated_with_api_keys_on_client_service_paths(
            self):
        if self._connectors_authenticated_with_api_keys_on_client_service_paths is None:
            detector_results = self.detect_authenticated_connectors_on_client_service_paths()
            self._connectors_authenticated_with_api_keys_on_client_service_paths = \
                self._detect_connector_detector_results_with_property(detector_results,
                                                                      self._is_authenticated_with_api_keys,
                                                                      "authenticated with API keys")
        return self._connectors_authenticated_with_api_keys_on_client_service_paths

    def calculate_connectors_authenticated_with_api_keys_on_client_service_paths_ratio(
            self):
        detector_results = self.detect_connectors_authenticated_with_api_keys_on_client_service_paths()
        if len(self._get_connectors_on_client_service_paths()) == 0:
            return None
        return (len(detector_results.successful) /
                len(self._get_connectors_that_require_authentication(self._get_connectors_on_client_service_paths())))

    def detect_connectors_authenticated_with_plaintext_on_client_service_paths(
            self):
        if self._connectors_authenticated_with_plaintext_on_client_service_paths is None:
            detector_results = self.detect_authenticated_connectors_on_client_service_paths()
            self._connectors_authenticated_with_plaintext_on_client_service_paths = \
                self._detect_connector_detector_results_with_property(detector_results,
                                                                      self._is_authenticated_with_plaintext,
                                                                      "authenticated with plaintext credentials")
        return self._connectors_authenticated_with_plaintext_on_client_service_paths

    def calculate_connectors_authenticated_with_plaintext_on_client_service_paths_ratio(
            self):
        detector_results = self.detect_connectors_authenticated_with_plaintext_on_client_service_paths()
        if len(self._get_connectors_on_client_service_paths()) == 0:
            return None
        return (len(detector_results.successful) /
                len(self._get_connectors_that_require_authentication(self._get_connectors_on_client_service_paths())))

    def detect_secure_connector_and_authenticated_connectors_on_client_service_paths(self):
        if self._secure_connector_and_authenticated_connectors_on_client_service_paths is None:
            authenticated_connectors = self.detect_authenticated_connectors_on_client_service_paths()
            secure_connectors = self._detect_secure_connectors(self._get_connectors_on_client_service_paths())

            results = self._secure_connector_and_authenticated_connectors_on_client_service_paths = DetectorResults()

            for c in self._get_connectors_on_client_service_paths():
                if (secure_connectors.is_model_element_in_successful(c) and
                        authenticated_connectors.is_model_element_in_successful(c)):
                    results.add_successful("is authenticated and has secure connection", [c])
                elif (secure_connectors.is_model_element_in_undefined(c) and
                      authenticated_connectors.is_model_element_in_undefined(c)):
                    results.add_undefined("undefined secure connection and authentication status", [c])
                else:
                    results.add_failed("either is not fully authenticated and has no secure connection", [c])
        return self._secure_connector_and_authenticated_connectors_on_client_service_paths

    def calculate_secure_connector_and_authenticated_connectors_on_client_service_paths_ratio(self):
        detector_results = \
            self.detect_secure_connector_and_authenticated_connectors_on_client_service_paths()
        if len(self._get_connectors_on_client_service_paths()) == 0:
            return None
        return (len(detector_results.successful) /
                len(self._get_connectors_that_require_authentication(self._get_connectors_on_client_service_paths())))

    def detect_securely_or_secure_connector_authenticated_connectors_on_client_service_paths(self):
        if self._securely_or_secure_connector_authenticated_connectors_on_client_service_paths is None:
            securely_authenticated = self.detect_securely_authenticated_connectors_on_client_service_paths()
            api_key_authenticated = self.detect_connectors_authenticated_with_api_keys_on_client_service_paths()
            secure_connector_authenticated = \
                self.detect_secure_connector_and_authenticated_connectors_on_client_service_paths()

            results = self._securely_or_secure_connector_authenticated_connectors_on_client_service_paths \
                = DetectorResults()

            for c in self._get_connectors_on_client_service_paths():
                if (securely_authenticated.is_model_element_in_successful(c) or
                        api_key_authenticated.is_model_element_in_successful(c) or
                        secure_connector_authenticated.is_model_element_in_successful(c)):
                    results.add_successful("is securely authenticated or with API key, " +
                                           "or is authenticated and has secure connection", [c])
                elif (securely_authenticated.is_model_element_in_undefined(c) and
                      api_key_authenticated.is_model_element_in_undefined(c) and
                      secure_connector_authenticated.is_model_element_in_undefined(c)):
                    results.add_undefined("undefined secure connection and authentication status", [c])
                else:
                    results.add_failed("either is not authenticated securely or with API key, " +
                                       "or has no secure connection", [c])
        return self._securely_or_secure_connector_authenticated_connectors_on_client_service_paths

    def calculate_securely_or_secure_connector_authenticated_connectors_on_client_service_paths_ratio(self):
        detector_results = \
            self.detect_securely_or_secure_connector_authenticated_connectors_on_client_service_paths()
        if len(self._get_connectors_on_client_service_paths()) == 0:
            return None
        return (len(detector_results.successful) /
                len(self._get_connectors_that_require_authentication(self._get_connectors_on_client_service_paths())))

    # BACKEND AUTHORIZATION

    @staticmethod
    def _is_authorization_not_required(connector):
        return contains_stereotype_of_type(connector, authorization_not_required)

    def _get_connectors_that_require_authorization(self, connectors):
        return [c for c in connectors if not self._is_authorization_not_required(c)]

    def _detect_authorized_connectors(self, connectors):
        # in memory connectors do not need to be authorized
        connectors_without_in_mem_connectors = self._get_connectors_without_in_mem_connectors(connectors)
        results = DetectorResults()
        for connector in connectors_without_in_mem_connectors:
            if self._is_authorization_not_required(connector):
                # we treat connectors that do not require authorization as though they are not part of the model
                # (neither positive nor negative impact)
                pass
            elif contains_stereotype_of_type(connector, authorization_connector_type):
                if contains_stereotype_of_type(connector, authorization_scope_none):
                    results.add_failed("Authorization connector used, but authorization scope 'none' is used",
                                       [connector])
                elif contains_stereotype_of_type(connector, authorization_scope_some_requests):
                    results.add_failed("Authorization connector used, but authorization scope 'some' is used",
                                       [connector])
                else:
                    results.add_successful("Fully authorized connector used", [connector])
            elif contains_stereotype_of_type(connector, no_authorization):
                results.add_failed("No Authorization connector used", [connector])
            else:
                results.add_undefined("Authorization status unclear", [connector])
        return results

    def detect_authorized_backend_connectors(self):
        if self._authorized_backend_connectors is None:
            self._authorized_backend_connectors = self._detect_authorized_connectors(
                self._distributed_backend_connectors)
        return self._authorized_backend_connectors

    def calculate_authorized_backend_connectors_ratio(self):
        if len(self._distributed_backend_connectors) == 0:
            return None
        return (len(self.detect_authorized_backend_connectors().successful) /
                len(self._get_connectors_that_require_authorization(self._distributed_backend_connectors)))

    @staticmethod
    def _is_authorized_with_authorization_tokens(connector):
        return contains_stereotype_of_type(connector, token_based_authorization)

    @staticmethod
    def _is_authorized_with_encrypted_information(connector):
        return contains_stereotype_of_type(connector, encrypted_authorization_information)

    def detect_backend_connectors_authorized_with_authorization_tokens(self):
        if self._backend_connectors_authorized_with_authorization_tokens is None:
            detector_results = self.detect_authorized_backend_connectors()
            self._backend_connectors_authorized_with_authorization_tokens = \
                self._detect_connector_detector_results_with_property(detector_results,
                                                                      self._is_authorized_with_authorization_tokens,
                                                                      "authorized with authorization tokens")
        return self._backend_connectors_authorized_with_authorization_tokens

    def calculate_backend_connectors_authorized_with_authorization_tokens_ratio(self):
        if len(self._distributed_backend_connectors) == 0:
            return None
        return (len(self.detect_backend_connectors_authorized_with_authorization_tokens().successful) /
                len(self._get_connectors_that_require_authorization(self._distributed_backend_connectors)))

    def detect_backend_connectors_authorized_with_encrypted_information(self):
        if self._backend_connectors_authorized_with_encrypted_information is None:
            detector_results = self.detect_authorized_backend_connectors()
            self._backend_connectors_authorized_with_encrypted_information = \
                self._detect_connector_detector_results_with_property(detector_results,
                                                                      self._is_authorized_with_encrypted_information,
                                                                      "is authorized with encrypted information")
        return self._backend_connectors_authorized_with_encrypted_information

    def calculate_backend_connectors_authorized_with_encrypted_information_ratio(self):
        if len(self._distributed_backend_connectors) == 0:
            return None
        return (len(self.detect_backend_connectors_authorized_with_encrypted_information().successful) /
                len(self._get_connectors_that_require_authorization(self._distributed_backend_connectors)))

    @staticmethod
    def _is_authorized_with_plaintext(connector):
        return contains_stereotype_of_type(connector, authorization_with_plaintext_information)

    def detect_backend_connectors_authorized_with_plaintext(self):
        if self._backend_connectors_authorized_with_plaintext is None:
            detector_results = self.detect_authorized_backend_connectors()
            self._backend_connectors_authorized_with_plaintext = \
                self._detect_connector_detector_results_with_property(detector_results,
                                                                      self._is_authorized_with_plaintext,
                                                                      "authorized with plaintext credentials")
        return self._backend_connectors_authorized_with_plaintext

    def calculate_backend_connectors_authorized_with_plaintext_ratio(self):
        if len(self._distributed_backend_connectors) == 0:
            return None
        return (len(self.detect_backend_connectors_authorized_with_plaintext().successful) /
                len(self._get_connectors_that_require_authorization(self._distributed_backend_connectors)))

    def detect_secure_connector_and_authorized_backend_connectors(self):
        if self._secure_connector_and_authorized_backend_connectors is None:
            authorized_connectors = self.detect_authorized_backend_connectors()
            secure_connectors = self.detect_secure_backend_connectors()
            distributed_backend_connectors = self._distributed_backend_connectors

            results = self._secure_connector_and_authorized_backend_connectors = DetectorResults()

            for c in distributed_backend_connectors:
                if self._is_authorization_not_required(c):
                    pass
                elif (secure_connectors.is_model_element_in_successful(c) and
                      authorized_connectors.is_model_element_in_successful(c)):
                    results.add_successful("is authorized and has secure connection", [c])
                elif (secure_connectors.is_model_element_in_undefined(c) and
                      authorized_connectors.is_model_element_in_undefined(c)):
                    results.add_undefined("undefined secure connection and authorization status", [c])
                else:
                    results.add_failed("either is not fully authorized and has no secure connection", [c])
        return self._secure_connector_and_authorized_backend_connectors

    def calculate_secure_connector_and_authorized_backend_connectors_ratio(self):
        if len(self._distributed_backend_connectors) == 0:
            return None
        return (len(self.detect_secure_connector_and_authorized_backend_connectors().successful) /
                len(self._get_connectors_that_require_authorization(self._distributed_backend_connectors)))

    def detect_securely_or_secure_connector_authorized_backend_connectors(self):
        if self._securely_or_secure_connector_authorized_backend_connectors is None:
            authorized_with_tokens = self.detect_backend_connectors_authorized_with_authorization_tokens()
            authorized_with_encrypted_info = self.detect_backend_connectors_authorized_with_encrypted_information()
            secure_connector_authorized = self.detect_secure_connector_and_authorized_backend_connectors()
            distributed_backend_connectors = self._distributed_backend_connectors

            results = self._securely_or_secure_connector_authorized_backend_connectors = DetectorResults()

            for c in distributed_backend_connectors:
                if self._is_authorization_not_required(c):
                    pass
                elif (authorized_with_tokens.is_model_element_in_successful(c) or
                      authorized_with_encrypted_info.is_model_element_in_successful(c) or
                      secure_connector_authorized.is_model_element_in_successful(c)):
                    results.add_successful("is securely authorized or is authorized and has secure connection", [c])
                elif (authorized_with_tokens.is_model_element_in_undefined(c) and
                      authorized_with_encrypted_info.is_model_element_in_undefined(c) and
                      secure_connector_authorized.is_model_element_in_undefined(c)):
                    results.add_undefined("undefined secure connection and authorization status", [c])
                else:
                    results.add_failed("either is not authorized securely or has no secure connection", [c])
        return self._securely_or_secure_connector_authorized_backend_connectors

    def calculate_securely_or_secure_connector_authorized_backend_connectors_ratio(self):
        if len(self._distributed_backend_connectors) == 0:
            return None
        return (len(self.detect_securely_or_secure_connector_authorized_backend_connectors().successful) /
                len(self._get_connectors_that_require_authorization(self._distributed_backend_connectors)))

    # AUTHORIZATION ON CLIENT (OR UI) to SERVICE PATHS

    def detect_authorized_connectors_on_client_service_paths(self):
        if self._authorized_connectors_on_client_service_paths is None:
            self._authorized_connectors_on_client_service_paths = \
                self._detect_authorized_connectors(
                    self._get_connectors_on_client_service_paths())
        return self._authorized_connectors_on_client_service_paths

    def calculate_authorized_connectors_on_client_service_paths_ratio(self):
        detector_results = self.detect_authorized_connectors_on_client_service_paths()
        if len(self._get_connectors_on_client_service_paths()) == 0:
            return None
        return len(detector_results.successful) / \
               len(self._get_connectors_that_require_authorization(self._get_connectors_on_client_service_paths()))

    def detect_connectors_authorized_with_authorization_tokens_on_client_service_paths(self):
        if self._connectors_authorized_with_authorization_tokens_on_client_service_paths is None:
            detector_results = self.detect_authorized_connectors_on_client_service_paths()
            self._connectors_authorized_with_authorization_tokens_on_client_service_paths = \
                self._detect_connector_detector_results_with_property(detector_results,
                                                                      self._is_authorized_with_authorization_tokens,
                                                                      "authorized with authorization tokens")
        return self._connectors_authorized_with_authorization_tokens_on_client_service_paths

    def calculate_connectors_authorized_with_authorization_tokens_on_client_service_paths_ratio(self):
        detector_results = self.detect_connectors_authorized_with_authorization_tokens_on_client_service_paths()
        if len(self._get_connectors_on_client_service_paths()) == 0:
            return None
        return len(detector_results.successful) / \
               len(self._get_connectors_that_require_authorization(self._get_connectors_on_client_service_paths()))

    def detect_connectors_authorized_with_encrypted_information_on_client_service_paths(self):
        if self._connectors_authorized_with_encrypted_information_on_client_service_paths is None:
            detector_results = self.detect_authorized_connectors_on_client_service_paths()
            self._connectors_authorized_with_encrypted_information_on_client_service_paths = \
                self._detect_connector_detector_results_with_property(
                    detector_results,
                    self._is_authorized_with_encrypted_information,
                    "authorized with encrypted authorization information")
        return self._connectors_authorized_with_encrypted_information_on_client_service_paths

    def calculate_connectors_authorized_with_encrypted_information_on_client_service_path_ratio(self):
        detector_results = self.detect_connectors_authorized_with_encrypted_information_on_client_service_paths()
        if len(self._get_connectors_on_client_service_paths()) == 0:
            return None
        return len(detector_results.successful) / \
               len(self._get_connectors_that_require_authorization(self._get_connectors_on_client_service_paths()))

    def detect_connectors_authorized_with_plaintext_on_client_service_paths(
            self):
        if self._connectors_authorized_with_plaintext_on_client_service_paths is None:
            detector_results = self.detect_authorized_connectors_on_client_service_paths()
            self._connectors_authorized_with_plaintext_on_client_service_paths = \
                self._detect_connector_detector_results_with_property(detector_results,
                                                                      self._is_authorized_with_plaintext,
                                                                      "authorized with plaintext credentials")
        return self._connectors_authorized_with_plaintext_on_client_service_paths

    def calculate_connectors_authorized_with_plaintext_on_client_service_paths_ratio(
            self):
        detector_results = self.detect_connectors_authorized_with_plaintext_on_client_service_paths()
        if len(self._get_connectors_on_client_service_paths()) == 0:
            return None
        return len(detector_results.successful) / \
               len(self._get_connectors_that_require_authorization(self._get_connectors_on_client_service_paths()))

    def detect_secure_connector_and_authorized_connectors_on_client_service_paths(self):
        if self._secure_connector_and_authorized_connectors_on_client_service_paths is None:
            authorized_connectors = self.detect_authorized_connectors_on_client_service_paths()
            secure_connectors = self._detect_secure_connectors(self._get_connectors_on_client_service_paths())

            results = self._secure_connector_and_authorized_connectors_on_client_service_paths = DetectorResults()

            for c in self._get_connectors_on_client_service_paths():
                if (secure_connectors.is_model_element_in_successful(c) and
                        authorized_connectors.is_model_element_in_successful(c)):
                    results.add_successful("is authorized and has secure connection", [c])
                elif (secure_connectors.is_model_element_in_undefined(c) and
                      authorized_connectors.is_model_element_in_undefined(c)):
                    results.add_undefined("undefined secure connection and authorization status", [c])
                else:
                    results.add_failed("either is not fully authorized and has no secure connection", [c])
        return self._secure_connector_and_authorized_connectors_on_client_service_paths

    def calculate_secure_connector_and_authorized_connectors_on_client_service_paths_ratio(self):
        detector_results = \
            self.detect_secure_connector_and_authorized_connectors_on_client_service_paths()
        if len(self._get_connectors_on_client_service_paths()) == 0:
            return None
        return (len(detector_results.successful) /
                len(self._get_connectors_that_require_authorization(self._get_connectors_on_client_service_paths())))

    def detect_securely_or_secure_connector_authorized_connectors_on_client_service_paths(self):
        if self._securely_or_secure_connector_authorized_connectors_on_client_service_paths is None:
            authorized_with_tokens = \
                self.detect_connectors_authorized_with_authorization_tokens_on_client_service_paths()
            authorized_with_encrypted_info = \
                self.detect_connectors_authorized_with_encrypted_information_on_client_service_paths()
            secure_connector_authorized = \
                self.detect_secure_connector_and_authorized_connectors_on_client_service_paths()

            results = self._securely_or_secure_connector_authorized_connectors_on_client_service_paths \
                = DetectorResults()

            for c in self._get_connectors_on_client_service_paths():
                if (authorized_with_tokens.is_model_element_in_successful(c) or
                        authorized_with_encrypted_info.is_model_element_in_successful(c) or
                        secure_connector_authorized.is_model_element_in_successful(c)):
                    results.add_successful("is securely authorized or is authorized and has secure connection", [c])
                elif (authorized_with_tokens.is_model_element_in_undefined(c) and
                      authorized_with_encrypted_info.is_model_element_in_undefined(c) and
                      secure_connector_authorized.is_model_element_in_undefined(c)):
                    results.add_undefined("undefined secure connection and authorizion status", [c])
                else:
                    results.add_failed("either is not authorized securely or has no secure connection", [c])
        return self._securely_or_secure_connector_authorized_connectors_on_client_service_paths

    def calculate_securely_or_secure_connector_authorized_connectors_on_client_service_paths_ratio(self):
        detector_results = \
            self.detect_securely_or_secure_connector_authorized_connectors_on_client_service_paths()
        if len(self._get_connectors_on_client_service_paths()) == 0:
            return None
        return (len(detector_results.successful) /
                len(self._get_connectors_that_require_authorization(self._get_connectors_on_client_service_paths())))

    #### BASIC TRAFFIC CONTROL - API GATEWAY, BFF, FACADE SERVICES ...

    @staticmethod
    def _is_api_gateway_or_bff(component):
        return (contains_stereotype_of_type(component, api_gateway) or
                contains_stereotype_of_type(component, backends_for_frontends_gateway))

    def _is_frontend_service(self, component):
        return (contains_stereotype_of_type(component, facade) and
                contains_stereotype_of_type(component, service) and not
                self._is_api_gateway_or_bff(component))

    def detect_client_service_paths_with_gateway_or_bff(self):
        if self._client_service_paths_with_gateway_or_bff is None:
            self._client_service_paths_with_gateway_or_bff = DetectorResults()
            for path in self._get_all_paths_from_clients_or_uis_to_system_services():
                if len([c for c in path if self._is_api_gateway_or_bff(c.class_object_class)]) > 0:
                    self._client_service_paths_with_gateway_or_bff.add_successful(
                        "API Gateway or BFF on client/ui - service path found", path)
                else:
                    self._client_service_paths_with_gateway_or_bff. \
                        add_failed("no API Gateway or BFF on client/ui - service path", path)
        return self._client_service_paths_with_gateway_or_bff

    def calculate_client_service_paths_with_gateway_or_bff_ratio(self):
        all_paths = self._get_all_paths_from_clients_or_uis_to_system_services()
        if len(all_paths) == 0:
            return None
        return len(self.detect_client_service_paths_with_gateway_or_bff().successful) / len(all_paths)

    def detect_client_service_paths_with_frontend_service(self):
        if self._client_service_paths_with_frontend_service is None:
            all_paths = self._get_all_paths_from_clients_or_uis_to_system_services()
            self._client_service_paths_with_frontend_service = DetectorResults()
            for path in all_paths:
                if len([c for c in path if self._is_frontend_service(c.class_object_class)]) > 0:
                    self._client_service_paths_with_frontend_service.add_successful(
                        "Frontend service on client/ui - service path found", path)
                else:
                    self._client_service_paths_with_frontend_service. \
                        add_failed("no frontend service on client/ui - service path", path)
        return self._client_service_paths_with_frontend_service

    def calculate_client_service_paths_with_frontend_service_ratio(self):
        all_paths = self._get_all_paths_from_clients_or_uis_to_system_services()
        if len(all_paths) == 0:
            return None
        return len(self.detect_client_service_paths_with_frontend_service().successful) / len(all_paths)

    def detect_client_service_paths_with_frontend_service_or_gw_or_bff(self):
        if self._client_service_paths_with_frontend_service_or_gw_or_bff is None:
            all_paths = self._get_all_paths_from_clients_or_uis_to_system_services()
            self._client_service_paths_with_frontend_service_or_gw_or_bff = DetectorResults()
            for path in all_paths:
                if len([c for c in path if (
                        self._is_frontend_service(c.class_object_class) or self._is_api_gateway_or_bff(
                    c.class_object_class))]) > 0:
                    self._client_service_paths_with_frontend_service_or_gw_or_bff.add_successful(
                        "Frontend service, API Gateway or BFF on client/ui - service path found", path)
                else:
                    self._client_service_paths_with_frontend_service_or_gw_or_bff. \
                        add_failed("no frontend service, API Gateway or BFF on client/ui - service path", path)
        return self._client_service_paths_with_frontend_service_or_gw_or_bff

    def calculate_client_service_paths_with_frontend_service_or_gw_or_bff_ratio(self):
        all_paths = self._get_all_paths_from_clients_or_uis_to_system_services()
        if len(all_paths) == 0:
            return None
        return len(self.detect_client_service_paths_with_frontend_service_or_gw_or_bff().successful) / len(all_paths)

    #### MONITORING and TRACING

    @staticmethod
    def _is_monitoring_or_tracing_component(component):
        return (contains_stereotype_of_type(component, monitoring_component) or
                contains_stereotype_of_type(component, tracing_component))

    def _get_all_monitoring_or_tracing_components(self):
        if self._monitoring_and_tracing_components is None:
            self._monitoring_and_tracing_components = []
            for element in self._model_bundle.elements:
                if self._is_monitoring_or_tracing_component(element.class_object_class):
                    self._monitoring_and_tracing_components.append(element)
        return self._monitoring_and_tracing_components

    def _get_all_system_services(self):
        if self._all_system_services is None:
            self._all_system_services = set()
            for element in self._model_bundle.elements:
                if self._is_system_service(element.class_object_class):
                    self._all_system_services.add(element)
        return list(self._all_system_services)

    def _get_all_gws_bffs_and_frontends(self):
        if self._all_gws_bffs_and_frontends is None:
            self._all_gws_bffs_and_frontends = set()
            for element in self._model_bundle.elements:
                if (self._is_api_gateway_or_bff(element.class_object_class) or
                        self._is_frontend_service(element.class_object_class)):
                    self._all_gws_bffs_and_frontends.add(element)
        return list(self._all_gws_bffs_and_frontends)

    def detect_observed_system_services(self):
        if self._observed_system_services is None:
            self._observed_system_services = DetectorResults()
            system_services = self._get_all_system_services()
            monitoring_components = [c.class_object_class for c in self._get_all_monitoring_or_tracing_components()]
            for component in system_services:
                has_observing_component_attached = False
                for connector in component.get_links_for_association(connectors_relation):
                    if (connector.source in monitoring_components or
                            connector.target in monitoring_components):
                        self._observed_system_services.add_successful("service has monitoring or tracing " +
                                                                      "component attached", [component])
                        has_observing_component_attached = True
                        break
                if not has_observing_component_attached:
                    self._observed_system_services.add_failed("service has no monitoring or tracing " +
                                                              "component attached", [component])
        return self._observed_system_services

    def calculate_observed_system_services_ratio(self):
        system_services = self._get_all_system_services()
        if len(system_services) == 0:
            return None
        return len(self.detect_observed_system_services().successful) / len(system_services)

    def detect_observed_gws_bffs_and_frontends(self):
        if self._observed_gws_bffs_and_frontends is None:
            self._observed_gws_bffs_and_frontends = DetectorResults()
            gws_bffs_and_frontends = self._get_all_gws_bffs_and_frontends()
            monitoring_components = [c.class_object_class for c in self._get_all_monitoring_or_tracing_components()]
            for component in gws_bffs_and_frontends:
                has_observing_component_attached = False
                for connector in component.get_links_for_association(connectors_relation):
                    if (connector.source in monitoring_components or
                            connector.target in monitoring_components):
                        self._observed_gws_bffs_and_frontends.add_successful(
                            "Gateway, BFF, or frontend has monitoring or tracing component attached", [component])
                        has_observing_component_attached = True
                        break
                if not has_observing_component_attached:
                    self._observed_gws_bffs_and_frontends.add_failed(
                        "Gateway, BFF, or frontend has no monitoring or tracing component attached", [component])
        return self._observed_gws_bffs_and_frontends

    def calculate_observed_gws_bffs_and_frontends_ratio(self):
        gws_bffs_and_frontends = self._get_all_gws_bffs_and_frontends()
        if len(gws_bffs_and_frontends) == 0:
            return None
        return len(self.detect_observed_gws_bffs_and_frontends().successful) / len(gws_bffs_and_frontends)

    def detect_observed_services_and_gws_bffs_and_frontends(self):
        if self._observed_services_gws_bffs_and_frontends is None:
            self._observed_services_gws_bffs_and_frontends = DetectorResults()
            observed_services = self.detect_observed_system_services()
            self._observed_services_gws_bffs_and_frontends.add_all(observed_services)
            observed_gws = self.detect_observed_gws_bffs_and_frontends()
            self._observed_services_gws_bffs_and_frontends.add_all(observed_gws)
        return self._observed_services_gws_bffs_and_frontends

    def calculate_observed_services_and_gws_bffs_and_frontends_ratio(self):
        system_services = self._get_all_system_services()
        gws_bffs_and_frontends = self._get_all_gws_bffs_and_frontends()
        if len(gws_bffs_and_frontends) + len(system_services) == 0:
            return None
        return (len(self.detect_observed_services_and_gws_bffs_and_frontends().successful) /
                (len(gws_bffs_and_frontends) + len(system_services)))

    # SENSITIVE DATA IN COMPONENT OR CONNECTOR CODE

    def detect_component_code_without_plaintext_sensitive_data(self):
        if self._component_code_without_plaintext_sensitive_data is None:
            all_components = self._model_bundle.elements
            self._component_code_without_plaintext_sensitive_data = DetectorResults()

            for component in all_components:
                if contains_stereotype_of_type(component.class_object_class, component_code_plaintext_sensitive_data):
                    self._component_code_without_plaintext_sensitive_data.add_failed(
                        "code contains plaintext sensitive data", [component])
                else:
                    self._component_code_without_plaintext_sensitive_data.add_successful(
                        "code contains no plaintext sensitive data", [component])
        return self._component_code_without_plaintext_sensitive_data

    def calculate_component_code_without_plaintext_sensitive_data_ratio(self):
        all_components = self._model_bundle.elements
        if len(all_components) == 0:
            return None
        return len(self.detect_component_code_without_plaintext_sensitive_data().successful) / len(all_components)

    def detect_connector_code_without_plaintext_sensitive_data(self):
        if self._connector_code_without_plaintext_sensitive_data is None:
            self._connector_code_without_plaintext_sensitive_data = DetectorResults()

            for connector in self._all_connectors:
                if contains_stereotype_of_type(connector, connector_code_plaintext_sensitive_data):
                    self._connector_code_without_plaintext_sensitive_data.add_failed(
                        "code contains plaintext sensitive data", [connector])
                else:
                    self._connector_code_without_plaintext_sensitive_data.add_successful(
                        "code contains no plaintext sensitive data", [connector])
        return self._connector_code_without_plaintext_sensitive_data

    def calculate_connector_code_without_plaintext_sensitive_data_ratio(self):
        if len(self._all_connectors) == 0:
            return None
        return len(self.detect_connector_code_without_plaintext_sensitive_data().successful) / len(self._all_connectors)

    def detect_component_or_connector_code_without_plaintext_sensitive_data(self):
        if self._component_or_connector_code_without_plaintext_sensitive_data is None:
            all_components = self._model_bundle.elements
            self._component_or_connector_code_without_plaintext_sensitive_data = DetectorResults()

            for component in all_components:
                if contains_stereotype_of_type(component.class_object_class, component_code_plaintext_sensitive_data):
                    self._component_or_connector_code_without_plaintext_sensitive_data.add_failed(
                        "component code contains plaintext sensitive data", [component])
                else:
                    self._component_or_connector_code_without_plaintext_sensitive_data.add_successful(
                        "component code contains no plaintext sensitive data", [component])
            for connector in self._all_connectors:
                if contains_stereotype_of_type(connector, connector_code_plaintext_sensitive_data):
                    self._component_or_connector_code_without_plaintext_sensitive_data.add_failed(
                        "connector code contains plaintext sensitive data", [connector])
                else:
                    self._component_or_connector_code_without_plaintext_sensitive_data.add_successful(
                        "connector code contains no plaintext sensitive data", [connector])
        return self._component_or_connector_code_without_plaintext_sensitive_data

    def calculate_component_and_connector_code_without_plaintext_sensitive_data_ratio(self):
        all_components = self._model_bundle.elements
        if len(self._all_connectors) + len(all_components) == 0:
            return None
        return (len(self.detect_component_or_connector_code_without_plaintext_sensitive_data().successful) /
                (len(self._all_connectors) + len(all_components)))
