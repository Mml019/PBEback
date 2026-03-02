import io
from datetime import time
from django.shortcuts import redirect, render, get_object_or_404, get_list_or_404
from django import forms

# imports to Normalize and clean data
import openpyxl as xl
import pandas as pd

from .models import OptionQuestion as oqm
from .models import *
from api.serializers import *
from .forms import LoginForm

from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
from rest_framework.generics import *
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import View, APIView
from rest_framework.viewsets import ModelViewSet

from .pagination import SmallPageNumberPagination

# -------- USER FUNTIONS -----------
class LoginView(View):

    def get(self, request):
        form = LoginForm()
        return render(request, "login.html", {'form': form}, status=HTTP_200_OK)
        return render(request, 'login.html',status=HTTP_200_OK)
        
    # login
    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():   # ← OBLIGATORIO
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
                    return render(request, "quizzes.html", {'user': user}, status=HTTP_200_OK)
                else: 
                    message = f'This user is not active, please contact with an admin.'
                    form.add_error(None, error=message)

                    return  render(request, "login.html", {'form': form}, status=HTTP_403_FORBIDDEN)
            else:
                if MyUser.objects.filter(username=request.POST["username"]).exists():

                    message = f'Contraseña incorrecta para usuario {request.POST["username"]}, vuelva a intentarlo.'
                    # forms.ValidationError(message=message, code=HTTP_400_BAD_REQUEST)
                    form.add_error(field='password', error=message)

                else:
                    message = 'Usuario inexistente, por favor regístrese por un admin.'
                    # forms.ValidationError(message=message, code=HTTP_404_NOT_FOUND)
                    form.add_error(field='username', error=message)
            
                return  render(request, "login.html", {'form': form}, status=HTTP_404_NOT_FOUND)
        return  render(request, "login.html", {'form': form}, status=HTTP_200_OK)
        
class LogoutView(APIView):
    # logout
    def post(self, request):
        logout(request)
        return redirect('login/')

class Registration(CreateAPIView):

    # register
    def post(self, request):
        # this serializer adds user with is_staff = True
        serializer = MyUserSerializerRegistration(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # user = MyUser.objects.create_user(username=request.POST['username'],password=request.POST['password'], is_staff=True)
            # print(user)
            # user = MyUser.objects.get(username=request.data['username'])
            if user is not None:
                # add all permissions except add or change answers
                group = create_group("interviewer")
                user.groups.add(group)

                # when user admin is created obtain the token access

            else:
                return Response({"error": "User not found " + user}, status=HTTP_404_NOT_FOUND)
            return Response({"success": serializer.data, "user": user}, status=HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=HTTP_400_BAD_REQUEST)

# ----------- QUIZ APP----------------
class QuizViews(APIView):
    parser_classes = [MultiPartParser]

    """ To get a quiz by id"""
    def get(self, request, id):
        # id = request.query_params.get('quiz')

        quiz = Quiz.objects.get(id)
        if quiz is None:
            return Response({"error": "Not found or not exits"}, status=HTTP_404_NOT_FOUND)
        quiz_serial = QuizSerializer(quiz)  # , many=True)

        return Response({"success": quiz_serial.data}, status=HTTP_200_OK)

    """ To show all quizzes paginated by 20 size to the admin"""
    def get(self, request):
        if Quiz.objects.exists() is False:
            return Response({"error": "There are any quizzes"}, status=HTTP_204_NO_CONTENT)

        quizzes = Quiz.objects.all()
        
        paginator = SmallPageNumberPagination()
        quiz_paginated = paginator.paginate_queryset(quizzes, request)
        
        quiz_serial = QuizSerializer(quiz_paginated, many=True)
        # paginate the response
        paginator= paginator.get_paginated_response({"quizzes": quiz_serial.data})
        return render(request, 'quizzes.html', {'paginator':paginator.data, 'quiz_paginated':quiz_paginated }, status=HTTP_200_OK)
    

    def post(self, request):
        # env = environ.Env()

        try:
            file = request.FILES.get("file")
        except:
            return Response({"error": "Not file in request.FILES"}, status=HTTP_400_BAD_REQUEST)
        print(request)
        if file is None:
            return Response({"error": "Not file added"}, status=HTTP_400_BAD_REQUEST)

        if not (file.name.endswith(".csv") or file.name.endswith(".xlsx")):
            return Response(
                {"error": "Incorrect Format, only .csv or Excel files permited"},
                status=HTTP_400_BAD_REQUEST,
            )

        # Dataframe to read and normalize
        if file.name.endswith("csv"):
            try:

                df = pd.read_csv(file, encoding="utf-8", delimiter=";")

            except:
                # Garantizes CSV UTF-8 because accents interpreted errors
                memo_file = ensureDecode(file)
                df = pd.read_csv(memo_file, encoding="utf-8", delimiter=";")
        elif file.name.endswith("xlsx"):
            df = pd.read_excel(file)
        else:
            return Response(
                {"error": "Incorrect Format, only CSV or XLSX files permited"},
                status=HTTP_400_BAD_REQUEST,
            )
        try:
            df_normal = normalizeFile(df)
        except ValidationError as v:
            return Response({f"Tiene valores vacíos. {v}"}, status=HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            quiz = Quiz.objects.create(file=file.name)
            """question_BD = []
            appearance_BD = []"""

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
                    return Response(
                        {
                            "error": f"Error al insertar la fila {i+1} la dimensión, área de interés o contenido nuclear. Error: {ve}"
                        },
                        status=HTTP_400_BAD_REQUEST,
                    )
                try:
                    question = Question.objects.create(
                        numero=i + 1,
                        statement=df_normal.iloc[i]["enunciado"],
                        time=time(0, 0, 30),
                        difficult_level=df_normal.iloc[i]["dificultad"],
                        version=0,
                        idD=dimensionN,
                        idA=areaIntN,
                        idC=coreCont,
                    )
                    """
                    question_BD.append(question)
                    appearance = AppearanceQuiz(quiz=quiz, question=question)
                    question.full_clean
                    appearance.full_clean
                    question_BD.append(question)
                    appearance_BD.append(appearance)
                    """
                    # Apperance model is through many to many field quiz question
                    quiz.question.add(question)

                except ValidationError as ve:
                    return Response(
                        {"error": f"Error al insertar la pregunta de la fila {i+1}, Error: {ve}"},
                        status=HTTP_400_BAD_REQUEST,
                    )
                """option_BD = []
                optionQ_BD = []"""
                for op in df_normal.iloc[i]["opciones"]:
                    try:

                        valor_op_mapeado = Opciones[op]
                        """
                        option = Option(valor_op_mapeado)
                        option.full_clean
                        # Create only one kind of option per quetsion in Option Table
                        if option not in option_BD:
                            option_BD.append(option)
                        """

                        # Create only one kind of option per quetsion in Option Table
                        option, _ = Option.objects.get_or_create(option=valor_op_mapeado)

                        """optionQ = OptionQuestion(idO=option, idP=question, motive=None)
                        optionQ.full_clean"""
                        optionQ = oqm.objects.create(idP=question, idO=option, motive=None)
                        if op == df_normal.iloc[i]["solucion"]:
                            optionQ.motive = df_normal.iloc[i]["motivo"]
                            optionQ.save()

                        # optionQ_BD.append(optionQ)

                    except ValidationError as ve:
                        return Response(
                            {
                                "error": f" Corrija la opción {valor_op_mapeado} del campo de opciones de la fila {i+1}"
                            },
                            status=HTTP_400_BAD_REQUEST,
                        )

            #     if i >= env("batch_size"):
            #         Question.objects.bulk_create(question_BD, batch_size=env("batch_size"))
            #         AppearanceQuiz.objects.create(appearance_BD, batch_size=env("batch_size"))
            #         Option.objects.bulk_create(option_BD, batch_size=env("batch_size"))
            #         OptionQuestion.objects.bulk_create(optionQ_BD, batch_size=env("batch_size"))

            # # if i have still some objects to create
            # Question.objects.bulk_create(question_BD)
            # AppearanceQuiz.objects.bulk_create(appearance_BD)
            # Option.objects.bulk_create(option_BD)
            # OptionQuestion.objects.bulk_create(optionQ_BD)

        return Response({"success"}, status=HTTP_200_OK)

    # --------- other funtions ---------
Opciones = {
    "Verdadero": "Verdadero",
    "True": "Verdadero",
    "Vertader": "Verdadero",
    "Falso": "Falso",
    "False": "Falso",
    "Fals": "Falso",
    "No lo sé": "No lo sé",
    "No ho sé": "No lo sé",
    "No en sé": "No lo sé",
    "No sé": "No lo sé",
}

"""
    Ensures right decode to CSV if is not a UTF-8 CSV, because accents can't be resolved corrected.
    Returns a new csv file in memory to be decoded into a new utf-8 file.
"""


def ensureDecode(file):
    contenido_str = file.read().decode("latin-1")
    # To read text and not bytes in memory we need io library
    archivo_en_memoria = io.StringIO(contenido_str)
    return archivo_en_memoria


def normalizeFile(df):

    NEW_header = [
        "enunciado",
        "dimension",
        "area",
        "contenido",
        "dificultad",
        "solucion",
        "motivo",
        "opciones",
    ]

    # Set columns header
    df.columns = NEW_header

    # set data types
    df = df.astype("string")
    df["dificultad"] = df["dificultad"].astype("int")

    # NA values
    df["dificultad"] = df["dificultad"].fillna(0)

    # Delete all NaN rows
    df = df.dropna(how="all")

    # Manage NA values of all dataframe
    # fill value as back or forward value
    # bfill is back fill with the next no NaN value
    # df_bfill = df.bfill()
    df = df.ffill()

    # Advertise NaN values
    nan_positions = df.isna()
    # Obtain nan rows and columns indexes
    nan_locations = nan_positions.stack()
    nan_rows_columns = nan_locations[nan_locations].index
    for row, col in nan_rows_columns:
        raise ValidationError(f"Fila: {row}, Columna: {col} no tiene un valor")

    # Guardar orden
    df["ordenD"] = df["dimension"].str.extract(r"(\d+)\.").astype(int)

    df["dimension"] = df["dimension"].str.extract(r"([a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+)")
    df["ordenA"] = df["area"].str.extract(r"(?<=\d\.)(\d+)").astype(int)
    df["area"] = df["area"].str.extract(r"([a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+)")
    df["solucion"] = df["solucion"].map(Opciones).astype("string")
    df["opciones"] = df["opciones"].str.split(";")

    # determine separator
    signos = ",;:?!.-_¨´+*^`[]¿¡'&%()$#·@!º\ª{} "
    signos_f = ",;:-_¨´+*^`[¿'&%($#·@º\ª{ "

    # # delete blanks before and after each colum
    for i in df.select_dtypes(include=["string"]).columns:
        df[i] = df[i].str.strip()
        df[i] = df[i].str.lstrip(signos + '"')
        df[i] = df[i].str.rstrip(signos_f)
        df[i] = df[i].str.capitalize()

    return pd.DataFrame(df)


def mapping(op):

    # Only the first option is capitalize to compare we need all of them
    if op.capitalize() in Opciones:
        op = Opciones[op.capitalize()]
        return op, Opciones[op.capitalize()]
    else:
        OptionError = Exception(f"No ha escrito bien las opciones")
        return OptionError

# ------ QUESTION VIEWS -------
# ModeliViewSet has already implemented to use create, retrieve, partial_update, update, destroy and list methods.
class QuestionView(ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer()

# ------ SHOW ANSWERS ----------------
class ShowAnswersByRespondant(APIView):

    def get(self, request):
        answers = Respuesta.objects.select_related("respondant")
        answers_respondant = answers.annotate("respondant").values(
            "respondant__id",
            "question__id",
            "statement",
            "solution",
            "answer",
            "date",
            "time",
        )
        if answers_respondant.exists():
            serializer = RespuestaSerializer(answers_respondant, many=True)

            return Response({"success", serializer.data}, status=HTTP_200_OK)
        return Response({"error": answers}, status=HTTP_404_NOT_FOUND)
   
class ShowAnswers():
    def get(self, request):
        respuestas = Respuesta.objects.all()
        return render(request, 'answers.html', respuestas)

class ShowResultsByQuestion(APIView):

    def get(self, request):
        pass

    # answers = Respuesta.objects.
    # if answers.exists():
    #     serializer = RespuestaSerializer(answers, many=True)
    #     return Response({'success'})
    # return Response({'error': answers}, status=HTTP_404_NOT_FOUND)


# ----------------- USERS -----------------
class ShowUsers():

    def get(self, request):
        respondant = Respondant.objects.all()
        return render(request, 'users.html', respondant)
