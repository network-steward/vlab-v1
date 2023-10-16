from jinja2 import Environment, FileSystemLoader, Template, DebugUndefined
import yaml
import settings
import argparse
import lab_builder

kvms = []

if __name__ == '__main__':
    with open(f"{settings.path}/kvm_hosts.yaml", 'r') as file:
        kvm_hosts = yaml.safe_load(file)

    parser = argparse.ArgumentParser(description='Start and Stop KVMs.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-a', '--action', dest='action', type=str, choices=['startvlab','stopvlab', 'generate_etc_hosts',
                        'generate_bootstrap_cfg'],
                        help='either specify action startvlab or stopvlab to start/stop the vlab')

    group.add_argument('-s', '--subaction', dest='subaction', type=str, nargs="+", action="extend",
                        choices=['image_init','create_xml', 'create_tap', 'create_ovs', 'define_vm', 'start_vm', 
                        'generate_dhcpd_conf', 'remove_etc_hosts','populate_etc_hosts', 'generate_bootstrap', 'stop_vm',
                        'delete_tap', 'delete_ovs', 'undefine_vm', 'vmx_license' ],
                        help='Allow a user to call a subaction of startvlab or stopvlab.')

    parser.add_argument('--hosts', dest='hosts', type=str, nargs="+", required=True,
                        help="at minimum specify '--hosts all' or specify the name of the host in the inventory file.")

    args = parser.parse_args()

    if args.hosts[0] == 'all':
        for vm in kvm_hosts['kvm_nodes']:
            print(f"Adding {vm['hostname']}  into the list of hosts to work against..")
            kvms.append(vm['hostname'])
        nodes_tuple = tuple(kvms)
    else:
        for node_name in args.hosts:
            print(f"Adding {node_name} into the list of hosts to work against..")
            kvms.append(node_name)
        nodes_tuple = tuple(kvms)

    if args.action == 'startvlab':
        lab_builder.make_xml(nodes_tuple)
        lab_builder.init_image(nodes_tuple)
        lab_builder.init_tap(nodes_tuple)
        lab_builder.init_ovs(nodes_tuple)
        lab_builder.init_vm(nodes_tuple)
        lab_builder.start_vm(nodes_tuple)
    elif args.action == 'stopvlab':
        lab_builder.stop_vm(nodes_tuple)
        lab_builder.delete_tap(nodes_tuple)
        if args.hosts[0] == 'all' :    
            lab_builder.delete_ovs(nodes_tuple)
        lab_builder.undefine_vm(nodes_tuple)

    if args.subaction != None:
        for a in args.subaction:
            print(f"Performing {a} !")
            if a == "image_init":
                lab_builder.image_init(nodes_tuple)
            elif a == "create_xml":    
                lab_builder.create_xml(nodes_tuple)
            elif a == "create_tap":    
                lab_builder.create_tap(nodes_tuple)
            elif a == "create_ovs":    
                lab_builder.create_ovs(nodes_tuple)
            elif a == "define_vm":    
                lab_builder.define_vm(nodes_tuple)
            elif a == "start_vm":    
                lab_builder.start_vm(nodes_tuple)
            elif a == "stop_vm":    
                lab_builder.stop_vm(nodes_tuple)
            elif a == "delete_tap":    
                lab_builder.delete_tap(nodes_tuple)
            elif a == "delete_ovs":    
                lab_builder.delete_ovs(nodes_tuple)
            elif a == "undefine_vm":    
                lab_builder.undefine_vm(nodes_tuple)

