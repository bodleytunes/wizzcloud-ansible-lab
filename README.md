Work in progress...
Starting a new version of the ovh cloud deployment lab but based entirely on Ansible rather than using mostly saltstack.

Examples:

###### Run the whole playbook

```
   ansible-playbook -i inventory.ini day0.yml --tags ovh_deploy
   ansible-playbook -i inventory.ini day0.yml 
```

##### Run specific Roles

```
 ansible-playbook -i inventory.ini day0.yml --tags proxmox
 ansible-playbook -i inventory.ini day0.yml --tags users
 ansible-playbook -i inventory.ini day0.yml --tags networking
 ansible-playbook -i inventory.ini day0.yml --tags firewall
 ```