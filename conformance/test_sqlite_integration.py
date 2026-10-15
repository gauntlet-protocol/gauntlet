"""Integration: signed database commit observed via a separate read-only connection.

The test proves digital state observation, NOT operational independence of
keys, integrity of the database host, or external physical consequences.
"""
import base64
import os
import sqlite3
import tempfile
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from signed_effect import sha, signable, verify


class SQLiteEffectIntegration(unittest.TestCase):
    def test_observed_commit_independent_connection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "ledger.sqlite")
            writer = sqlite3.connect(path)
            writer.execute("CREATE TABLE accounts (id TEXT PRIMARY KEY, balance INTEGER NOT NULL)")
            writer.execute("INSERT INTO accounts VALUES ('a1', 500)")
            writer.commit()
            reader = sqlite3.connect("file:" + path + "?mode=ro", uri=True)
            self.assertEqual(reader.execute("SELECT balance FROM accounts WHERE id='a1'").fetchone()[0], 500)

            private = {role: Ed25519PrivateKey.generate()
                       for role in ("authority", "executor", "database", "observer")}
            kinds = {"authority": "AUTHORIZATION", "executor": "EXECUTION_RECEIPT",
                     "database": "SOURCE_STATE", "observer": "EFFECT_ATTESTATION"}
            trust = {"source_integrity_independently_audited": True, "keys": {
                role: {"operator": role, "allowed_kinds": [kind],
                       "public_hex": private[role].public_key().public_bytes(
                           Encoding.Raw, PublicFormat.Raw).hex()}
                for role, kind in kinds.items()}}
            def receipt(role, payload):
                env = {"kind": kinds[role], "key_id": role, "payload": payload}
                env["signature"] = base64.b64encode(private[role].sign(signable(env))).decode()
                return env

            auth = receipt("authority", {"effect_id": "e1", "scope": "balance",
                "decision": "ALLOW", "issued_at": 10, "expires_at": 30,
                "predicate": {"field": "balance", "delta": -100}})
            execution = receipt("executor", {"effect_id": "e1", "scope": "balance",
                "transaction_id": "t1", "authorization_sha256": sha(auth),
                "result": "SUCCESS"})
            # The writer commits first; the independent read-only connection
            # must then see the durable state. SQLite is the authority here.
            writer.execute("BEGIN IMMEDIATE")
            writer.execute("UPDATE accounts SET balance=balance-100 WHERE id='a1'")
            writer.commit()
            observed = reader.execute("SELECT balance FROM accounts WHERE id='a1'").fetchone()[0]
            self.assertEqual(observed, 400)
            source = receipt("database", {"effect_id": "e1", "scope": "balance",
                "transaction_id": "t1", "execution_sha256": sha(execution),
                "committed_at": 20, "source_commit_id": "t1",
                "before": {"balance": 500}, "after": {"balance": observed}})
            attestation = receipt("observer", {"effect_id": "e1", "transaction_id": "t1",
                "execution_sha256": sha(execution), "source_sha256": sha(source),
                "predicate_sha256": sha(auth["payload"]["predicate"])})
            bundle = {"authorization": auth, "execution": execution,
                      "source_state": source, "observation": attestation}
            self.assertEqual(verify(bundle, trust)["status"], "VERIFIED_EFFECT")
            reader.close()
            writer.close()


if __name__ == "__main__":
    unittest.main()
