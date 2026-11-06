from quickstart_server import add_numbers, build_learning_prompt, explain_mcp_concept


def test_add_numbers() -> None:
    assert add_numbers(2, 40) == 42


def test_explain_known_concept() -> None:
    assert "Server" in explain_mcp_concept("server")


def test_explain_unknown_concept_lists_suggestions() -> None:
    result = explain_mcp_concept("transport")

    assert "暂时没有收录" in result
    assert "host" in result
    assert "stdio" in result


def test_build_learning_prompt_defaults_to_beginner() -> None:
    result = build_learning_prompt("tools")

    assert "零基础入门" in result
    assert "tools" in result
    assert "一句话定义" in result
