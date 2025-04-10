import pytest
from maestro_mcp.maestro_cli import MaestroCli


@pytest.fixture
def maestro_cli():
    return MaestroCli(
        api_key=os.environ.get("MAESTRO_API_KEY", None),
        maestro_binary_path=os.environ.get("MAESTRO_BINARY_PATH", None),
        api_server=os.environ.get("MAESTRO_API_SERVER", "https://api.copilot.mobile.dev"),
    )


def test_run_code(maestro_cli):
    res = maestro_cli.run_code("tapOn: login")
    print(res)
    assert res.index("Running on") >= 0


def test_cheat_sheet(maestro_cli):
    res = maestro_cli.cheat_sheet()
    print(res)
    assert "Maestro Flow Script Cheat Sheet" in res


def test_query_docs(maestro_cli):
    res = maestro_cli.query_docs("tapping?")
    print(res)
    assert res.index("tapOn") >= 0


def test_maestro_cli_check_syntax(maestro_cli):
    try:
        maestro_cli.check_syntax("""
        tapO n: "123"
        """)
        assert False # should fail
    except Exception as e:
        print(e)
        assert e.__str__().index("Did you mean `tapOn`?") != -1

    res = maestro_cli.check_syntax("""
    tapOn: "123"
    """)
    print(res)
    assert res == "OK"
