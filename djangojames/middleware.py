# -*- coding: utf-8 -*-
#
# ITerativ GmbH
# http://www.iterativ.ch/
#
# Copyright (c) 2012 ITerativ GmbH. All rights reserved.
#
# Created on May 6, 2012
# @author: maersu <me@maersu.ch>
import collections
from contextlib import contextmanager

from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin


try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()

def get_request():
    return getattr(_thread_locals, "request", None)

def get_user():
    request = get_request()
    if request:
        return getattr(request, "user", None)

class ThreadLocalMiddleware(MiddlewareMixin):
    # clean up _thread_locals after the request: https://stackoverflow.com/a/3227515/669561
    def process_request(self, request):
        _thread_locals.request = request

    def process_response(self, request, response):
        _thread_locals.request = None
        return response

    def process_exception(self, request, exception):
        _thread_locals.request = None


DummyRequest = collections.namedtuple('DummyRequest', ['user'])

@contextmanager
def change_user(user=None, username=None):
    """Temporarily change the current user

    To be used as a context manager.

    Supply either a user object or alternatively a username:
    :param user: a user object
    :param username: a string containing the username

    Example:
    >>> with change_user(username='nightly-import'):
    ...     import_users()
    """
    old_request = get_request()
    if not user:
        User = get_user_model()
        user = User.objects.get(username=username)
    _thread_locals.request = DummyRequest(user)
    yield user
    if old_request:
        _thread_locals.request = old_request
    else:
        del _thread_locals.request
