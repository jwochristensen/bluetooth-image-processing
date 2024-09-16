


#import flask_demo
import requests

#server = flask_demo.app.run()


#api endpoint
api_url = 'http://127.0.0.1:5000/send_ble/'

json_msg = {'msg':'testing message via requests'}

r = requests.post(url=api_url, json=json_msg)

return_msg = r.text

print(return_msg)

