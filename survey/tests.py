import unittest
# from django.test import TestCase


class SurveyTestCase(unittest.TestCase):
    def setUp(self):
        print('------ start to setup')


class DummyTest(SurveyTestCase):
    # dummy test case
    def test_parser(self):
        fileName = 'survey_diary'
        self.assertEqual('survey_diary', fileName)
