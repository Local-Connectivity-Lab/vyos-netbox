import json
from add_ip import *

CONFIG_FILE = "export-json-9-19-25.json"

with open(CONFIG_FILE) as f:
    d = json.load(f)

# print(d.keys())
# print(d['interfaces']['wireguard']['wg0']['peer'])


first_lvl = d['interfaces']['wireguard']
wgs = first_lvl.keys()

site_key = {"wg0":"wg2-people", "wg1":"wg2-people",
            "wg2":"wg2-people", "wg4":"wg4-VPN-guest-network",
            "wg5":"wg2-people"} # what site for wg3?

# For wg0, wg1, and wg2, and wg5 add everything to the wg2-people site.
# We'll manually adjust non-people later to different sites

# wg4, add everything to wg4-VPN-guest-network site

temp_url_dcim = "/api/dcim/"
temp_url_ipam = '/api/ipam/ip-addresses/'


for wg_id in first_lvl.keys():
    # if-branch for all wg# except wg3, currently
    if site_key.get(wg_id):
        wg_site_name = site_key[wg_id]

        ##############################################
        # if site exists....
        filt_params_site = {"name": wg_site_name}
        site_obj = netbox_object_exists(
            endpoint_path=temp_url_dcim + "sites/",
            filter_params=filt_params_site,
            object_type_name="Site"
        )
        if site_obj:
            # print(f"site already exists: {site_obj['name']}")
            # TODO: figure out what device for people IPs...
            pass
        else:
            site_info = {
                "name": wg_site_name,
                "slug": wg_site_name.lower(),
                "status": "active"
            }
            site_obj = create_netbox_object(temp_url_dcim + "sites/",
                                                site_info, "Site")
        if site_obj:
            print(f"\nsuccessfully created site {wg_site_name}")
        else:
            print(f"\nFailed to create site {wg_site_name}, please investigate!!!")
        # TODO: catch if site-creation fails

        ##############################################
        # if device exists....
        device_name = f"rtr-{wg_site_name.lower()}"
        filt_params_device = {"name": device_name}
        device_obj = netbox_object_exists(
            endpoint_path=temp_url_dcim + "devices/",
            filter_params=filt_params_device,
            object_type_name="Device"
        )
        if device_obj:
            # print(f"device {device_obj['name']} already exists at site "
            #       f"{site_obj['name']}")
            pass
        else:
            device_info = {
                "name": device_name,
                "device_type": 14,  # Ideally, look this ID up dynamically too
                "role": 3,  # Ideally, look this ID up dynamically too
                "site": site_obj['id'],
                "status": "active"
            }
            device_obj = create_netbox_object(temp_url_dcim + "devices/",
                                          device_info, 'Device')
        # TODO: catch if device-creation fails
        if device_obj:
            print(f"\nsuccessfully created device {device_name}")
        else:
            print(f"\nFailed to create device {device_name}, please investigate!!!")

        ##############################################
        # if interface exists....
        interface_device_id = "interface_" + wg_site_name
        # filter in case device name exists on other devices
        interface_filter = {
            "device_id": device_obj['id'],
            "name": interface_device_id
        }

        interface_obj = netbox_object_exists(
            endpoint_path=temp_url_dcim + "interfaces/",
            filter_params=interface_filter,
            object_type_name="Interface"
        )
        if interface_obj:
            # print(f"interface {interface_obj['name']} "
            #       f"already exists at site {site_obj['name']} "
            #       f"on device {device_obj['name']}")
            pass
        else:
            interface_info = {
                "device": device_obj['id'],
                "name": interface_device_id,
                "type": "1000base-t",
                "enabled": True
            }
            interface_obj = create_netbox_object(temp_url_dcim + "interfaces/",
                                             interface_info, 'Interface')

        # TODO: catch if interface-creation fails
        if interface_obj:
            print(f"\nsuccessfully created interface {interface_obj['name']}")
        else:
            print(f"\nFailed to create interface {interface_device_id}, please investigate!!!")

        ##############################################
        # if IPs exist....
        """
        TODO: figure out how to handle some IPs giving this result:
        An HTTP error occurred while creating IP Address: 400 Client Error: Bad Request for url: https://demo.netbox.dev/api/ipam/ip-addresses/
        --- Server Response ---
        {
            "__all__": [
                "172.16.36.16 is a network ID, which may not be assigned to an interface."
            ]
        }
        """
        peers_to_add = first_lvl[wg_id]['peer'].keys()
        for peer in peers_to_add:
            ip_addr = first_lvl[wg_id]["peer"][peer]["allowed-ips"]
            filt_params_ip = {"address": ip_addr[0]}

            ip_obj = netbox_object_exists(
            endpoint_path=temp_url_ipam,
            filter_params=filt_params_ip,
            object_type_name='IP Address'
        )
            if ip_obj:
                # print(f"IP address {ip_addr} for peer {peer} already exists on device "
                #       f"{device_obj['name']} at site {site_obj['name']}")
                pass
            else:
                ip_info = {
                    "address": ip_addr[0],
                    "status": "active",
                    "assigned_object_type": "dcim.interface",
                    "assigned_object_id": interface_obj['id'],
                }
                ip_obj = create_netbox_object(temp_url_ipam,
                                          ip_info,
                                          'IP Address')
            # TODO: catch if ip-creation fails
            if ip_obj:
                print(f"\nsuccessfully created ip {ip_addr}")
            else:
                print(f"\nFailed to create ip {ip_addr}, please investigate!!!")


    # wg3, take first part of peer name (everything before Tunnel), add -Gateway,
    # and match that name to the device with that name (eg, "peer BrickHouse-TC4-Tunnel"
    # becomes "BrickHouse-TC4-Gateway")
    else:
        print("figuring out wg3!")
        peers = first_lvl[wg_id]["peer"]

        for peer in list(peers.keys()):
            peer_name = peer.split("Tunnel")[0] + "Gateway"
            # TODO: loop thro devices?
            if netbox_object_exists(
                    endpoint_path="/api/dcim/devices/",
                    filter_params={"slug": "scn-lab-01"},  # Using slug is often more reliable than name
                    object_type_name=peer_name
            ):
                # check for/create interface
                create_netbox_object("/api/dcim/sites/", site_data, wg_site_name)
                # create IP
                ip = peers[peer]["allowed-ips"] # TODO: would there ever be more than 1?
                create_netbox_object("/api/dcim/sites/", site_data, ip)



