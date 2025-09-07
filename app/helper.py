import base64
import uuid

def short_uuid():
  return base64.urlsafe_b64encode(uuid.uuid4().bytes).rstrip(b'=').decode('ascii')
