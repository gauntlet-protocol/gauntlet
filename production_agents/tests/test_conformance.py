import unittest

from production_agents.conformance import EFFECT_GATES, MATRIX, evaluate, evaluate_suite


def valid_case(question="Q01", material_effect=False):
    fields = MATRIX[question][1] + (EFFECT_GATES if material_effect else ())
    return {"question": question, "material_effect": material_effect,
            "evidence": {key: True for key in fields}}


class ConformanceTests(unittest.TestCase):
    def test_full_matrix(self):
        self.assertEqual(len(MATRIX), 18)
        self.assertEqual(sorted(MATRIX), [f"Q{i:02}" for i in range(1, 19)])
        suite = {"cases": [valid_case(q) for q in MATRIX]}
        report = evaluate_suite(suite)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(len(report["results"]), 18)

    def test_all_effect_gates_fail_closed(self):
        for gate in EFFECT_GATES:
            with self.subTest(gate=gate):
                item = valid_case("Q13", True)
                item["evidence"][gate] = False
                self.assertEqual(evaluate(item).status, "FAIL")
                item["evidence"][gate] = None
                self.assertEqual(evaluate(item).status, "INSUFFICIENT_EVIDENCE")

    def test_all_question_signals_fail_closed(self):
        for question, (_, fields) in MATRIX.items():
            for field in fields:
                with self.subTest(question=question, field=field):
                    item = valid_case(question)
                    del item["evidence"][field]
                    self.assertEqual(evaluate(item).status, "INSUFFICIENT_EVIDENCE")
                    item["evidence"][field] = False
                    self.assertEqual(evaluate(item).status, "FAIL")

    def test_attack_scenarios(self):
        attacks = (
            ("Q04", "independent_observation"),  # timeout after execution
            ("Q08", "governed_effect_path"),      # parallel bypass
            ("Q13", "effect_idempotent"),         # duplicated retry
            ("Q03", "recovery_reconciled"),       # stale state restored
            ("Q17", "fresh_authority"),            # revoked mandate
            ("Q05", "receipt_effect_binding"),    # self-reported receipt
        )
        for question, gate in attacks:
            with self.subTest(question=question, gate=gate):
                item = valid_case(question, True)
                item["evidence"][gate] = False
                self.assertEqual(evaluate(item).status, "FAIL")

    def test_bogus_evidence_is_unknown(self):
        item = valid_case("Q04", True)
        item["evidence"]["fresh_authority"] = "yes"
        self.assertEqual(evaluate(item).status, "INSUFFICIENT_EVIDENCE")
        item.pop("material_effect")
        self.assertEqual(evaluate(item).status, "INSUFFICIENT_EVIDENCE")

    def test_suite_requires_nonempty_unique_cases(self):
        with self.assertRaises(ValueError):
            evaluate_suite({"cases": []})
        with self.assertRaises(ValueError):
            evaluate_suite({"cases": [valid_case(), valid_case()]})

    def test_stable_report(self):
        payload = {"cases": [valid_case("Q18", True)]}
        self.assertEqual(evaluate_suite(payload), evaluate_suite(payload))


if __name__ == "__main__":
    unittest.main()
