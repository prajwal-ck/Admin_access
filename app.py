from fastapi import FastAPI
from fastapi.responses import JSONResponse
import process_request
import uvicorn

app = FastAPI()

@app.get("/")
def homepage():
    try:
        result = process_request.main()
        # Return the result in JSON format
        return JSONResponse(content={"message": "Script executed successfully!", "result": result})
    except Exception as e:
        # Return error details in JSON format
        return JSONResponse(content={"message": "An error occurred.", "error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app)
