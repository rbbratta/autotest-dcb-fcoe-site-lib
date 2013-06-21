#!/usr/bin/env python

#  Copyright(c) 2013 Intel Corporation.
#
#  This program is free software; you can redistribute it and/or modify it
#  under the terms and conditions of the GNU General Public License,
#  version 2, as published by the Free Software Foundation.
#
#  This program is distributed in the hope it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin St - Fifth Floor, Boston, MA 02110-1301 USA.
#
#  The full GNU General Public License is included in this distribution in
#  the file called "COPYING".


import re
import logging
import pprint

split_values = re.compile(r"^(\w[^:]+):\s+(\S.*)$\n", re.M)


def comma_sep_ints(s):
    # autodetect int base because we may get 0x04
    return tuple(int(p, 0) for p in s.split(','))


def str2bool(s):
    return not (s in ['False', 'false', '0', 0, 0.0, [], '', ])


def default(s):
    return s


def errors(s):
    num, _, s = s.split()
    return int(num, 0), s


def up2tc(s):
    """ '0       0       3       1       2       0       4       0'
    -> {0: 0, 1: 0, 2: 3, 3: 1, 4: 2, 5: 0, 6: 4, 7: 0} """
    return dict(enumerate([int(n, 16) for n in s]))


def percentages(s):
    pct = re.compile(r"(\d+)%")
    # import pdb ; pdb.set_trace()
    return tuple(int(w) for w in pct.findall(s))


def enable_bits(s):
    # Set all Bits to either True or False
    return dict([(p[0], bool(p[1])) for p in enumerate([int(n, 16) for n in s])])

get_oper_fields = {
    "Oper Mode": str2bool,
    "Syncd": str2bool,
    "Enable": str2bool,
    "Willing": str2bool,
    "Advertise": str2bool,
    "Oper Version": int,
    "Max Version": int,
    "Errors": errors,
    "up2tc": lambda x: up2tc(x.split()),
    # pgid 'f' is LSP so the pgids are in hex
    "pgid": lambda x: up2tc(x.split()),
    "pg strict": lambda x: enable_bits(x.split()),
    "appcfg": lambda x: int(x, 16),
    "num TC's": int,
    "pfcup": lambda x: enable_bits(x.split()),
    "pgpct": percentages,
    "uppct": percentages
}


def parse(s):

    entries = split_values.findall(s)
    vals = {}
    for name, val in entries:
        # print e
        vals[name] = get_oper_fields.get(name, default)(val)

    # import pprint ; pprint.pprint(vals)
    return vals


def get_app(app):
    if app == '0':
        return 'fcoe'
    elif app == '1':
        return 'iscsi'
    elif app == '2':
        return 'fip'
    else:
        return app

set_oper_fields = {
    'e': str2bool,
    'a': str2bool,
    'w': str2bool,
    'pfcup': enable_bits,
    'pgid': up2tc,
    'pgpct': comma_sep_ints,
    'uppct': comma_sep_ints,
    "appcfg": lambda x: int(x, 16),
}


set_field_name_transform = {
    'e': lambda x: 'enable',
    'a': lambda x: 'advertise',
    'w': lambda x: 'willing',
}


def parse_set(s):

    args = s.split()
    vals = {'interface': args[2], 'feature': args[3]}
    feature_args = args[4:]
    entries = [f.split(':') for f in feature_args]
    for e in entries:
        key = set_field_name_transform.get(e[0], default)(e[0])
        # print e
        vals[key] = set_oper_fields.get(e[0], default)(e[1])

    logging.debug(pprint.pformat(vals))
    return vals


if __name__ == "__main__":
    dcbtool_go_pg = """Command:        Get Oper
Feature:        Priority Groups
Port:           eth3
Status:         Successful
Oper Version:   0
Max Version:    0
Errors:         0x00 - none
Oper Mode:      true
Syncd:          true
up2tc:          0       0       3       1       2       0       4       0
pgpct:          20%     10%     40%     20%     10%     0%      0%      0%
pgid:           0       0       3       1       2       0       4       0
uppct:          25%     25%     100%    100%    100%    25%     100%    25%
pg strict:      0       0       0       0       0       0       0       0
"""
    pprint.pprint(parse(dcbtool_go_pg))

    dcbtool_gc_pfc = """
Command:        Get Config
Feature:        Priority Flow Control
Port:           eth3
Status:         Successful
Enable:         true
Advertise:      true
Willing:        false
pfcup:          0       0       1       1       1       0       1       0
num TC's:       8
"""

    pprint.pprint(parse(dcbtool_gc_pfc))

    dcbtool_go_app_fcoe = """
Command:        Get Oper
Feature:        Application FCoE
Port:           eth3
Status:         Successful
Oper Version:   0
Max Version:    0
Errors:         0x00 - none
Oper Mode:      true
Syncd:          true
appcfg:         40
"""

    pprint.pprint(parse(dcbtool_go_app_fcoe))

    dcbtool_go_app_iscsi = """
Command:        Get Oper
Feature:        Application iSCSI
Port:           eth3
Status:         Successful
Oper Version:   0
Max Version:    0
Errors:         0x00 - none
Oper Mode:      true
Syncd:          true
appcfg:         10
"""

    pprint.pprint(parse(dcbtool_go_app_iscsi))
