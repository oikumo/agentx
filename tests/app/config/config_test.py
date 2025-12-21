import unittest

from agent_x.app.config.config import Config

class ConfigTest(unittest.TestCase):
    def test_parse(self):
        json = '{"description":"x", "llmModels": [{"name": "uno"}]}'
        config = Config.model_validate_json(json)
        self.assertTrue(len(config.llmModels) == 1)
