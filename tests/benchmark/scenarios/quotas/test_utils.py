# Copyright 2014: Kylin Cloud
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock

from rally.benchmark.scenarios.quotas import utils
from tests.benchmark.scenarios import test_utils
from tests import fakes
from tests import test


class QuotasScenarioTestCase(test.TestCase):

    def setUp(self):
        super(QuotasScenarioTestCase, self).setUp()

    def _test_atomic_action_timer(self, atomic_actions_time, name):
        action_duration = test_utils.get_atomic_action_timer_value_by_name(
            atomic_actions_time, name)
        self.assertIsNotNone(action_duration)
        self.assertIsInstance(action_duration, float)

    def test__update_quotas(self):
        tenant_id = 'fake_tenant'
        quotas = {
                'metadata_items': 10,
                'key_pairs': 10,
                'injected_file_content_bytes': 1024,
                'injected_file_path_bytes': 1024,
                'ram': 5120,
                'instances': 10,
                'injected_files': 10,
                'cores': 10,
        }
        fake_nova = fakes.FakeNovaClient()
        fake_nova.quotas.update = mock.MagicMock(return_value=quotas)
        fake_clients = fakes.FakeClients()
        fake_clients._nova = fake_nova
        scenario = utils.QuotasScenario(admin_clients=fake_clients)
        scenario._generate_quota_values = mock.MagicMock(return_value=quotas)

        result = scenario._update_quotas('nova', tenant_id)

        self.assertEqual(quotas, result)
        fake_nova.quotas.update.assert_called_once_with(tenant_id, **quotas)
        self._test_atomic_action_timer(scenario.atomic_actions(),
                                       'quotas.update_quotas')

    def test__delete_quotas(self):
        tenant_id = 'fake_tenant'
        fake_nova = fakes.FakeNovaClient()
        fake_nova.quotas.delete = mock.MagicMock()
        fake_clients = fakes.FakeClients()
        fake_clients._nova = fake_nova
        scenario = utils.QuotasScenario(admin_clients=fake_clients)

        scenario._delete_quotas('nova', tenant_id)

        fake_nova.quotas.delete.assert_called_once_with(tenant_id)
        self._test_atomic_action_timer(scenario.atomic_actions(),
                                       'quotas.delete_quotas')
