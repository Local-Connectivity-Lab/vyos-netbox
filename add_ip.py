import requests
import json

# --- Configuration ---
#NETBOX_URL = "https://netbox.infra.seattlecommunitynetwork.org"
NETBOX_URL = "https://demo.netbox.dev"
API_TOKEN = "aPDpENpngm49qel9HIg2EsPxkWY1oIIfQCjLQkhL"  # TODO: Find an API token for SCN Netbox

# --- API Endpoint ---
IP_ADDRESSES_ENDPOINT = f"{NETBOX_URL}/api/ipam/ip-addresses/"

new_site_data = {
    "name": "Seattle Office",
    "slug": "seattle-office",
    "status": "active",
}

# Info for a new device
# device role, type, site and status are required
new_device_data = {
    "name": "seattle-edge-router-01",
    "device_type": {"slug": "pfsense-sg-2100"},
    "device_role": {"slug": "edge-router"},
    "site": {"slug": "seattle-office"},
    "status": "active",
}

new_interface_data = {
    "device": {"name": "seattle-edge-router-01"},
    "name": "ge-0/0/0",
     "type": "1000base-t",
}

# example info to add for IP address
# 'address' field is required, in address/prefix format
# assigned_object_type and assigned_object_id are needed to assign to an interface
new_ip_data = {
    "address": "192.0.2.101/24", # TODO: auto-read in from vyos
    "status": "active",
    "assigned_object_type": "dcim.interface",
    "assigned_object_id": "interface_id"
}

# Info for a new interface


# --- Request Headers ---
# API token for authorization and specify the content type.
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Token {API_TOKEN}"
}

# single method to check for existence of various Netbox objects
# sites, devices, interfaces, and IP addresses
#
# returns object ID? maybe should return boolean...
def netbox_object_exists(endpoint_path, filter_params, object_type_name="Site"):
    full_endpoint_url = f"{NETBOX_URL}{endpoint_path}"
    print(f"Checking if {object_type_name} exists with parameters: {filter_params}...")
    # add filter to the GET request
    try:
        response = requests.get(
            full_endpoint_url,
            headers = headers,
            params = filter_params,
            timeout = 10
        )
        response.raise_for_status() # exception for bad status codes (4xx or 5xx)
        results = response.json()
        # print(json.dumps(results, indent=4))
        # API response includes a "count" field, if > 0, then object exists
        if results["count"] > 0:
            object_id = results["results"][0]["id"]
            print(f"{object_type_name} exists with ID: {object_id}")
            # return object_id
            return results["results"][0]
        else:
            print(f"{object_type_name} not found.")
            return None
    except requests.exceptions.RequestException as e:
        raise e
    except (KeyError, IndexError) as e:
        print(f"Could not parse the API response. Error: {e}")
        return None

def assign_ip_address():
    pass

def unassign_ip_address():
    pass


def create_netbox_object(endpoint_path, object_data, object_type_name="object"):
    full_endpoint_url = f"{NETBOX_URL}{endpoint_path}"
    object_identifier = object_data.get("name") or object_data.get("address", "N/A")
    print(f"Attempting to create {object_type_name}: {object_identifier}")
    try:
        response = requests.post(
            full_endpoint_url,
            headers=headers,  # Assumes 'headers' is a global variable with your token
            data=json.dumps(object_data),
            timeout=15
        )
        response.raise_for_status()
        if response.status_code == 201:  # 201 Created is the success code for POST
            created_object = response.json()
            new_id = created_object.get("id")
            print(f"Successfully created {object_type_name} with ID: {new_id}")
            return created_object
        else:
            print(f"Received unexpected status code {response.status_code} for {object_type_name}")
            return None
    except requests.exceptions.HTTPError as e:
        print(f"An HTTP error occurred while creating {object_type_name}: {e}")
        print("--- Server Response ---")
        try:
            print(json.dumps(e.response.json(), indent=4))
        except json.JSONDecodeError:
            print(e.response.text)
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None



if __name__ == "__main__":
    site_data = {
        "name": "SCN-Lab-01",
        "slug": "scn-lab-01",
        "status": "active"
    }

    device_data = {
        "name": "sw-access-01",
        "device_type": 14,  # ID of the Device Type (e.g., Cisco Catalyst 9300)
        "role": 3,  # ID of the Device Role (e.g., Access Switch)
        "site": site_data['slug'],  # ID of the Site (e.g., SCN-Lab-01)
        "status": "active"
    }

    end_path_site = "/api/dcim/sites/"
    end_path_device = "/api/dcim/devices/"
    end_path_interface = "/api/dcim/interfaces/"
    end_path_ip = "/api/ipam/ip-addresses/"

    filt_params_site = {"slug": "scn-lab-01"}
    filt_params_device = {"name": "seattle-edge-router-01", "site_id": "scn-lab-01"}
    filt_params_interface = {"device_id": "seattle-edge-router-01", "name": "ge-0/0/0"}
    filt_params_ip = {"address": "192.0.2.101/24"}
    #  A `slug` is a unique, URL-friendly identifier for an object in NetBox
    #  (e.g., "scn-lab-01"). Since it must be unique, filtering by slug ensures
    #  you will find at most one site.
    #  You can also filter by `name`, but since NetBox doesn't strictly enforce
    #  unique names for sites, it's theoretically possible to get multiple results.

    obj_type = "Site" # Site, Device, Interface, IP Address
    # created_site = create_netbox_object("/api/dcim/sites/", site_data, "Site")
    print(f"checkingfor existence after...")
    site_id = netbox_object_exists(
        endpoint_path=end_path_ip,
        filter_params=filt_params_site,  # Using slug is often more reliable than name
        object_type_name=obj_type
    )



    """
    When seeing Peer, the peer name will be the name of the device.
    1st, check if IP is already there (including site, device, interface, and assignment to device)
        If so, do nothing!
        
    
    2nd, check if device is already there, if not create device and interface.
    Then, see if ip address already exists and is unassigned. if so, assign it
    
    if it already exists and is assigned to something else! then unassign it, and assign to current device
    
    If ip does NOT exist, then create it and assign to device we already created above
    
    if device is there, and interface is there, AND IP address is there that's different from current one, 
    then we need to boot that IP address and replace it with the current one
    
    
    
    """



