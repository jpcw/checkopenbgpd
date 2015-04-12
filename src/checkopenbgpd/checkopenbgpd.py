#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Doc here.
"""

import argparse
from collections import namedtuple
import logging
import platform
import subprocess

import nagiosplugin


__docformat__ = 'restructuredtext en'

_log = logging.getLogger('nagiosplugin')

fields = ('Neighbor', 'AS', 'MsgRcvd', 'MsgSent', 'OutQ', 'Up_Down',
          'State_PrfRcvd')

Session = namedtuple('Session', fields)


def _popen(cmd):  # pragma: no cover
    """Try catched subprocess.popen.

    raises explicit error
    """
    try:
        proc = subprocess.Popen(cmd,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        return stdout, stderr

    except OSError as e:
        message = "%s" % e
        raise nagiosplugin.CheckError(message)


class CheckBgpCtl(nagiosplugin.Resource):
    """Check bgpctl sessions plugin."""

    hostname = platform.node()
    cmd = 'bgpctl show'

    def __init__(self, idle_list):
        self.idle_list = idle_list

    def _get_sessions(self):
        """Runs 'bgpctl show'."""

        _log.debug("running '%s'", self.cmd)
        stdout, stderr = _popen(self.cmd.split())

        if stderr:
            message = "%s %s" % (self.hostname, stderr.splitlines()[-1])
            _log.info(message)
            raise nagiosplugin.CheckError(message)

        if stdout:
            output = stdout.splitlines()[1:]
            if output:
                return [Session(*line.rsplit(None, len(Session._fields) - 1))
                        for line in output]

    def check_session(self, session):
        """check session is up, or not in idle list if idle."""
        result = 'U'
        state = session.State_PrfRcvd

        if state.isdigit():
            result = int(state)

        if state == 'Idle':
            if self.idle_list is not None:
                if session.Neighbor in self.idle_list:
                    result = 0

        return result

    def probe(self):
        """."""
        self.sessions = self._get_sessions()
        if self.sessions:
            for session in self.sessions:
                yield nagiosplugin.Metric(session.Neighbor,
                                          self.check_session(session),
                                          min=0, context='bgpctl')


class AuditSummary(nagiosplugin.Summary):
    """Status line conveying informations.
    """

    def ok(self, results):
        """Summarize OK(s)."""
        return 'All bgp sessions in correct state'


def parse_args():  # pragma: no cover
    """Arguments parser."""
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase output verbosity (use up to 3 times)')
    argp.add_argument('--idle-list', nargs='*')

    return argp.parse_args()


@nagiosplugin.guarded
def main():  # pragma: no cover

    args = parse_args()
    check = nagiosplugin.Check(CheckBgpCtl(args.idle_list),
                               nagiosplugin.ScalarContext('bgpctl', None,
                                                          '0:'),
                               AuditSummary())
    check.main(args.verbose)

# vim:set et sts=4 ts=4 tw=80:
