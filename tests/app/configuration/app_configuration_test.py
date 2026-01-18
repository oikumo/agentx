import unittest

from agent_x.repl_app.configuration.app_configuration import AppConfiguration


class ConfigTest(unittest.TestCase):
    def test_parse(self):
        json = '{"description":"x", "llmModels": [{"name": "uno"}]}'
        config = AppConfiguration.model_validate_json(json)
        self.assertTrue(len(config.llmModels) == 1)
