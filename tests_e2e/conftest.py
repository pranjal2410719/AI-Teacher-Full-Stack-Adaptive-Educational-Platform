import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import pytest
from tests_e2e.harness import E2ETestHarness, FIXTURES_DIR

@pytest.fixture(scope="session")
def harness():
    """Provides an initialized E2ETestHarness instance for test sessions."""
    return E2ETestHarness()

@pytest.fixture(scope="session")
def fixtures_dir():
    """Returns absolute path to the educational fixtures directory."""
    return FIXTURES_DIR

@pytest.fixture(scope="session")
def math_pdf_path(fixtures_dir):
    return os.path.join(fixtures_dir, "calculus_limits.pdf")

@pytest.fixture(scope="session")
def cs_docx_path(fixtures_dir):
    return os.path.join(fixtures_dir, "binary_search_trees.docx")

@pytest.fixture(scope="session")
def bio_pptx_path(fixtures_dir):
    return os.path.join(fixtures_dir, "cell_biology.pptx")

@pytest.fixture(scope="session")
def history_txt_path(fixtures_dir):
    return os.path.join(fixtures_dir, "industrial_revolution.txt")

@pytest.fixture(scope="session")
def empty_pdf_path(fixtures_dir):
    return os.path.join(fixtures_dir, "empty_document.pdf")

@pytest.fixture(scope="session")
def corrupt_docx_path(fixtures_dir):
    return os.path.join(fixtures_dir, "corrupted_format.docx")

@pytest.fixture(scope="session")
def large_syllabus_path(fixtures_dir):
    return os.path.join(fixtures_dir, "large_syllabus.txt")
