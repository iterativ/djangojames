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
# Created on Feb 28, 2012
# @author: github.com/maersu


from django import template
import re
from django.core.urlresolvers import reverse
register = template.Library()

class IsActiveNode(template.Node):
    
    def __init__(self, ref_url, return_value):
        self.ref_url = ref_url
        self.return_value = return_value
    def render(self, context): 
        current_path = context['request'].path
        if current_path == self.ref_url:
            return self.return_value
        try:
            if current_path == reverse(self.ref_url):
                return self.return_value
        except:
            pass          
        return ''

@register.tag
def isactive(parser,token):
    try:
        # split_contents() knows not to split quoted strings.
        tokens = token.split_contents()
        tag_name, ref_url = tokens[0], tokens[1]
        
        if len(tokens) == 3:
            return_value = tokens[2][1:-1]
        else:
            return_value = 'active'
        
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    if not (ref_url[0] == ref_url[-1] and ref_url[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    return IsActiveNode(ref_url[1:-1],return_value)

register.tag('isactive', isactive)