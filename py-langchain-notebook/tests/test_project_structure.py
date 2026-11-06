from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ProjectStructureTest(unittest.TestCase):
    def test_expected_directories_exist(self) -> None:
        expected = [
            ROOT / "docs" / "langchain-langgraph",
            ROOT / "examples" / "01_models",
            ROOT / "examples" / "02_agents",
            ROOT / "examples" / "03_tools",
            ROOT / "examples" / "04_memory",
            ROOT / "examples" / "05_graph_basics",
            ROOT / "examples" / "06_workflows",
            ROOT / "examples" / "07_persistence_hitl",
            ROOT / "examples" / "08_streaming_testing",
            ROOT / "src" / "learning_langchain",
            ROOT / "tests",
        ]

        for path in expected:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), f"missing path: {path}")

    def test_docs_index_links_all_core_topics(self) -> None:
        readme = ROOT / "docs" / "langchain-langgraph" / "README.md"
        content = readme.read_text(encoding="utf-8")

        expected_links = [
            "./01_environment_and_models.md",
            "./02_langchain_agents.md",
            "./03_tools_and_structured_output.md",
            "./04_short_term_memory_and_context.md",
            "./05_langgraph_state_and_nodes.md",
            "./06_workflow_patterns.md",
            "./07_persistence_and_human_in_the_loop.md",
            "./08_streaming_observability_and_testing.md",
        ]

        for link in expected_links:
            with self.subTest(link=link):
                self.assertIn(link, content)

    def test_example_scripts_exist(self) -> None:
        expected_scripts = [
            ROOT / "examples" / "01_models" / "model_basics.py",
            ROOT / "examples" / "02_agents" / "agent_with_tools.py",
            ROOT / "examples" / "03_tools" / "structured_output.py",
            ROOT / "examples" / "04_memory" / "short_term_memory.py",
            ROOT / "examples" / "05_graph_basics" / "simple_state_graph.py",
            ROOT / "examples" / "06_workflows" / "conditional_workflow.py",
            ROOT / "examples" / "07_persistence_hitl" / "interrupt_demo.py",
            ROOT / "examples" / "08_streaming_testing" / "stream_events.py",
        ]

        for script in expected_scripts:
            with self.subTest(script=script):
                self.assertTrue(script.exists(), f"missing example: {script}")

    def test_uv_python_version_files_exist(self) -> None:
        python_version = ROOT / ".python-version"
        self.assertTrue(python_version.exists(), "missing .python-version")
        self.assertEqual(python_version.read_text(encoding="utf-8").strip(), "3.12")

        root_readme = ROOT / "README.md"
        content = root_readme.read_text(encoding="utf-8")
        self.assertIn("uv sync", content)


if __name__ == "__main__":
    unittest.main()
