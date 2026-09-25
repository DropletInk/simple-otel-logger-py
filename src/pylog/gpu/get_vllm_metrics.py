import requests

def capture_metrics_to_logs(port: int):
    address = f"http://vllm-vlm:{port}/metrics"
    try:
        # Query the vLLM metrics endpoint
        response = requests.get(address)
        if response.status_code == 200:
            print(f"Vllm............Response: {response.text}")
    except Exception as e:
        print(f"Vllm............Failed to fetch metrics: {e}")
