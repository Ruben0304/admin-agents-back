from models.auth import LoginRequest, LoginResponse

class AuthService:
    @staticmethod
    def authenticate_user(credentials: LoginRequest) -> LoginResponse:
        if credentials.username == "admin" and credentials.password == "password123":
            return LoginResponse(
                token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.hardcoded.token",
                message="Login successful"
            )
        else:
            return LoginResponse(
                token="",
                message="Invalid credentials"
            )