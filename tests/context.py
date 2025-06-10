"""Test context for dynamic_baml package.

This module provides proper import handling for tests as recommended 
in the Python Package Repository Structure Guide.
"""

import os
import sys

# Add the parent directory to the path so we can import dynamic_baml
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import dynamic_baml 