from src.utils import sanitize_filename

def test_sanitize_filename():
    name = "KUMARI, PRITI"
    result = sanitize_filename(name)

    assert result == "KUMARI_PRITI"