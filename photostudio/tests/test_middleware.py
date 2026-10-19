import pytest


@pytest.mark.django_db
def test_middleware_konsolga_yozadi(client, capsys):
    client.get('/about/')
    output = capsys.readouterr().out
    assert '[Middleware] GET /about/ -> 200' in output
    assert 'ms)' in output
