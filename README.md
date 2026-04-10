# n00b Attempt at SCN Netbox Automation for IPAM

## First task:

* Get wg IPs from Vyos-internal router
* Add "devices", "interfaces", and corresponding IPs

### Reminder from 2/18/2026:
vyos-parse-example.py currently (mostly successfully) runs through wg0, wg1, and wg2 to add info in json example file to create sites, devices, interfaces, and ips when they don't already exist. 

For now, I'm just using a [demo netbox](https://demo.netbox.dev/), so need to login and create an ip address when re-starting this script for testing. 

#### Todos:
* Address the "ip address is a network-ID issue"
* Figure out what site to use for wg3
* Check that wg4 and wg5 logic works too
* Test on real netbox site
