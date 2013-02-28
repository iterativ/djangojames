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
from django.core.management.base import NoArgsCommand
import os
import sys
from djangojames.db.utils import reset_schema
from optparse import make_option
from django.core import serializers
from django.db.models import Model, ForeignKey, ManyToManyField, OneToOneField
import json
from django.db.models.loading import get_model
import pprint

FIXTUERS_EXT = '.json'


class JsonFixtures(object):
    def __init__(self, root_dir):
        self._root_dir = root_dir

    def _extract_fixture_name(self, file_name):
        return os.path.splitext(os.path.basename(file_name))[0]

    def _get_relns(self):

        def _get(model):
            for a in models:
                if a[0] == model:
                    return a

        def _add(model, to):
            to_objects = _get(to)
            if to_objects:
                l = relations.get(model[-1], [])
                l.append(to_objects[-1])
                relations[model[-1]] = l

        def _get_models(fixture_file):

            models_list = set()
            data = json.load(open(fixture_file, 'r'))

            for o in data:
                if o.has_key('model'):
                    name = o['model']
                    m = name.split('.')
                    models_list.add((get_model(*(m[0], m[1])), self._extract_fixture_name(fixture_file)))

            return models_list

        relations = {}
        models = []
        for f in self.get_files():
            models.extend(_get_models(f))

        for model in models:
            if model[0]:
                for field in model[0]._meta.fields + model[0]._meta.many_to_many:
                    if any([isinstance(field, OneToOneField),
                            isinstance(field, ForeignKey),
                            isinstance(field, ManyToManyField)]):
                        _add(model, field.rel.to)

        return relations

    def get_files(self):
        if not hasattr(self, '__all_fixtures'):
            self.__all_fixtures = []

            def _find(arg, dirname, names):
                if (dirname.endswith('fixtures')) and (dirname.find('unit_test') == -1):
                    for name in names:
                        if (name.endswith(FIXTUERS_EXT)) and (name.find('initial_data') == -1):
                            self.__all_fixtures.append(os.path.join(dirname, name))

            os.path.walk(self._root_dir, _find, None)

        return self.__all_fixtures

    def get(self):
        return [self._extract_fixture_name(f) for f in self.get_files()]

    def get_folders(self):
        return tuple(set([os.path.split(f)[0] for f in self.get_files()]))

    def get_sorted(self):
        relns = self._get_relns()
        fixlist = self.get()
        changes = True
        i = len(fixlist) #avoid infinites loop

        while changes and i >= 0:
            i -= 1
            changes = False
            for fr, tos in relns.items():
                fr_index = fixlist.index(fr)
                for t in tos:
                    to_index = fixlist.index(t)
                    if to_index > fr_index:
                        fixlist.remove(t)
                        fixlist.insert(fr_index, t)
                        changes = True

        return fixlist


class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('-i', '--ignore_reset', action='store_true', dest='ignore_reset',
                    help='Do not extecute the reset command (equivalent to syncdb)'),
        make_option('-y', '--rebuild_haystack', action='store_true', dest='rebuild_haystack',
                    help='call haystack rebuild_index command'),
    )
    help = "Drops and recreates database (from jsons)."


    def handle_noargs(self, **options):
        from django.conf import settings
        from django.db import models

        from django.core.management.sql import emit_post_sync_signal
        from django.db.utils import DEFAULT_DB_ALIAS
        from django.core.management import call_command

        ignore_reset = options.get('ignore_reset', False)
        rebuild_haystack = options.get('rebuild_haystack', False)
        db = options.get('database', DEFAULT_DB_ALIAS)
        database_config = settings.DATABASES[db]

        if not ignore_reset:
            reset_schema(database_config)

        # init db schema
        call_command('syncdb', interactive=False)

        # Emit the post sync signal. This allows individual
        # applications to respond as if the database had been
        # sync'd from scratch.
        emit_post_sync_signal(models.get_models(), 0, 0, db)

        # get all fixtures
        jf = JsonFixtures(settings.PROJECT_ROOT)
        fixtures = jf.get_sorted()

        sys.stdout.write("Load fixtures: %s\n" % " ".join(fixtures))
        call_command('loaddata', *fixtures)

        if rebuild_haystack:
            call_command('rebuild_index', interactive=False)
        