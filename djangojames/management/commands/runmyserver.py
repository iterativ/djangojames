# -*- coding: utf-8 -*-
#
# ITerativ GmbH
# http://www.iterativ.ch/
#
# Copyright (c) 2012 ITerativ GmbH. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# Created on Sept 28, 2012
# @author: github.com/maersu

from optparse import make_option
from django.contrib.staticfiles.management.commands.runserver import Command as BaseCommand
import socket

DEFAULT_PORT = 8000

class Command(BaseCommand):
    help = "Starts the Web server under the machine IPs."
    option_list = BaseCommand.option_list + (
        make_option('--port', '-p', dest='port', default=DEFAULT_PORT,
            help='Specifies the port'),
    )
        
    def handle(self, addrport='', *args, **options):
        if not addrport:
            port = self.use_ipv6 = options.get('port', DEFAULT_PORT)
            addrport = '%s:%s' % (socket.gethostbyname(socket.gethostname()), port)
        super(Command, self).handle(addrport, *args, **options)
        
        
        
