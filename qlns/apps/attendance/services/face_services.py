import json

import requests
from django.conf import settings

CREDENTIAL_HEADERS = {
    "Ocp-Apim-Subscription-Key": settings.COGNITIVE_API_KEY,
    "Content-Type": "application/json"
}

URL = settings.COGNITIVE_END_POINT


def detect_faces(image):
    """
    :param image: read image
    :return: Return azure person_id if action succeed, otherwise return None
    """
    url = f'{URL}/detect'
    headers = CREDENTIAL_HEADERS
    headers["Content-Type"] = 'application/octet-stream'

    res = requests.post(url, headers=headers, data=image)
    if res.status_code in [200]:
        return json.loads(res.text)
    else:
        return []


def create_person(name):
    """
    :param name: Person's name
    :return: Return azure person_id if action succeed, otherwise return None
    """
    headers = CREDENTIAL_HEADERS
    res = requests.post(
        f"{URL}/persongroups/ps1/persons",
        headers=headers,
        data=json.dumps({"name": name})
    )

    payload = json.loads(res.text)
    return payload.get('personId', None)


def add_recognition_image(person_id, image):
    """
    :param person_id: azure person_id
    :param image: read image
    :return: Return True if action succeed otherwise return False
    """
    faces = detect_faces(image)
    if len(faces) != 1:
        return False

    url = f'{URL}/persongroups/ps1/persons/{person_id}/persistedFaces'
    headers = CREDENTIAL_HEADERS
    headers["Content-Type"] = 'application/octet-stream'

    res = requests.post(url, headers=headers, data=image)
    return res.status_code in [200]


def verify(person_id, image):
    """
    :param person_id: azure person_id
    :param image: read image
    :return: True if face identification pass other wise return false
    """
    faces = detect_faces(image)
    if len(faces) != 1:
        return False

    face_id = faces[0]["faceId"]

    url = f'{URL}/verify'
    headers = CREDENTIAL_HEADERS
    headers["Content-Type"] = 'application/json'
    body = {
        "faceId": face_id,
        "personId": person_id,
        "personGroupId": "ps1"
    }
    res = requests.post(url, headers=headers, data=json.dumps(body))
    if res.status_code not in [200]:
        return False
    else:
        recognition_result = json.loads(res.text)
        print(recognition_result['confidence'])
        return recognition_result['isIdentical']
