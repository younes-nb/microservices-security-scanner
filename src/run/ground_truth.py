# secure connections

# 4 encrypted connections everywhere
# 3 encrypted connections in all vulnerable/external connections (client connections, UI connections (static web sites))
# 2 (encrypted connections in >=70% vulnerable/external connections OR
#    (encrypted connections in >=50% vulnerable/external connections AND
#     encrypted connections in >=50% everywhere))
# 1 some encrypted connections, below the thresholds in (2)
# 0 no encrypted connections

secure_connections_values = {
    "DM": {"GT": ""}
}

# system backend authentication

# 4 all backend connectors (w/o in-mem connectors) authenticated with Protocol-based Secure Authentication OR Secure Authentication Token
# 3 all backend connectors (w/o in-mem connectors) authenticated with Protocol-based Secure Authentication OR Secure Authentication Token
#   OR if plaintext backend connectors, they use secure connections
# 2 (>70% of backend connectors (w/o in-mem connectors)
#    are authenticated either with Protocol-based Secure Authentication OR Secure Authentication Token
#    OR if plaintext backend connectors, they use secure connections)
#   OR
#   (all backend connectors (w/o in-mem connectors)  authenticated, but some of those are with Plaintext Credentials OR API Keys)
# 1 at least some backend connectors (w/o in-mem connectors) authenticated, but all or some of those are with
#   Plaintext Credentials OR API Keys, or below the thresholds from (2)
# 0 no authenticated used on backend connectors (w/o in-mem connectors)

backend_authentication_values = {
    "DM": {"GT": ""}
}

# authentication on paths from clients or uis to system services

# 4 all connectors on paths from clients or uis to system services authenticated with Protocol-based Secure Authentication OR Secure Authentication Token
# 3 all connectors on paths from clients or uis to system services authenticated with Protocol-based Secure Authentication OR Secure Authentication Token OR API Keys
#   OR if plaintext backend connectors, they use secure connections
# 2 (>70% of connectors on paths from clients or uis to system services
#    are authenticated either with Protocol-based Secure Authentication OR Secure Authentication Token OR API Keys
#    OR if plaintext backend connectors, they use secure connections)
#   OR
#   (all backend connectors (w/o in-mem connectors)  authenticated, but some of those are with Plaintext Credentials)
# 1 at least some backend connectors (w/o in-mem connectors) authenticated, but all or some of those are with
#   Plaintext Credentials, or below the thresholds from (2)
# 0 no authenticated used on backend connectors (w/o in-mem connectors)

authentication_on_client_service_paths_values = {
    "DM": {"GT": ""}
}

# system backend authorization

# 4 all backend connectors (w/o in-mem connectors) authorized with Token-based Authorization
# 3 all backend connectors (w/o in-mem connectors) authorized with Token-based Authorization OR
#   Encrypted Authorization Information OR with if authorized with Plaintext Information
#   connectors, they use secure connections
# 2 (>70% of backend connectors (w/o in-mem connectors) authorized with Token-based Authorization or
#    Encrypted Authorization Information OR with if authorized with Plaintext Information
#    connectors, they use secure connections)
#   OR
#   (all backend connectors (w/o in-mem connectors)  authorized, but some of those are with Plaintext Information)
# 1 some backend connectors (w/o in-mem connectors) authorized, but some or all of those
#   are authorized with Plaintext Information, or below the thresholds from (2)
# 0 no authorization used for backend connectors (w/o in-mem connectors)

backend_authorization_values = {
    "DM": {"GT": ""}
}

# authorization on paths from clients or uis to system services

# 4 all connectors on paths from clients or uis to system services authorized with Token-based Authorization
#   or Encrypted Authorization Information
# 3 all connectors on paths from clients or uis to system services authorized with Token-based Authorization or
#   Encrypted Authorization Information OR with if authorized with Plaintext Information
#   connectors, they use secure connections
# 2 (>70% of connectors on paths from clients or uis to system services authorized with Token-based Authorization or
#    Encrypted Authorization Information OR with if authorized with Plaintext Information
#    connectors, they use secure connections)
#   OR
#   (all connectors on paths from clients or uis to system services authorized,
#    but some of those are with Plaintext Information)
# 1 some connectors on paths from clients or uis to system services authorized, but some or all of those
#   are authorized with Plaintext Information, or below the thresholds from (2)
# 0 no authorization used for connectors on paths from clients or uis to system services

authorization_on_client_service_paths_values = {
    "DM": {"GT": ""}
}

# basic traffic control with API gateways/bffs

# 4 all client-system service paths go through dedicated API Gateways or BFFs
# 3 all client-system service paths go through dedicated API Gateways or BFFs or some kind of frontend service
# 2 >=70% client-system service paths go through dedicated API Gateways or BFFs or some kind of frontend service
# 1 some client-system service paths go through dedicated API Gateways or BFFs or some kind of frontend service
# 0 no API Gateway, BFF, or frontend service used on client-system service paths


api_gateways_bffs_for_traffic_control_values = {
    "DM": {"GT": ""}
}

# OBSERVABILITY: monitoring & tracing

# 4 all system services (not third party services) and API Gateways/BFFs/frontend services are monitored/traced
# 3 all system services (not third party services) or all API Gateways/BFFs/frontend services are monitored/traced
# 2 >=70% of system services (not third party services) and API Gateways/BFFs/frontend services are monitored/traced
# 1 <70% of system services (not third party services) and API Gateways/BFFs/frontend services are monitored/traced
# 0 no system services (not third party services) or API Gateways/BFFs/frontend services are monitored/traced

observability_values = {
    "DM": {"GT": ""}
}

# SENSITIVE DATA

# prior:
# 4 no component or connector codes contain plaintext sensitive data
# 3 >=90% of the component or connector codes contains no plaintext sensitive data
# 2 >=80% of the component or connector codes contains no plaintext sensitive data
# 1 >=70% of the component or connector codes contains no plaintext sensitive data
# 0 <70% of the component or connector codes contains no plaintext sensitive data

# updated:
# 3(=++) no component or connector codes contain plaintext sensitive data
# 2(=~) >=90% of the component or connector codes contains no plaintext sensitive data
# 1 >=70% of the component or connector codes contains no plaintext sensitive data
# 0 <70% of the component or connector codes contains no plaintext sensitive data

sensitive_data_values = {
    "DM": {"GT": ""}
}



