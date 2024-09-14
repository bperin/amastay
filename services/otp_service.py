import requests
import supabase

class OtpService:
    
    @staticmethod
    def send_otp(phone_number):
        try:
            response = requests.post(
                f"{supabase['url']}/auth/v1/otp",
                json={"phone": phone_number},
                headers={"apikey": supabase['key'], "Content-Type": "application/json"}
            )
            response.raise_for_status()
            return {"message": "OTP sent"}
        except requests.RequestException as e:
            return {"error": str(e)}

    @staticmethod
    def verify_otp(phone_number, otp):
        try:
            response = requests.post(
                f"{supabase['url']}/auth/v1/verify",
                json={"phone": phone_number, "otp": otp},
                headers={"apikey": supabase['key'], "Content-Type": "application/json"}
            )
            response.raise_for_status()
            return {"message": "OTP verified"}
        except requests.RequestException as e:
            return {"error": str(e)}
