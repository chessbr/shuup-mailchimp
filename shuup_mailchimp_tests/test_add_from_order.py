# -*- coding: utf-8 -*-
# This file is part of Shuup Mailchimp Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import pytest
import requests
from mock import Mock, patch

from shuup import configuration
from shuup.testing.factories import create_empty_order
from shuup_mailchimp.configuration_keys import MC_ENABLED
from shuup_mailchimp.interface import update_or_create_contact_from_order
from shuup_mailchimp.models import MailchimpContact
from shuup_mailchimp_tests.mock_responses import (
    raise_on_request, success_response
)


@pytest.mark.django_db
@patch.object(requests, 'post', Mock(side_effect=raise_on_request))
@patch.object(requests, 'put', Mock(side_effect=success_response))
@patch.object(requests, 'get', Mock(side_effect=raise_on_request))
def test_creating_contact_from_order_email(default_shop, valid_company, valid_test_configuration):
    configuration.set(default_shop, MC_ENABLED, True)

    # First test without marketing permission
    order = create_empty_order(shop=default_shop)
    order.email = "valid@example.com"
    order.marketing_permission = False
    order.save()

    assert MailchimpContact.objects.count() == 0
    update_or_create_contact_from_order(order.__class__, order)
    assert MailchimpContact.objects.count() == 0

    # Then with marketing permission should go through
    order = create_empty_order(shop=default_shop)
    order.email = "valid@example.com"
    order.marketing_permission = True
    order.save()

    update_or_create_contact_from_order(order.__class__, order)
    mailchimp_contact = MailchimpContact.objects.get(email=order.email)
    assert mailchimp_contact.sent_to_mailchimp is not None
