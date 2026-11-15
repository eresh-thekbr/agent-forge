import unittest

from .knowledge import ENTITIES, FACTS, Fact, find_paths
from .workflow import build_workflow


class KnowledgeGraphTests(unittest.TestCase):
    def test_facts_reference_existing_entities(self):
        for fact in FACTS:
            self.assertIn(fact.source, ENTITIES)
            self.assertIn(fact.target, ENTITIES)

    def test_two_hop_query_and_evidence(self):
        result = build_workflow().invoke({"technology": "  PYTHON "})
        self.assertEqual(result["people"], ["Alice", "Bob"])
        self.assertEqual(result["evidence"], [
            "Alice --WORKS_ON--> Atlas; Atlas --USES--> Python",
            "Bob --WORKS_ON--> Atlas; Atlas --USES--> Python",
        ])

    def test_other_project(self):
        result = build_workflow().invoke({"technology": "TypeScript"})
        self.assertEqual(result["people"], ["Carol"])

    def test_missing_facts_and_unknown_entity_are_distinct(self):
        graph = build_workflow()
        for technology, message in [("Rust", "No matching facts"), ("Java", "Unknown technology"), ("", "Unknown technology")]:
            with self.subTest(technology=technology):
                result = graph.invoke({"technology": technology})
                self.assertEqual(result["people"], [])
                self.assertEqual(result["evidence"], [])
                self.assertIn(message, result["answer"])

    def test_relationship_direction_and_type_matter(self):
        facts = (Fact("atlas", "USES", "python"),
                 Fact("atlas", "WORKS_ON", "alice"),
                 Fact("bob", "LIKES", "atlas"))
        self.assertEqual(find_paths("python", facts), [])


if __name__ == "__main__":
    unittest.main()
