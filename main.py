import json
import urllib.parse
from microdot import Microdot, Response

app = Microdot()
Response.default_content_type = "text/html"

css_path = "node_modules/@picocss/pico/css/pico.min.css"
title = "New Expert System"

head_tags = f"""
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="stylesheet" href={css_path} />
    <title>{title}</title>
</head>
"""

# Load expert knowledge from JSON file
with open("expert.json") as f:
    expert_data = json.load(f)

expert_questions = expert_data["questions"]
conditions = expert_data["conditions"]


@app.route(css_path)
def pico_css(request):
    return Response.send_file(css_path)


@app.route(f"{css_path}.map")
def pico_css_map(request):
    return Response.send_file(f"{css_path}.map")


@app.route("/")
def landing_page(request):
    page_html = f"""
    <!DOCTYPE html>
    <html lang="en">
      {head_tags}
      <body>
        <main class="container">
          <h1>Welcome to the Expert System</h1>
          <a href="/expert_system"><button>Blood disease symptom diagnosis</button></a>
          <a href="/deep_learning"><button>Exploring white blood cells</button></a>
        </main>
      </body>
    </html>
    """
    return page_html


def process_response(request, question_id, answer_id):
    question = expert_questions[question_id - 1]
    answer = question["answers"][answer_id - 1]
    condition = answer.get("condition")

    if condition:
        condition_data = next((c for c in conditions if c["id"] == condition), None)
        if condition_data:
            response_html = f"""
            <h1>{condition_data["name"]}</h1>
            <p>{condition_data["description"]}</p>
            """
        else:
            response_html = "<p>Condition not found.</p>"
    else:
        follow_up_questions = answer.get("follow_up_questions")
        if follow_up_questions:
            next_question = follow_up_questions[0]
            response_html = present_options(request, next_question)
        else:
            response_html = "<p>End of expert system.</p>"

    return response_html


def present_options(request, question):
    question_id = question["id"]
    question_text = question["text"]
    answers = question["answers"]

    options_html = "".join(
        f'<a href="/procedure/{question_id}/{answer["id"]}"><button>{answer["text"]}</button></a>'
        for answer in answers
    )

    response_html = f"""
    <h1>{question_text}</h1>
    <br>
    {options_html}
    """

    return response_html


@app.route("/expert_system")
@app.route("/procedure/<int:question_id>/<int:answer_id>", methods=["GET", "POST"])
def expert_system(request, question_id=None, answer_id=None):
    if question_id is None:
        # Initial state
        response_html = present_options(request, expert_questions[0])
    elif question_id > 0 and answer_id > 0:
        # Process the response
        response_html = process_response(request, question_id, answer_id)
    else:
        response_html = "<p>Invalid question or answer ID.</p>"

    page_html = f"""
    <!DOCTYPE html>
    <html lang="en">
        {head_tags}
        <body>
            <main class="container">
                {response_html}
            </main>
        </body>
    </html>
    """
    return page_html


@app.route("/deep_learning")
def deep_learning_module(request):
    h1_text = "Deep Learning Module"
    page_html = f"""
    <!DOCTYPE html>
    <html lang="en">
        {head_tags}
        <body>
            <main class="container">
                <h1>{h1_text}</h1>
                <!-- Add code for deep learning module -->
            </main>
        </body>
    </html>
    """
    return page_html


app.run(debug=True, port=8000)
