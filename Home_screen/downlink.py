import requests
import json
import base64

# Configuration
TTN_REGION = "eu1"  # e.g., "eu1", "nam1", etc.
APPLICATION_ID = "josetestserver"
DEVICE_ID = "eui-70b3d57ed0065033"
TTN_API_KEY = "NNSXS.DFUXI5L24B3XO7XK4LFUOOADZ7QBTE2GACLP3KI.KCTMC32PZSAZ6ZVGORNXUC2UCREYFLEECIOLBNMS4D27UGV4ESXA"

def schedule_downlink(device_id, payload, f_port, app_id, access_key):
    url = f"https://eu1.cloud.thethings.network/api/v3/as/applications/{app_id}/devices/{device_id}/down/push"
    
    headers = {
        'Authorization': f'Bearer {access_key}',
        'Content-Type': 'application/json'
    }
    
    # Convert the payload to a base64 encoded string
    payload_bytes = payload.to_bytes((payload.bit_length() + 7) // 8, 'big') or b'\0'
    payload_b64 = base64.b64encode(payload_bytes).decode('utf-8')
    
    data = {
        "downlinks": [
            {
                "frm_payload": payload_b64,
                "f_port": f_port,
                "priority": "NORMAL"  # or "HIGH" if needed
            }
        ]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Example usage (to be called in another module)
if __name__ == "__main__":
    device_id = "your_device_id"
    payload = "3500"  # Assuming you want to send this as a string
    f_port = 1
    app_id = "your_application_id"
    access_key = "your_access_key"

    try:
        response = schedule_downlink(DEVICE_ID, 3500, f_port, APPLICATION_ID, TTN_API_KEY)
        print("Downlink scheduled successfully:", response)
    except Exception as e:
        print("Error scheduling downlink:", str(e))
