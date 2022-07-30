from simplegmail import Gmail

def send_email_verify(email, token):
    gmail = Gmail('tokens/client_secret.json', 'tokens/gmail_token.json')
    params = {
        "to": email,
        "sender": "csdlmysql@gmail.com",
        "subject": "Verify sun account!",
        "msg_html": f"<h1>Please click link to verify account!</h1><br /><a href='http://210.245.54.243:5002/verify?token={token}'>Click here</a>",
        "msg_plain": "Don't reply to this message!",
        "signature": False  # use my account signature
    }
    message = gmail.send_message(**params)
    return True