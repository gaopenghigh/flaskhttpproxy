from flask import Flask, request, Response
import requests

# Using a non-standard static_url_path ensures the built-in static file handler
# won't intercept requests to /static before they reach our proxy handler
app = Flask(__name__, static_url_path=None, static_folder=None)

# Set the VM URL (Use private IP if in a VNet)
VM_BASE_URL = "http://10.0.0.4:5001"  # Replace with your VM's IP & port

@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy(path):
    """
    Proxy request to the target VM
    """
    target_url = f"{VM_BASE_URL}/{path}"
    
    # Forward headers and data
    headers = {key: value for key, value in request.headers if key.lower() != "host"}
    response = requests.request(
        method=request.method,
        url=target_url,
        headers=headers,
        data=request.get_data(),
        params=request.args,
        allow_redirects=False
    )

    # Return the response back to the client
    return Response(response.content, response.status_code, response.headers.items())

@app.route("/health")
def health_check():
    return "Proxy is running!", 200

if __name__ == "__main__":
    app.run()
