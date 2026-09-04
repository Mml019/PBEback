# from datetime import time as datetime_time
from django.shortcuts import redirect, render, get_object_or_404, get_list_or_404
from django import forms
from django.urls import reverse_lazy
from django.utils import timezone

# imports to Normalize and clean data
# import openpyxl as xl
import pandas as pd
import io
import time as time
import datetime as datetime
from django.db.models.functions import Cast, Round
from django.db.models import Q, F, FloatField, Count
# from django.core.paginator import Paginator
from django.views.generic import DetailView, DeleteView, ListView, UpdateView
from .models import OptionQuestion as oqm
from .models import *
from api.serializers import *
from .forms import LoginForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils.mixins import PaginationBlockMixin
from .utils.utils import normalizeFile, format, Opciones, export_as_csv_or_excel

from django.db import transaction
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
from rest_framework.generics import *
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import View, APIView

# -------- USER FUNTIONS -----------
class LoginView(View):

    def get(self, request):
        form = LoginForm()
        return render(request, "login.html", {"form": form}, status=HTTP_200_OK)

    # login
    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():  # ← OBLIGATORIO
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(
                request,
                username=username,
                password=password,
            )

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect("quizzes")
                else:
                    message = f"This user is not active, please contact with an admin."
                    form.add_error(None, error=message)

                    return render(request, "login.html", {"form": form}, status=HTTP_403_FORBIDDEN)
            else:
                if MyUser.objects.filter(username=request.POST["username"]).exists():

                    message = f'Contraseña incorrecta para usuario {request.POST["username"]}, vuelva a intentarlo.'
                    # forms.ValidationError(message=message, code=HTTP_400_BAD_REQUEST)
                    form.add_error(field="password", error=message)

                else:
                    message = "Usuario inexistente, por favor regístrese por un admin."
                    # forms.ValidationError(message=message, code=HTTP_404_NOT_FOUND)
                    form.add_error(field="username", error=message)

                return render(request, "login.html", {"form": form}, status=HTTP_404_NOT_FOUND)
        return render(request, "login.html", {"form": form}, status=HTTP_200_OK)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.user 
        return context
    

class LogoutView(LoginRequiredMixin, View):
    # logout
    def post(self, request):
        logout(request)
        return redirect("login")

# ----------- QUIZ APP----------------
class QuizDetailView(View):
    """To get a quiz by id and its questions"""

    def get(self, request, idQ):
        # prefetch related allow to load in memory a query m2m
        # Do one query to get quiz and then another to get all questions from quiz
        try:
            quiz = Quiz.objects.prefetch_related("question").get(idQ=idQ)
            # count for each question total corrects
            questions = quiz.question.annotate(
                total_corrects=Count("respuesta", filter=Q(respuesta__is_correct=True))
            ).order_by("idP")

        except Quiz.DoesNotExist:
            return render(request, "quiz/quizzes_list.html")

        return render(request, "quiz/detailquiz.html", {"quiz": quiz, "questions": questions})

class QuizListView(LoginRequiredMixin, PaginationBlockMixin, ListView):
    parser_classes = [MultiPartParser]
    model = Quiz
    template_name = "quizzes.html"
    context_object_name = "quizzes"
    paginate_by = 3
    ordering = ["idQ"]

    " Import in excel or csv a quiz with its questions"
    def post(self, request):
        try:
            file = request.FILES.get("file")
        except:
            error={"error": "Not file in request.FILES"}
            return render(request, 'quizzes_list', {'error':error}, status=HTTP_400_BAD_REQUEST)
            return redirect('quizzes.html', {'error':error})
        
        if file is None or not file:
            error={"error": "Not file added"}
            return render(request,'quizzes.html', {'error':error})

        if not (file.name.endswith(".csv") or file.name.endswith(".xlsx")):
            error={"error": "Incorrect Format, only .csv or Excel files permited"},
            return render(request,'quizzes.html', {'error':error})

        # Dataframe to read and normalize
        if file.name.endswith("csv"):
            contenido = file.read()
            try:
                texto = contenido.decode("utf-8")
            except UnicodeDecodeError:
                texto = contenido.decode("latin-1")

            df = pd.read_csv(io.StringIO(texto), delimiter=";")
        elif file.name.endswith("xlsx"):
                df = pd.read_excel(file)
        else:
            error ={"error": "Incorrect Format, only CSV or XLSX files permited"},
            return render(request,'quizzes.html', {'error':error})
        try:
            df_normal = normalizeFile(df)
        except ValidationError as v:
            error = {f"Tiene valores vacíos. {v}"}
            return render(request, 'quizzes.html', {'error':error})
        
        with transaction.atomic():
            quiz = Quiz.objects.create(file=file.name)

            for i in range(len(df_normal)):

                try:
                    dimensionN, _ = Dimension.objects.get_or_create(
                        orden=df_normal.iloc[i]["ordenD"], dimension=df_normal.iloc[i]["dimension"]
                    )

                    areaIntN, _ = InterestArea.objects.get_or_create(
                        orden=df_normal.iloc[i]["ordenA"],
                        int_area=df_normal.iloc[i]["area"],
                        idD=dimensionN,
                    )

                    coreCont, _ = CoreContent.objects.get_or_create(
                        core_cont=df_normal.iloc[i]["contenido"],
                        idA=areaIntN,
                    )
                except ValidationError as ve:
                    error={"error": f"Error al insertar la fila {i+1} la dimensión, área de interés o contenido nuclear. Error: {ve}"}
                    return render(request,'quizzes.html', {'error':error})
                try:
                    row = df_normal.iloc[i]
                    # if Question.objects.filter(statement=df_normal.iloc[i]["enunciado"]).exists():
                    #     question = Question.objects.get(statement=df_normal.iloc[i]["enunciado"])
                    # else:    
                    #     question = Question.objects.create(
                    #         numero=i + 1,
                    #         statement=df_normal.iloc[i]["enunciado"],
                    #         time=time(0, 0, 30),
                    #         difficult_level=df_normal.iloc[i]["dificultad"],
                    #         version=0,
                    #         idD=dimensionN,
                    #         idA=areaIntN,
                    #         idC=coreCont,
                    #     )

                    question, _ = Question.objects.get_or_create(
                        statement=row["enunciado"],
                        defaults={
                            'numero':i + 1,
                            'statement':row["enunciado"],
                            'time':datetime.time(0, 0, 30),
                            'difficult_level':row["dificultad"],
                            'version':0,
                            'idD':dimensionN,
                            'idA':areaIntN,
                            'idC':coreCont
                        }
                    )
          
                    # Apperance model is through many to many field quiz question
                    quiz.question.add(question)

                except ValidationError as ve:
                    error = {"error": f"Error al insertar la pregunta de la fila {i+1}, Error: {ve}"}
                    return render(request,'quizzes.html', {'error':error})

                for op in row["opciones"]:
                    try:
                        valor_op_mapeado = Opciones[op]
                        # Create only one kind of option per quetsion in Option Table
                        option, _ = Option.objects.get_or_create(option=valor_op_mapeado)
                       
                        optionQ, _ = oqm.objects.get_or_create(
                            idP=question, 
                            idO=option, 
                            defaults={"motive": None})
                    
                        if op == row["solucion"]:
                            optionQ.motive = row["motivo"]
                            optionQ.save()

                        # optionQ_BD.append(optionQ)

                    except ValidationError as ve:
                        error = {"error": f" Corrija la opción {valor_op_mapeado} del campo de opciones de la fila {i+1}"}
                        return render(request, 'quizzes.html', {'error':error})
            return redirect("quizzes")
               

class QuizDeleteView(LoginRequiredMixin, DeleteView):
    model = Quiz
    success_url = reverse_lazy("quizzes_list")
    pk_url_kwarg = "idQ"

# ------ QUESTION VIEWS -------
# ModeliViewSet to APIView has already implemented to use create, retrieve, partial_update, update, destroy and list methods.
class BaseQuestionMixin:
    model = Question
    pk_url_kwarg = "idP"

# To see Question values
class QuestionDetailView(LoginRequiredMixin, BaseQuestionMixin, DetailView):
    template_name = "question.html"
    context_object_name = "question"
    fields = [
        "idP",
        "numero",
        "difficult_level",
        "version" "statement",
        "idD__dimension",
        "idD__orden",
        "idA__int_area",
        " idA__orden",
        "idC__core_cont",
        "time",
        "date",
    ]


# To modify a question
class QuestionUpdateView(LoginRequiredMixin, BaseQuestionMixin, UpdateView):
    template_name = "question.html"
    context_object_name = "question"
    fields = [
        "statement",
        "idD__dimension",
        "idD__orden",
        "idA__int_area",
        " idA__orden",
        "idC__core_cont",
    ]

# ------ SHOW ANSWERS ----------------
class ShowAnswers(LoginRequiredMixin, PaginationBlockMixin, ListView):
    model = Respuesta
    template_name = "answers.html"
    context_object_name = "answers"
    # paginate_by = 20
    # if you want personalize page range by default 5
    # block_page_size = 10 

    def get_queryset(self):
        answers = Respuesta.respuesta_manager.answers_queryset()
        #filter basic view
        idQ = self.request.GET.get("idQ") or None
        idRes = self.request.GET.get("idRes") or None
        # initDate = self.request.GET.get("initDate") or None
        # finalDate = self.request.GET.get("finalDate") or None
        # currentDate = timezone.now().date()
        if idQ:
            answers = answers.filter(question__question_in_each_quiz=idQ)

        if idRes:
            answers = answers.filter(respondant__pk=(idRes))
        
        # if initDate is not None and finalDate is not None:
        #     answers = answers.by_dates(initDate,finalDate)
        # elif initDate:
        #     answers = answers.by_dates(initDate,currentDate)
        # else: #finalDate Not None
        #     answers = answers.by_dates(currentDate,finalDate)

        # page = self.request.GET.get("page", 1) 
        # pages = self.request.GET.get("pages", 1000)
        # if page and pages:
        #     page_size = pages
        #     start = (page - 1) * page_size
        #     end = start + page_size

        # answers = answers[start:end]

        return answers
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        idQ= self.request.GET.get("idQ")
        idRes= self.request.GET.get("idRes")
        quizzes_ids= Quiz.objects.all().order_by('idQ').values_list('idQ', flat=True).distinct()
        respondants_ids=(Respondant.objects.filter(respuesta__isnull=False).distinct()
                                        .order_by('pk')
                                        .values_list('pk', flat=True))
        if idQ is not None:
            respondants_ids.filter(question__respondant_answer_to_question=idQ)

        if idRes is not None:
            quizzes_ids.filter(question__question_in_each_quiz=idQ)

        context["select_quiz_filter"] = self.request.GET.get("idQ") or ""
        context["select_user_filter"] = self.request.GET.get("idRes") or ""
        context['quizzes_ids'] = quizzes_ids
        context['respondants_ids'] = respondants_ids
        #context["select_pages"] = self.request.GET.get("pages") or "20"    
        return context

class ShowAnswersFromQuiz(LoginRequiredMixin, PaginationBlockMixin, ListView):
    model = Respuesta
    template_name = "answers.html"
    context_object_name = "answers"
    # paginate_by = 20
    pk_url_kwarg = "idQ"

    def get_queryset(self):
        idQ = self.kwargs["idQ"]
        answers = Respuesta.respuesta_manager.answers_queryset()
        answers = answers.by_quiz(idQ)
        # answers = answers.filter(question__question_in_each_quiz=idQ)
        return answers
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["idQ"] = self.kwargs["idQ"]
        context["select_pages"] = self.request.GET.get("pages") or "20"     
        return context

'''Search one respondant selected into a filter from the table of answers'''
class ShowAnswersFromRespondant(LoginRequiredMixin, PaginationBlockMixin,ListView):
    model = Respuesta
    template_name = "answers.html"
    context_object_name = "answers"
    # paginate_by = 20
    pk_url_kwarg = "idRes"
    
    def get_queryset(self):
        idRes = self.kwargs["idRes"]
        answers = Respuesta.respuesta_manager.answers_queryset()
        answers = answers.by_user(idRes)
        return answers
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["idRes"] = self.kwargs["idRes"]
        context["select_pages"] = self.request.GET.get("pages") or "20"     
        return context

def get_answered_by_respondant(request):
    answers = Respuesta.respuesta_manager.answers_queryset()
    # groupby informtaion by respondant or must be reverse
    answers_respondant = answers.by_respondant_summary()
    idRes = request.GET.get('idRes')
    if idRes:
        answers_respondant = answers_respondant.by_user(idRes)
    return answers_respondant       
  
'''Show all answers responded by each respondant, their success and quizzes answered'''
class ShowAnswersByRespondant(LoginRequiredMixin, PaginationBlockMixin,ListView):
    model = Respuesta
    template_name = "answers_users.html"
    context_object_name = "answers"
    # paginate_by = 20

    def get_queryset(self):
        return get_answered_by_respondant(self.request)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['respondants_ids'] = (Respondant.objects.filter(respuesta__isnull=False).distinct()
                                        .order_by('pk')
                                        .values_list('pk', flat=True))
        context['select_user_filter'] = self.request.GET.get('idRes') or ""
        context["select_pages"] = self.request.GET.get("pages") or "20"     
        return context
    
def get_answered_by_quiz(request):
    answers = Respuesta.respuesta_manager.answers_queryset()
    idQ = request.GET.get('idQ')
    if idQ:
        answers = answers.by_quiz(idQ)

    answers = answers.by_quiz_summary()
    return answers

class ShowAnswersByQuiz(LoginRequiredMixin, PaginationBlockMixin,ListView):
        model = Respuesta
        template_name = "answers_quizzes.html"
        context_object_name = "answers"
        # paginate_by = 20

        def get_queryset(self):
            return get_answered_by_quiz(self.request)
            # answers = Respuesta.respuesta_manager.answers_queryset()
            # answers = answers.by_quiz_summary()
            # idQ = self.request.GET.get('idQ')
            # if idQ:
            #     answers = answers.by_quiz(idQ)
            # return answers

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['quizzes_ids'] = Quiz.objects.values_list('idQ', flat=True)
            context['select_quiz_filter'] = self.request.GET.get('idQ') or ""
            context["select_pages"] = self.request.GET.get("pages") or "20"     
            return context
        
''' export all answers by quiz summary'''
def export_by_quiz_summary(request):
    answers = get_answered_by_quiz(request)
    # answers = Respuesta.respuesta_manager.answers_queryset()
    # answers = answers.by_quiz_summary()
    # idQ = request.GET.get('idQ')
    
    # if idQ:
    #     answers = answers.by_quiz(idQ)
    df = pd.DataFrame(list(answers))
    df = format(df) 
    response = export_as_csv_or_excel(request, df, 'answers_by_quiz')
    return response

def export_by_user_summary(request):
    answers = get_answered_by_respondant(request)
    # answers = Respuesta.respuesta_manager.answers_queryset()
    # answers = answers.by_respondant_summary()
    # idRes = request.GET.get('idRes')
    
    # if idRes:
    #     answers = answers.by_user(uuid.UUID(idRes))
    df = pd.DataFrame(list(answers))
    df = format(df) 
    response = export_as_csv_or_excel(request, df, 'answers_by_respondant')
    return response

# Export answers as csv or excel
def export_answers(request, **kwargs):
    answers = Respuesta.respuesta_manager.answers_queryset()
    idQ = request.GET.get('idQ') or kwargs.get("idQ") 
    idRes= request.GET.get('idRes') or kwargs.get("idRes") 
    
    if idQ:
        answers = answers.by_quiz(idQ=idQ)
    
    if idRes:
        answers = answers.by_user(idRes)

    answers = answers.export()
    df = pd.DataFrame(list(answers))
    df = format(df)

    response = export_as_csv_or_excel(request=request, df=df, resultName='answers')
    return response
# ----------------- USERS -----------------
class ShowUsers(LoginRequiredMixin, PaginationBlockMixin, ListView):
    model = Respondant
    # paginate_by = 20
    template_name = "users.html"
    context_object_name = "respondants"


    def get_queryset(self):
        respondants = Respondant.respondant_manager.respondant_queryset()

        # select from users view to filter by user
        idRes=self.request.GET.get("idRes") 
        # print(idRes)
        if idRes:
            respondants = respondants.filter(pk=idRes)
        
        # has answered param if filter is true or false if you want to see respondants ids 
        # that has answered a quiz o not
        has_answered = self.request.GET.get("has_answered") 
        if has_answered: #if not None filter query
            respondants = respondants.answered_respondants(has_answered)
        
        return respondants

    """Return all objects that can be m2m to put in table's header"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_res = self.get_queryset()
        
        context["activities"] =Activity.objects.all().distinct() #query_res.values('profesional__activities')
        context["sectors"] = Sector.objects.all().distinct() #query_res.values('profesional__sectors')
        context["enviroments"] = Enviroment.objects.all().distinct() #query_res.values('profesional__enviroments')#
        context["profesionalareas"] = ProfesionalArea.objects.all().distinct()#query_res.values('profarea')#
        context["respondants_ids"]= query_res.values_list('pk', flat=True)
        # Respondant.objects.filter(respuesta__isnull=False).distinct().values_list('respondant_id', flat=True)                      
        context["select_user"] = self.request.GET.get("idRes") or ""
        context["select_answered"] = self.request.GET.get("has_answered") or ""    
        context["select_pages"] = self.request.GET.get("pages") or "20"                         

        for r in context["respondants"]:
            if hasattr(r, "profesional"):
                
                r.dedications={}
                for a in context['activities']:
                    r.dedications[a.idAct] = 0

                for d in r.profesional.id_between_activity_profesional.all():
                       r.dedications[d.activity_id] = d.percentatge   

        return context

""" Export users in a csv o excel file with m2m data as stadistics
    export with 0s and 1s and values m2m as headers"""
def export_users(request):
    type = request.GET.get('type')
    if type == 'simple':
        response = export_users_simple(request)
    else:  
        response = export_users_complex(request)
    return response

# Export respondants to excel
def export_users_complex(request):
    # export simple values
    respondants = Respondant.respondant_manager.respondant_queryset()

    # first build columns their headers
    columns = []
    rfields = Respondant._meta.get_fields()
    pfields = Profesional._meta.get_fields()
    
    default_secs = ["Público", "Privado", "Centro concertado o mixto"]
    default_envs = [
        "Atención especializada",
        "Atención Primaria/ domiciliaria",
        "Centro sociosanitario",
        "Sistema escolar",
        "Universidad",
        "Consulta propia",
    ]
    activities = Activity.objects.all().distinct()
    sectors = Sector.objects.values_list("sector", flat=True).distinct()
    enviroments = Enviroment.objects.values_list("enviroment", flat=True).distinct()
    profesionalareas = ProfesionalArea.objects.values_list("profarea", flat=True).distinct()

    for rfield in rfields:
        # reverse relations out
        if rfield.auto_created and not rfield.concrete:
            continue

        if hasattr(rfield, "verbose_name") and rfield.name != "respondant":
            if rfield.verbose_name == "Satisfacciones":
                for sq in Satisfation.objects.values_list("questionS", flat=True).distinct():
                    pregunta = sq.split()[-1]
                    columns.append(pregunta)

            elif rfield.verbose_name == "Áreas Profesionales":
                for ap in profesionalareas:
                    columns.append(ap)
            else:
                columns.append(rfield.verbose_name)
                # add field name detalles to put description field
                if rfield.name == "academic_level":
                    columns.append("Detalle")

    for pfield in pfields:

        if hasattr(pfield, "verbose_name") and pfield.name != "profesional":
            match pfield.verbose_name:
                case "Actividades":
                    for act in activities:
                        columns.append(act.activity)
                case "Sectores":
                    for sec in sectors:
                        if sec == "Otros":
                            columns.append(sec + "_sec")
                        # not include others sectors
                        if sec in default_secs:
                            columns.append(sec)
                case "Entornos":
                    for env in enviroments:
                        if env == "Otros":
                            columns.append(env + "_env")
                        # not include others enviroments
                        if env in default_envs:
                            columns.append(env)
                case _:
                    columns.append(pfield.verbose_name)

    # Treat rest of data generate rows
    rows = []
    # Put values on each field and explore each m2m field to bind themselfs
    for r in respondants:
        data = {}
        # add respondants attributes
        for rfield in rfields:
            # reverse relations out
            if rfield.auto_created and not rfield.concrete:
                continue
            # boolean columns transform to Sí o No
            if isinstance(rfield, models.BooleanField):
                if getattr(r, rfield.name) == True:
                    data[rfield.verbose_name] = "Sí"
                else:
                    data[rfield.verbose_name] = "No"
            else:
                # rest of fields
                data[rfield.verbose_name] = getattr(r, rfield.name)

        data["Cuestionarios"] = r.quizzes #",".join(str(q) for q in r.quizzes)

        if r.academic_level:
            # Speciality
            data["Detalle"] = r.academic_level.description
        else:
             data["Detalle"]="Ninguno"

        # M2M
        # data['Áreas Profesionales'] = ",".join(a.profarea for a in r.profarea.all())
        for pa in profesionalareas:
            data[pa] = 0
        for rpa in r.profarea.all():
            data[rpa.profarea] = 1

        # Satisfations
        for s in r.satisfation.all():
            pregunta = s.questionS.split()[-1]
            data[pregunta] = s.value

        if hasattr(r, "profesional"):
            for pfield in pfields:
                # reverse relations and autocreated out
                if pfield.auto_created and not pfield.concrete:
                    continue

                # tranform true or false into sí o no
                if isinstance(pfield, models.BooleanField):
                    if getattr(r.profesional, pfield.name) == True:
                        data[pfield.verbose_name] = "Si"
                    else:
                        data[pfield.verbose_name] = "No"
                else:
                    # assign each profesional field a value
                    data[pfield.verbose_name] = getattr(r.profesional, pfield.name)

            # sectors
            for sec in sectors:
                data[sec] = 0
            for psec in r.profesional.sectors.all():
                data[psec.sector] = 1

            data["Otros_sec"] = ",".join(
                oth_sec.sector
                for oth_sec in r.profesional.sectors.all()
                if oth_sec.sector not in default_secs
            )

            # enviroments
            for env in enviroments:
                data[env] = 0
            for penv in r.profesional.enviroments.all():
                data[penv.enviroment] = 1

            data["Otros_env"] = ",".join(
                oth_env.enviroment
                for oth_env in r.profesional.enviroments.all()
                if oth_env.enviroment not in default_envs
            )

            for a in activities:
                data[a.activity] = 0

            for d in r.profesional.id_between_activity_profesional.all():
                data[d.activity.activity] = d.percentatge 

        # Add each respondant info
        rows.append(data)

    # Generate dataframe with the columns as header and rows as user infomation
    df = pd.DataFrame(rows, columns=columns)
    response = export_as_csv_or_excel(request=request, df=df, resultName='users_complex')

    return response

"""export users data as m2m binded with commas """
def export_users_simple(request):
    respondants = Respondant.respondant_manager.respondant_queryset()
    activities = Activity.objects.all().distinct()
    # first build columns their headers
    columns = []
    rfields = Respondant._meta.get_fields()
    pfields = Profesional._meta.get_fields()

    # Get all fields from a Respondant and Profesional
    for rfield in rfields:
        # reverse relations out
        if rfield.auto_created and not rfield.concrete:
            continue

        if hasattr(rfield, "verbose_name") and rfield.name != "respondant":
            # Split satisfation in each value
            if rfield.verbose_name == "Satisfacciones":
                for sq in Satisfation.objects.values_list("questionS", flat=True).distinct():
                    pregunta = sq.split()[-1]
                    columns.append(pregunta)
            else:
                columns.append(rfield.verbose_name)
                # add detalle to put more info related on academic level
                if rfield.name == "academic_level":
                    columns.append("Detalle")

    for pfield in pfields:
        if hasattr(pfield, "verbose_name") and pfield.name != "profesional":
            if pfield.verbose_name == "Actividades":
                for act in Activity.objects.values_list("activity", flat=True).distinct():
                    columns.append(act)
            else:
                columns.append(pfield.verbose_name)

    # Treat rest of data generate rows
    rows = []
    # Put values on each field and explore each m2m field to bind themselfs
    for r in respondants:
        data = {}

        # add respondants attributes
        for rfield in rfields:
            # reverse relations out
            if rfield.auto_created and not rfield.concrete:
                continue

            # boolean columns transform to Sí o No
            if isinstance(rfield, models.BooleanField):
                if getattr(r, rfield.name) == True:
                    data[rfield.verbose_name] = "Sí"
                else:
                    data[rfield.verbose_name] = "No"
            else:
                # rest of fields
                data[rfield.verbose_name] = getattr(r, rfield.name)

        # data["Cuestionarios"] = ",".join(str(q) for q in r.quizzes)
        data["Cuestionarios"] = r.quizzes

        # Speciality
        if r.academic_level:
            # Speciality
            data["Detalle"] = r.academic_level.description
        else:
            data["Detalle"]="Ninguno"

        # M2M
        data["Áreas Profesionales"] = ",".join(a.profarea for a in r.profarea.all())

        # Satisfations
        for s in r.satisfation.all():
            pregunta = s.questionS.split()[-1]
            data[pregunta] = s.value

        if hasattr(r, "profesional"):
            for pfield in pfields:
                # reverse relations and autocreated out
                if pfield.auto_created and not pfield.concrete:
                    continue
                # data[pfield.verbose_name] = getattr(r.profesional, pfield.name)
                # boolean columns transform to Sí o No
                if isinstance(pfield, models.BooleanField):
                    if getattr(r.profesional, pfield.name) == True:
                        data[pfield.verbose_name] = "Sí"
                    else:
                        data[pfield.verbose_name] = "No"
                else:
                    # rest of fields
                    data[pfield.verbose_name] = getattr(r.profesional, pfield.name)

            # sectors
            data["Sectores"] = ",".join(sec.sector for sec in r.profesional.sectors.all())

            # enviroments
            data["Entornos"] = ",".join(env.enviroment for env in r.profesional.enviroments.all())

            # activities
            for a in activities:
                data[a.activity] = 0

            for d in r.profesional.id_between_activity_profesional.all():
                data[d.activity.activity] = d.percentatge 

        # Add each respondant info
        rows.append(data)
    # Generate dataframe with the columns as header and rows as user infomation
    df = pd.DataFrame(rows, columns=columns)
    response = export_as_csv_or_excel(request=request, df=df, resultName='users_simple')
   
    return response

def export_prueba(request):
    query = Respondant.respondant_manager.all()

    rows = []
    
    for r in query:
        data={}    
        if(hasattr('respondant')):
            data.append(Profesional.objects.get(profesional=r).values())

    rows.append(data)

    # Generate dataframe with the columns as header and rows as user infomation
    df = pd.DataFrame(rows)
    response = export_as_csv_or_excel(request=request, df=df, resultName='users_complex')

    return response