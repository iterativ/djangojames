# -*- coding: utf-8 -*-
#
# ITerativ GmbH
# http://www.iterativ.ch/
#
# Copyright (c) 29/09/14 ITerativ GmbH. All rights reserved.
#
# Created on 29/09/14
# @author: maersu
from django.conf import settings


class UserPassesTestMixin(object):
    def get_test_func(self):
        return getattr(self, 'test_func', lambda u: True)

    def get_login_url(self):
        return getattr(self, 'login_url', settings.LOGIN_URL)

    def get_redirect_field_name(self):
        return getattr(self, 'redirect_field_name', 'next')

    def dispatch(self, request, *args, **kwargs):
        from django.contrib.auth.decorators import user_passes_test

        return user_passes_test(
            self.get_test_func(),
            login_url=self.get_login_url(),
            redirect_field_name=self.get_redirect_field_name()
        )(super(StaffMixin, self).dispatch
        )(request, *args, **kwargs)


class LoginMixin(UserPassesTestMixin):
    def test_func(self, user):
        return user.is_authenticated()


class StaffMixin(UserPassesTestMixin):
    def test_func(self, user):
        return user.is_staff