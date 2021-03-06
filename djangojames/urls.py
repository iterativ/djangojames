# -*- coding: utf-8 -*-
#
# Atizo - The Open Innovation Platform
# http://www.atizo.com/
#
# Copyright (c) 2008-2010 Atizo AG. All rights reserved.
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
from django.conf.urls.defaults import patterns, include, url
from djangojames.admin_dashboard import get_statistics_modules
from django.conf import settings

# dummy redirect
urlpatterns = patterns('',
    url(r'^admin_tools/', include('admin_tools.urls')),  
)

statistics_modules = get_statistics_modules()
for mod in statistics_modules:
    
    admin_stats = mod()
    urlpatterns += patterns('',
       url(r'^statistics/%s/' % admin_stats.prefix, include(admin_stats.get_urls())),
    )

use_export_chart = hasattr(settings, 'JAMES_CHART_EXPORT_JS_URL')

if len(statistics_modules) > 0 and use_export_chart:  
    urlpatterns += patterns('djangojames.statistics.views',
        url(r'^statistics/export/$', 'export_highchart_svg', name='export-highchart'),
    )
    
