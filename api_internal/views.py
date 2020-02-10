from django.http import HttpResponse
from django.shortcuts import render, redirect
import json

from lib.utils import Decorators


@Decorators.firebase_login_required
def get_user_quizzes(request):
    from api_internal.services.quiz_query_service import QuizQueryService
    return QuizQueryService(request).get_view()
