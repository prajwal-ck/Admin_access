from flask import Flask, render_template_string
import process_request

app = Flask(__name__)

@app.route("/")
def homepage():
    try:
        # Execute the Python function and capture its output
        result = process_request.main()
        return render_template_string(
            """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Script Execution</title>
            </head>
            <body>
                <h2>Script executed successfully!</h2>
                <pre>{{ result }}</pre>
            </body>
            </html>
            """, result=result
        )
    except Exception as e:
        return render_template_string(
            """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Script Execution</title>
            </head>
            <body>
                <h2>An error occurred:</h2>
                <pre>{{ error }}</pre>
            </body>
            </html>
            """, error=str(e)
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
