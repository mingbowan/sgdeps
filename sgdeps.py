#!/usr/bin/env python
from __future__ import print_function
from boto.ec2 import connect_to_region, regions
from sys import exit
import argparse
import textwrap

class Sg_deps(object):

    """to list AWS security group dependencies"""

    def __init__(self, region_name):
        """collect info for a region """
        if not region_name or region_name not in map(lambda x: x.name, regions()):
            print("\nError: please specify a valid region name with --region ")
            print("  valid regions: " + ", ".join(map(lambda x: x.name, regions()))+ "\n")
            exit(1)
        self.sg_by_id={}
        self.sg_by_name={}
        try:
            sgs =  connect_to_region(region_name).get_all_security_groups()
        except Exception as e:
            print("\nError: please check your credentials and network connectivity\n")
            exit(1)
        for sg in sgs:
            self.sg_by_name[sg.name] = sg.id
            if sg.id not in self.sg_by_id:
                self.sg_by_id[sg.id] = {}
                self.sg_by_id[sg.id]["deps"]=set()
            self.sg_by_id[sg.id]["name"] = sg.name
            for rule in sg.rules:
                for grant in rule.grants:
                    if not grant.group_id:
                        continue
                    if grant.group_id not in self.sg_by_id:
                        self.sg_by_id[grant.group_id]={}
                        self.sg_by_id[grant.group_id]["deps"]=set()
                    self.sg_by_id[grant.group_id]["deps"].add(sg.id)

    def show_sg(self, sg):
        if sg:
            if sg in self.sg_by_id:
                sgid = sg
            elif sg in self.sg_by_name:
                sgid= self.sg_by_name[sg]
            else:
                print("\nError: cannot find the security group with name or id: " + sg + "\n")
                exit(1)
            self._show(sgid, [], [])
        else:
            for sgid in self.sg_by_id:
                print()
                self._show(sgid, [], [])

    def _show(self, sgid, previous, indent):
        if not previous:
            print(self._string_sg(sgid), end="")
        else:
            pre = "".join(["|  " if x else "   " for x in indent[:-1]])
            if indent[-1]:
                pre += "|--"
            else:
                pre += "`--"
            print(pre + " " + self._string_sg(sgid), end="")
        if sgid in previous:
            print(" ** loop")
            return
        else:
            print()
        deps =list(self.sg_by_id[sgid]["deps"])
        for dep in deps:
            if dep == deps[-1]:
                self._show(dep, previous+[sgid], indent+[False])
            else:
                self._show(dep, previous+[sgid], indent+[True])



    def _string_sg(self, sgid):
        if "name" not in self.sg_by_id[sgid]:
            name = " N/A "
        elif not self.sg_by_id[sgid]["name"]:
            name = " N/A "
        else:
            name= self.sg_by_id[sgid]["name"]
        return sgid + " ("+ name + ")"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description="show AWS security group dependencies", epilog=textwrap.dedent('''
        please setup your boto credentails first.
            here's a few options:
             setup environment varialbes: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
             or create one or some of below files (boto will evaluate in order):
                /etc/boto.cfg
                ~/.boto
                ~/.aws/credentials 
             and put your credentials in the file(s) with below format:
               [Credentials]
               aws_access_key_id = <your_access_key_here>
               aws_secret_access_key = <your_secret_key_here>'''))
    parser.add_argument("--region", choices=map(lambda x: x.name, regions()), help="region connect to")
    parser.add_argument("security_group", help="security group id or name, id takes precedence, if you have more than one group with same name, this program will show random one, you should use group id instead. leave empty for all groups", default="", nargs="?")
    args=parser.parse_args()
    Sg_deps(args.region).show_sg(args.security_group)
