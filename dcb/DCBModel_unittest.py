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

import os

import unittest
import DCBModel
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
\t  Ethertype: 0x8914, Priority Map: 0x08
\tUnknown DCBX sub-TLV: 0000800080
\tUnknown DCBX sub-TLV: 0000800180
End of LLDPDU TLV
"""

ieee_lldptool_tni = """Chassis ID TLV
\tMAC: 00:1b:21:90:8d:e8
Port ID TLV
\tMAC: 00:1b:21:90:8d:e8
Time to Live TLV
\t120
IEEE 8021QAZ ETS Configuration TLV
\t Willing: yes
\t CBS: not supported
 \t MAX_TCS: 8
\t PRIO_MAP: 0:0 1:1 2:2 3:3 4:4 5:5 6:6 7:7
\t TC Bandwidth: 12% 12% 12% 12% 13% 13% 13% 13%
\t TSA_MAP: 0:ets 1:ets 2:ets 3:ets 4:ets 5:ets 6:ets 7:ets
IEEE 8021QAZ PFC TLV
\t Willing: yes
\t MACsec Bypass Capable: no
\t PFC capable traffic classes: 8
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


class test_PFC(unittest.TestCase):

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

    def test_pfc_lldptool_get_eq_dcbtool_get(self):
        lldptool_pfc = DCBModel.LLDPTool.PFC.from_lldptool(lldptool_tni)
        dcbtool_pfc = DCBModel.DCBTool.PFC.from_dcbtool_get(
            self.dcbtool_gc_pfc)
        assert dcbtool_pfc == lldptool_pfc

    def test_pfc_dcbtool_get_eq_dcbtool_set(self):
        gc_pfc = DCBModel.DCBTool.PFC.from_dcbtool_get(self.dcbtool_gc_pfc)
        dcbtool_sc_pfc = "dcbtool sc eth3 pfc e:1 a:1 w:0 pfcup:00111010"
        sc_pfc = DCBModel.DCBTool.PFC.from_dcbtool_set(dcbtool_sc_pfc)
        assert gc_pfc == sc_pfc

    @staticmethod
    def test_pfc_lldptool_get_eq_lldptool_set():
        lldptool_pfc = DCBModel.LLDPTool.PFC.from_lldptool(lldptool_tni)
        lldptool_set_pfc = "lldptool -Ti eth3 -V PFC enableTx=yes willing=no enabled=2,3,4,6"
        set_pfc = DCBModel.LLDPTool.PFC.from_lldptool_set(lldptool_set_pfc)
        print set_pfc
        assert lldptool_pfc == set_pfc

    @staticmethod
    def test_lldptool_get_pfc_enabled():
        enabled = {0: 1, 1: 1, 2: 0, 3: 0, 4: 0, 5: 0, 6: 1, 7: 1}
        assert DCBModel.LLDPTool.PFC.pfc_enabled(enabled) == "0,1,6,7"

    @staticmethod
    def test_dcbtool_get_pfc_enabled():
        enabled = {0: 1, 1: 1, 2: 0, 3: 0, 4: 0, 5: 0, 6: 1, 7: 1}
        assert DCBModel.DCBTool.PFC.pfc_enabled(enabled) == "11000011"

    @staticmethod
    def test_pfc_from_dcbtool_set_to_dcbtool_set():
        orig_dcbtool_sc_pfc = "dcbtool sc eth3 pfc e:1 a:1 w:0 pfcup:00111010"
        pfc_model = DCBModel.DCBTool.PFC.from_dcbtool_set(orig_dcbtool_sc_pfc)
        to_sc_pfc = DCBModel.DCBTool.PFC.to_dcbtool_set("eth3", pfc_model)
        assert orig_dcbtool_sc_pfc == to_sc_pfc

    @staticmethod
    def test_pfc_lldptool_set_eq_dcbtool_set():
        lldptool_set_pfc = "lldptool -Ti eth3 -V PFC enableTx=yes willing=no enabled=2,3,4,6"
        pfc_model = DCBModel.LLDPTool.PFC.from_lldptool_set(lldptool_set_pfc)
        to_sc_pfc = DCBModel.DCBTool.PFC.to_dcbtool_set("eth3", pfc_model)
        assert to_sc_pfc == "dcbtool sc eth3 pfc e:1 a:1 w:0 pfcup:00111010"

    @staticmethod
    def test_pfc_dcbtool_set_eq_lldptool_set():
        orig_dcbtool_sc_pfc = "dcbtool sc eth3 pfc e:1 a:1 w:0 pfcup:00111010"
        pfc_model = DCBModel.DCBTool.PFC.from_dcbtool_set(orig_dcbtool_sc_pfc)
        lldptool_set_pfc = DCBModel.LLDPTool.PFC.to_lldptool_set(
            "eth3", pfc_model)
        assert lldptool_set_pfc == "lldptool -Ti eth3 -V PFC enableTx=yes willing=no enabled=2,3,4,6"


class test_ETS(unittest.TestCase):

    @staticmethod
    def test_ets_lldptool_from():
        lldptool_ets = DCBModel.LLDPTool.ETS.from_lldptool(ieee_lldptool_tni)
        assert lldptool_ets.control.enable
        assert lldptool_ets.control.advertise
        assert lldptool_ets.control.willing
        assert lldptool_ets.data.up2tc == {0: 0, 1: 1, 2: 2, 3: 3,
                                           4: 4, 5: 5, 6: 6, 7: 7}
        assert lldptool_ets.data.tsa == {0: 'ets', 1: 'ets', 2:
                                         'ets', 3: 'ets', 4: 'ets', 5: 'ets', 6: 'ets', 7: 'ets'}
        assert lldptool_ets.data.tcbw == (12, 12, 12, 12, 13, 13, 13, 13)

    @staticmethod
    def test_ets_lldptool_from_set():
        lldptool_ets = DCBModel.LLDPTool.ETS.from_lldptool_set(
            "lldptool -Ti eth3 -V ETS-CFG enableTx=yes willing=yes "
            "tsa=0:ets,1:ets,2:ets,3:ets,4:ets,5:ets,6:ets,7:ets "
            "up2tc=0:0,1:1,2:2,3:3,4:4,5:5,6:6,7:7 tcbw=12,12,12,12,13,13,13,13")
        assert lldptool_ets.data.up2tc == {0: 0, 1: 1, 2: 2, 3: 3,
                                           4: 4, 5: 5, 6: 6, 7: 7}
        assert lldptool_ets.data.tsa == {0: 'ets', 1: 'ets', 2:
                                         'ets', 3: 'ets', 4: 'ets', 5: 'ets', 6: 'ets', 7: 'ets'}
        assert lldptool_ets.data.tcbw == (12, 12, 12, 12, 13, 13, 13, 13)

    @staticmethod
    def test_ets_lldptool_get_eq_lldptool_set():
        lldptool_ets_model = DCBModel.LLDPTool.ETS.from_lldptool(
            ieee_lldptool_tni)
        lldptool_ets_set_model = DCBModel.LLDPTool.ETS.from_lldptool_set(
            "lldptool -Ti eth3 -V ETS-CFG enableTx=yes willing=yes "
            "tsa=0:ets,1:ets,2:ets,3:ets,4:ets,5:ets,6:ets,7:ets "
            "up2tc=0:0,1:1,2:2,3:3,4:4,5:5,6:6,7:7 tcbw=12,12,12,12,13,13,13,13")
        assert lldptool_ets_model == lldptool_ets_set_model

    @staticmethod
    def test_ets_lldptool_get_cee():
        lldptool_ets = DCBModel.LLDPTool.ETS.from_lldptool(lldptool_tni)
        assert lldptool_ets.data.up2tc == {0: 0, 1: 0, 2: 3, 3: 1,
                                           4: 2, 5: 0, 6: 4, 7: 0}
        assert lldptool_ets.data.tcbw == (20, 10, 40, 20, 10, 0, 0, 0)
        assert lldptool_ets.data.tsa == {
            0: 'ets',
            1: 'ets',
            2: 'ets',
            3: 'ets',
            4: 'ets',
            5: 'ets',
            6: 'ets',
            7: 'ets',
        }

    @staticmethod
    def test_ets_lldptool_get_cee_eq_lldptool_set():
        lldptool_cee_ets = DCBModel.LLDPTool.ETS.from_lldptool(lldptool_tni)
        lldptool_ets = DCBModel.LLDPTool.ETS.from_lldptool_set(
            "lldptool -Ti eth3 -V ETS-CFG enableTx=yes willing=no" " "
            "up2tc=0:0,1:0,2:3,3:1,4:2,5:0,6:4,7:0 tcbw=20,10,40,20,10,0,0,0" " "
            "tsa=0:ets,1:ets,2:ets,3:ets,4:ets,5:ets,6:ets,7:ets")
        assert lldptool_cee_ets.control == lldptool_ets.control
        assert lldptool_cee_ets.data == lldptool_ets.data

    @staticmethod
    def test_ets_dcbtool_get_cee_eq_lldptool_set():
        dcbtool_go_pg = """
Command:        Get Oper
Feature:        Priority Groups
Port:           eth3
Status:         Successful
Oper Version:   0
Max Version:    0
Errors:         0x00 - none
Oper Mode:      true
Syncd:          true
up2tc:          0       0       3       1       2       0       4       0
pgpct:          20%     10%     40%     30%     0%      0%      0%      0%
pgid:           0       0       3       1       2       0       f       0
uppct:          25%     25%     100%    100%    100%    25%     100%    25%
pg strict:      0       0       0       0       0       0       0       0
"""
        lldptool_cee_ets = DCBModel.DCBTool.ETS.from_dcbtool_get(dcbtool_go_pg)
        lldptool_ets = DCBModel.LLDPTool.ETS.from_lldptool_set(
            "lldptool -Ti eth3 -V ETS-CFG " " "
            "up2tc=0:0,1:0,2:3,3:1,4:2,5:0,6:4,7:0 tcbw=20,10,40,30,00,0,0,0" " "
            "tsa=0:ets,1:ets,2:ets,3:ets,4:ets,5:ets,6:strict,7:ets")
        assert lldptool_cee_ets.control == lldptool_ets.control
        assert lldptool_cee_ets.data == lldptool_ets.data

    @staticmethod
    def test_ets_lldptool_get_ieee_eq_from_dcbtool_set():
        lldptool_ets = DCBModel.LLDPTool.ETS.from_lldptool(ieee_lldptool_tni)
        dcbtool_ets = DCBModel.DCBTool.ETS.from_dcbtool_set(
            "dcbtool sc eth3 pg e:1 a:1 w:1 uppct:7,6,5,4,3,2,1,0 pgid:01234567 pgpct:12,12,12,12,13,13,13,13")
        assert lldptool_ets.control == dcbtool_ets.control
        assert lldptool_ets.data == dcbtool_ets.data

    @staticmethod
    def test_ets_lldptool_get_ieee_eq_to_dcbtool_set():
        ets_model = DCBModel.LLDPTool.ETS.from_lldptool(ieee_lldptool_tni)
        to_set_ets = DCBModel.DCBTool.ETS.to_dcbtool_set("eth3", ets_model)
        assert to_set_ets == \
            "dcbtool sc eth3 pg e:1 a:1 w:1 pgid:01234567 pgpct:12,12,12,12,13,13,13,13"

    @staticmethod
    def test_ets_from_dcbtool_set_eq_from_dcbtool_set():
        from_dcbtool_set = "dcbtool sc eth3 pg e:1 a:1 w:1 pgid:0f23f56f pgpct:21,0,22,15,0,21,21,0"
        ets_model = DCBModel.DCBTool.ETS.from_dcbtool_set(from_dcbtool_set)
        to_set_ets = DCBModel.DCBTool.ETS.to_dcbtool_set("eth3", ets_model)
        assert from_dcbtool_set == to_set_ets

    @staticmethod
    def test_ets_dcbtool_get_eq_from_dcbtool_set():
        from_dcbtool_set = "dcbtool sc eth3 pg e:1 a:1 w:1 pgid:0f23f56f pgpct:21,0,22,15,0,21,21,0"
        ets_model = DCBModel.DCBTool.ETS.from_dcbtool_set(from_dcbtool_set)
        to_set_ets = DCBModel.LLDPTool.ETS.to_lldptool_set("eth3", ets_model)
        assert to_set_ets == "lldptool -Ti eth3 -V ETS-CFG enableTx=yes willing=yes up2tc=0:0,1:1,2:2,3:3,4:4,5:5,6:6,7:7 tcbw=21,0,22,15,0,21,21,0 tsa=0:ets,1:strict,2:ets,3:ets,4:strict,5:ets,6:ets,7:strict"

    @staticmethod
    def test_ets_lldptool_set_eq_from_dcbtool_set():
        from_lldptool_set = "lldptool -Ti eth3 -V ETS-CFG enableTx=yes willing=yes up2tc=0:0,1:1,2:2,3:3,4:4,5:5,6:6,7:7 tcbw=21,0,22,15,0,21,21,0 tsa=0:ets,1:strict,2:ets,3:ets,4:strict,5:ets,6:ets,7:strict"
        from_dcbtool_set = "dcbtool sc eth3 pg e:1 a:1 w:1 pgid:0f23f56f pgpct:21,0,22,15,0,21,21,0"
        dcbtool_ets_model = DCBModel.DCBTool.ETS.from_dcbtool_set(
            from_dcbtool_set)
        lldptool_ets_model = DCBModel.LLDPTool.ETS.from_lldptool_set(
            from_lldptool_set)
        to_set_ets = DCBModel.LLDPTool.ETS.to_lldptool_set(
            "eth3", dcbtool_ets_model)
        assert to_set_ets == from_lldptool_set
        assert dcbtool_ets_model == lldptool_ets_model

    @staticmethod
    def test_ets_weird():
        from_dcbtool_set = 'dcbtool sc eth3 pg e:1 a:0 w:0 pgid:77117716 pgpct:0,5,0,0,0,0,30,65'
        dcbtool_ets_model = DCBModel.DCBTool.ETS.from_dcbtool_set(
            from_dcbtool_set)
        assert dcbtool_ets_model.data.up2tc == {
            0: 7, 1: 7, 2: 1, 3: 1, 4: 7, 5: 7, 6: 1, 7: 6}
        assert dcbtool_ets_model.data.tsa == dict((n, 'ets') for n in range(8))
        to_set_ets = DCBModel.DCBTool.ETS.to_dcbtool_set(
            "eth3", dcbtool_ets_model)
        assert from_dcbtool_set == to_set_ets


class test_App(unittest.TestCase):

    @staticmethod
    def test_app_lldptool_get_cee():
        lldptool_app = DCBModel.LLDPTool.App.from_lldptool(lldptool_tni)
        assert lldptool_app.control.enable
        assert lldptool_app.control.advertise
        assert not lldptool_app.control.willing
        assert set(lldptool_app.data.applications) == set({
            DCBModel.AppPriorityEntry(2, 1, 35078): True,
            DCBModel.AppPriorityEntry(3, 1, 35092): True,
            DCBModel.AppPriorityEntry(4, 4, 3260): True,
        })

    @staticmethod
    def test_app_lldptool_from_set():
        lldptool_app = DCBModel.LLDPTool.App.from_lldptool_set(
            "lldptool -Ti eth3 -V APP enableTx=yes app=3,1,0x8906")
        assert lldptool_app.data.applications == {(3, 1, 35078): True}

    @staticmethod
    def test_app_lldptool_get_eq_lldptool_set():
        lldptool_app_model = DCBModel.LLDPTool.App.from_lldptool(
            ieee_lldptool_tni)
        lldptool_app_set_model = DCBModel.LLDPTool.App.from_lldptool_set(
            "lldptool -Ti eth3 -V APP enableTx=yes app=5,1,35078 app=2,2,3260")
        assert lldptool_app_model == lldptool_app_set_model

    @staticmethod
    def test_app_lldptool_get_cee_eq_lldptool_set():
        lldptool_cee_app = DCBModel.LLDPTool.App.from_lldptool(lldptool_tni)
        lldptool_app = DCBModel.LLDPTool.App.from_lldptool_set(
            "lldptool -Ti eth3 -V APP enableTx=yes" " "
            "app=2,1,35078 app=3,1,0x8914 app=4,4,3260")
        assert lldptool_cee_app.data == lldptool_app.data

    @staticmethod
    def test_app_dcbtool_get_cee_eq_lldptool_set_fcoe():
        dcbtool_gc_app = """Command:   \tGet Config
Feature:   \tApplication FCoE
Port:      \tp1p2
Status:    \tSuccessful
Enable:    \ttrue
Advertise: \ttrue
Willing:   \ttrue
appcfg:     \t08
"""
        lldptool_cee_app = DCBModel.DCBTool.App.from_dcbtool_get(
            dcbtool_gc_app)
        lldptool_app = DCBModel.LLDPTool.App.from_lldptool_set(
            "lldptool -Ti eth3 -V APP app=3,1,35078")
        assert lldptool_cee_app.data == lldptool_app.data

    @staticmethod
    def test_app_dcbtool_get_cee_eq_lldptool_set_iscsi():
        dcbtool_gc_app = """Command:   \tGet Config
Feature:   \tApplication iSCSI
Port:      \tp1p2
Status:    \tSuccessful
Enable:    \ttrue
Advertise: \ttrue
Willing:   \ttrue
appcfg:     \t10
"""
        lldptool_cee_app = DCBModel.DCBTool.App.from_dcbtool_get(
            dcbtool_gc_app)
        lldptool_app = DCBModel.LLDPTool.App.from_lldptool_set(
            "lldptool -Ti eth3 -V APP app=4,4,3260")
        assert lldptool_cee_app.data == lldptool_app.data

    @staticmethod
    def test_app_lldptool_get_ieee_eq_from_dcbtool_set():
        lldptool_app = DCBModel.LLDPTool.App.from_lldptool(ieee_lldptool_tni)
        dcbtool_app = DCBModel.DCBTool.App.from_dcbtool_set(
            "dcbtool sc eth3 app:fcoe e:1 a:1 w:1 appcfg:20")
        assert dcbtool_app.control == lldptool_app.control
        assert set(dcbtool_app.data.applications).issubset(
            set(lldptool_app.data.applications))

    @staticmethod
    def test_app_lldptool_get_ieee_eq_to_dcbtool_set():
        app_model = DCBModel.LLDPTool.App.from_lldptool(ieee_lldptool_tni)
        to_set_app = DCBModel.DCBTool.App.to_dcbtool_set("eth3", app_model)
        assert "dcbtool sc eth3 app:fcoe e:1 a:1 w:1 appcfg:20" in to_set_app

    @staticmethod
    def test_app_from_dcbtool_set_eq_from_dcbtool_set():
        from_dcbtool_set = "dcbtool sc eth3 app:fcoe e:1 a:1 w:1 appcfg:20"
        app_model = DCBModel.DCBTool.App.from_dcbtool_set(from_dcbtool_set)
        to_set_app = DCBModel.DCBTool.App.to_dcbtool_set("eth3", app_model)
        assert from_dcbtool_set in to_set_app

    @staticmethod
    def test_app_dcbtool_get_eq_from_dcbtool_set():
        from_dcbtool_set = "dcbtool sc eth3 app:fcoe e:1 a:1 w:1 appcfg:20"
        app_model = DCBModel.DCBTool.App.from_dcbtool_set(from_dcbtool_set)
        to_set_app = DCBModel.LLDPTool.App.to_lldptool_set("eth3", app_model)
        # IEEE App does not have willing
        assert to_set_app == "lldptool -Ti eth3 -V APP enableTx=yes app=5,1,35078"

    @staticmethod
    def test_app_lldptool_set_eq_from_dcbtool_set():
        from_lldptool_set = "lldptool -Ti eth3 -V APP enableTx=yes app=5,1,35078"
        from_dcbtool_set = "dcbtool sc eth3 app:fcoe e:1 a:1 w:1 appcfg:20"
        dcbtool_app_model = DCBModel.DCBTool.App.from_dcbtool_set(
            from_dcbtool_set)
        lldptool_app_model = DCBModel.LLDPTool.App.from_lldptool_set(
            from_lldptool_set)
        to_set_app = DCBModel.LLDPTool.App.to_lldptool_set(
            "eth3", dcbtool_app_model)
        assert to_set_app == from_lldptool_set
        assert dcbtool_app_model == lldptool_app_model


class DCBModelTest(unittest.TestCase):

    @staticmethod
    def test_pfc_attributes():
        kwargs = {
            'enabled': {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1},
            'max_tcs': 8,
        }
        d = DCBModel.PFCModel(**kwargs)
        for k, v in kwargs.iteritems():
            assert getattr(d, k) == v

    @staticmethod
    def test_cee_to_ieee_ets():
        pgid = dcbtool.up2tc('77117716')
        tsa_map, up2tc = DCBModel.DCBTool.cee_to_ieee_ets(pgid)
        assert {0: 7, 1: 7, 2: 1, 3: 1, 4: 7, 5: 7, 6: 1, 7: 6} == up2tc
        assert dict((n, 'ets') for n in range(8)) == tsa_map

    @staticmethod
    def test_cee_to_ieee_ets_strict():
        pgid = dcbtool.up2tc('012f45ff')
        assert {0: 0, 1: 1, 2: 2, 3: 15, 4: 4, 5: 5, 6: 15, 7: 15} == pgid
        tsa_map, up2tc = DCBModel.DCBTool.cee_to_ieee_ets(pgid)
        assert {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7} == up2tc
        assert tsa_map == {0: 'ets', 1: 'ets', 2: 'ets', 3:
                           'strict', 4: 'ets', 5: 'ets', 6: 'strict', 7: 'strict'}
        # assert dict((n, 'ets') for n in range(8)) == tsa_map
        pgid_str = DCBModel.DCBTool.ETS.get_pgid(up2tc, tsa_map)
        assert "pgid:012f45ff" == pgid_str

    @staticmethod
    def test_get_protocol_and_selector():
        assert (1, 0x8906) == DCBModel.DCBTool.App.get_protocol_and_selector(
            "Application FCoE")

    @staticmethod
    def test_appcfg_to_dict():
        appcfg = DCBModel.bitmask_to_dict(int("0x0d", 0))
        assert appcfg == {
            0: True,
            2: True,
            3: True,
        }

    @staticmethod
    def test_make_appcfg():
        assert "0e" == DCBModel.make_bitmask(1, 2, 3)

    @staticmethod
    def test_many_app_tlvs():
        # TODO: finish this
        many_apps = {
            DCBModel.AppPriorityEntry(4, 2, 3260): True,
            DCBModel.AppPriorityEntry(2, 2, 3260): True,
            DCBModel.AppPriorityEntry(5, 1, 0x8906): True,
            DCBModel.AppPriorityEntry(4, 2, 3260): True,
            DCBModel.AppPriorityEntry(2, 2, 3260): True,
            DCBModel.AppPriorityEntry(5, 1, 0x8906): True,
            DCBModel.AppPriorityEntry(6, 1, 0x8906): True,
            DCBModel.AppPriorityEntry(4, 2, 3260): True,
            DCBModel.AppPriorityEntry(2, 2, 3260): True,
            DCBModel.AppPriorityEntry(5, 1, 0x8906): True,
            DCBModel.AppPriorityEntry(6, 1, 0x8906): True,
            DCBModel.AppPriorityEntry(4, 2, 3260): True,
            DCBModel.AppPriorityEntry(2, 2, 3260): True,
            DCBModel.AppPriorityEntry(5, 1, 0x8906): True,
        }


class TestRandom(unittest.TestCase):

    @staticmethod
    def test_random_dcbtool():
        os.chdir(os.path.dirname(__file__))
        dcbtool_commands = open("dcbtool-random.txt")
        try:
            for l in dcbtool_commands:
                if 'pg' in l:
                    dcbtool_ets_model = DCBModel.DCBTool.ETS.from_dcbtool_set(
                        l)
                    to_set_ets = DCBModel.DCBTool.ETS.to_dcbtool_set(
                        "eth3", dcbtool_ets_model)
                    assert l[:-1] == to_set_ets
                if 'pfc' in l:
                    dcbtool_pfc_model = DCBModel.DCBTool.PFC.from_dcbtool_set(
                        l)
                    to_set_pfc = DCBModel.DCBTool.PFC.to_dcbtool_set(
                        "eth3", dcbtool_pfc_model)
                    assert l[:-1] == to_set_pfc
        finally:
            dcbtool_commands.close()

    @staticmethod
    def test_random_lldptool():
        os.chdir(os.path.dirname(__file__))
        lldptool_commands = open("lldptool-random.txt")
        try:
            for l in lldptool_commands:
                if 'ETS' in l:
                    lldptool_ets_model = DCBModel.LLDPTool.ETS.from_lldptool_set(
                        l)
                    to_set_ets = DCBModel.LLDPTool.ETS.to_lldptool_set(
                        "eth3", lldptool_ets_model, tlv_name='ETS-REC')
                    assert l[:-1] == to_set_ets
                if 'PFC' in l:
                    lldptool_pfc_model = DCBModel.LLDPTool.PFC.from_lldptool_set(
                        l)
                    to_set_pfc = DCBModel.LLDPTool.PFC.to_lldptool_set(
                        "eth3", lldptool_pfc_model)
                    assert l[:-1] == to_set_pfc
        finally:
            lldptool_commands.close()
