import vonage # New import
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import EmergencyContact

class TriggerSOS(APIView):
    def post(self, request):
        user = request.user
        location_url = request.data.get('location_url', 'No location provided')
        contacts = EmergencyContact.objects.filter(user=user)
        
        if not contacts.exists():
            return Response({"error": "No contacts found"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Initialize Vonage Client
        client = vonage.Client(key=settings.VONAGE_API_KEY, secret=settings.VONAGE_API_SECRET)
        sms = vonage.Sms(client)

        success_count = 0
        for contact in contacts:
            # 2. Send the message
            response = sms.send_message({
                "from": settings.VONAGE_FROM_NUMBER,
                "to": contact.phone_number,
                "text": f"🚨 EMERGENCY! {user.username} is in danger. Location: {location_url}",
            })

            # 3. Nexmo response check
            if response["messages"][0]["status"] == "0":
                success_count += 1
            else:
                print(f"Error: {response['messages'][0]['error-text']}")

        return Response({"status": f"Alerts sent to {success_count} contacts!"})
