import json
from pathlib import Path
from src.ui_app import FlightHubSyncClient

cfg=json.loads(Path('config/flighthub2.json').read_text(encoding='utf-8'))
client=FlightHubSyncClient(cfg)
payload={
  'name':'auto-test-1',
  'wayline_uuid':'a0d29984-fe54-49ed-b41f-f6c2c85eee4c',
  'sn':'1581F7K3C251900C55PL',
  'rth_altitude':60,
  'rth_mode':'optimal',
  'wayline_precision_type':'gps',
  'out_of_control_action_in_flight':'return_home',
  'resumable_status':'manual',
  'task_type':'immediate',
  'time_zone':'Europe/Berlin'
}
try:
    resp=client._request_json('POST','/openapi/v0.1/flight-task',payload=payload,extra_headers=client._auth_headers())
    print('RESP',resp)
except Exception as ex:
    print('ERR',ex)
