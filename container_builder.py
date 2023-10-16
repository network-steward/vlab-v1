from jinja2 import Environment, FileSystemLoader, Template, DebugUndefined
import yaml
import os
import settings

with open(f'{settings.path}kvm_hosts.yaml', 'r') as file:
    kvm_inventory = yaml.safe_load(file)

def init_container(node_name = ()):
    """
    Creates containers from container image already created outside this script 
    """

    for container in node_name:
        for host_inv in kvm_inventory['container_nodes']:
            if container['hostname']  == host_inv['hostname']:
                if host_inv['node_type'] == "ubuntu_container":
                        print(f"creating container {host_inv['hostname']}")
                        os.system("docker run -d --name " + host_inv['hostname'] + " -h " + host_inv['hostname'] + " --ip " + host_inv['mgmtip'] + " --cap-add=NET_ADMIN -i -t " + host_inv['docker_image'] + " /bin/bash")
                else:
                    print(f"container {host_inv['hostname']} with type {host_inv['node_type']} not recognized! ")

def init_cont_interfaces(node_name = ()):
    """
    Create and connect the logical docker interfaces to the OVS bridge found in the inventory file
    """

    for container in node_name:
        for host_inv in kvm_inventory['container_nodes']:
            if container['hostname']  == host_inv['hostname']:
                if host_inv['node_type'] == "ubuntu_container":
                    print(f"creating container interfaces for host {host_inv['hostname']}")
                    for i in host_inv['interfaces']:
                        if i['type'] == "logical":
                            os.system("ovs-docker add-port " + i['bridge'] + " " + i['interface'] + " " + host_inv['hostname'])
                else:
                    print(f"container {host_inv['hostname']} with type {host_inv['node_type']} not recognized! ")

def init_cont_conf(node_name = ()):
    """
    Configure the logical and bond interfaces for the docker container 
    """

    for container in node_name:
        for host_inv in kvm_inventory['container_nodes']:
            if container['hostname']  == host_inv['hostname']:
                if host_inv['node_type'] == "ubuntu_container":
                    print(f"configuring container interfaces for host {host_inv['hostname']}")
                    for i in host_inv['interfaces']:
                        os.system("docker exec -it " + host_inv['hostname'] + " ip link set " + i['interface'] + " up")
                        os.system("docker exec -it " + host_inv['hostname'] + " ip address add " +  i['ip_address'] + " dev " + i['interface'])
                else:
                    print(f"container {host_inv['hostname']} with type {host_inv['node_type']} not recognized! ")

def container_interface_delete(node_name = ()):
    """
    Configure the logical and bond interfaces for the docker container 
    """
    print("trying to delete interfaces")
    for container in node_name:
        for host_inv in kvm_inventory['container_nodes']:
            if container['hostname'] == host_inv['hostname']:
                if host_inv['node_type'] == "ubuntu_container":
                    print(f"deleting container interfaces for host {host_inv['hostname']}")
                    for i in host_inv['interfaces']:
                        if i['type'] == "logical":
                            os.system("ovs-docker del-port " + i['bridge'] + " " + i['interface'] + " " + host_inv['hostname'])
                else:
                    print(f"container {host_inv['hostname']} with type {host_inv['node_type']} not recognized! ")

def container_delete(node_name = ()):
    """
    Configure the logical and bond interfaces for the docker container 
    """

    for container in node_name:
        for host_inv in kvm_inventory['container_nodes']:
            if container['hostname'] == host_inv['hostname']:
                if host_inv['node_type'] == "ubuntu_container":
                    print(f"delete container {host_inv['hostname']}")
                    os.system("docker stop " + host_inv['hostname'])
                    os.system("docker rm " + host_inv['hostname'])
                else:
                    print(f"container {host_inv['hostname']} with type {host_inv['node_type']} not recognized! ")

def init_lldp(node_name = ()):
    """
    For now just used to start lldp but could be used to start any service in the future on the containers.
    """

    for container in node_name:
        for host_inv in kvm_inventory['container_nodes']:
            if container['hostname']  == host_inv['hostname']:
                if host_inv['node_type'] == "ubuntu_container":
                    print(f"starting LLDP on {host_inv['hostname']}")
                    os.system("docker exec -it "  + host_inv['hostname'] + " service lldpd start")
                else:
                    print(f"container {host_inv['hostname']} with type {host_inv['node_type']} not recognized! ")

def init_static_routes(node_name = ()):
    """
    deploy known static routes so we can do inter SVI routing between groups that land in the L3 VRF
    """
    for container in node_name:
        for host_inv in kvm_inventory['container_nodes']:
            if container['hostname']  == host_inv['hostname']:
                if host_inv['node_type'] == "ubuntu_container":
                    print(f"deploying static routes on {host_inv['hostname']}")
                    for r in host_inv['routes']:
                        print(f"deploying static route {r['subnet']} via gw {r['gateway']} on {host_inv['hostname']}")
                        os.system("docker exec -it "  + host_inv['hostname'] + " route add -net "+ r['subnet'] + " gw " + r['gateway'])
                else:
                    print(f"container {host_inv['hostname']} with type {host_inv['node_type']} not recognized! ")

