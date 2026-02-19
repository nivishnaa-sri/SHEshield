import vonage
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import EmergencyContact, UnsafeArea
from .serializers import UnsafeAreaSerializer


class TriggerSOS(APIView):
    """
    Handles the SOS panic button. Sends SMS to all emergency contacts.
    """

    def post(self, request):
        location_url = request.data.get('location_url', 'No location provided')

        # 1️⃣ Get all contacts from the database
        contacts = EmergencyContact.objects.all()

        if not contacts.exists():
            return Response(
                {"error": "No emergency contacts found in database."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2️⃣ Initialize Vonage Client (API Key + Secret)
        client = vonage.Client(
            key=settings.VONAGE_API_KEY,
            secret=settings.VONAGE_API_SECRET
        )

        sms = vonage.Sms(client)

        success_count = 0

        # 3️⃣ Send SMS to each contact
        for contact in contacts:
            response = sms.send_message({
                "from": settings.VONAGE_FROM_NUMBER,
                "to": contact.phone_number,
                "text": f"🚨 EMERGENCY! A user needs help. Location: {location_url}",
            })

        print("Full Vonage Response:", response)  # 👈 ADD THIS

        status_code = response["messages"][0]["status"]

        if status_code == "0":
            success_count += 1
        else:
            error_text = response["messages"][0].get("error-text")
            print(f"Failed to send to {contact.phone_number}")
            print("Status Code:", status_code)
            print("Error Text:", error_text)


            return Response(
                {
                    "status": "Success",
                    "message": f"Alerts successfully sent to {success_count} contacts."
                },
                status=status.HTTP_200_OK
            )


class HeatmapData(APIView):
    """
    Returns a list of unsafe coordinates for the map display.
    """

    def get(self, request):
        areas = UnsafeArea.objects.all()
        serializer = UnsafeAreaSerializer(areas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
