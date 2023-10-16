from jinja2 import Environment, FileSystemLoader, Template, DebugUndefined
import yaml
import argparse
import settings
import container_builder

containers = []

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start and Stop a Containers')
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('-a', '--action', dest='action', type=str, choices=['start_containers','stop_containers'],
                        help='either specify action start_containers or stop_containers to start/stop the containers')

    group.add_argument('-s', '--subaction', dest='subaction', type=str, nargs="+", action="extend",
                        choices=['init_container','init_cont_interfaces', 'init_cont_conf', 'ontainer_interface_delete', 
                        'container_delete', 'init_lldp','init_static_routes'],
                        help='Allow a user to call a subaction of start_containers or stop_containers.')

    parser.add_argument('--hosts', dest='hosts', type=str, nargs="+", required=True,
                        help="at minimum specify '--hosts all' or specify the name of the host in the inventory file.")

    args = parser.parse_args()


    with open(f"{settings.path}/kvm_hosts.yaml", 'r') as file:
        container_hosts = yaml.safe_load(file)

    if args.hosts[0] == 'all':
            [ containers.append(host_inv) for host_inv in container_hosts['container_nodes'] ]     
    else:
        for node_name in args.hosts:
            [ containers.append(host_inv) for c in args.hosts for host_inv in container_hosts if host_inv['hostname'] == c]  

    container_tuple = tuple(containers)
    if args.action == 'start_containers':
        print (f"some dbug output to start containers")

        container_builder.init_container(containers)
        container_builder.init_cont_interfaces(containers)
        container_builder.init_cont_conf(containers)
        container_builder.init_lldp(containers)
        container_builder.init_static_routes(containers)
    elif args.action == 'stop_containers':
        print (f"some dbug output to stop containers")
        container_builder.container_interface_delete(container_tuple)
        container_builder.container_delete(container_tuple)  

