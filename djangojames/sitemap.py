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
# Created on June 27, 2012
# @author: github.com/maersu

from django.contrib.sitemaps import Sitemap
from datetime import datetime
from django.conf import settings

class _DummyItem:
    def __init__(self, url):
        self.url = url

    def get_absolute_url(self):
        return self.url

class StaticSitemap(Sitemap):

    def items(self):
        return [_DummyItem(page) 
                for page in getattr(settings, 'JAMES_SITEMAP_PAGES', [])]

    def lastmod(self, obj):
        return datetime.now()

    def changefreq(self, obj):
        return getattr(settings, 'JAMES_SITEMAP_CHANGEFREQ', 'weekly')

    def priority(self, obj):
        return getattr(settings, 'JAMES_SITEMAP_PRIORITY', 0.7)