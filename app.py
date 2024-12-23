from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import process_request
import uvicorn
app = FastAPI()

# Serve static files from the "static" directory
@app.get("/")
def homepage():
    try:
        result = process_request.main()
        # Execute the Python file and capture its output
        # if result.returncode == 0:
        return HTMLResponse(content=f"<h2>Script executed successfully!</h2><pre>{result}</pre>")
        # else:
        #     return HTMLResponse(content=f"<h2>Script execution failed!</h2><pre>{result.stderr}</pre>")
    except Exception as e:
        return HTMLResponse(content=f"<h2>An error occurred:</h2><pre>{str(e)}</pre>")

if __name__ == "__main__":
    uvicorn.run(app)
