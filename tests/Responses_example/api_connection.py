from requests import Response, get, post, put


def _check_response_status(response: Response):
    """
    Ensures the response status is valid.

    - First check the HTTP status code for a 2xx response; if not then raise an
      HTTPError.
    - Then check the internal response status code. If it is not 792000, raise a
      RuntimeError.

    :param Response response: The HTTP response object to check.
    :raises HTTPError: If the HTTP request returned an unsuccessful status code.
    :raises RuntimeError: If the JSON response contains a status code other than 792000.
    """
    response.raise_for_status()
    if response.json()["statusCode"] != "790200":
        raise RuntimeError(f"Error with status code {response.json()['statusCode']}")


class NetBrainConnection:
    def __init__(self, username, password, tenant_name, domain_name):
        self.nb_req_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.username = username
        self.password = password
        self.tenant_name = tenant_name
        self.domain_name = domain_name
        self.tenant_id = None
        self.domain_id = None

    def connect_to_api(self) -> None:
        """
        Establishes a connection to the API using the provided credentials and
        tenant/domain details. Sets the tenant and domain for future API calls during
        the current session.

        :param username: The username for API authentication.
        :param password: The password for API authentication.
        :param tenant_name: The name of the tenant to access.
        :param domain_name: The name of the domain within the tenant.
        :return: The access token obtained after successful authentication.

        """
        self.login_to_api()
        self.get_tenant_id()
        self.get_domain_id()
        self.set_tenant_and_domain()

    def login_to_api(self) -> None:
        """
        Authenticates the user by logging into the NetBrain API and retrieves the
        access token required for further API requests.
        """
        login_response = post(
            "https://netbrain-api.example.com/ServicesAPI/API/V1/Session",
            json={
                "username": self.username,
                "password": self.password,
            },
            headers=self.nb_req_headers,
        )
        _check_response_status(login_response)
        self.nb_req_headers["token"] = login_response.json()["token"]

    def get_tenant_id(self) -> None:
        """
        Retrieve the tenant ID for a given tenant name from the NetBrain API. If a tenant
        with the specified name is not found, a RuntimeError is raised.

        :raises RuntimeError: If a tenant with the specified name is not found
        """
        tenant_response = get(
            "https://netbrain-api.example.com/ServicesAPI/API/V1/CMDB/Tenants", headers=self.nb_req_headers
        )
        _check_response_status(tenant_response)
        tenant_list: list = tenant_response.json()["tenants"]
        for one_tenant in tenant_list:
            if one_tenant["tenantName"] == self.tenant_name:
                self.tenant_id = one_tenant["tenantId"]
                return
        raise RuntimeError(f"Tenant with name {self.tenant_name} not found")

    def get_domain_id(self) -> None:
        """
        Retrieves the domain ID for a specific domain name accessible to the specified
        tenant. If the domain is not found, it raises a RuntimeError.

        :raises RuntimeError: If the domain with the specified name is not found
        """
        domain_response = get(
            "https://netbrain-api.example.com/ServicesAPI/API/V1/CMDB/Domains",
            params={"TenantId": self.tenant_id},
            headers=self.nb_req_headers,
        )
        _check_response_status(domain_response)
        domain_list: list = domain_response.json()["domains"]
        for one_domain in domain_list:
            if one_domain["domainName"] == self.domain_name:
                self.domain_id = one_domain["domainId"]
                return
        raise RuntimeError(f"Domain with name {self.domain_name} not found")

    def set_tenant_and_domain(self) -> None:
        """
        Set the tenant and domain for the current session.
        """
        session_response = put(
            "https://netbrain-api.example.com//ServicesAPI/API/V1/Session/CurrentDomain",
            headers=self.nb_req_headers,
            json={
                "tenantId": self.tenant_id,
                "domainId": self.domain_id,
            },
        )
        _check_response_status(session_response)
