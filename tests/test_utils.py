from src.utils import sanitize_filename

def test_sanitize_filename():
    name = "DOE, JANE"
    result = sanitize_filename(name)

    assert result == "DOE_JANE"