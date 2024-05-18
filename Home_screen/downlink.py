import requests

api_key = None

with open('api_key_josetestserver.txt', 'r') as file:
    api_key = file.readline()
    print("API Key:", api_key)


application_id = 'josetestserver'
webhook_id = 'josetestwebhook'
device_id = 'eui-70b3d57ed0065033'
request = requests.post(
    url=f'https://eu1.cloud.thethings.network/api/v3/as/applications/{application_id}/webhooks/{webhook_id}/devices/{device_id}/down/push',
    data= {
        "downlinks":[{
            "decoded_payload": {
                "bytes": [1, 2, 3]
            }
        }]
    },
    headers={
    'Authorization': f"Bearer {api_key}" ,
})

print(request)

# import ttn