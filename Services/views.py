# views.py
from django.shortcuts import render
import google.generativeai as genai
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