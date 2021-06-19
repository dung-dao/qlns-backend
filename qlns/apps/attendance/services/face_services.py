import json

import requests
from django.conf import settings

CREDENTIAL_HEADERS = {
    "Ocp-Apim-Subscription-Key": settings.COGNITIVE_API_KEY,
    "Content-Type": "application/json"
}

URL = settings.COGNITIVE_END_POINT


def create_person(name):
    headers = CREDENTIAL_HEADERS
    res = requests.post(
        f"{URL}/persongroups/ps1/persons",
        headers=headers,
        data=json.dumps({"name": name})
    )

    payload = json.loads(res.text)
    return payload.get('personId', None)

