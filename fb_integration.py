from imgapi.imgapi import ImgAPI
from flask import Flask, request, jsonify, redirect
import requests

app = Flask(__name__)

api = ImgAPI()
api.setup(config_file="config.json")

class FB:
    def retrieve_data(self):
        api.api_entry = "https://headingtomars.com/api"
        data = api.api_call("/news/query?interest_score__gte=6&creation_date__gte=1 hour&ai_summary__ne=NULL&order_by=-creation_date&skip=0&limit=5&")
        return data

    def retrieve_article(self):
        api.api_entry = "https://headingtomars.com/api"
        data = api.api_call("/news/query?interest_score__gte=6&creation_date__gte=1 hour&ai_summary__ne=NULL&order_by=-creation_date&skip=0&limit=5&")
        articles = []
        for item in data["news"]:
            articles.append(item["articles"])
        return articles

    def create_facebook_notification(self, article, recipient_id, access_token):
    """
        Creates a Facebook notification for a given article string.

        Args:
            article (str): The article content or title to include in the notification.
            recipient_id (str): The Facebook User ID to send the notification to.
            access_token (str): Your Facebook app access token.

        Returns:
            dict: Response from the Facebook API.
        """
        # Truncate the article for notification (limit to 50 characters)
        notification_text = article[:50] + "..." if len(article) > 50 else article

        # Facebook API endpoint for notifications
        url = f"https://graph.facebook.com/{recipient_id}/notifications"

        # Payload with the notification details
        payload = {
            "template": notification_text,
            "href": "https://example.com/article",  # Replace with the link to your article
            "access_token": access_token
        }

        # Send the request to Facebook
        response = requests.post(url, data=payload)

        if response.status_code == 200:
            print("Notification sent successfully!")
        else:
            print(f"Failed to send notification: {response.status_code}, {response.text}")

        return response.json()
