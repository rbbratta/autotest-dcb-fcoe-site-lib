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
#  You should have received a copy of the GNU General Public License along wit
#  this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin St - Fifth Floor, Boston, MA 02110-1301 USA.
#
#  The full GNU General Public License is included in this distribution in
#  the file called "COPYING".

from collections import namedtuple
import logging
import itertools
import math

import lldptool
import dcbtool

try:
    # noinspection PyCompatibility
    bin(1)
except NameError:
    import common
    from autotest.client.shared.backports import bin


MAX_UPS = 8

logging.basicConfig(level=logging.DEBUG)


def format_if_not_none(template, val, func):
    if val is not None:
        return template % func(val)
    else:
        return ""


def bool_to_yes_no(b):
    return ("no", "yes")[b]

bool_to_one_zero = int


def key_colon_value_comma_join(val):
    return ",".join(["%s:%s" % k_v for k_v in val.iteritems()])


def comma_join(val):
    return ",".join(str(v) for v in val)


def bitmask_to_dict(s):
    # appcfg = dict((n, False) for n in range(8))
    # appcfg = dict([(p[0], bool(int(p[1]))) for p in
    # enumerate(bin(s)[:1:-1])])
    return dict([(up, True) for up, enable in enumerate(bin(s)[:1:-1]) if int(enable)])


def make_bitmask(*priorities):
    return "%02x" % int(sum((math.pow(2, n) for n in priorities)))

# class DCBModel(SmartDict):
#     pass
#
# class DCBControlModel(SmartDict):
#     pass
#
# class PFCModel(SmartDict):
#     pass
#
# class ETSModel(SmartDict):
#     pass
#
# class AppPriorityEntry(SmartDict):
#     pass

DCBModel = namedtuple("DCBModel", ["control", "data"])
DCBControlModel = namedtuple(
    "DCBControlModel", ["enable", "advertise", "willing"])
PFCModel = namedtuple("PFCModel", ["enabled", "max_tcs"])
AppPriorityEntry = namedtuple(
    "AppPriorityEntry", ["priority", "selector", "protocol"])
AppModel = namedtuple('AppModel', ['applications'])

# Convert f to strict
ETSModel = namedtuple("ETSModel", ['up2tc', 'tcbw', 'tsa'])


class LLDPTool(object):
    cmd = "lldptool"

    class PFC(DCBModel):

        @classmethod
        def from_lldptool_cee(cls, tlvs):
            """
            :rtype: DCBModel
            """
            lldptool_cee = tlvs['CEE DCBX TLV']['Priority Flow Control TLV:']
            return cls(
                control=DCBControlModel(
                    enable=lldptool_cee["Enable"],
                    # advertise is always true because we are either transmitting
                    #  or receiving when displayed by lldptool
                    advertise=True,
                    willing=lldptool_cee["Willing"]),
                data=PFCModel(
                    enabled=lldptool_cee['PFC enabled priorities'],
                    max_tcs=lldptool_cee["Number of TC's supported"]))

        @classmethod
        def from_lldptool_ieee(cls, tlvs):
            """
            :rtype: DCBModel
            """
            lldptool_ieee = tlvs['IEEE 8021QAZ PFC TLV']
            return cls(
                control=DCBControlModel(
                    enable=True,
                    # advertise is always true because we are either transmitting
                    #  or receiving when displayed by lldptool
                    advertise=True,
                    willing=lldptool.yes_no_to_bool(lldptool_ieee["Willing"])),
                data=ETSModel(
                    enabled=lldptool_ieee['PFC enabled'],
                    max_tcs=lldptool_ieee["PFC capable traffic classes"]))

        @classmethod
        def from_lldptool(cls, output):
            """
            :rtype: DCBModel
            """
            tlvs = lldptool.parse(output)
            # TODO: what if there is both CEE and IEEE?
            if "CEE DCBX TLV" in tlvs:
                return cls.from_lldptool_cee(tlvs)
            elif "IEEE 8021QAZ PFC TLV" in tlvs:
                return cls.from_lldptool_ieee(tlvs)

        @classmethod
        def from_lldptool_set(cls, output):
            """
            :rtype: DCBModel
            """
            cli = lldptool.parse_set(output)
            # max_tcs is 8 by default and cannot be overridden by lldptool
            return cls(
                control=DCBControlModel(
                    # enable is always true for IEEE
                    enable=True,
                    advertise=cli['advertise'],
                    willing=cli['willing']),
                data=PFCModel(
                    enabled=cli['enabled'],
                    max_tcs=cli['max_tcs']))

        @staticmethod
        def pfc_enabled(enabled):
            return ",".join(sorted([str(k) for k, v in enabled.iteritems() if v]))

        @classmethod
        def to_lldptool_set(cls, intf, model):
            """
            :rtype: str
            """
            pfcup = format_if_not_none(
                "enabled=%s", model.data.enabled, cls.pfc_enabled)

            return "%s -Ti %s -V PFC %s %s %s" % (
                LLDPTool.cmd, intf,
                format_if_not_none(
                    "enableTx=%s", model.control.advertise, bool_to_yes_no),
                format_if_not_none(
                    "willing=%s", model.control.willing, bool_to_yes_no),
                pfcup)

    class ETS(DCBModel):

        @classmethod
        def from_lldptool_cee(cls, tlvs):
            """
            :rtype: DCBModel
            """
            lldptool_cee = tlvs['CEE DCBX TLV']['Priority Groups TLV:']
            tsa_map, up2tc = DCBTool.cee_to_ieee_ets(
                lldptool_cee['PGID Priorities'])
            return cls(
                control=DCBControlModel(
                    enable=True,
                    # advertise is always true because we are either transmitting
                    #  or receiving when displayed by lldptool
                    advertise=True,
                    willing=lldptool.yes_no_to_bool(lldptool_cee["Willing"])),
                data=ETSModel(
                    up2tc=up2tc,
                    tcbw=lldptool_cee['PGID Percentages'],
                    tsa=tsa_map))

        @classmethod
        def from_lldptool_ieee(cls, tlvs):
            """
            :rtype: DCBModel
            """
            lldptool_ieee = tlvs['IEEE 8021QAZ ETS Configuration TLV']
            return cls(
                control=DCBControlModel(
                    enable=True,
                    # advertise is always true because we are either transmitting
                    #  or receiving when displayed by lldptool
                    advertise=True,
                    willing=lldptool.yes_no_to_bool(lldptool_ieee["Willing"])),
                data=ETSModel(
                    up2tc=lldptool.up2tc(lldptool_ieee['PRIO_MAP']),
                    tcbw=dcbtool.percentages(lldptool_ieee['TC Bandwidth']),
                    tsa=lldptool.tsa(lldptool_ieee["TSA_MAP"])))

        @classmethod
        def from_lldptool(cls, output):
            """
            :rtype: DCBModel
            """
            tlvs = lldptool.parse(output)
            # TODO: what if there is both CEE and IEEE?
            if "CEE DCBX TLV" in tlvs:
                return cls.from_lldptool_cee(tlvs)
            elif "IEEE 8021QAZ PFC TLV" in tlvs:
                return cls.from_lldptool_ieee(tlvs)

        @classmethod
        def from_lldptool_set(cls, output):
            """
            :rtype: DCBModel
            """
            cli = lldptool.parse_set(output)
            # max_tcs is 8 by default and cannot be overridden by lldptool
            return cls(
                control=DCBControlModel(
                    # enable is always true for IEEE
                    enable=True,
                    advertise=cli.get('advertise', None),
                    willing=cli.get('willing', None)),
                data=ETSModel(
                    tsa=cli['tsa'],
                    up2tc=cli['up2tc'],
                    tcbw=cli['tcbw']))

        @classmethod
        def to_lldptool_set(cls, intf, model, tlv_name='ETS-CFG'):
            """
            :rtype: str
            """
            # TODO: needs more coverage
            # TODO: need ETS-CFG or ETS-REC
            tsa = format_if_not_none(
                "tsa=%s", model.data.tsa, key_colon_value_comma_join)
            up2tc = format_if_not_none(
                "up2tc=%s", model.data.up2tc, key_colon_value_comma_join)
            tcbw = format_if_not_none("tcbw=%s", model.data.tcbw, comma_join)

            return "%s -Ti %s -V %s %s %s %s %s %s" % (
                LLDPTool.cmd, intf, tlv_name,
                format_if_not_none(
                    "enableTx=%s", model.control.advertise, bool_to_yes_no),
                format_if_not_none(
                    "willing=%s", model.control.willing, bool_to_yes_no),
                up2tc, tcbw, tsa)

    class App(DCBModel):

        selectors = {
            'Ethertype': 1,
            'TCP/UDP Port': 4,
        }

        @classmethod
        def from_lldptool_cee(cls, tlvs):
            """
            :rtype: DCBModel
            """
            lldptool_cee = tlvs['CEE DCBX TLV']['Application TLV:']
            # _ = {'Applications': {('Ethertype', 35078): {8: True},
            #                              ('Ethertype', 35092): {8: True},
            #                              ('TCP/UDP Port', 3260): {16: True}}}
            applications = {}
            for app_entry, priority_mask in lldptool_cee['Applications'].iteritems():
                selector, protocol = app_entry
                priorities = bitmask_to_dict(priority_mask)
                for up in priorities:
                    applications[AppPriorityEntry(priority=up,
                                                  selector=cls.selectors[
                                                  selector],
                                                  protocol=protocol)] = True
            return cls(
                control=DCBControlModel(
                    enable=True,
                    # advertise is always true because we are either transmitting
                    #  or receiving when displayed by lldptool
                    advertise=True,
                    willing=lldptool.yes_no_to_bool(lldptool_cee["Willing"])),
                data=AppModel(applications=applications))

        @classmethod
        def from_lldptool_ieee(cls, tlvs):
            """
            :rtype: DCBModel
            """
            lldptool_ieee = tlvs['IEEE 8021QAZ APP TLV']
  #           _ =  ('IEEE 8021QAZ APP TLV',
  # [('App#0:', [['Priority', '2'], ['Sel', '2'], ['{S}TCP Port', '3260']]),
  #  ('App#1:', [['Priority', '5'], ['Sel', '1'], ['Ethertype', '0x8906']])]),
            app_list = (elem[1] for elem in lldptool_ieee)
            # select the second element
            # app_tuples = []
            # for app_entry in app_list:
            #     aaa = []
            #     try:
            #         for c in app_entry:
            #             aaa.append(int(c[1], 0))
            #     except TypeError:
            #         print lldptool_ieee
            #         raise TypeError(lldptool_ieee)
            #     app_tuples.append(aaa)

            app_tuples = ((int(c[
                          1], 0) for c in app_entry) for app_entry in app_list)
            applications = dict((AppPriorityEntry(
                *b), True) for b in app_tuples)

            return cls(
                control=DCBControlModel(
                    enable=True,
                    # advertise is always true because we are either transmitting
                    #  or receiving when displayed by lldptool
                    advertise=True,
                    # IEEE App does not have willing
                    willing=True),
                data=AppModel(applications=applications))

        @classmethod
        def from_lldptool(cls, output):
            """
            :rtype: DCBModel
            """
            tlvs = lldptool.parse(output)
            # TODO: what if there is both CEE and IEEE?
            # return multiple
            # error
            if "CEE DCBX TLV" in tlvs:
                return cls.from_lldptool_cee(tlvs)
            elif "IEEE 8021QAZ APP TLV" in tlvs:
                return cls.from_lldptool_ieee(tlvs)

        @classmethod
        def from_lldptool_set(cls, output):
            cli = lldptool.parse_set(output)
            app_entries = cli['app']
            applications = dict((AppPriorityEntry(
                *app), True) for app in app_entries)

            # max_tcs is 8 by default and cannot be overridden by lldptool
            return cls(
                control=DCBControlModel(
                    # enable is always true for IEEE
                    enable=True,
                    advertise=cli.get('advertise', None),
                    # IEEE App does not have willing
                    willing=True),
                data=AppModel(applications=applications))

        @classmethod
        def to_lldptool_set(cls, intf, model, ):

            # TODO: what if applications is empty?

            # IEEE App does not have willing
            lldptool_strings = ["%s -Ti %s -V APP %s" % (
                LLDPTool.cmd, intf,
                format_if_not_none(
                    "enableTx=%s", model.control.advertise, bool_to_yes_no))]
            lldptool_strings.extend(["app=%s,%s,%s" %
                                    app for app in model.data.applications])
            return " ".join(lldptool_strings)


class DCBTool(object):
    cmd = "dcbtool"

    @staticmethod
    def dcbtool_guess_enable(tlvs):
        try:
            return tlvs['Enable']
        except KeyError:
            try:
                # does "Oper Mode" = True really imply Enable = True
                return tlvs['Oper Mode']
            except KeyError:
                pass
        return None

    @staticmethod
    def dcbtool_guess_advertise(tlvs):
        try:
            # get config
            return tlvs['Advertise']
        except KeyError:
            if tlvs['Command'] == 'Get Peer':
                return True
            else:
                return None
                # must be get oper
                # TODO: fix this or remove it
                try:
                    return tlvs['Sycnd'] is False
                except KeyError:
                    return False
            # for IEEE is not enableTx do we setlocal config?
            return False

    @staticmethod
    def dcbtool_guess_willing(tlvs):
        try:
            # get config
            return tlvs['Willing']
        except KeyError:
            return None

    @staticmethod
    def cee_to_ieee_ets(pgid):
        # set all TCs to strict by default and then set the used TCs to ETS
        # default to ets lest we end up with fffff
        tsa_map = dict((tc, "ets") for tc in range(8))
        # with pgid if up is 'f' then up == tc and tsa='strict'
        # only set "strict" for TC 15 == 0xf == PGID Strict
        tsa_map.update((
            up, "strict") for up, tc in pgid.iteritems() if tc == 15)
        # if there is a strict, find the missing TCs and set that TC to strict
        missing_tcs = frozenset(range(8)) - frozenset(pgid.values())
        # round-robin missing TCs
        cycle = itertools.cycle(missing_tcs)
        up2tc = pgid.copy()
        for up in pgid:
            if pgid[up] == 15:
                up2tc[up] = cycle.next()
        return tsa_map, up2tc

    class PFC(DCBModel):

        @classmethod
        def from_dcbtool_get(cls, output):

            tlvs = dcbtool.parse(output)
            # uppercase Willing
            return cls(
                control=DCBControlModel(
                    enable=DCBTool.dcbtool_guess_enable(tlvs),
                    advertise=DCBTool.dcbtool_guess_advertise(tlvs),
                    willing=DCBTool.dcbtool_guess_willing(tlvs)),
                data=PFCModel(
                    enabled=tlvs['pfcup'],
                    max_tcs=tlvs["num TC's"],
                ))

        @classmethod
        def from_dcbtool_set(cls, output):
            cli = dcbtool.parse_set(output)
            # 8 is default and cannot be overridden by dcbtool sc
            return cls(
                control=DCBControlModel(
                    enable=cli['enable'],
                    advertise=cli['advertise'],
                    willing=cli['willing']),
                data=PFCModel(
                    enabled=cli['pfcup'],
                    max_tcs=8))

        @staticmethod
        def pfc_enabled(enabled):
            bool_enabled = (
                enabled.get(prio, False) for prio in range(MAX_UPS))
            return "%s" % "".join((str(int(n)) for n in bool_enabled))

        @classmethod
        def to_dcbtool_set(cls, intf, model):
            # TODO: auto-detect pg versus pfc versus app
            pfcup = format_if_not_none(
                "pfcup:%s", model.data.enabled, cls.pfc_enabled)

            # covert bool to int with %d
            return "%s sc %s pfc %s %s %s %s" % (
                DCBTool.cmd, intf,
                format_if_not_none(
                    "e:%d", model.control.enable, bool_to_one_zero),
                format_if_not_none(
                    "a:%d", model.control.advertise, bool_to_one_zero),
                format_if_not_none(
                    "w:%d", model.control.willing, bool_to_one_zero),
                pfcup)

    class ETS(DCBModel):

        @classmethod
        def from_dcbtool_get(cls, output):

            tlvs = dcbtool.parse(output)
            # uppercase Willing
            tsa_map, up2tc = DCBTool.cee_to_ieee_ets(tlvs['pgid'])

            return cls(
                control=DCBControlModel(
                    enable=DCBTool.dcbtool_guess_enable(tlvs),
                    advertise=DCBTool.dcbtool_guess_advertise(tlvs),
                    willing=DCBTool.dcbtool_guess_willing(tlvs)),
                data=ETSModel(
                    up2tc=up2tc,
                    tcbw=tlvs["pgpct"],
                    tsa=tsa_map,
                ))

        @classmethod
        def from_dcbtool_set(cls, output):
            cli = dcbtool.parse_set(output)
            tsa_map, up2tc = DCBTool.cee_to_ieee_ets(cli['pgid'])

            return cls(
                control=DCBControlModel(
                    enable=cli['enable'],
                    advertise=cli['advertise'],
                    willing=cli['willing']),
                data=ETSModel(
                    up2tc=up2tc,
                    tcbw=cli['pgpct'],
                    tsa=tsa_map))

        @classmethod
        def get_pgid(cls, up2tc, tsa):
            if up2tc is not None and tsa is not None:
                pgid = dict((up, str(tc)) for up, tc in up2tc.iteritems())
                strict = ((
                    up, 'f') for up, tsa in tsa.iteritems() if tsa == 'strict')
                pgid.update(strict)
            else:
                return ""
            return "pgid:%s" % "".join(pgid.itervalues())

        @classmethod
        def to_dcbtool_set(cls, intf, model):

            # TODO: auto-detect pg versus pfc versus app
            pgid = cls.get_pgid(model.data.up2tc, model.data.tsa)
            pgpct = format_if_not_none("pgpct:%s", model.data.tcbw, comma_join)

            # covert bool to int with %d
            return "%s sc %s pg %s %s %s %s %s" % (
                DCBTool.cmd, intf,
                format_if_not_none(
                    "e:%d", model.control.enable, bool_to_one_zero),
                format_if_not_none(
                    "a:%d", model.control.advertise, bool_to_one_zero),
                format_if_not_none(
                    "w:%d", model.control.willing, bool_to_one_zero),
                pgid, pgpct)

    class App(DCBModel):

        @staticmethod
        def cee_appcfg(*priorities):
            return "appcfg:%s" % make_bitmask(*priorities)

        @classmethod
        def get_protocol_and_selector(cls, name):
            if name in ('Application FCoE', 'app:0', 'app:fcoe'):
                return 1, 0x8906
            elif name in ('Application iSCSI', 'app:1', 'app:iscsi'):
                return 4, 3260
            elif name in ('Application FIP', 'app:2', 'app:fip'):
                return 1, 0x8914

        @classmethod
        def from_dcbtool_get(cls, output):

            tlvs = dcbtool.parse(output)
            selector, protocol = cls.get_protocol_and_selector(tlvs['Feature'])
            priorities = bitmask_to_dict(tlvs['appcfg'])
            applications = dict(
                ((AppPriorityEntry(priority=up, selector=selector,
                 protocol=protocol), True) for up in priorities)
            )
            return cls(
                control=DCBControlModel(
                    enable=DCBTool.dcbtool_guess_enable(tlvs),
                    advertise=DCBTool.dcbtool_guess_advertise(tlvs),
                    willing=DCBTool.dcbtool_guess_willing(tlvs)),
                data=AppModel(applications=applications))

        @classmethod
        def from_dcbtool_set(cls, output):
            cli = dcbtool.parse_set(output)
            selector, protocol = cls.get_protocol_and_selector(cli['feature'])
            priorities = bitmask_to_dict(cli['appcfg'])
            applications = dict(
                ((AppPriorityEntry(priority=up, selector=selector,
                 protocol=protocol), True) for up in priorities)
            )
            return cls(
                control=DCBControlModel(
                    enable=cli['enable'],
                    advertise=cli['advertise'],
                    willing=cli['willing']),
                data=AppModel(
                    applications=applications))

        @classmethod
        def to_lldptool_set(cls, intf, model, ):
            # TODO: what if applications is empty?
            lldptool_strings = ["%s -Ti %s -V APP %s %s" % (
                LLDPTool.cmd, intf,
                format_if_not_none(
                    "enableTx=%s", model.control.advertise, bool_to_yes_no),
                format_if_not_none(
                    "willing=%s", model.control.willing, bool_to_yes_no))]
            lldptool_strings.extend(["app=%s,%s,%s" %
                                    app for app in model.data.applications])
            return " ".join(lldptool_strings)

        @classmethod
        def make_dcbtool_cmd_line(cls, intf, model, protocol, appcfg):
            return "%s sc %s %s %s %s %s %s" % (
                DCBTool.cmd, intf, protocol,
                format_if_not_none(
                    "e:%d", model.control.enable, bool_to_one_zero),
                format_if_not_none(
                    "a:%d", model.control.advertise, bool_to_one_zero),
                format_if_not_none(
                    "w:%d", model.control.willing, bool_to_one_zero),
                appcfg)

        @classmethod
        def to_dcbtool_set(cls, intf, model):

            fcoe_apps = (
                app for app in model.data.applications if app.protocol == 0x8906 and app.selector == 1)
            fcoe_ups = cls.cee_appcfg(*(a.priority for a in fcoe_apps))
            fip_apps = (
                app for app in model.data.applications if app.protocol == 0x8914 and app.selector == 1)
            fip_ups = cls.cee_appcfg(*(a.priority for a in fip_apps))
            iscsi_apps = (
                app for app in model.data.applications if app.protocol == 3260 and app.selector in (2, 4))
            iscsi_ups = cls.cee_appcfg(*(a.priority for a in iscsi_apps))

            protocols = []
            if fcoe_ups:
                protocols.append(cls.make_dcbtool_cmd_line(
                    intf, model, "app:fcoe", fcoe_ups))
            elif fip_ups:
                protocols.append(cls.make_dcbtool_cmd_line(
                    intf, model, "app:fip", fip_ups))
            elif iscsi_ups:
                protocols.append(cls.make_dcbtool_cmd_line(
                    intf, model, "app:iscsi", iscsi_ups))
            return protocols
