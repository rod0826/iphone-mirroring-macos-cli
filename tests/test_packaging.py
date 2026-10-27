import hashlib
import importlib.util
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("company_package", ROOT / "scripts/package-company.py")
packaging = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packaging)


def test_single_zip_contains_verifiable_payload_and_external_checksum(tmp_path):
    payload = tmp_path / "IPhone-Mirroring-CLI-0.1.1-company-test-arm64"
    payload.mkdir()
    (payload / "cli").mkdir()
    (payload / "cli/program").write_bytes(b"real payload bytes")
    (payload / "먼저읽기.md").write_text("test guide")
    archive = packaging.finalize_archive(payload)
    assert archive.name == payload.name + ".zip"
    checksum = Path(str(archive) + ".sha256").read_text()
    assert checksum == hashlib.sha256(archive.read_bytes()).hexdigest() + "  " + archive.name + "\n"
    extracted = tmp_path / "extracted with spaces"
    subprocess.run(["/usr/bin/ditto", "-x", "-k", str(archive), str(extracted)], check=True)
    result = subprocess.run(["/bin/bash", str(extracted / payload.name / "검증.command")], capture_output=True)
    assert result.returncode == 0, result.stderr
    (extracted / payload.name / "cli/program").write_bytes(b"tampered")
    result = subprocess.run(["/bin/bash", str(extracted / payload.name / "검증.command")], capture_output=True)
    assert result.returncode != 0
    # The installer must stop before touching a real user directory on integrity failure.
    result = subprocess.run(["/bin/bash", str(extracted / payload.name / "설치.command")], capture_output=True)
    assert result.returncode != 0 and b"SHA" in result.stdout + result.stderr


def test_verifier_does_not_remove_quarantine(tmp_path):
    payload = tmp_path / "payload"
    payload.mkdir()
    marker = payload / "example.txt"
    marker.write_text("test")
    subprocess.run(["/usr/bin/xattr", "-w", "com.apple.quarantine", "0081;00000000;Test;", str(marker)], check=True)
    packaging.finalize_archive(payload)
    subprocess.run(["/bin/bash", str(payload / "검증.command")], check=True, capture_output=True)
    result = subprocess.run(["/usr/bin/xattr", "-p", "com.apple.quarantine", str(marker)], check=True, capture_output=True)
    assert b"0081" in result.stdout
