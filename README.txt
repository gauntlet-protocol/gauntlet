GAUNTLET
Vendor-neutral adversarial conformance tests.

CAP-03 is a preliminary cumulative normative regression detector.
Run: python capture/cap03/capture.py capture/cap03/history.json
Tests: cd capture/cap03 && python -m unittest discover -s tests -v

Scope limitation: declarations are supplied as inputs; CAP-03 does not independently execute historical counterexamples. This prototype does not certify vendors or establish standards capture.
