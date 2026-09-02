# views.py
import os
import re
import json
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from google import genai


def get_gemini_client():
    api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.getenv('GEMINI_API_KEY', '')
    return genai.Client(api_key=api_key)


def generate_gemini_content(prompt, model=None):
    """
    Generates text content using the official Google GenAI SDK.
    Uses chat session with fallback support to ensure high availability.
    """
    client = get_gemini_client()
    primary_model = model or getattr(settings, 'GEMINI_MODEL', 'gemini-3.5-flash-lite')

    models_to_try = [primary_model]
    if primary_model != 'gemini-3.5-flash':
        models_to_try.append('gemini-3.5-flash')
    if 'gemini-3.1-flash-lite' not in models_to_try:
        models_to_try.append('gemini-3.1-flash-lite')

    last_error = None
    for m in models_to_try:
        try:
            chat = client.chats.create(model=m)
            response = chat.send_message(prompt)
            if response and response.text:
                return response.text
        except Exception as err:
            last_error = err
            continue

    if last_error:
        raise last_error
    return ""


def clean_html_response(text):
    """
    Strips markdown code fences (```html ... ``` or ``` ... ```) from model outputs
    so that raw HTML is rendered cleanly in templates.
    """
    if not text:
        return ""
    cleaned = text.strip()
    cleaned = re.sub(r'^```(?:html)?\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*```$', '', cleaned)
    return cleaned.strip()


def generate_story(request):
    # Default response
    generated_text = "Please provide a prompt to generate content."

    if request.method == "POST":
        # Get the prompt from the user input
        prompt = request.POST.get('prompt')

        if prompt:
            try:
                generated_text = generate_gemini_content(prompt)
            except Exception as e:
                generated_text = f"Error: {str(e)}"

    # Render the result in the template
    return render(request, 'generate_story.html', {'generated_text': generated_text})


def dashboard(request):
    return render(request, "dashboard.html")


def get_weather(request):
    # Default response
    weather_data = "Please provide a city to get the weather forecast."

    if request.method == "POST":
        # Get the city name from the user input
        city = request.POST.get('city')

        if city:
            try:
                # Make a GET request to wttr.in with the city name
                url = f"https://wttr.in/{city}?format=%C+%t+%w"
                response = requests.get(url)
                response_text = response.text.strip()

                if response.status_code == 200 and response_text:
                    # Format the response text into a readable format
                    weather_data = f"Weather in {city}: {response_text}"
                else:
                    weather_data = "Error: Unable to fetch weather data."

            except Exception as e:
                weather_data = f"Error: {str(e)}"

    # Render the weather data in the template
    return render(request, 'weather_forecast.html', {'weather_data': weather_data})


def chatbot(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        if user_message:
            try:
                prompt = (
                    f"{user_message}\n\n"
                    "Please provide the answer in HTML format, including appropriate HTML tags "
                    "such as <h1>, <p>, <ul>, <li>, etc., for headings, paragraphs, and lists."
                )
                bot_response = generate_gemini_content(prompt)
                bot_response = clean_html_response(bot_response)
            except Exception as e:
                bot_response = f"<p>Error: {str(e)}</p>"
            return render(request, 'chatbot.html', {'user_message': user_message, 'bot_response': bot_response})

    return render(request, 'chatbot.html')


def itinery(request):
    if request.method == 'POST':
        # Handle form submission
        location = request.POST.get('location')
        no_of_days = request.POST.get('noOfDays')
        budget = request.POST.get('budget')
        traveler = request.POST.get('traveler')

        # Create a prompt for generating the trip itinerary
        prompt = (
            f"Generate a detailed travel itinerary for a trip to {location} for {no_of_days} days "
            f"for a {traveler} with a {budget} budget. Please provide the itinerary in HTML format, "
            "including appropriate HTML tags such as <h1>, <p>, <ul>, <li>, etc., for headings, paragraphs, and lists."
        )

        try:
            generated_text = generate_gemini_content(prompt)
            generated_text = clean_html_response(generated_text)
            # Pass the generated text to the template
            return render(request, 'trip_result.html', {'trip_itinerary': generated_text})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return render(request, 'itinery.html')


# Create a new view to render the generated content (itinerary)
def trip_result(request, trip_id):
    # Fetch the itinerary from the database or generate based on trip_id
    # For now, we assume the content is stored in a variable after generation.

    # Placeholder itinerary data
    trip_itinerary = "This is a generated itinerary for your trip! Enjoy your stay!"

    return render(request, 'trip_result.html', {"trip_itinerary": trip_itinerary})


def documentation(request):
    return render(request, "documentation.html")


def weather(request):
    return render(request, "weather.html")
