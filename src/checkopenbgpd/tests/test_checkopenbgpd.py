
import mock

try:
    import unittest2 as unittest
except ImportError:  # pragma: no cover
    import unittest

import nagiosplugin
from nagiosplugin.metric import Metric
from nagiosplugin import CheckError

from checkopenbgpd import checkopenbgpd

no_sudoer = 'bgpctl: connect: /var/run/bgpd.sock: Permission denied'
no_bgpd = 'bgpctl: connect: /var/run/bgpd.sock: No such file or directory'


bgpctl_sh = 'Neighbor     AS MsgRcvd MsgSent OutQ Up/Down   State/PrfRcvd\n'\
            'FIRST     65001   75386       6     0 5d02h04m Idlei\n'\
            'SECOND    65001 2832677  113152     0 5d01h58m 529001\n'\
            'THIRD     65002 3914143  103074     0 3d11h59m Idle'


class Test_checkopenbgpd(unittest.TestCase):

    def test_bgpd_is_not_running(self):
        check = checkopenbgpd.CheckBgpCtl(None)
        err_message = no_bgpd

        with mock.patch("checkopenbgpd.checkopenbgpd._popen") as _popen:
            _popen.return_value = '', err_message
            with self.assertRaises(CheckError):
                check._get_sessions()  # NOQA

    def test_user_is_not_sudoer(self):
        check = checkopenbgpd.CheckBgpCtl(None)
        err_message = no_sudoer

        with mock.patch("checkopenbgpd.checkopenbgpd._popen") as _popen:
            _popen.return_value = '', err_message
            with self.assertRaises(CheckError):
                check._get_sessions()  # NOQA

    def test__get_sessions(self):
        check = checkopenbgpd.CheckBgpCtl(None)
        output = bgpctl_sh

        with mock.patch("checkopenbgpd.checkopenbgpd._popen") as _popen:
            _popen.return_value = output, ''
            sessions = check._get_sessions()
            self.assertEquals(len(sessions), 3)
            self.assertEquals(type(sessions[0]), checkopenbgpd.Session)

    def test_check_session_is_up(self):
        check = checkopenbgpd.CheckBgpCtl(None)
        output = bgpctl_sh

        with mock.patch("checkopenbgpd.checkopenbgpd._popen") as _popen:
            _popen.return_value = output, ''
            sessions = check._get_sessions()
            result = check.check_session(sessions[1])
            self.assertEquals(result, 529001)

    def test_check_idle_session_in_idle_list(self):
        check = checkopenbgpd.CheckBgpCtl(['THIRD'])
        output = bgpctl_sh

        with mock.patch("checkopenbgpd.checkopenbgpd._popen") as _popen:
            _popen.return_value = output, ''
            sessions = check._get_sessions()
            result = check.check_session(sessions[2])
            self.assertEquals(result, 0)

    def test_check_idle_session_not_in_idle_list(self):
        check = checkopenbgpd.CheckBgpCtl(['THIRD'])
        output = bgpctl_sh

        with mock.patch("checkopenbgpd.checkopenbgpd._popen") as _popen:
            _popen.return_value = output, ''
            sessions = check._get_sessions()
            result = check.check_session(sessions[0])
            self.assertEquals(result, 'U')

    def test_check_probe_without_idle_list(self):
        check = checkopenbgpd.CheckBgpCtl(None)
        output = bgpctl_sh

        with mock.patch("checkopenbgpd.checkopenbgpd._popen") as _popen:
            _popen.return_value = output, ''
            check._get_sessions()
            probe = check.probe()
            first = next(probe)
            self.assertEqual(type(first), Metric)
            self.assertEquals(first.value, 'U')
            second = next(probe)
            self.assertEquals(second.value, 529001)
            third = next(probe)
            self.assertEquals(third.value, 'U')

    def test_check_probe_with_idle_list(self):
        check = checkopenbgpd.CheckBgpCtl(['THIRD'])
        output = bgpctl_sh

        with mock.patch("checkopenbgpd.checkopenbgpd._popen") as _popen:
            _popen.return_value = output, ''
            check._get_sessions()
            probe = check.probe()
            first = next(probe)
            self.assertEqual(type(first), Metric)
            self.assertEquals(first.value, 'U')
            second = next(probe)
            self.assertEquals(second.value, 529001)
            third = next(probe)
            self.assertEquals(third.value, 0)


class Test_AuditSummary(unittest.TestCase):

    def test_ok(self):
        from nagiosplugin.result import Result, Results
        from nagiosplugin.state import Ok
        from checkopenbgpd.checkopenbgpd import AuditSummary
        results = Results()
        ok_r1 = Result(Ok, '', nagiosplugin.Metric('met1', 529001))
        ok_r2 = Result(Ok, '', nagiosplugin.Metric('met1', 0))
        results.add(ok_r1)
        results.add(ok_r2)
        summary = AuditSummary()
        sum_ok = summary.ok(results)
        self.assertEqual(sum_ok, 'All bgp sessions in correct state')
