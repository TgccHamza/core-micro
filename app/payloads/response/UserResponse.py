from typing import Optional

from pydantic import BaseModel


class UserResponse(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    user_email: Optional[str] = None
    username: Optional[str] = None
    user_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None

    def get(self, property_name):
        if property_name == 'user_id':
            return self.user_id
        elif property_name == 'user_email':
            return self.user_email
        elif property_name == 'username':
            return self.username
        elif property_name == 'user_name':
            return self.user_name
        elif property_name == 'first_name':
            return self.first_name
        elif property_name == 'last_name':
            return self.last_name
        elif property_name == 'full_name':
            return self.full_name
        elif property_name == 'email':
            return self.email
        else:
            return None