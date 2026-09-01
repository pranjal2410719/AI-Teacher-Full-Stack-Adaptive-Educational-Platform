"""
Tier 2 Boundary & Corner Cases: Corrupt and Empty Inputs
Tests rejection and clean error handling for 0-byte files, corrupt headers, unsupported MIME types, and missing IDs.
"""

import os
import pytest
from tests_e2e.harness import E2ETestHarness

@pytest.fixture
def harness():
    return E2ETestHarness()

def test_empty_0byte_file_upload_rejected(harness, empty_pdf_path):
    """Verifies that uploading a 0-byte empty file is rejected with HTTP 400."""
    res = harness.upload_material(empty_pdf_path)
    assert res["status_code"] == 400
    assert "empty" in str(res["data"]).lower()

def test_corrupt_format_file_upload_rejected(harness, corrupt_docx_path):
    """Verifies that uploading a corrupted binary file is rejected with HTTP 400."""
    res = harness.upload_material(corrupt_docx_path)
    assert res["status_code"] == 400
    assert "corrupt" in str(res["data"]).lower()

def test_unsupported_file_extension_rejected(harness, tmp_path):
    """Verifies that uploading unsupported extension like .exe or .bin returns HTTP 400."""
    fake_exe = tmp_path / "malicious.exe"
    fake_exe.write_bytes(b"MZ\x90\x00\x03\x00\x00\x00")
    
    res = harness.upload_material(str(fake_exe))
    assert res["status_code"] == 400
    assert "unsupported" in str(res["data"]).lower() or "allowed" in str(res["data"]).lower()

def test_nonexistent_plan_id_returns_404(harness):
    """Verifies querying an invalid plan_id returns HTTP 404."""
    res = harness.get_lesson_plan("plan_non_existent_99999")
    assert res["status_code"] == 404

def test_nonexistent_video_task_returns_404(harness):
    """Verifies polling an invalid task_id returns HTTP 404."""
    res = harness.get_video_status("task_non_existent_99999")
    assert res["status_code"] == 404

def test_nonexistent_video_manifest_returns_404(harness):
    """Verifies fetching an invalid lesson_id manifest returns HTTP 404."""
    res = harness.get_video_manifest("les_non_existent_99999")
    assert res["status_code"] == 404
