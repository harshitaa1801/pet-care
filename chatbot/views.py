import json
from django.shortcuts import render

# Create your views here.
import openai
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view
import os
import json

# OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

@api_view(['POST'])
def generate_response(request):
    data = json.loads(request.body)
    user_input = data.get("message")

    if not user_input:
        return JsonResponse({"error": "Message is required"}, status=400)

    try:
        client = openai.Client(api_key='abcd')
        response = client.chat.completions.create(
            model="gpt-4o",  # Or your custom GPT model
            messages=[{"role": "user", "content": user_input}],
            max_tokens=500,
            temperature=0.7
        )
        response_content = response.choices[0].message.content.strip()
        print(response_content)

        # return JsonResponse({"response": response["choices"][0]["message"]["content"]})
        return JsonResponse({"response": response_content})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)




# asst_R9bdwgvWfd97tvW69YeW8nI8




ASSISTANT_ID = "asst_CefoSr6xBfbH4TwNmzYEmNfQ"  # Replace with your assistant ID

@api_view(['POST'])
def query_assistant(request):
    data = request.data
    user_query = data.get("query")

    if not user_query:
        return JsonResponse({"error": "Query is required"}, status=400)

    client = openai.Client(api_key=OPENAI_API_KEY)
    thread = client.beta.threads.create()

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_query
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )

    while run.status in ['queued', 'in_progress']:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    # follow_up_questions = messages.data[0].content

    extracted_responses = []
    for message in messages.data:
        for content_block in message.content:
            if hasattr(content_block, 'text'):
                # Try parsing text content as JSON if possible, otherwise treat it as plain text
                try:
                    parsed_content = json.loads(content_block.text.value)
                    extracted_responses.append(parsed_content)
                except json.JSONDecodeError:
                    extracted_responses.append(content_block.text.value)

    return JsonResponse({"follow_up_questions": extracted_responses, "thread_id": thread.id})









@api_view(['POST'])
def submit_answers(request):
    data = request.data
    answers = data.get("answers")

    if not answers:
        return JsonResponse({"error": "Answers are required"}, status=400)

    client = openai.Client(api_key=OPENAI_API_KEY)
    thread_id = data.get("thread_id")

    # Submit user answers to the assistant
    formatted_answers = "\n".join(f"{k}: {v}" for k, v in answers.items())

    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=formatted_answers
    )

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=ASSISTANT_ID
    )

    while run.status in ['queued', 'in_progress']:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

    messages = client.beta.threads.messages.list(thread_id=thread_id)
    # response_content = messages.data[0].content

    print(messages)

    extracted_responses = []
    for message in messages.data:
        for content_block in message.content:
            if hasattr(content_block, 'text'):
                try:
                    parsed_content = json.loads(content_block.text.value)
                    extracted_responses.append(parsed_content)
                except json.JSONDecodeError:
                    extracted_responses.append(content_block.text.value)

    # Extract only causes and recommendations
    filtered_response = []
    for item in extracted_responses:
        if isinstance(item, dict) and 'causes' in item and 'recommendations' in item:
            filtered_response.append({
                "causes": item.get("causes", []),
                "recommendations": item.get("recommendations", [])
            })

    return JsonResponse(filtered_response, safe=False)




