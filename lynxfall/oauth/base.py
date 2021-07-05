from typing import List, Optional
from itsdangerous import URLSafeSerializer
from aioredis import Connection

class BaseOauth():
    IDENTIFIER = "base"
    AUTHORIZE_URL = "https://example.com/api/oauth2/authorize"
    TOKEN_URL = "https://example.com/api/oauth2/token"
    API_URL = "https://example.com/api"
    
    def __init__(self, auth_jwt_key: str, oc: OauthConfig, redis: Connection):
        self.auth_s = URLSafeSerializer(auth_jwt_key, "auth")
        self.client_id = oc.client_id
        self.client_secret = oc.client_secret
        self.redirect_uri = oc.redirect_uri
        self.redis = redis
        
    def get_scopes(self, scopes_lst: List[str]) -> str:
        return "%20".join(scopes_lst)

    def create_state(self, id):
        return self.auth_s.dumps(str(id))

    def get_oauth(self, scopes: List[str], state_data: dict, redirect_uri: Optional[str] = None):
        """Creates a secure oauth. State data is any data you want to have about a user after auth like user settings/login stuff etc."""
        
        state_id = uuid.uuid4()
        state = self.create_state(state_id)
        redirect_uri = self.redirect_uri if not redirect_uri else redirect_uri
        scopes = self.get_scopes(scopes)
        await self.redis.set(f"oauth.{self.IDENTIFIER}-{state_id}", orjson.dumps(state_data))
        
        return f"{self.login_url}?client_id={self.client_id}&redirect_uri={redirect_uri}&state={state}&response_type=code&scope={scopes}"
