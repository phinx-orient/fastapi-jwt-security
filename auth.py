import os
import jwt # used for encoding and decoding jwt tokens
from fastapi import HTTPException # used to handle error handling
from passlib.context import CryptContext # used for hashing the password 
import datetime


class Auth():
    hasher= CryptContext(schemes=['bcrypt'])
    secret = os.getenv("JWT_SECRET")
    algorithm = os.getenv("JWT_ALGORITHM")

    def encode_password(self, password):
        return self.hasher.hash(password)

    def verify_password(self, password, encoded_password):
        return self.hasher.verify(password, encoded_password)
    
    def encode_token(self, username):
        payload = {
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(days=0, minutes=30),
            "iat": datetime.datetime.now(datetime.timezone.utc),
            "scope": "access_token",
            "sub": username,
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)
    
    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            if (payload['scope'] == 'access_token'):
                return payload['sub']   
            raise HTTPException(status_code=401, detail='Scope for the token is invalid')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')
	    
    def encode_refresh_token(self, username):
        payload = {
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(days=0, hours=10),
            "iat": datetime.datetime.now(datetime.timezone.utc),
            "scope": "refresh_token",
            "sub": username,
        }
        return jwt.encode(
            payload, 
            self.secret,
            algorithm='HS256'
        )
    def refresh_token(self, refresh_token):
        try:
            payload = jwt.decode(
                refresh_token, self.secret, algorithms=[self.algorithm]
            )
            if (payload['scope'] == 'refresh_token'):
                username = payload['sub']
                new_token = self.encode_token(username)
                return new_token
            raise HTTPException(status_code=401, detail='Invalid scope for token')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Refresh token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid refresh token')
