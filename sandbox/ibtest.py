from ib.clientportal_http import ClientPortalHttp
from ib.clientportal_websockets import ClientPortalWebsocketsBase

client_http = ClientPortalHttp()
client_ws = ClientPortalWebsocketsBase()

r = client_http.clientrequest_authentication_status()
r = client_ws.loop()

