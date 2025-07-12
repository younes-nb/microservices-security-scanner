"""
"""
from src.codeable_models import CStereotype, CEnum, CClass, CObject, CBundle
from src.metamodels.component_metamodel import connector_type, connectors_relation, component, component_type

# authentication_types = CEnum("Authentication Types", values=["None", "Plaintext Credentials",
#                                                              "HTTP Basic Authentication",
#                                                              "Form-Based Login", "Single Sign-On", "Session-Based",
#                                                              "API Keys",
#                                                              "Plaintext Authentication Plugin",
#                                                              "SSL Authentication",
#                                                              "SASL Authentication",
#                                                              "Secure Authentication Plugin",
#                                                              "OpenID Connect Identity Token",
#                                                              "Credentials Provided as Plaintext",
#                                                              "Secure Token Provided"])
# sensitive_data_management_types = CEnum("Sensitive Data Management Types",
#                                         values=["No Sensitive Data", "Sensitive Data as Plaintext",
#                                                 "Sensitive Data Encrypted",
#                                                 "Sensitive Data as Encrypted Token",
#                                                 "Sensitive Data Encrypted from Keystore"])
# authorization_types = CEnum("Authorization Types", values=["None",
#                                                            "Token-based Authorization",
#                                                            "OAuth2 Access Tokens",
#                                                            "OAuth2/JWT Tokens"])
# request_scope_types = CEnum("Request Scope Types", values=["None", "Some Requests", "All Requests"])

# connector_security_annotations = CStereotype("Connector Type Security Annotation", extended=connectors_relation,
#                                              attributes={"encrypted": bool,
#                                                          # "authentication scope": request_scope_types,
#                                                          ## list elements should be of type authentication_types
#                                                          # "authentication type": list,
#                                                          "sensitive data management": sensitive_data_management_types
#                                                          })
# connector_type.superclasses = connector_type.superclasses.copy() + [connector_security_annotations]
#
# component_security_annotations = CStereotype("Component Type Security Annotation", extended=component,
#                                              attributes={"sensitive data management": sensitive_data_management_types
#                                                          })
# component_type.superclasses = component_type.superclasses.copy() + [component_security_annotations]

# authentication_component = CStereotype("Authentication", superclasses=component_type,
#                                        attributes={"authentication scope": request_scope_types,
#                                                    # list elements should be of type authentication_types
#                                                    "authentication type": list})
#
# authentication_connector = CStereotype("Authentication", superclasses=connector_type,
#                                        attributes={"authentication scope": request_scope_types,
#                                                    # list elements should be of type authentication_types
#                                                    "authentication type": list})
#
# authorization_component = CStereotype("Authorization", superclasses=component_type,
#                                       attributes={"authorization scope": request_scope_types,
#                                                   # list elements should be of type authorization_types
#                                                   "authorization type": list})
# authorization_connector = CStereotype("Authorization", superclasses=connector_type,
#                                       attributes={"authorization scope": request_scope_types,
#                                                   # list elements should be of type authorization_types
#                                                   "authorization type": list})

authentication_connector_type = CStereotype("Authentication", superclasses=connector_type)
no_authentication = CStereotype("No Authentication", superclasses=connector_type)
authentication_not_required = CStereotype("Authentication Not Required", superclasses=connector_type)
authentication_with_plaintext_credentials = CStereotype("Authentication with Plaintext Credentials",
                                                        superclasses=authentication_connector_type)
http_basic_authentication = CStereotype("HTTP Basic Authentication",
                                        superclasses=authentication_with_plaintext_credentials)
form_based_login_authentication = CStereotype("Form-based Login Authentication",
                                              superclasses=authentication_with_plaintext_credentials)
authentication_with_api_keys = CStereotype("Authentication with API Keys", superclasses=authentication_connector_type)
protocol_based_secure_authentication = CStereotype("Protocol-based Secure Authentication",
                                                   superclasses=authentication_connector_type)
ssl_authentication = CStereotype("SSL Authentication", superclasses=protocol_based_secure_authentication)
sasl_authentication = CStereotype("SASL Authentication", superclasses=protocol_based_secure_authentication)

# secure_authentication_token = (in contrast to API keys)  digitally signed or verified with an authoritative source.
# Additionally, some services may require either single-use tokens or short-lived tokens
secure_authentication_token = CStereotype("Secure Authentication Token", superclasses=authentication_connector_type)
open_id_connect_identity_token = CStereotype("Open-ID Identity Token Based Authentication",
                                             superclasses=secure_authentication_token)

authentication_scope_type = CStereotype("Authentication Scope", superclasses=connector_type)
authentication_scope_none = CStereotype("Authentication Scope / None", superclasses=authentication_scope_type)
authentication_scope_some_requests = CStereotype("Authentication Scope / Some Requests",
                                                 superclasses=authentication_scope_type)
authentication_scope_all_requests = CStereotype("Authentication Scope / All Requests",
                                                superclasses=authentication_scope_type)

single_sign_on = CStereotype("Single Sign-On", superclasses=connector_type)
session_based = CStereotype("Session-Based", superclasses=connector_type)

authorization_connector_type = CStereotype("Authorization", superclasses=connector_type)
no_authorization = CStereotype("No Authorization", superclasses=connector_type)
authorization_not_required = CStereotype("Authorization Not Required", superclasses=connector_type)
encrypted_authorization_information = CStereotype("Encrypted Authorization Information",
                                                  superclasses=authorization_connector_type)
token_based_authorization = CStereotype("Token-based Authorization", superclasses=encrypted_authorization_information)
oauth2_access_token_authorization = CStereotype("OAuth2 Access Tokens Based Authorization",
                                                superclasses=token_based_authorization)
oauth2_jwt_token_authorization = CStereotype("OAuth2/JWT Tokens Based Authorization",
                                             superclasses=token_based_authorization)
authorization_with_plaintext_information = CStereotype("Authorization with Plaintext Information",
                                                       superclasses=authorization_connector_type)

authorization_scope_type = CStereotype("Authorization Scope", superclasses=connector_type)
authorization_scope_none = CStereotype("Authorization Scope / None", superclasses=authorization_scope_type)
authorization_scope_some_requests = CStereotype("Authorization Scope / Some Requests",
                                                superclasses=authorization_scope_type)
authorization_scope_all_requests = CStereotype("Authorization Scope / All Requests",
                                               superclasses=authorization_scope_type)


sensitive_data_in_connector_code_type = CStereotype("Sensitive Data in Connector Code Type",
                                                    superclasses=connector_type)
connector_code_no_sensitive_data = CStereotype("Connector Code Contains No Sensitive Data",
                                               superclasses=sensitive_data_in_connector_code_type)
connector_code_plaintext_sensitive_data = CStereotype("Connector Code Contains Sensitive Data as Plaintext",
                                                      superclasses=sensitive_data_in_connector_code_type)
connector_code_encrypted_sensitive_data = CStereotype("Connector Code Contains Encrypted Sensitive Data",
                                                      superclasses=sensitive_data_in_connector_code_type)
connector_code_encrypted_token_sensitive_data = CStereotype("Connector Code Contains Sensitive Data As Encrypted Token",
                                                            superclasses=sensitive_data_in_connector_code_type)

sensitive_data_in_component_code_type = CStereotype("Sensitive Data in Component Code Type",
                                                    superclasses=component_type)
component_code_no_sensitive_data = CStereotype("Component Code Contains No Sensitive Data",
                                               superclasses=sensitive_data_in_component_code_type)
component_code_plaintext_sensitive_data = CStereotype("Component Code Contains Sensitive Data as Plaintext",
                                                      superclasses=sensitive_data_in_component_code_type)
component_code_encrypted_sensitive_data = CStereotype("Component Code Contains Encrypted Sensitive Data",
                                                      superclasses=sensitive_data_in_component_code_type)
component_code_encrypted_token_sensitive_data = CStereotype("Component Code Contains Sensitive Data As Encrypted Token",
                                                            superclasses=sensitive_data_in_component_code_type)
encrypted_communication = CStereotype("Encrypted", superclasses=connector_type)
unencrypted_communication = CStereotype("Unencrypted", superclasses=connector_type)

auth_provider = CStereotype("Auth Provider", superclasses=connector_type)
auth_server = CStereotype("Auth Server", superclasses=component_type)
oauth2_server = CStereotype("OAuth2 Server", superclasses=auth_server)
identity_server = CStereotype("Identity Server", superclasses=auth_server)
authentication_service = CStereotype("Authentication Service", superclasses=auth_server)

# Cross-site Request Forgery Protection is needed, if you use Cookies (for authentication),
# HTTP-basic auth, or a similar mechanism
# See e.g.: https://security.stackexchange.com/questions/166724/should-i-use-csrf-protection-on-rest-api-endpoints,
# https://security.stackexchange.com/questions/151203/csrf-in-microservice-architecture
csrf_protection_type = CStereotype("CSRF Protection Type", superclasses=component_type)
no_csrf_protection = CStereotype("No CSRF Protection", superclasses=csrf_protection_type)
token_based_csrf_protection = CStereotype("Token-based CSRF Protection", superclasses=csrf_protection_type)

csrf_scope_type = CStereotype("CSRF Scope", superclasses=component_type)
csrf_scope_none = CStereotype("CSRF Scope / None", superclasses=csrf_scope_type)
csrf_scope_some_requests = CStereotype("CSRF Scope / Some Requests", superclasses=csrf_scope_type)
csrf_scope_all_requests = CStereotype("CSRF Scope / All Requests", superclasses=csrf_scope_type)

connector_elements = []
for e in [authentication_connector_type,
          authentication_scope_type, authorization_connector_type,
          sensitive_data_in_connector_code_type, encrypted_communication, unencrypted_communication,
          auth_provider]:
    connector_elements.extend(e.get_connected_elements(add_stereotypes=True, stop_elements_inclusive=[connector_type]))
security_connector_annotations = CBundle("security_connector_annotations", elements=connector_elements)

component_elements = []
for e in [csrf_protection_type, csrf_scope_type, auth_server,
          sensitive_data_in_component_code_type]:
    component_elements.extend(e.get_connected_elements(add_stereotypes=True, stop_elements_inclusive=[component_type]))
security_component_annotations = CBundle("security_component_annotations", elements=component_elements)

security_annotation_metamodel_views = [
    security_connector_annotations, {},
    security_component_annotations, {},
]
