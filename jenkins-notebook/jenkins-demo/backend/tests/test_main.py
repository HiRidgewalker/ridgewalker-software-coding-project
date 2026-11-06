from app.main import get_item, get_items, health


def test_health():
    assert health() == {"status": "ok"}


def test_get_items():
    data = get_items()
    assert len(data) == 3


def test_get_item():
    assert get_item(1)["name"] == "Learn Docker"


def test_get_item_not_found():
    assert get_item(999) == {"error": "not found"}
