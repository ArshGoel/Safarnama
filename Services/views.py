import os
import re
import json
import mimetypes
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, FileResponse, Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from google import genai
from google.genai import types

from .models import ChatMessage, TravelDocument


def get_gemini_client():
    api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.getenv('GEMINI_API_KEY', '')
    return genai.Client(api_key=api_key)


def get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def get_user_filter_kwargs(request):
    """
    Returns query filter kwargs matching either the authenticated user
    or the current anonymous session.
    """
    if request.user.is_authenticated:
        return {'user': request.user}
    else:
        return {'session_key': get_session_key(request), 'user__isnull': True}


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


def generate_gemini_content(prompt, history=None, model=None):
    """
    Generates text content using the official Google GenAI SDK.
    Supports chat history so the conversation has continuous memory.
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
            if history:
                chat = client.chats.create(model=m, history=history)
            else:
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


def generate_story(request):
    generated_text = "Please provide a prompt to generate content."

    if request.method == "POST":
        prompt = request.POST.get('prompt')
        if prompt:
            try:
                generated_text = generate_gemini_content(prompt)
            except Exception as e:
                generated_text = f"Error: {str(e)}"

    return render(request, 'generate_story.html', {'generated_text': generated_text})


def dashboard(request):
    return render(request, "dashboard.html")


def get_weather(request):
    weather_data = "Please provide a city to get the weather forecast."

    if request.method == "POST":
        city = request.POST.get('city')
        if city:
            try:
                url = f"https://wttr.in/{city}?format=%C+%t+%w"
                response = requests.get(url)
                response_text = response.text.strip()

                if response.status_code == 200 and response_text:
                    weather_data = f"Weather in {city}: {response_text}"
                else:
                    weather_data = "Error: Unable to fetch weather data."
            except Exception as e:
                weather_data = f"Error: {str(e)}"

    return render(request, 'weather_forecast.html', {'weather_data': weather_data})


def chatbot(request):
    """
    Chatbot with persistent memory stored in database (ChatMessage model).
    Remembers previous conversation context using Gemini multi-turn history.
    """
    filter_kwargs = get_user_filter_kwargs(request)

    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        if user_message:
            # 1. Fetch recent conversation history (last 10 messages) for context
            past_chats = ChatMessage.objects.filter(**filter_kwargs).order_by('created_at')[:10]
            gemini_history = []
            for item in past_chats:
                gemini_history.append(
                    types.Content(role='user', parts=[types.Part.from_text(text=item.message)])
                )
                gemini_history.append(
                    types.Content(role='model', parts=[types.Part.from_text(text=item.response)])
                )

            # 2. Formulate prompt instruction with HTML format
            formatted_prompt = (
                f"{user_message}\n\n"
                "(Please provide the answer formatted cleanly in HTML tags such as "
                "<h1>, <p>, <ul>, <li>, <strong>, etc., without markdown code blocks.)"
            )

            try:
                bot_response = generate_gemini_content(formatted_prompt, history=gemini_history)
                bot_response = clean_html_response(bot_response)
            except Exception as e:
                bot_response = f"<p>Error: {str(e)}</p>"

            # 3. Store conversation in database
            ChatMessage.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=get_session_key(request),
                message=user_message,
                response=bot_response
            )

            # Redirect to GET to prevent form re-submission on refresh
            return redirect('chatbot')

    # GET request: load complete chat history from DB
    chat_history = ChatMessage.objects.filter(**filter_kwargs).order_by('created_at')
    return render(request, 'chatbot.html', {'chat_history': chat_history})


@require_POST
def clear_chat(request):
    """Clears conversation history for the current user/session."""
    filter_kwargs = get_user_filter_kwargs(request)
    ChatMessage.objects.filter(**filter_kwargs).delete()
    return redirect('chatbot')


def itinery(request):
    if request.method == 'POST':
        location = request.POST.get('location')
        no_of_days = request.POST.get('noOfDays')
        budget = request.POST.get('budget')
        traveler = request.POST.get('traveler')

        prompt = (
            f"Generate a detailed travel itinerary for a trip to {location} for {no_of_days} days "
            f"for a {traveler} with a {budget} budget. Please provide the itinerary in HTML format, "
            "including appropriate HTML tags such as <h1>, <p>, <ul>, <li>, etc., for headings, paragraphs, and lists."
        )

        try:
            generated_text = generate_gemini_content(prompt)
            generated_text = clean_html_response(generated_text)
            return render(request, 'trip_result.html', {'trip_itinerary': generated_text})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return render(request, 'itinery.html')


def trip_result(request, trip_id):
    trip_itinerary = "This is a generated itinerary for your trip! Enjoy your stay!"
    return render(request, 'trip_result.html', {"trip_itinerary": trip_itinerary})


def documentation(request):
    """
    Renders document vault with documents stored in database (TravelDocument model)
    and backed by Cloudinary storage.
    """
    filter_kwargs = get_user_filter_kwargs(request)
    documents = TravelDocument.objects.filter(**filter_kwargs).order_by('-created_at')
    return render(request, "documentation.html", {'documents': documents})


@require_POST
def upload_document(request):
    """
    Uploads a travel document safely.
    Stores file bytes directly in the database (file_data) to guarantee compatibility with
    Vercel's read-only serverless environment and provide free inline PDF viewing.
    """
    try:
        file_obj = request.FILES.get('file')
        if not file_obj:
            return JsonResponse({'success': False, 'error': 'No file was provided'}, status=400)

        name = request.POST.get('name') or file_obj.name
        file_bytes = file_obj.read()
        file_size = len(file_bytes)

        mime_type = getattr(file_obj, 'content_type', None)
        if not mime_type or mime_type == 'application/octet-stream':
            mime_type, _ = mimetypes.guess_type(file_obj.name)
        if not mime_type:
            mime_type, _ = mimetypes.guess_type(name)
        mime_type = mime_type or 'application/pdf'

        doc = TravelDocument(
            user=request.user if request.user.is_authenticated else None,
            session_key=get_session_key(request),
            name=name,
            file_data=file_bytes,
            mime_type=mime_type,
            file_size=file_size
        )

        # Only attempt local disk file save if NOT in Vercel serverless read-only environment
        if not os.getenv('VERCEL'):
            try:
                doc.file = file_obj
            except Exception:
                pass

        doc.save()

        return JsonResponse({
            'success': True,
            'document': {
                'id': doc.id,
                'name': doc.name,
                'formatted_size': doc.formatted_size,
                'date': doc.created_at.strftime('%Y-%m-%d'),
                'extension': doc.extension
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': f"Upload failed: {str(e)}"}, status=500)


@require_POST
def rename_document(request, doc_id):
    """Renames an existing travel document in the database."""
    filter_kwargs = get_user_filter_kwargs(request)
    filter_kwargs['id'] = doc_id
    doc = get_object_or_404(TravelDocument, **filter_kwargs)

    try:
        data = json.loads(request.body.decode('utf-8'))
        new_name = data.get('name', '').strip()
    except Exception:
        new_name = request.POST.get('name', '').strip()

    if not new_name:
        return JsonResponse({'error': 'New name cannot be empty'}, status=400)

    doc.name = new_name
    doc.save()
    return JsonResponse({'success': True, 'id': doc.id, 'name': doc.name})


@require_POST
def delete_document(request, doc_id):
    """Deletes a travel document from database and storage."""
    filter_kwargs = get_user_filter_kwargs(request)
    filter_kwargs['id'] = doc_id
    doc = get_object_or_404(TravelDocument, **filter_kwargs)

    try:
        if doc.file:
            doc.file.delete(save=False)
    except Exception:
        pass

    doc.delete()
    return JsonResponse({'success': True, 'id': doc_id})


def view_document_file(request, doc_id):
    """
    Streams the uploaded document or PDF directly from database binary with inline Content-Disposition,
    allowing in-browser native PDF viewing on Vercel and locally with zero external tier restrictions.
    """
    filter_kwargs = get_user_filter_kwargs(request)
    filter_kwargs['id'] = doc_id
    doc = get_object_or_404(TravelDocument, **filter_kwargs)

    # 1. Primary: stream directly from database binary
    if doc.file_data:
        response = HttpResponse(bytes(doc.file_data), content_type=doc.mime_type or 'application/pdf')
        response['Content-Disposition'] = f'inline; filename="{doc.name}"'
        response['X-Frame-Options'] = 'SAMEORIGIN'
        return response

    # 2. Fallback: stream from local file if exists
    try:
        if doc.file and os.path.exists(doc.file.path):
            response = FileResponse(open(doc.file.path, 'rb'), content_type=doc.mime_type or 'application/pdf')
            response['Content-Disposition'] = f'inline; filename="{doc.name}"'
            response['X-Frame-Options'] = 'SAMEORIGIN'
            return response
    except Exception:
        pass

    if doc.file:
        return redirect(doc.file.url)
    raise Http404("Document content not found.")


def download_document_file(request, doc_id):
    """
    Direct download endpoint streaming file bytes as attachment.
    """
    filter_kwargs = get_user_filter_kwargs(request)
    filter_kwargs['id'] = doc_id
    doc = get_object_or_404(TravelDocument, **filter_kwargs)

    if doc.file_data:
        response = HttpResponse(bytes(doc.file_data), content_type=doc.mime_type or 'application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{doc.name}"'
        return response

    try:
        if doc.file and os.path.exists(doc.file.path):
            response = FileResponse(open(doc.file.path, 'rb'), content_type=doc.mime_type or 'application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{doc.name}"'
            return response
    except Exception:
        pass

    if doc.file:
        return redirect(doc.file.url)
    raise Http404("Document content not found.")


DESTINATION_TEMPLATES = {
    'gujarat': 'expediia/gujrat-details.html',
    'gujrat': 'expediia/gujrat-details.html',
    'goa': 'expediia/goa-details.html',
    'chardham': 'expediia/chardham-details.html',
    'himachal': 'expediia/himachal-details.html',
    'manali': 'expediia/manali-details.html',
    'srinagar': 'expediia/srinagar-details.html',
}


def destination_detail(request, slug):
    """Renders the detailed day-by-day travel itinerary for a destination."""
    template_name = DESTINATION_TEMPLATES.get(slug.lower())
    if not template_name:
        raise Http404(f"Destination '{slug}' not found.")
    return render(request, template_name, {'slug': slug})


def travel_planner(request):
    """Renders the interactive travel planner."""
    return render(request, 'expediia/plan.html')


def weather(request):
    return render(request, "weather.html")

