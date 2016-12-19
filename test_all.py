import responses
from unittest import mock
import pika
import io
from contextlib import redirect_stdout
from producer import get_page, produce
from consumer import consumer
import json
import settings


simple_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Test</title>
</head>
<body>

<div></div>
<div>
    <div>
        <p><a href="test1.html"></a></p>
        <p></p>
    </div>
    <a href="test2.html">Test2</a>
    <table>
        <tr>
            <td><a href="https://outside.domain.com"><img src="img.jpg" alt=""></a></td>
            <td><a href="mailto://test@test.com">mail</a></td>
        </tr>
        <tr><td>1</td></tr>
    </table>
</div>
</body>
</html>'''

@responses.activate
def test_get_page():
    responses.add(responses.GET, 'http://test.com/test',
                  body=simple_html, status=200,
                  content_type='text/html')
    r1 = get_page('http://test.com/test')
    assert r1 == simple_html
    assert responses.calls[0].request.url == 'http://test.com/test'
    responses.add(responses.GET, 'http://test.com/bad',
                  body=simple_html, status=400,
                  content_type='text/html')
    r2 = get_page('http://test.com/bad')
    assert r2 == None

@responses.activate
@mock.patch.object(pika.adapters.blocking_connection.BlockingChannel, 'basic_publish', autospec=True)
def test_produce(mock_basic_publish):
    responses.add(responses.GET, 'http://test.com/test',
                  body=simple_html, status=200,
                  content_type='text/html')
    produce('http://test.com/test')
    mock_basic_publish.assert_called_with(mock.ANY, exchange='',
                              routing_key=settings.QUEUE_NAME,
                              body=json.dumps({'link': 'http://test.com/test', 'source': simple_html}))

def test_consumer():
    body = json.dumps({'link': 'http://test.com/test', 'source': simple_html}).encode()
    f = io.StringIO()
    with redirect_stdout(f):
        consumer(None, None, None, body)
    assert f.getvalue() == 'http://test.com/test, http://test.com/test1.html http://test.com/test2.html https://outside.domain.com\n'