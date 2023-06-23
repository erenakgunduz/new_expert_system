import json
import urllib.parse
from microdot import Microdot, Response

app = Microdot()
Response.default_content_type = "text/html"

css_path = "node_modules/@picocss/pico/css/pico.min.css"


@app.route(css_path)
def pico_css(request):
    return Response.send_file(css_path)


@app.route("/")
def hello(request):
    h1_text = "Hello, world!"
    page_html = f"""
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <link rel="stylesheet" href={css_path} />
            <title>Document</title>
        </head>
        <body>
            <main class="container">
                <h1>{h1_text}</h1>
            </main>
        </body>
    </html>
    """
    return page_html


app.run(debug=True, port=8000)
