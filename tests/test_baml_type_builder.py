"""
A simple functional test for the BAML TypeBuilder.
"""

import unittest
from unittest.mock import patch
from baml_py import BamlRuntime
from dynamic_baml.baml import type_builder

class TestBamlTypeBuilderFunctional(unittest.TestCase):

    def test_type_builder_functional(self):
        """
        A functional test that uses a real BamlRuntime to test the TypeBuilder.
        This avoids the complexities of mocking the runtime and its dependencies.
        """
        # The BAML project for this test is located in the root of the project.
        # baml_src is a directory that contains the baml files.
        runtime = BamlRuntime.from_files(root_path="baml_src", files={"main.baml": ""}, env_vars={})
        
        with patch('dynamic_baml.baml.globals.DO_NOT_USE_DIRECTLY_UNLESS_YOU_KNOW_WHAT_YOURE_DOING_RUNTIME', runtime):
            tb = type_builder.TypeBuilder()
            
            self.assertIsInstance(tb.Resume, type_builder.ResumeAst)
            self.assertIsInstance(tb.Resume.props, type_builder.ResumeProperties)
            
            # Test the properties on the props object.
            self.assertIsNotNone(tb.Resume.props.name)
            self.assertIsNotNone(tb.Resume.props.email)
            self.assertIsNotNone(tb.Resume.props.experience)
            self.assertIsNotNone(tb.Resume.props.skills)

            # Test the viewer
            viewer = type_builder.ResumeViewer(tb)
            properties = sorted(viewer.list_properties(), key=lambda x: x[0])
            self.assertEqual(len(properties), 4)
            self.assertEqual(properties[0][0], "email")
            self.assertEqual(properties[1][0], "experience")
            self.assertEqual(properties[2][0], "name")
            self.assertEqual(properties[3][0], "skills")

            # Test the type method
            field_type = tb.Resume.type()
            self.assertIsNotNone(field_type)


if __name__ == "__main__":
    unittest.main() 