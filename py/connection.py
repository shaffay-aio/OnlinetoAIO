import os
from pyngrok import ngrok, conf

# Define a file to store the tunnel URL
TUNNEL_URL_FILE = "./resource/ngrok_tunnel_url.txt"

def get_existing_tunnel_url():
    """
    Check if an ngrok URL already exists in the file.
    """
    if os.path.exists(TUNNEL_URL_FILE):
        with open(TUNNEL_URL_FILE, "r") as file:
            url = file.read().strip()
            if url:
                return url
    return None

def save_tunnel_url(url):
    """
    Save the ngrok URL to the file.
    """
    with open(TUNNEL_URL_FILE, "w") as file:
        file.write(url)

def create_or_reuse_tunnel():
    """
    Reuse an existing tunnel URL if it's active; otherwise, create a new one.
    """
    existing_url = get_existing_tunnel_url()
    if existing_url:
        # Check if the existing tunnel is still active
        active_tunnels = ngrok.get_tunnels()
        for tunnel in active_tunnels:
            if tunnel.public_url == existing_url:
                print("Reusing existing active tunnel URL:", existing_url)
                return existing_url
        print("Existing tunnel URL is inactive. Creating a new tunnel...")

    # Create a new tunnel and save the URL
    ngrok.set_auth_token("YOUR_NGROK_AUTH_TOKEN")  # Replace with your actual ngrok auth token
    tunnel = ngrok.connect(8501, bind_tls=True)
    tunnel_url = tunnel.public_url
    save_tunnel_url(tunnel_url)
    print("New tunnel URL created:", tunnel_url)
    return tunnel_url

# Main Execution
if __name__ == "__main__":
    tunnel_url = create_or_reuse_tunnel()
    print(' * Tunnel URL:', tunnel_url)

    try:
        # Keep the script running to maintain the tunnel
        ngrok_process = ngrok.get_ngrok_process()
        ngrok_process.proc.wait()
    except KeyboardInterrupt:
        print("Shutting down ngrok tunnel...")
        ngrok.disconnect(tunnel_url)
        ngrok.kill()
        print("Tunnel closed.")
