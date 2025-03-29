import json

from rest_framework import viewsets, status
from rest_framework.response import Response

from django.shortcuts import get_object_or_404, render
from .models import Query, Question, Answer, Remedy
from .serializers import QuerySerializer, AnswerSerializer, QueryResponseSerializer, SmartQuerySerializer
from .utils import GeminiService
import uuid


# homepage
def home(request):
    return render(request, 'chatbot/home.html')



# to integrate with frontend
class QueryView(viewsets.ViewSet):
    """
    API endpoint to handle user queries about pet care
    """
    def create(self, request):
        # Extract query text from request
        query_text = request.data.get('query')
        if not query_text:
            return Response(
                {'error': 'Query text is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create session ID
        session_id = request.data.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Check if query is pet-related using Gemini
        ai_service = GeminiService()
        is_pet_related = ai_service.is_pet_related(query_text)
        
        # Create query record
        query = Query.objects.create(
            text=query_text,
            is_pet_related=is_pet_related,
            session_id=session_id
        )
        
        # If not pet-related, return appropriate message
        if not is_pet_related:
            return Response({
                'query_id': query.id,
                'next_question': None,
                'remedy': None,
                'message': 'This is not my expertise, please ask a medical query for pets'
            })
        
        # Generate follow-up questions using Gemini
        questions = ai_service.generate_followup_questions(query_text)
        
        # Store questions in database
        for i, question_text in enumerate(questions):
            Question.objects.create(
                query=query,
                text=question_text,
                order=i+1
            )
        
        # Get the first question to return
        first_question = query.questions.first()
        
        # Return response with query ID and first question
        return Response({
            'query_id': query.id,
            'next_question': {
                'id': first_question.id,
                'text': first_question.text,
                'order': first_question.order
            } if first_question else None,
            'remedy': None,
            'message': None
        })

class AnswerView(viewsets.ViewSet):
    """
    API endpoint to handle user answers to follow-up questions
    """
    def create(self, request):
        # Extract data from request
        question_id = request.data.get('question_id')
        answer_text = request.data.get('answer')
        
        if not question_id or not answer_text:
            return Response(
                {'error': 'Question ID and answer text are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the question
        question = get_object_or_404(Question, id=question_id)
        query = question.query
        
        # Store the answer
        Answer.objects.create(
            question=question,
            text=answer_text
        )
        
        # Find the next unanswered question
        answered_questions = Answer.objects.filter(question__query=query).values_list('question_id', flat=True)
        next_question = Question.objects.filter(query=query).exclude(id__in=answered_questions).order_by('order').first()
        
        # If no more questions, generate remedy
        if not next_question:
            # Collect all Q&A pairs
            qa_pairs = []
            for q in Question.objects.filter(query=query).order_by('order'):
                try:
                    answer = q.answer
                    qa_pairs.append({
                        'question': q.text,
                        'answer': answer.text
                    })
                except Answer.DoesNotExist:
                    # Skip questions without answers
                    pass
            
            # Generate remedy using Gemini
            ai_service = GeminiService()
            remedy_text = ai_service.generate_remedy(query.text, qa_pairs)
            
            # Store remedy
            remedy = Remedy.objects.create(
                query=query,
                text=remedy_text
            )
            
            # Return response with remedy
            return Response({
                'query_id': query.id,
                'next_question': None,
                'remedy': remedy_text,
                'message': None
            })
        
        # Return response with next question
        return Response({
            'query_id': query.id,
            'next_question': {
                'id': next_question.id,
                'text': next_question.text,
                'order': next_question.order
            },
            'remedy': None,
            'message': None
        })    



# for directly interacting with drf interface
class SmartQueryViewSet(viewsets.ViewSet):
    serializer_class = SmartQuerySerializer

    def get_serializer(self, *args, **kwargs):
        return SmartQuerySerializer(*args, **kwargs)

    def list(self, request):
        return Response({
            "message": "Welcome to the Smart Query API. Use POST to submit a pet health query or answer."
        })


    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        query_text = data.get("query")
        answer_text = data.get("answer")

        # 1. Get or create session ID from the user's browser session
        session_id = request.session.get("chat_session_id")
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session["chat_session_id"] = session_id

        # 2. If user is starting a new query
        if query_text:
            ai_service = GeminiService()
            is_pet_related = ai_service.is_pet_related(query_text)

            query = Query.objects.create(
                text=query_text,
                is_pet_related=is_pet_related,
                session_id=session_id
            )

            if not is_pet_related:
                return Response({
                    'message': 'This is not my expertise, please ask a medical query for pets'
                })

            questions = ai_service.generate_followup_questions(query_text)
            for i, q in enumerate(questions):
                Question.objects.create(query=query, text=q, order=i+1)

            first_question = query.questions.first()
            return Response({
                'message': "Thanks! Here's your first follow-up question, please answer in the text box named 'Answer' :",
                'question': first_question.text
            })

        # 3. If answering a question (no query_text, only answer)
        elif answer_text:
            try:
                query = Query.objects.filter(session_id=session_id).latest('created_at')
            except Query.DoesNotExist:
                return Response({'error': 'No active session found'}, status=400)

            # Get the next unanswered question
            answered_ids = Answer.objects.filter(question__query=query).values_list('question_id', flat=True)
            next_q = Question.objects.filter(query=query).exclude(id__in=answered_ids).order_by('order').first()

            if not next_q:
                return Response({'message': 'All questions answered or invalid session'}, status=400)

            Answer.objects.create(question=next_q, text=answer_text)

            # Check if more questions remain
            next_unanswered = Question.objects.filter(query=query).exclude(id__in=answered_ids).exclude(id=next_q.id).order_by('order').first()

            if not next_unanswered:
                # All answered, generate remedy
                qa_pairs = []
                for q in Question.objects.filter(query=query).order_by('order'):
                    try:
                        qa_pairs.append({'question': q.text, 'answer': q.answer.text})
                    except Answer.DoesNotExist:
                        pass

                ai_service = GeminiService()
                raw_remedy = ai_service.generate_remedy(query.text, qa_pairs)
                if isinstance(raw_remedy, str):
                    try:
                        remedy_data = json.loads(raw_remedy)
                    except json.JSONDecodeError:
                        remedy_data = {"note": "Unable to parse remedy", "raw": raw_remedy}
                else:
                    remedy_data = raw_remedy


                Remedy.objects.create(query=query, text=remedy_data)

                return Response({
                    'message': "Thanks! Here's what I recommend:",
                    'remedy': remedy_data
                })

            return Response({
                'message': "Got it! Here's the next question, please answer in the text box named 'Answer' :",
                'question': next_unanswered.text
            })

        return Response({'error': 'Please enter either a query or an answer'}, status=400)
