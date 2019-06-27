# Guidin' George
Team: Jane Le, Josiah Parappally, Sam Yu. 

# Inspiration
It's scary being lost especially without wifi or mobile data, Guidin' George sends you SMS directions to your target location.

A lot of our friends consistently were getting lost in unfamiliar places as they didn't have mobile data. Guidin' George allows users to text a phone number with their location and a search query, and Guidin' George directs them to their destination through text messages without the use of internet/mobile data.

# What it does
Guidin' George is a friendly text-messaging app that sends you directions based on where you are and your target location. If there are multiple nearby locations, Guidin' George lets you select which location you want to go to.

# How We built it
Google Cloud Platform: Google Directions API - Used the Google Directions API to receive step by step directions between Point A and Point B. Google Cloud Platform: Google Places API - Used the Google Places API to return results matching the users search query ordered in proximity to the user.

# Challenges We ran into
It was difficult to maintain a conversational flow for Guidin' George, considering the input could be any text. To combat this, we implemented a model to track which state of the conversation Guidin' George is in to help him decide his tasks.

# What's next for Guidin' George
We started a web-app for new users to register their phone numbers to Guidin' George but did not complete the back-end. In addition, we're thinking of adding security features to Guidin' George such as collecting the last location of the user and if they have not arrived within a certain time frame, Guidin' George sends a search party.

# Built With
python 3,
django,
twilio,
google-cloud,
google-directions api,
google-places api,
django-rest-framework.
