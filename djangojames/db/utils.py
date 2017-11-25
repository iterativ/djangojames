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
from __future__ import unicode_literals
from django.apps import apps

import os
from subprocess import call, check_output
from random import choice
from django.db.utils import IntegrityError
from django.db.models import EmailField

def _get_engine(database_config):
    return database_config['ENGINE'].split('.')[-1]

def get_dumpdb_name(): 
    from django.conf import settings
    return 'dump_%s.sql' % os.path.split(settings.PROJECT_ROOT)[-1]

def create_db_if_not_exists(database_config):
    db_engine = _get_engine(database_config)
    if db_engine in ['postgresql_psycopg2', 'postgresql']:
        result = str(check_output(["psql", "-ltA", "-R=,"]))
        if not database_config['NAME'] in [line.split('|')[0] for line in result.split(',')]:
            call(['createdb', database_config['NAME']])
    elif db_engine == 'sqlite3':
        pass
    else:
        raise NotImplementedError("This database backend is not yet supported: %s" % db_engine)

def reset_schema(database_config):
    from django.db import connection
    from django.db import transaction
    
    db_engine = _get_engine(database_config)
    sql_list = None
    
    if db_engine in ['postgresql_psycopg2', 'postgresql']:
        sql_list = (
            'DROP  SCHEMA public CASCADE',
            'CREATE SCHEMA public AUTHORIZATION %s' % database_config['USER'],
            'GRANT ALL ON SCHEMA public TO postgres',
            'GRANT ALL ON SCHEMA public TO public',
            "COMMENT ON SCHEMA public IS 'standard public schema';",
        )

    elif db_engine == 'mysql':
        sql_list = (
            'DROP DATABASE %s' % database_config['NAME'],
            'CREATE DATABASE %s' % database_config['NAME'],
            'USE %s' % database_config['NAME']
        )
    elif db_engine == 'sqlite3':
        db_path = database_config['NAME']
        if os.path.exists(db_path):
            print("Remove sqlite3 db file: %s" % db_path)
            os.remove(db_path)
        else:
            print("File does not exists: %s" % db_path)
    
    elif db_engine == 'postgis':
        print("\nATTENTION: You have to drop and create the postgis 'DB' %s manually!\n" % database_config['NAME'])
    else:
        raise NotImplementedError("This database backend is not yet supported: %s" % db_engine)

    cursor = connection.cursor()
    if sql_list and len(sql_list):
        for sql in sql_list:
            cursor.execute(sql)
    transaction.commit()
            
def restore_db(database_config, backup_file):
    
    if not (os.path.exists(backup_file) and os.path.isfile(backup_file)):
        raise Exception("Backup file '%s' doesn't exists" % backup_file)
    
    db_engine = _get_engine(database_config)
    database_config['FILE'] = backup_file
    if db_engine in ['postgresql_psycopg2', 'postgresql']:

        fileName, fileExtension = os.path.splitext(backup_file)
        if fileExtension.lower() == '.sql':
            cmd = 'psql -U %(USER)s -d %(NAME)s < %(FILE)s  > /dev/null 2>&1'  % database_config
        else:
            cmd = 'pg_restore -U %(USER)s -d %(NAME)s %(FILE)s  > /dev/null 2>&1'  % database_config
    elif db_engine == 'mysql':    
        cmd = 'mysql --user=%(USER)s --password=%(PASSWORD)s %(NAME)s < %(FILE)s' % database_config
    else:
        raise NotImplementedError("This database backend is not yet supported: %s" % db_engine)

    print(cmd)
    call(cmd, shell=True)    

def dump_db(database_config, outputpath='/tmp/'):
    db_engine = _get_engine(database_config)
    database_config['OUTPUT_FILE'] = os.path.join(outputpath, get_dumpdb_name())

    if db_engine in ['postgresql_psycopg2', 'postgresql']:     
        cmd = 'pg_dump -U postgres %(NAME)s > %(OUTPUT_FILE)s' % database_config
    elif db_engine == 'mysql':
        
        if database_config['HOST']:
            database_config['HOST'] = '--host %s' % database_config['HOST']
        cmd = '/usr/bin/mysqldump %(NAME)s %(HOST)s -u %(USER)s -p%(PASSWORD)s >  %(OUTPUT_FILE)s' % database_config
    else:
        raise NotImplementedError("This database backend is not yet supported: %s" % db_engine)

    print(cmd)
    call(cmd, shell=True)
    
def get_random_text(length=10, allowed_chars='abcdefghijklmnopqrstuvwxyz'):
    return ''.join([choice(allowed_chars) for i in range(length)])
    
def foo_emails(domain_extension='foo'):
    def _get_foo_email(email):
        try:
            ll = email.split('@')
            return (ll[0]+'@'+domain_extension+'-'+ll[1]).lower()
        except:
            fragment = get_random_text()
            new_mail = (fragment+'@'+domain_extension+'-'+fragment+'.ch').lower()
            print('WARNING: Invalid Email found: "' + email +'" (-> '+ new_mail)
            return new_mail
    
    from django.conf import settings
    from django.db import transaction
    from django.db import connection
    
    app_label = lambda app: app[app.rfind('.')+1:]
    
    email_cnt = 0
    # set fake emails for all EmailFields
    if connection.vendor == 'postgresql':
        print('\nPosgtreSQL detected use fast_postgres_foo_emails')
        email_cnt = fast_postgres_foo_emails(domain_extension)
    else:
        for app in settings.INSTALLED_APPS:
            try:
                label = app_label(app)
                app_config = apps.get_app_config(label)
                if not app_config:
                    continue

                model_list = app_config.models
                for key, model in model_list.items():
                    field_names = [f.attname for f, m in model._meta.get_fields_with_model() if f.__class__ is EmailField]
                    if len(field_names):
                        try:
                            for model_instance in model.objects.all():
                                for field_name in field_names:
                                    orig_email = getattr(model_instance, field_name)
                                    if orig_email:
                                        repl_email = _get_foo_email(orig_email)
                                        setattr(model_instance, field_name, repl_email)
                                        email_cnt += 1
                                try:
                                    model_instance.save()
                                    transaction.commit()
                                except IntegrityError as ie:
                                    print('\nError while processing: ', model_instance)
                                    print(ie)
                                    transaction.rollback()
                        except Exception as e:
                            print('\nError while processing: ', model)
                            print(e)
                            transaction.rollback()
            except Exception as e:
                print(label)
                print(app)
                print(e)
                        
    return email_cnt

def fast_postgres_foo_emails(domain_extension):
    from django.db import connection
    from django.conf import settings

    email_cnt = 0
    app_label = lambda app: app[app.rfind('.')+1:]
    
    handled_columns = set()

    for app in settings.INSTALLED_APPS:
        label = app_label(app)
        app_config = apps.get_app_config(label)
        if not app_config:
            continue

        model_list = app_config.models

        for key, model in model_list.items():
            field_column_names = [f.db_column or f.attname for f, m in model._meta.get_fields_with_model() if f.__class__ is EmailField]

            if len(field_column_names):
                db_table_name = model._meta.db_table
                for column_name in field_column_names:
                    if (column_name, db_table_name) in handled_columns:
                        continue
                    cursor = connection.cursor()
                    sql = u"UPDATE {0} SET {1} = regexp_replace({1}, '@(.*)', '@{2}-\\1') WHERE {1} != ''".format(
                        db_table_name, column_name, domain_extension)
                    cursor.execute(sql)
                    handled_columns.add((column_name, db_table_name))
                    email_cnt += cursor.rowcount

    return email_cnt