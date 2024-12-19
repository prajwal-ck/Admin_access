from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import vercel_API.api_v1 as api_v1

app = FastAPI()

# Serve static files from the "static" directory
app.mount("/static", StaticFiles(directory="static"), name="test")

@app.get("/")
def homepage():
    try:
        result = api_v1.main()
        # Execute the Python file and capture its output
        # if result.returncode == 0:
        return HTMLResponse(content=f"<h2>Script executed successfully!</h2><pre>{result}</pre>")
        # else:
        #     return HTMLResponse(content=f"<h2>Script execution failed!</h2><pre>{result.stderr}</pre>")
    except Exception as e:
        return HTMLResponse(content=f"<h2>An error occurred:</h2><pre>{str(e)}</pre>")
# if __name__ == "__main__":
#     main()cls