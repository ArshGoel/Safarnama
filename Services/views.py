# views.py
from django.shortcuts import render
import google.generativeai as genai
from django.conf import settings
import google.generativeai as genai
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

def generate_story(request):
    # Default response
    generated_text = "Please provide a prompt to generate content."

    if request.method == "POST":
        # Get the prompt from the user input
        prompt = request.POST.get('prompt')

        if prompt:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                # Initialize the Gemini model with the API key
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                # Generate content using the provided prompt
                response = model.generate_content(prompt)
                
                # Extract the generated text from the response
                generated_text = response.text
            except Exception as e:
                generated_text = f"Error: {str(e)}"

    # Render the result in the template
    return render(request, 'generate_story.html', {'generated_text': generated_text})


def dashboard(request):
    return render (request,"dashboard.html")

import requests
from django.shortcuts import render

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
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(user_message+"Please provide the answer in HTML format, including appropriate HTML tags such as <h1>, <p>, <ul>, <li>, etc., for headings, paragraphs, and lists.")
        generated_text = response.text
        ind=generated_text.index("html")
        bot_response = f"{generated_text}"  # Replace with actual bot logic
        # print(bot_response)
        return render(request, 'chatbot.html', {'user_message': user_message, 'bot_response': bot_response[ind+4:]})

    return render(request, 'chatbot.html')


def itinery(request):
    if request.method == 'POST':
        # Handle form submission
        location = request.POST.get('location')
        no_of_days = request.POST.get('noOfDays')
        budget = request.POST.get('budget')
        traveler = request.POST.get('traveler')

        # Create a prompt for generating the trip itinerary
        prompt = f"Generate a detailed travel itinerary for a trip to {location} for {no_of_days} days for a {traveler} with a {budget} budget. Please provide the itinerary in HTML format, including appropriate HTML tags such as <h1>, <p>, <ul>, <li>, etc., for headings, paragraphs, and lists."


        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            generated_text = response.text
            print(generated_text)
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
    return render (request,"documentation.html")

def weather(request):
    return render (request,"weather.html")

