from flask_app import create_app
from flask_app.config import Developer, Production
#import ssl

app = create_app(config_class=Developer)

if __name__ == '__main__':
    #context = ssl.SSLContext()
    #context.load_cert_chain('cert.pem', 'key.pem')
    #app.run(host='0.0.0.0', ssl_context='adhoc')
    app.run(host='0.0.0.0', port='5001')
