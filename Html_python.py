from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import subprocess  # To execute the Python file

app = FastAPI()

# Serve static files from the "static" directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def homepage():
    # Serve the HTML file
    with open("static/test.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/run-script")
def run_script():
    try:
        # Execute the Python file and capture its output
        result = subprocess.run(
            ["python", "api_v1.py"], capture_output=True, text=True
        )
        if result.returncode == 0:
            return HTMLResponse(content=f"<h2>Script executed successfully!</h2><pre>{result.stdout}</pre>")
        else:
            return HTMLResponse(content=f"<h2>Script execution failed!</h2><pre>{result.stderr}</pre>")
    except Exception as e:
        return HTMLResponse(content=f"<h2>An error occurred:</h2><pre>{str(e)}</pre>")
