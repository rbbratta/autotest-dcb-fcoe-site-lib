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


import unittest
import dcbtool


class test_dcbtool(unittest.TestCase):

    def test_get_oper_pg(self):
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
pgpct:          20%     10%     40%     20%     10%     0%      0%      0%
pgid:           0       0       3       1       2       0       4       0
uppct:          25%     25%     100%    100%    100%    25%     100%    25%
pg strict:      0       0       0       0       0       0       0       0
"""

        r = dcbtool.parse(dcbtool_go_pg)
        self.assertEqual(r['Command'], "Get Oper")
        self.assertEqual(r['Feature'], "Priority Groups")
        self.assertEqual(r['Port'], "eth3")
        self.assertEqual(r['Status'], "Successful")
        self.assertEqual(r['Oper Version'], 0)
        self.assertEqual(r['Max Version'], 0)
        self.assertEqual(r['Errors'], (0, "none"))
        self.assertEqual(r['Oper Mode'], True)
        self.assertEqual(r['Syncd'], True)
        self.assertEqual(r['up2tc'], {
                         0: 0, 1: 0, 2: 3, 3: 1, 4: 2, 5: 0, 6: 4, 7: 0})
        self.assertEqual(r['pgid'], {
                         0: 0, 1: 0, 2: 3, 3: 1, 4: 2, 5: 0, 6: 4, 7: 0})
        self.assertEqual(r['pgpct'], (20, 10, 40, 20, 10, 0, 0, 0))
        self.assertEqual(r['uppct'], (25, 25, 100, 100, 100, 25, 100, 25))
        self.assertEqual(r['pg strict'], dict(((n, False) for n in range(8))))
        # pprint.#pprint(r)

    def test_get_oper_pg_lsp(self):
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

        r = dcbtool.parse(dcbtool_go_pg)
        self.assertEqual(r['Command'], "Get Oper")
        self.assertEqual(r['Feature'], "Priority Groups")
        self.assertEqual(r['Port'], "eth3")
        self.assertEqual(r['Status'], "Successful")
        self.assertEqual(r['Oper Version'], 0)
        self.assertEqual(r['Max Version'], 0)
        self.assertEqual(r['Errors'], (0, "none"))
        self.assertEqual(r['Oper Mode'], True)
        self.assertEqual(r['Syncd'], True)
        self.assertEqual(r['up2tc'], {
                         0: 0, 1: 0, 2: 3, 3: 1, 4: 2, 5: 0, 6: 4, 7: 0})
        self.assertEqual(r['pgid'], {
                         0: 0, 1: 0, 2: 3, 3: 1, 4: 2, 5: 0, 6: 15, 7: 0})
        self.assertEqual(r['pgpct'], (20, 10, 40, 30, 0, 0, 0, 0))
        self.assertEqual(r['uppct'], (25, 25, 100, 100, 100, 25, 100, 25))
        self.assertEqual(r['pg strict'], dict(((n, False) for n in range(8))))
        # pprint.#pprint(r)

    def test_get_oper_pfc(self):
        dcbtool_go_pfc = """
Command:        Get Oper
Feature:        Priority Flow Control
Port:           eth3
Status:         Successful
Oper Version:   0
Max Version:    0
Errors:         0x00 - none
Oper Mode:      true
Syncd:          true
pfcup:          0       0       1       1       1       0       1       0
"""

        r = dcbtool.parse(dcbtool_go_pfc)
        self.assertEqual(r['Command'], "Get Oper")
        self.assertEqual(r['Feature'], "Priority Flow Control")
        self.assertEqual(r['Port'], "eth3")
        self.assertEqual(r['Status'], "Successful")
        self.assertEqual(r['Oper Version'], 0)
        self.assertEqual(r['Max Version'], 0)
        self.assertEqual(r['Errors'], (0, "none"))
        self.assertEqual(r['Oper Mode'], True)
        self.assertEqual(r['Syncd'], True)
        self.assertEqual(r['pfcup'], {
            0: False,
            1: False,
            2: True,
            3: True,
            4: True,
            5: False,
            6: True,
            7: False
        })
        # pprint.#pprint(r)

    def test_get_oper_app_fcoe(self):
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

        r = dcbtool.parse(dcbtool_go_app_fcoe)
        self.assertEqual(r['Command'], "Get Oper")
        self.assertEqual(r['Feature'], "Application FCoE")
        self.assertEqual(r['Port'], "eth3")
        self.assertEqual(r['Status'], "Successful")
        self.assertEqual(r['Oper Version'], 0)
        self.assertEqual(r['Max Version'], 0)
        self.assertEqual(r['Errors'], (0, "none"))
        self.assertEqual(r['Oper Mode'], True)
        self.assertEqual(r['Syncd'], True)
        self.assertEqual(r['appcfg'], 64)
        # pprint.#pprint(r)

    def test_get_oper_app_iscsi(self):
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

        r = dcbtool.parse(dcbtool_go_app_iscsi)
        self.assertEqual(r['Command'], "Get Oper")
        self.assertEqual(r['Feature'], "Application iSCSI")
        self.assertEqual(r['Port'], "eth3")
        self.assertEqual(r['Status'], "Successful")
        self.assertEqual(r['Oper Version'], 0)
        self.assertEqual(r['Max Version'], 0)
        self.assertEqual(r['Errors'], (0, "none"))
        self.assertEqual(r['Oper Mode'], True)
        self.assertEqual(r['Syncd'], True)
        self.assertEqual(r['appcfg'], 16)
        # pprint.pprint(r)

    def test_get_config_pg(self):
        dcbtool_gc_pg = """
Command:        Get Config
Feature:        Priority Groups
Port:           eth3
Status:         Successful
Enable:         true
Advertise:      true
Willing:        true
up2tc:          0       1       2       3       4       5       6       7
pgpct:          13%     13%     13%     13%     12%     12%     12%     12%
pgid:           0       1       2       3       4       5       6       7
uppct:          100%    100%    100%    100%    100%    100%    100%    100%
pg strict:      0       0       0       0       0       0       0       0
num TC's:       8
"""

        r = dcbtool.parse(dcbtool_gc_pg)
        self.assertEqual(r['Command'], "Get Config")
        self.assertEqual(r['Feature'], "Priority Groups")
        self.assertEqual(r['Port'], "eth3")
        self.assertEqual(r['Status'], "Successful")
        self.assertEqual(r['Enable'], True)
        self.assertEqual(r['Advertise'], True)
        self.assertEqual(r['Willing'], True)
        self.assertEqual(r['up2tc'], {
                         0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7})
        self.assertEqual(r['pgid'], {
                         0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7})
        self.assertEqual(r['pgpct'], (13, 13, 13, 13, 12, 12, 12, 12))
        self.assertEqual(r['uppct'], (100, 100, 100, 100, 100, 100, 100, 100))
        self.assertEqual(r['pg strict'], dict(((n, False) for n in range(8))))
        self.assertEqual(r["num TC's"], 8)

    def test_get_config_pfc(self):
        dcbtool_gc_pfc = """
Command:        Get Config
Feature:        Priority Flow Control
Port:           eth3
Status:         Successful
Enable:         true
Advertise:      true
Willing:        true
pfcup:          0       0       0       0       0       0       0       0
num TC's:       8
"""
        r = dcbtool.parse(dcbtool_gc_pfc)
        self.assertEqual(r['Command'], "Get Config")
        self.assertEqual(r['Feature'], "Priority Flow Control")
        self.assertEqual(r['Port'], "eth3")
        self.assertEqual(r['Status'], "Successful")
        self.assertEqual(r['Enable'], True)
        self.assertEqual(r['Advertise'], True)
        self.assertEqual(r['Willing'], True)
        self.assertEqual(r['pfcup'], dict(((n, False) for n in range(8))))
        self.assertEqual(r["num TC's"], 8)

    def test_get_config_app_fcoe(self):
        dcbtool_gc_app_fcoe = """
Command:        Get Config
Feature:        Application FCoE
Port:           eth3
Status:         Successful
Enable:         true
Advertise:      true
Willing:        true
appcfg:         08
"""

        r = dcbtool.parse(dcbtool_gc_app_fcoe)
        self.assertEqual(r['Command'], "Get Config")
        self.assertEqual(r['Feature'], "Application FCoE")
        self.assertEqual(r['Port'], "eth3")
        self.assertEqual(r['Status'], "Successful")
        self.assertEqual(r['Enable'], True)
        self.assertEqual(r['Advertise'], True)
        self.assertEqual(r['Willing'], True)
        self.assertEqual(r['appcfg'], 8)

    def test_get_config_app_iscsi(self):
        dcbtool_gc_app_iscsi = """
Command:        Get Config
Feature:        Application iSCSI
Port:           eth3
Status:         Successful
Enable:         true
Advertise:      true
Willing:        true
appcfg:         10
"""
        r = dcbtool.parse(dcbtool_gc_app_iscsi)
        self.assertEqual(r['Command'], "Get Config")
        self.assertEqual(r['Feature'], "Application iSCSI")
        self.assertEqual(r['Port'], "eth3")
        self.assertEqual(r['Status'], "Successful")
        self.assertEqual(r['Enable'], True)
        self.assertEqual(r['Advertise'], True)
        self.assertEqual(r['Willing'], True)
        self.assertEqual(r['appcfg'], 16)

    def test_set_config_pfc(self):
        r = dcbtool.parse_set("dcbtool sc eth3 pfc e:1 a:1 w:1 pfcup:00111010")
        self.assertEqual(r['enable'], True)
        self.assertEqual(r['willing'], True)
        self.assertEqual(r['advertise'], True)
        self.assertEqual(r['interface'], "eth3")
        self.assertEqual(r['pfcup'], {
            0: False,
            1: False,
            2: True,
            3: True,
            4: True,
            5: False,
            6: True,
            7: False
        })

    def test_set_config_pg(self):
        r = dcbtool.parse_set(
            "dcbtool sc eth3 pg e:1 a:1 w:1 uppct:7,6,5,4,3,2,1,0 pgid:00111010 pgpct:0,1,2,3,4,5,6,7")
        self.assertEqual(r['enable'], True)
        self.assertEqual(r['willing'], True)
        self.assertEqual(r['advertise'], True)
        self.assertEqual(r['interface'], "eth3")
        self.assertEqual(r['pgid'], {
                         0: 0, 1: 0, 2: 1, 3: 1, 4: 1, 5: 0, 6: 1, 7: 0})
        self.assertEqual(r['pgpct'], (0, 1, 2, 3, 4, 5, 6, 7))
        self.assertEqual(r['uppct'], (7, 6, 5, 4, 3, 2, 1, 0))

    def test_set_config_app_fcoe(self):
        r = dcbtool.parse_set("dcbtool sc eth3 app:0 e:1 a:1 w:1 appcfg:20")
        self.assertEqual(r['enable'], True)
        self.assertEqual(r['willing'], True)
        self.assertEqual(r['advertise'], True)
        self.assertEqual(r['interface'], "eth3")
        self.assertEqual(r['appcfg'], 32)

    @staticmethod
    def test_get_app():
        assert 'fcoe' == dcbtool.get_app('0')
        assert 'fcoe' == dcbtool.get_app('fcoe')
        assert 'iscsi' == dcbtool.get_app('1')
        assert 'iscsi' == dcbtool.get_app('iscsi')
        assert 'fip' == dcbtool.get_app('fip')
        assert 'fip' == dcbtool.get_app('2')

if __name__ == "__main__":
    unittest.main()
