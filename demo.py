import yaml
import urllib.parse
from microdot import Microdot, Response


# Define procedures as functions
def clotting_factor():
    return "Administer appropriate clotting factor replacement if necessary."


def blood_transfusion():
    return "blood transfusion if necessary."


def oncologist():
    return "Refer to a hematologist-oncologist."


emergency_procedures = """
Anemia:
  question: Is the anemia acute or chronic?
  responses:
    Acute: Treat the underlying cause of acute anemia. Provide $blood_transfusion
    Chronic: Evaluate the type and cause of chronic anemia. Initiate appropriate treatment.
Hemophilia:
  question: What is the severity of bleeding?
  responses:
    Mild: Apply pressure to the bleeding site. $clotting_factor
    Moderate: Apply pressure to the bleeding site. $clotting_factor Seek medical help if bleeding persists.
    Severe: Apply pressure to the bleeding site. $clotting_factor Seek immediate medical help.
Leukemia:
  question: What type of leukemia is suspected?
  responses:
    Acute Lymphoblastic Leukemia (ALL): Initiate chemotherapy and supportive care. Refer to a specialized oncology center.
    Acute Myeloid Leukemia (AML): Initiate chemotherapy and supportive care. Refer to a specialized oncology center.
    Chronic Lymphocytic Leukemia (CLL): Monitor the patient's condition and initiate treatment if necessary. $oncologist
    Chronic Myeloid Leukemia (CML): Initiate targeted therapy. $oncologist
Thrombocytopenia:
  question: Is the patient experiencing severe bleeding?
  responses:
    No: Monitor platelet count and observe for symptoms. Treat underlying cause if identified.
    Yes: Administer platelet transfusion. Treat underlying cause if identified. Seek immediate medical help.
Hemolytic Anemia:
  question: What is the suspected cause of hemolysis?
  responses:
    Autoimmune Hemolytic Anemia: Initiate immunosuppressive therapy. Consider $blood_transfusion
    Hereditary Spherocytosis: Manage symptoms and complications. Consider splenectomy in severe cases.
    G6PD Deficiency: Avoid triggers and medications that can cause hemolysis. Supportive care and monitoring.
Multiple Myeloma:
  question: What is the stage of multiple myeloma?
  responses:
    Stage 1: Monitor the patient's condition and initiate treatment if necessary. $oncologist
    Stage 2: Initiate chemotherapy and supportive care. Refer to a specialized oncology center.
    Stage 3: Initiate chemotherapy and supportive care. Refer to a specialized oncology center.
"""


# Convert YAML to dictionary
emergency_procedures = yaml.safe_load(emergency_procedures)

app = Microdot()
Response.default_content_type = "text/html"

current_state = {}

css_style = """
<style>
body {
    font-family: Arial, sans-serif;
    background-color: #f0f8ff;
    margin: 0;
    padding: 0;
}

h1 {
    color: #0d6efd;
    text-align: center;
    padding: 20px;
}

a {
    color: #0d6efd;
    text-decoration: none;
}

button {
    display: block;
    width: 200px;
    height: 50px;
    margin: 20px auto;
    background-color: #0d6efd;
    color: white;
    border: none;
    border-radius: 5px;
}

button:hover {
    background-color: #0b5ed7;
}

.response-box {
    width: 60%;
    margin: 20px auto;
    padding: 20px;
    border-radius: 5px;
    background-color: white;
    box-shadow: 0px 4px 8px rgba(0,0,0,0.2);
    text-align: center;
    font-size: 20px;
}
</style>
"""


def process_response(request, responses):
    if isinstance(responses, str):
        if responses.startswith("$"):
            func_name = responses[1:]  # Remove the "$" character
            func = globals().get(func_name)
            if func and callable(func):
                result = func()
            else:
                result = f"Function '{func_name}' not found."
        else:
            result = responses
    elif isinstance(responses, dict):
        if "question" in responses and "responses" in responses:
            result = present_options(
                request, responses["question"], responses["responses"]
            )
        else:
            result = process_response(request, responses["responses"])
    else:
        result = str(responses)
    return f'<div class="response-box">{result}</div>'


def present_options(request, question, responses):
    options_html = "".join(
        f'<a href="/procedure/{urllib.parse.quote(option)}"><button>{option}</button></a>'
        for option in responses.keys()
    )
    current_state["current_responses"] = responses  # Store the current state
    return f"<h1>{question}</h1><br>{options_html}"


@app.route("/")
@app.route("/procedure/<response>", methods=["GET", "POST"])
def handle_procedure(request, response=None):
    if response is None:  # If no response provided, begin procedure
        current_state.clear()
        response_html = present_options(
            request,
            "What is the nature of the blood-related disease or medical emergency?",
            emergency_procedures,
        )
    else:  # If a response is provided, handle it
        response = urllib.parse.unquote(response)
        next_step = current_state["current_responses"].get(
            response
        )  # Get the actions for the current response
        if next_step:
            response_html = process_response(request, next_step)

    return css_style + response_html


app.run(debug=True, port=8008)
