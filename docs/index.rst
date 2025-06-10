Dynamic BAML Documentation
===========================

Dynamic BAML is a Python library for structured data extraction from text using Large Language Models with dynamically generated schemas.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   api_reference
   examples
   advanced_usage

Features
--------

* **Dynamic Schema Generation**: Create BAML schemas on-the-fly from Python data structures
* **Multi-Provider Support**: Works with OpenAI, Anthropic, Ollama, OpenRouter, and more
* **Type Safety**: Full type hints and runtime validation with Pydantic
* **Error Handling**: Comprehensive exception hierarchy for robust applications
* **High Performance**: Optimized for both single extractions and batch processing

Quick Start
-----------

.. code-block:: python

   from dynamic_baml import DynamicBAML

   # Initialize with your provider
   extractor = DynamicBAML(provider="openai", api_key="your-key")

   # Define your data structure
   schema = {
       "name": str,
       "age": int,
       "email": str
   }

   # Extract structured data
   text = "John Doe is 30 years old. His email is john@example.com"
   result = extractor.extract(text, schema)
   print(result.name, result.age, result.email)

Installation
------------

.. code-block:: bash

   pip install dynamic_baml

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 