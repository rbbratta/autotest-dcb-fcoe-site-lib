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

import optparse

import sys
import re
import pprint
try:
    from collections import defaultdict
except ImportError:
    import common
    from autotest.client.shared.backports.collections import defaultdict
import dcbtool

lldptool_tni = """
Chassis ID TLV
\tIPv4: 10.0.0.150
Port ID TLV
\tIfname: Te 0/13
Time to Live TLV
\t120
Port Description TLV
\tTe 0/13
System Name TLV
\tbroc150_jack
System Description TLV
\tCEE Switch
System Capabilities TLV
\tSystem capabilities:  Bridge, Router
\tEnabled capabilities: Bridge
Management Address TLV
\tIPv4: 10.0.0.150
Unknown interface subtype: 0
CEE DCBX TLV
\tControl TLV:
\t  SeqNo: 1, AckNo: 3
\tPriority Groups TLV:
\t  Enabled, Not Willing, No Error
\t  PGID Priorities:  0:[0,1,5,7] 1:[3] 2:[4] 3:[2] 4:[6]
\t  PGID Percentages: 0:20% 1:10% 2:40% 3:20% 4:10% 5:0% 6:0% 7:0%
\t  Number of TC's supported: 8
\tPriority Flow Control TLV:
\t  Enabled, Not Willing, No Error
\t  PFC enabled priorities: 2, 3, 4, 6
\t  Number of TC's supported: 8
\tApplication TLV:
\t  Enabled, Not Willing, No Error
\t  Ethertype: 0x8906, Priority Map: 0x04
\t  TCP/UDP Port: 0x0cbc, Priority Map: 0x10
\tUnknown DCBX sub-TLV: 0000800080
\tUnknown DCBX sub-TLV: 0000800180
End of LLDPDU TLV
"""

cee_sub_tlv = """
CEE DCBX TLV
\tControl TLV:
\t  SeqNo: 1, AckNo: 3
\tPriority Groups TLV:
\t  Enabled, Not Willing, No Error
\t  PGID Priorities:  0:[0,1,5,7] 1:[3] 2:[4] 3:[2] 4:[6]
\t  PGID Percentages: 0:20% 1:10% 2:40% 3:20% 4:10% 5:0% 6:0% 7:0%
\t  Number of TC's supported: 8
\tPriority Flow Control TLV:
\t  Enabled, Not Willing, No Error
\t  PFC enabled priorities: 2, 3, 4, 6
\t  Number of TC's supported: 8
\tApplication TLV:
\t  Enabled, Not Willing, No Error
\t  Ethertype: 0x8906, Priority Map: 0x04
\t  TCP/UDP Port: 0x0cbc, Priority Map: 0x10
\tUnknown DCBX sub-TLV: 0000800080
\tUnknown DCBX sub-TLV: 0000800180
"""

lldptool_ti = """Chassis ID TLV
\tMAC: 00:1b:21:87:ac:7d
Port ID TLV
\tMAC: 00:1b:21:87:ac:7d
Time to Live TLV
\t120
CEE DCBX TLV
\tControl TLV:
\t  SeqNo: 8, AckNo: 2
\tPriority Groups TLV:
\t  Enabled, Willing, No Error
\t  PGID Priorities:  0:[0] 1:[1] 2:[2] 3:[3] 4:[4] 5:[5] 6:[6] 7:[7]
\t  PGID Percentages: 0:13% 1:13% 2:13% 3:13% 4:12% 5:12% 6:12% 7:12%
\t  Number of TC's supported: 8
\tPriority Flow Control TLV:
\t  Enabled, Willing, No Error
\t  PFC enabled priorities: none
\t  Number of TC's supported: 8
\tApplication TLV:
\t  Enabled, Willing, No Error
\t  Ethertype: 0x8906, Priority Map: 0x08
\t  TCP/UDP Port: 0x0cbc, Priority Map: 0x10
\t  Ethertype: 0x8914, Priority Map: 0x0f
End of LLDPDU TLV
"""

ieee_lldptool_tni = ieee_lldptool_ti = """Chassis ID TLV
\tMAC: a0:36:9f:0b:3f:9c
Port ID TLV
\tMAC: a0:36:9f:0b:3f:9c
Time to Live TLV
\t120
IEEE 8021QAZ ETS Configuration TLV
\t Willing: no
\t CBS: not supported
\t MAX_TCS: 4
\t PRIO_MAP: 0:0 1:0 2:1 3:1 4:2 5:2 6:3 7:3
\t TC Bandwidth: 25% 25% 25% 25% 0% 0% 0% 0%
\t TSA_MAP: 0:ets 1:ets 2:ets 3:ets 4:strict 5:strict 6:strict 7:strict
IEEE 8021QAZ ETS Recommendation TLV
\t PRIO_MAP:  0:0 1:0 2:1 3:1 4:2 5:2 6:3 7:3
\t TC Bandwidth: 25% 25% 25% 25% 0% 0% 0% 0%
\t TSA_MAP: 0:ets 1:ets 2:ets 3:ets 4:strict 5:strict 6:strict 7:strict
IEEE 8021QAZ PFC TLV
\t Willing: no
\t MACsec Bypass Capable: no
\t PFC capable traffic classes: 4
\t PFC enabled: 1 2 5 7
IEEE 8021QAZ APP TLV
\tApp#0:
\t Priority: 2
\t Sel: 2
\t {S}TCP Port: 3260

\tApp#1:
\t Priority: 5
\t Sel: 1
\t Ethertype: 0x8906

End of LLDPDU TLV
"""


COLON_SPLIT_NO_WHITESPACE_RE = re.compile(r"\s*([^:]+)\s*:\s*(.*)\s*")


def yes_no_to_bool(s):
    return s == 'yes'


def tsa(s):
    key_vals = find_all_colon_key_vals(s)
    return dict((int(k), v) for k, v in key_vals)


def up2tc(s):
    key_vals = find_all_colon_key_vals(s)
    return dict((int(k), int(v)) for k, v in key_vals)


class State(object):

    def __init__(self, parser):
        self.parser = parser


class Start(State):

    def tlv(self, l):
        self.parser.tlv_state.set_tlv_type(l)
        self.parser.state = self.parser.tlv_state

    def non_tlv(self, l):
        # save error TLV
        self.parser.tlv_list.append((l, None))
        return self

    def tlv_data(self, _):
        self.parser.state = self.parser.error_state

    def end_tlv(self, l):
        self.parser.tlv_list.append((l, None))
        self.parser.state = self.parser.end_state


class TLV(State):

    def __init__(self, parser):
        State.__init__(self, parser)
        self.tlv_type = None

    def set_tlv_type(self, l):
        self.name = l

    def tlv(self, _):
        self.tlv_type = None
        self.parser.state = self.parser.error_state

    def non_tlv(self, _):
        self.tlv_type = None
        self.parser.state = self.parser.error_state

    def tlv_data(self, l):
        self.parser.tlv_data_state.start_tlv(self.name, l)
        self.parser.state = self.parser.tlv_data_state

    def end_tlv(self, _):
        self.parser.state = self.parser.error_state


class TLVData(State):

    def __init__(self, parser):
        State.__init__(self, parser)
        self.tlv_type = None
        self.tlv_values = None

    def start_tlv(self, name, l):
        self.tlv_type = name
        self.tlv_values = [l]

    def tlv(self, l):
        self.parser.add_tlv((self.tlv_type, self.tlv_values))
        self.tlv_type = l
        self.tlv_values = []
        self.parser.state = self.parser.tlv_data_state

    def non_tlv(self, l):
        self.parser.add_tlv((self.tlv_type, self.tlv_values))
        self.tlv_type = None
        self.tlv_values = []
        self.parser.tlv_list.append((l, None))
        self.parser.state = self.parser.start_state

    def tlv_data(self, l):
        self.tlv_values.append(l)

    def end_tlv(self, l):
        self.parser.add_tlv((self.tlv_type, self.tlv_values))
        self.tlv_type = None
        self.tlv_values = []
        self.parser.tlv_list.append((l, None))
        self.parser.state = self.parser.end_state


class ErrorState(State):
    pass


class EndState(State):
    pass


class Parser(object):

    def __init__(self, tlv_handlers):
        self.tlv_handlers = tlv_handlers
        self.tlv_list = []
        self.start_state = Start(self)
        self.tlv_state = TLV(self)
        self.tlv_data_state = TLVData(self)
        self.error_state = ErrorState(self)
        self.end_state = EndState(self)

        # not raw string because we use \n
        # pylint: disable=W1401
        self.tlv_re = re.compile("^(\S[^\n]+)TLV")
        # pylint: disable=W1401
        self.tlv_data_re = re.compile("^\\s+([^\n]+)")
        # pylint: disable=W1401
        self.non_tlv_re = re.compile("^(\S[^\n]+)(?!TLV)")
        self.end_tlv_re = re.compile("^End of LLDPDU TLV")

    def add_tlv(self, tlv):
        res = self.tlv_handlers.get(tlv[0], default_handler)(tlv[1])
        self.tlv_list.append((tlv[0], res))

    def parse(self, lines):
        self.state = self.start_state
        # import pdb ; pdb.set_trace()
        if len(sys.argv) > 1 and sys.argv[1] == "rpdb":
            import rpdb2
            rpdb2.start_embedded_debugger('foo', True, True)

        for l in lines.splitlines():
            if self.state == self.error_state:
                raise SyntaxError(l)
            elif self.state == self.end_state:
                return self.tlv_list
            elif self.end_tlv_re.match(l):
                self.state.end_tlv(l)
            elif self.tlv_re.match(l):
                self.state.tlv(l)
            elif self.non_tlv_re.match(l):
                self.state.non_tlv(l)
            elif self.tlv_data_re.match(l):
                self.state.tlv_data(l)
        if self.state == self.end_state:
            return self.tlv_list
        else:
            raise SyntaxError("EOF without End of LLDPDU TLV")


def control_tlv_handler(val):
    values = {}
    for line in val:
        values.update(
            [COLON_SPLIT_NO_WHITESPACE_RE.search(v).groups() for v in line.split(',')])
    return values


def parse_enabled_willing_error(val):
    enabled, willing, error = [s.strip() for s in val.split(',')]
    values = {'Enable': (enabled == 'Enabled'),
              'Willing': (willing == 'Willing'),
              'Errors': error}
    return values


def pgid_priorities(pgid_priorities):
    pgids = re.findall(r'(\d):\[([^]]+)\]', pgid_priorities)
    pgid_map = dict((int(k), map(int, v.split(','))) for k, v in pgids)
    up2tc = {}
    for tc, ups in pgid_map.iteritems():
        for up in ups:
            up2tc[up] = tc
    return up2tc


def pgid_percentages(pgid_percentages):
    percentages = re.findall(r'\d:(\d+)%', pgid_percentages)
    return tuple(int(p) for p in percentages)


def priority_group_tlv_handler(val):
    handlers = {
        'PGID Priorities': pgid_priorities,
        'PGID Percentages': pgid_percentages,
        "Number of TC's supported": int
    }
    values = {}
    values.update(parse_enabled_willing_error(val[0]))
    for v in val[1:]:
        tlv_name, tlv_val = v.split(":", 1)
        values[tlv_name] = handlers[tlv_name](tlv_val)
    return values


def priority_flow_control_tlv_handler(val):
    handlers = {
        'PFC enabled priorities': priority_flow_control_enabled_handler,
        "Number of TC's supported": int
    }
    values = {}
    values.update(parse_enabled_willing_error(val[0]))
    for v in val[1:]:
        tlv_name, tlv_val = v.split(":", 1)
        values[tlv_name] = handlers[tlv_name](tlv_val)
    return values


def priority_flow_control_enabled_handler(pfc_enabled):
    enabled_prios = dict((up, False) for up in range(8))
    enabled_prios.update((int(
        p.strip()), True) for p in pfc_enabled.split(",") if not 'none' in p)
    return enabled_prios


def ieee_priority_flow_control_enabled_handler(pfc_enabled):
    enabled_prios = dict((up, False) for up in range(8))
    enabled_prios.update((int(
        p.strip()), True) for p in pfc_enabled.split() if not 'none' in p)
    return enabled_prios


def application_tlv_handler(val):
# Application TLV:
#   Enabled, Not Willing, No Error
#   Ethertype: 0x8906, Priority Map: 0x04
#   TCP/UDP Port: 0x0cbc, Priority Map: 0x10
    handlers = {
        'Ethertype': int_auto_base,
        'TCP/UDP Port': int_auto_base,
    }
    values = {}
    values.update(parse_enabled_willing_error(val[0]))
    selectors = defaultdict(dict)
    for app in val[1:]:
        selector, priority_map = [tuple(
            s.strip() for s in v.split(':', 1)) for v in app.split(',')]
        # values[selector].
        converted_selector = (selector[0], handlers[selector[0]](selector[1]))
        selectors[converted_selector] = int(priority_map[1], 16)
        # if selector[0] == "Ethertype" and selector[1] == '0x8906':
        #    pass
        # elif selector[0] == "TCP/UDP Port" and selector[1] == '0x0cbc':
        #    pass
    values['Applications'] = dict(selectors)
    return values

sub_tlv_handlers = {
    'Control TLV:': control_tlv_handler,
    'Priority Groups TLV:': priority_group_tlv_handler,
    'Priority Flow Control TLV:': priority_flow_control_tlv_handler,
    'Application TLV:': application_tlv_handler,
}


class CEESubTLVParser(object):

    def __init__(self, tlv_handlers=sub_tlv_handlers):
        self.tlv_handlers = tlv_handlers
        self.tlv_list = []
        self.start_state = Start(self)
        self.tlv_state = TLV(self)
        self.tlv_data_state = TLVData(self)
        self.error_state = ErrorState(self)
        self.end_state = EndState(self)

        self.tlv_re = re.compile("^(?:\t| {8})\S[^\n]+TLV")
        self.tlv_data_re = re.compile("^(?:\t| {8})\s+\S[^\n]+")

    def add_tlv(self, tlv):
        res = self.tlv_handlers.get(tlv[0], default_handler)(tlv[1])
        self.tlv_list.append((tlv[0], res))

    def parse(self, lines):
        self.state = self.start_state

        # raw text TLV for already split into lines
        if '\n' in lines:
            lines = lines.splitlines()

        for l in lines:
            if self.state == self.error_state:
                raise SyntaxError(l)
            elif self.tlv_re.match(l):
                # use lstrip() because we just use the re for matching and
                # discard the groups
                self.state.tlv(l.lstrip())
            elif self.tlv_data_re.match(l):
                self.state.tlv_data(l.lstrip())
        # fake an end tlv
        self.state.end_tlv('')
        return self.tlv_list[:-1]


class IEEEAppTLVParser(object):

    def __init__(self, tlv_handlers={}):
        self.tlv_handlers = tlv_handlers
        self.tlv_list = []
        self.start_state = Start(self)
        self.tlv_state = TLV(self)
        self.tlv_data_state = TLVData(self)
        self.error_state = ErrorState(self)
        self.end_state = EndState(self)

        self.tlv_re = re.compile("^(?:\t| {8})App#\d+:")
        self.tlv_data_re = re.compile("^(?:\t| {8})\s+\S[^\n]+")

    def add_tlv(self, tlv):
        res = self.tlv_handlers.get(tlv[0], default_handler)(tlv[1])
        # TODO: We have a loop in the parser, so it is adding duplicates
        # for now prevent appending duplicates
        if res:
            if (tlv[0], res) not in self.tlv_list:
                self.tlv_list.append((tlv[0], res))

    def parse(self, lines):
        self.state = self.start_state

        # raw text TLV for already split into lines
        if '\n' in lines:
            lines = lines.splitlines()

        for l in lines:
            if self.state == self.error_state:
                raise SyntaxError(l)
            elif self.tlv_re.match(l):
                self.state.tlv(l.lstrip())
            elif self.tlv_data_re.match(l):
                self.state.tlv_data(l.lstrip())
            # fake an end tlv
        self.state.end_tlv('')
        return [tlv for tlv in self.tlv_list[:-1] if tlv[1] is not None]


def default_handler(tlvs):
    values = []
    for tlv in tlvs:
        if ':' in tlv:
            values.append([s.strip() for s in tlv.split(':', 1)])
        else:
            values.append(tlv.strip())
    return values


def sub_tlv_as_dict_handler_factory(sub_tlv_handlers):
    def save_tlvs_as_dict(tlvs):
        values = {}
        for tlv in tlvs:
            if ':' in tlv:
                name, value = COLON_SPLIT_NO_WHITESPACE_RE.search(tlv).groups()
                converted_value = sub_tlv_handlers.get(
                    name, lambda x: x)(value)
                values[name] = converted_value
            else:
                v = tlv.strip()
                values[v] = v
        return values

    return save_tlvs_as_dict

ieee_pfc_handlers = {
    "PFC enabled": ieee_priority_flow_control_enabled_handler,
    "PFC capable traffic classes": int,
    "Willing": yes_no_to_bool,
    "MACsec Bypass Capable": yes_no_to_bool,
}


def cee_sub_tlv_handler_into_list(val):
    p = CEESubTLVParser()
    return p.parse(val)


def cee_sub_tlv_handler(val):
    p = CEESubTLVParser()
    return dict(p.parse(val))


def ieee_app_tlv_handler(val):
    p = IEEEAppTLVParser()
    return dict(p.parse(val))

tlv_handlers = {
    'CEE DCBX TLV': cee_sub_tlv_handler,
    'IEEE 8021QAZ ETS Configuration TLV': sub_tlv_as_dict_handler_factory({}),
    'IEEE 8021QAZ ETS Recommendation TLV': sub_tlv_as_dict_handler_factory({}),
    'IEEE 8021QAZ PFC TLV': sub_tlv_as_dict_handler_factory(ieee_pfc_handlers),
    'IEEE 8021QAZ APP TLV': IEEEAppTLVParser().parse,
}


def parse_into_list(s):
    p = Parser(tlv_handlers)
    return p.parse(s)


def parse(s):
    p = Parser(tlv_handlers)
    return dict(p.parse(s))


def int_auto_base(n):
    """Convert string to an int, automatically detecting the base."""
    return int(n, base=0)


class AppCollector(object):
    def __init__(self):
        super(AppCollector, self).__init__()
        self.apps = {}

    def __call__(self, *args, **kwargs):
        self.apps[dcbtool.comma_sep_ints(args[0])] = True
        return self.apps


set_field_names_transform = {
    'enableTx': "advertise",
}


def parse_set(s):
    set_fields = {
        'enabled': priority_flow_control_enabled_handler,
        'willing': yes_no_to_bool,
        'enableTx': yes_no_to_bool,
        'tsa': tsa,
        'up2tc': up2tc,
        'tcbw': dcbtool.comma_sep_ints,
        'app': AppCollector(),
    }

    parser = optparse.OptionParser(prog="lldptool")
    parser.add_option(
        "-g", action="store", default=False, dest="bridge_scope")
    parser.add_option("-n", choices=("nb", "ncb", "nntpmrb",
                                     "nearest_bridge",
                                     "neareast_customer_bridge",
                                     "nearest_nontpmr_bridge"),
                      dest="neighboor")
    parser.add_option(
        "-T", action="store_true", default=False, dest="set_tlv")
    parser.add_option(
        "-t", action="store_true", default=False, dest="get_tlv")
    parser.add_option(
        "-L", action="store_true", default=False, dest="set_lldp")
    parser.add_option(
        "-l", action="store_true", default=False, dest="get_lldp")
    parser.add_option(
        "-r", action="store_true", default=False, dest="raw_client")
    parser.add_option(
        "-R", action="store_true", default=False, dest="only_raw_client")
    parser.add_option(
        "-c", action="store_true", default=False, dest="query_config")
    parser.add_option("-i", action="store", dest="interface")
    parser.add_option("-V", action="store", dest="tlvid")
    opts, args = parser.parse_args(s.split())
    progname = args[0]
    args = args[1:]
    # by default set max_tcs to 8, we can't even set it on the command line
    vals = {'max_tcs': 8, "interface": opts.interface}
    if not opts.query_config:
        for name, val in (t.split('=') for t in args):
            vals[set_field_names_transform.get(
                # TODO: AppCollector needs to be cleared
                # TODO: can we have multiple for every field?
                name, name)] = set_fields[name](val)
    return vals


if __name__ == '__main__':
    # print parse("    Chassis ID TLV\nTLV\n")
    p = Parser(tlv_handlers)
    pprint.pprint(p.parse(lldptool_ti))
    pprint.pprint(p.parse(ieee_lldptool_ti))
    # pprint.pprint(p.parse(lldptool_tni))
    # p = CEESubTLVParser({})
    # pprint.pprint(p.parse(cee_sub_tlv))


def find_all_colon_key_vals(s):
    return re.findall(r'(\d):(\w+)', s)
