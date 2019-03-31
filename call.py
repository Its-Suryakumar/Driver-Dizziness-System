from twilio.rest import Client
from flask import Response
import time

def call(message, to='+919884026065'):
    xml = "<?xml version='1.0' encoding='UTF-8'?><Response>\n\t<Say voice='alice'>"+ message +"</Say>\n</Response>"  
    # Your Account Sid and Auth Token from twilio.com/console
    account_sid = 'ACcc6a4e9517065ad6810a3f9c827ae321'
    auth_token = 'baca84689e5e24cbcde69651e5d35042'
    client = Client(account_sid, auth_token)

    msg = client.messages.create(
        to=to,
        from_='+16602102659',
        body=message
    )
    print(msg)

    print(Response(xml, mimetype='text/xml'))
    call = client.calls.create(
                            url='https://twilio.com/docs/demo.xml',
                            to=to,
                            from_='+16602102659'
                        )
    print(call.sid)

if __name__ == '__main__':
    call('meh')