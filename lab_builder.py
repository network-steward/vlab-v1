from jinja2 import Environment, FileSystemLoader, Template, DebugUndefined
import yaml
import os
import shutil
import libvirt
import settings

from libvirt import libvirtError

with open(f'{settings.path}kvm_hosts.yaml', 'r') as file:
        kvm_inventory = yaml.safe_load(file)

env = Environment(loader = FileSystemLoader(f'{settings.path}'), trim_blocks = True, lstrip_blocks=True, undefined=DebugUndefined)
kvm_name = ("veos01", "vjunos01")


def make_xml(kvm_name = ()):
  for vm in kvm_name:
    for host in kvm_inventory['kvm_nodes']:
      if vm == host['hostname']:
        if host['type'] == "veos":
            template = env.get_template('veos-xml.j2')
        elif host['type'] == "vjunos":
            template = env.get_template('vjunos-xml.j2')
        with open(f'{settings.path}{host["hostname"]}.xml','w') as config:
            config.write(template.render(host))
            print(f"created {host['hostname']}.xml !")

def init_image(kvm_name = ()):
  for vm in kvm_name:
    for host in kvm_inventory['kvm_nodes']:
      if vm == host['hostname']:
        if host['type'] == "veos":
            if os.path.exists(f"{settings.path}{host['hostname']}.qcow2"):
              print(f"{settings.path}{host['hostname']}.qcow2 image already exists! not creating image!")
            else:
              print(f"{settings.path}{host['hostname']}.qcow2  image doesn't exist! creating!")
              shutil.copy(f"{settings.base_kvm_images}vEOS-lab-4.27.1.1F.qcow2", f"{settings.path}{host['hostname']}.qcow2" )
        if host['type'] == "vjunos":
            if os.path.exists(f"{settings.path}{host['hostname']}.qcow2"):
              print(f"{settings.path}{host['hostname']}.qcow2 image already exists! not creating image!")
            else:
              print(f"{settings.path}{host['hostname']}.qcow2  image doesn't exist! creating!")
              shutil.copy(f"{settings.base_kvm_images}vjunos-switch-23.1R1.8.qcow2", f"{settings.path}{host['hostname']}.qcow2" )

def init_tap(kvm_name = ()):
  for vm in kvm_name:
    for host in kvm_inventory['kvm_nodes']:
      if vm == host['hostname']:  
        for i in host['interfaces']:
            print(f"creating tap interface {host['hostname']}-{i['interface']}")
            os.system(f"ip tuntap add {host['hostname']}-{i['interface']} mode tap")

def init_ovs(kvm_name = ()):
    """
    no ovswitch python library creates bridges and also passes options.. so onto the CLI we go
    """
    for vm in kvm_name:
        for host_inv in kvm_inventory['kvm_nodes']:
            if vm == host_inv['hostname']:
                if host_inv['type'] != 'vmx_node':
                    for i in host_inv['interfaces']:
                        print("creating ovs bridge " + i['bridge'])
                        os.system("ovs-vsctl add-br " + i['bridge'])
                        os.system("ovs-vsctl set bridge " + i['bridge'] +" other-config:forward-bpdu=true")
                elif host_inv['type'] == 'vmx_node':
                    print("creating ovs bridge " + host_inv['hostname'] + "-cp-br")
                    os.system("ovs-vsctl add-br " + host_inv['hostname'] + "-cp-br")
                    os.system("ovs-vsctl set bridge " + host_inv['hostname'] +"-cp-br other-config:forward-bpdu=true")
                    for i in host_inv['interfaces']:
                        print("creating ovs bridge " + i['bridge'])
                        os.system("ovs-vsctl add-br " + i['bridge'])
                        os.system("ovs-vsctl set bridge " + i['bridge'] +" other-config:forward-bpdu=true")


def init_vm(node_name = ()):
    """
    define the VM in KVM
    """
  
    with libvirt.open("qemu:///system") as virsh:
        for vm in node_name:
            for host_inv in kvm_inventory['kvm_nodes']:
                if vm == host_inv['hostname']:
                  with open (f"{settings.path}{host_inv['hostname']}.xml") as f:
                      xml = f.read()
                  try:
                      virsh_device = virsh.defineXML(xml)
                      print(f"{settings.path}{host_inv['hostname']} has been defined!")
                  except libvirtError as e:
                      if "already exists" in str(e):
                          continue




def start_vm(node_name = ()):
    """
    define the VM in KVM
    """
    with libvirt.open("qemu:///system") as virsh:
        for vm in node_name:
            for host_inv in kvm_inventory['kvm_nodes']:
                if vm == host_inv['hostname']:

                    try:
                        vm = virsh.lookupByName(host_inv['hostname'])
                        vm.create()
                        print(f"{settings.path}{host_inv['hostname']} has been started!")
                    except libvirtError as e:
                        if "already running" in str(e):
                            print(f"{settings.path}{host_inv['hostname']} is already running!")
                            continue
    



def delete_ovs(node_name = ()):
    """
    delete ovs bridges for ALL hosts in inventory file
    """
    for vm in node_name:
        for host_inv in kvm_inventory['kvm_nodes']:
            if vm == host_inv['hostname']:
              for i in host_inv['interfaces']:
                  print("deleting ovs switch: " + i['bridge'])
                  os.system("ovs-vsctl del-br " + i['bridge'])



def delete_tap(node_name = ()):
    """
    delete tap interfaces 
    """
    for vm in node_name:
        for host_inv in kvm_inventory['kvm_nodes']:
            if vm == host_inv['hostname']:
                for i in host_inv['interfaces']:
                    print("deleting tap interface " + host_inv['hostname'] + "-" + i['interface'])
                    os.system("ip tuntap del "+ host_inv['hostname'] + "-" + i['interface'] +" mode tap" )

def stop_vm(node_name = ()):

    with libvirt.open("qemu:///system") as virsh:
        for vm in node_name:
            for host_inv in kvm_inventory['kvm_nodes']:
                if vm == host_inv['hostname']:
              
                  try:
                      virsh_device = virsh.lookupByName(host_inv['hostname'])
                      virsh_device.destroy()
                      print(f"{settings.path}{host_inv['hostname']} has been destroyed/stopped")
                  except libvirtError as e:
                      if "Domain not found" in str(e):
                          continue


def undefine_vm(node_name = ()):

    with libvirt.open("qemu:///system") as virsh:
        for vm in node_name:
            for host_inv in kvm_inventory['kvm_nodes']:
                if vm == host_inv['hostname']:
                  try:
                      virsh_device = virsh.lookupByName(host_inv['hostname'])
                  except libvirtError as e:
                      if "Domain not found" in str(e):
                          continue
                  if virsh_device.isActive():
                      print(f"{settings.path}{host_inv['hostname']} is still active - please destroy first")
                  else:
                      virsh_device.undefine()
                      print(f"{settings.path}{host_inv['hostname']} has been undefined")

