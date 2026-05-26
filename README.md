# IoT Security Lab

This repository contains an RFID/NFC security laboratory simulation under `rfid_nfc_lab/`.
It includes simulators, attack demonstrations, defense mechanisms, and reporting utilities for RFID/NFC security concepts.

## Repository structure

- `rfid_nfc_lab/`
  - `rfid/` - RFID EM4100 and related reader/cloner simulation
  - `nfc/` - NFC NTAG213 tag, reader, and injector simulation
  - `access_control/` - Access control server that authorizes UIDs
  - `attacks/` - Attack scenarios: eavesdropping, replay, relay, cloning
  - `defense/` - Defense modules: secure reader, secure tag
  - `dashboard/` - Flask dashboard for monitoring events
  - `test_lab.py` - Full end-to-end lab test runner
  - `final_report.py` - Detailed summary of lab completion and requirements

## Setup

1. Install Python dependencies:

```bash
cd /workspaces/IoT
python3 -m pip install -r rfid_nfc_lab/requirements.txt
```

2. Run the full lab test suite:

```bash
python3 rfid_nfc_lab/test_lab.py
```

The test runner now resolves internal script paths correctly, so it can be executed from the repository root.

## Expected output

The lab test suite verifies:

- Simulator modules start and respond on their TCP ports
- Attack scenarios reproduce security weaknesses
- Defense mechanisms are validated where available

A successful run should show:

- `3/3` simulator tests pass
- `4/4` attack tests pass
- `1/3` defense tests pass, with one `SKIP` and one `PARTIAL`
- Overall test result: `8/10 tests passed (80%)`

### Meaning of results

- `PASS` means the module responded correctly and the test objective was met.
- `SKIP` means the coverage check could not run because a supporting server was not started (for example, `secure_tag.py`).
- `PARTIAL` means the module is reachable, but the expected security property is not fully enforced.

### Specific findings from the current lab run

- Simulators:
  - `RFID EM4100` responded with UID and type
  - `NFC NTAG213` responded with UID and NDEF support
  - `Access Control` loaded the card database successfully
- Attacks:
  - `Eavesdropping` captured an unencrypted UID
  - `Replay Attack` demonstrated reauthorization using the same UID
  - `Brute Force` executed a UID sweep with no valid UID found in the tested range
  - `RFID Cloning` exposed owner information leakage
- Defenses:
  - `Anti-Replay` successfully blocked repeated authentication attempts
  - `NDEF HMAC` is not exercised because the secure tag server is not running
  - `NFC Write Protection` remains only partially enforced because NDEF content is still readable

## Output location

Test results are written to:

- `rfid_nfc_lab/test_results.json`

Use this file to inspect the exact status and detailed messages produced by the test runner.
