# GAUNTLET provenance contract (draft v0)

Portable, optional validation at the GAUNTLET protocol boundary; no import from VALO core, ACE, HEIMEL, Hermes or Agy.

| Source | Minimum classification | Reason |
| --- | --- | --- |
| VALO adversarial suite without external checker | `SIMULATED` | Built-in heuristic, not an actual governance-chain test |
| HEIMEL synthetic benchmark | `SIMULATED` | Synthetic actors and effect sink, even when receipts validate |
| GAUNTLET local Agy + gateway test | `LOCAL_EXECUTED` | Live target plus isolated effect parser, without independent attestation |
| External verifier with independently checked evidence | `VERIFIED` candidate | Requires verification evidence and distinct verifier identity |
| Separate independent attestor | `INDEPENDENTLY_ATTESTED` candidate | Requires distinct attestor and independent evidence |

`contract.py` rejects unsupported assurance claims and self-verification **at metadata level only**. An attacker can fabricate IDs and digests: passing the contract is **not** cryptographic verification. Never issue a verified badge from this validator alone. Future trusted verification must validate actual content digests, signatures, identity binding, execution chain and effect observations.

ACE remains the source of truth for expected-versus-realized economics and Veritas-bound receipts. This contract does not duplicate ACE's realization logic. No VALO implementation has been changed.