import locale, asyncio, calendar, random, math, activite_relance as ar
from time import strftime
from django.http.response import HttpResponse
from numpy.core.getlimits import finfo
import pandas as pd, numpy as np, datetime as dt, tempfile, dateutil
import dashboard.models as dash_mod, json, requests, os
# from pandas.io import json
from operator import attrgetter
from secrets import token_hex
from django.shortcuts import render
from django.http import HttpResponseBadRequest, JsonResponse
from django.core.files.storage import FileSystemStorage
from pathlib import Path
from datetime import datetime, timedelta
from .models import PatientListing
from .extractxlsx import PatientExtractXLSX
from openpyxl.utils import get_column_letter, column_index_from_string
from dashboard.models import SiteInfo
from relance_patient.utils import download as file_download, converter
from pandas import DataFrame
from asgiref.sync import sync_to_async
from activite_relance.models import Patient, DateRDV, Venue, PersonSoutien
from relance_patient.utils import get_month_limit, get_year_month, get_list_year, download_data
from django.views import View
from relance_patient.utils import export_to_pdf
from django.core.paginator import Paginator
from django.db import connections
from relance_patient.settings import base


def generate_filename():
    now_date = datetime.now().date()
    now_time = datetime.now().time()
    return str(now_date).replace('-', '') + str(now_time).split('.')[0].replace(':', '')

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]

    for row in cursor.fetchall():
        yield dict(zip(columns, row))


def check_if_patient_exist(code_patient):
    return ar.models.Patient.objects.filter(code_patient=code_patient).exists()

def save_patient_data(patients:list, rdv_date:list, persones_soutiens: list, site: dash_mod.SiteInfo):
    result = []
    for x, y, z in zip(patients, rdv_date, persones_soutiens):
        patient_data = {"site":site, "first_name":x['Nom_Patient'], "last_name":x['Prenoms_Patient'], "sexe":x['Sexe'], "age":x['Age'], "situation_matrimoniale":x['Situation_matrimoniale'], "contact":x['Contact_Téléphonique'], "domicile":x['Lieu_Habitation']}

        rdv_data = { "date_last_arv":y['Date_dernier_ARV'], "date_proch_arv":y['Date_prochain_ARV'],"date_last_cv":y['Date_Dernier_CV'],"date_proch_cv":y['Date_prochain_CV']}

        person_soutient_data = {"first_name":z['Nom_Personne_Soutien'], "last_name":z['Prénoms_Personne_Soutien'], "adresse":z['Adresse_Personne_Soutien'], "contact":z['Contact_Personne_Soutien'], "lien":z['Lien_Patient']}

        patient, patient_created = ar.models.Patient.objects.update_or_create(code_patient=x['Code_Patient'], defaults = patient_data)
        rdv, rdv_created = ar.models.DateRDV.objects.update_or_create(patient=patient, defaults=rdv_data)
        person, person_created = ar.models.PersonSoutien.objects.update_or_create(patient=patient, defaults=person_soutient_data)
        
        if patient_created and rdv_created and person_created:
            result.append(True)
        else:
            result.append(False)

    return all(result)

# Patient listing home
def index(request):
    now = dt.datetime.now()
    if request.session.get('data_used'):
        try:
            if (now-dt.datetime.strptime(request.session['data_used']['time'],"%Y-%m-%d %H:%M:%S")>dt.timedelta(minutes=5)):
                data_used = {
                    'time':dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'data':download_data(base.DATA_URL,base.AUTH_SIGDEP)
                }
                request.session['data_used']=data_used
            else:
                pass
        except Exception:
            return render(request, "connexion_error.html")
    else:
        try:
            data_used = {
                'time':dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'data':download_data(base.DATA_URL,base.AUTH_SIGDEP)
            }
            request.session['data_used']=data_used
        except Exception:
            return render(request, "connexion_error.html")
    return render(request, "patientlisting/index.html")

def extract_patient_data(filename, file_type="xlsx", header=1):
    df = None
    if file_type == "xlsx":
        df = pd.read_excel(filename, header=header)
    
    df_patient = df.loc[:,'Code_Patient':'Contact_Téléphonique']
    df_dateRDV = df.loc[:,'Date_Dernier_CV':'Date_prochain_ARV']
    df_person_soutient = df.loc[:,'Nom_Personne_Soutien':'Lien_Patient']

    patient_list = []
    date_RDV_list = []
    person_soutien_list = []

    for i, row in df_patient.iterrows():
        patient_list.append(row.to_dict())

    for i, row in df_dateRDV.iterrows():
        date_RDV_list.append(row.to_dict())

    for i, row in df_person_soutient.iterrows():
        person_soutien_list.append(row.to_dict())

    return [patient_list, date_RDV_list, person_soutien_list,]


def upload_patient_file(request):
    site = SiteInfo.objects.filter(site_code=request.user.user.site_code).first()
    if request.method == "POST":
        patient_file = request.FILES['patient_file']
        fs = FileSystemStorage()
        file_path = Path(patient_file.name)
        new_file_name = f'{token_hex(8)}{generate_filename()}{file_path.suffix}'
        filename = fs.save(new_file_name, patient_file)
        url = fs.url(filename)
        
        if site:
            site.patient_file = url
            site.save()

            patient_list, dateDRV_list, person_soutien_list = extract_patient_data(url)

            result = sync_to_async(save_patient_data(patient_list, dateDRV_list, person_soutien_list, site), thread_sensitive=True)

            if result:
                return JsonResponse({'type': 'success', 'message': 'Enregistrement des patients réussie'})
            else:
                return JsonResponse({'type': 'error', 'message': 'Erreur d\'enregistrement des patients'})
        else:
            return JsonResponse({'type': 'error', 'message': 'Erreur d\'enregistrement des patients'})

    patients = ar.models.Patient.objects.filter(site=site)
    context = {
        'patients': patients
    }
    return render(request, "patientlisting/upload_patient.html", context)


# Download patient fiche modele file
def download_patient_model_file(request):
    filename = "documents/modele_fiche_patient.xlsx"
    download = file_download(request, filename)
    return download

# Download site last upload file
def download_patient_uploaded_file(request):
    filename = request.user._get_account_site.patient_file
    download = file_download(request, filename, is_uploaded=True)
    return download

#save file content to db
def save_file_content(request):
    if request.method == "POST":
        patient_listing = PatientListing.objects.filter(account=request.user)

def waited_patient(request):
    list_of_month = get_year_month()
    years = get_list_year(2000, 2099)
    now = dt.date.today()
    period = ""
    rdv = []
    session_data = []
    start_date = None
    end_date = None

    if request.GET.get('listing_type')=='interval':
        period = dt.datetime.strptime(request.GET['listing_interval_start'],'%Y-%m-%d').strftime("%d-%m-%Y") + "/" + dt.datetime.strptime(request.GET['listing_interval_end'],'%Y-%m-%d').strftime("%d-%m-%Y")
        start_date = dt.datetime.strptime(request.GET['listing_interval_start'],'%Y-%m-%d').date()
        end_date = dt.datetime.strptime(request.GET['listing_interval_end'],'%Y-%m-%d').date()
    elif request.GET.get('listing_type')=='month':
        month = int(request.GET['listing_month']) or now.month
        year = int(request.GET['listing_year']) or now.year
        period = str([k for k in get_year_month() if k[0]==month][0][1]) + " " + str(year)
        start_date, end_date = get_month_limit(year, month)

    if start_date and end_date:
        data=pd.DataFrame(json.loads(request.session['data_used']['data']))
        for i,row in data.iterrows():
            if start_date<=dt.datetime.strptime(row['proch_rdv'],'%Y-%m-%d').date()<=end_date:
                session_data.append(row.to_dict())
                row['proch_rdv'] = dt.datetime.strptime(row['proch_rdv'].split('/')[0], '%Y-%m-%d').date()
                row['rupture_arv'] = dt.datetime.strptime(row['rupture_arv'].split('/')[0], '%Y-%m-%d').date()
                rdv.append(row.to_dict())  
    if session_data:
        rdv_cal=sorted(session_data, key=lambda x:x['proch_rdv'], reverse=True)
        serialize_data=rdv_cal
        cal_rdv = {
            'type' : 'month',
            'period' : period,
            'data' : json.dumps(serialize_data, default=converter)
        }
        request.session['month_rdv']=cal_rdv
    else:
        pass

    rdv_cal=sorted(rdv, key=lambda x:x['proch_rdv'], reverse=True) 
    paginator = Paginator(rdv_cal, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj, 'years': years, 'cur_year': now.year, 'list_of_month': list_of_month, }

    return render(request, 'patientlisting/listing/month_rdv.html', context)


def missed_rdv_patient(request):
    list_of_month = get_year_month()
    years = get_list_year(2000, 2099)
    now = dt.date.today()
    period = ""
    rdv = []
    session_data = []

    if request.GET.get('listing_month') or request.GET.get('listing_year'):
        month = int(request.GET['listing_month']) or now.month
        year = int(request.GET['listing_year']) or now.year
        period = str([k for k in get_year_month() if k[0]==month][0][1]) + " " + str(year)
        start_date, end_date = get_month_limit(year, month)
        data=pd.DataFrame(json.loads(request.session['data_used']['data']))
        for i,row in data.iterrows():
            if start_date<=dt.datetime.strptime(row['proch_rdv'],'%Y-%m-%d').date()<=end_date and now>dt.datetime.strptime(row['proch_rdv'],'%Y-%m-%d').date():
                session_data.append(row.to_dict())
                row['proch_rdv'] = dt.datetime.strptime(row['proch_rdv'].split('/')[0], '%Y-%m-%d').date()
                row['rupture_arv'] = dt.datetime.strptime(row['rupture_arv'].split('/')[0], '%Y-%m-%d').date()
                rdv.append(row.to_dict())  
    if session_data:
        rdv_cal=sorted(session_data, key=lambda x:x['proch_rdv'], reverse=True)
        serialize_data=rdv_cal
        cal_rdv = {
            'type' : 'month',
            'period' : period,
            'data' : json.dumps(serialize_data, default=converter)
        }
        request.session['missed_rdv']=cal_rdv
    else:
        pass

    rdv_cal=sorted(rdv, key=lambda x:x['proch_rdv'], reverse=True) 
    paginator = Paginator(rdv_cal, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj, 'years': years, 'cur_year': now.year, 'list_of_month': list_of_month, }

    return render(request, 'patientlisting/listing/missed_rdv.html', context)

def patient_PVD(request):
    now = dt.date.today()
    losted_patient = []
    session_data = []

    if request.GET.get('type_losted'):
        days_losted = int(request.GET.get('type_losted'))
        data=pd.DataFrame(json.loads(request.session['data_used']['data']))
        for i,row in data.iterrows():
            if datetime.strptime(row['proch_rdv'],'%Y-%m-%d').date()<=now-timedelta(days=days_losted):
                session_data.append(row.to_dict())
                row['proch_rdv'] = dt.datetime.strptime(row['proch_rdv'].split('/')[0], '%Y-%m-%d').date()
                row['rupture_arv'] = dt.datetime.strptime(row['rupture_arv'].split('/')[0], '%Y-%m-%d').date()
                losted_patient.append(row.to_dict())

    if session_data:
        rdv_cal=sorted(session_data, key=lambda x:x['proch_rdv'], reverse=True)
        serialize_data=rdv_cal
        cal_rdv = {
            'type' : 'month',
            'time': days_losted,
            'data' : json.dumps(serialize_data, default=converter)
        }
        request.session['patient_pvd']=cal_rdv
    else:
        pass
    
    rdv_cal=sorted(losted_patient, key=lambda x:x['proch_rdv'], reverse=True) 
    paginator = Paginator(rdv_cal, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj }

    return render(request, 'patientlisting/listing/lost_patient.html', context)


# GENERATE MONTH RDV LIST
class GenerateMonthRDVListingPDF(View):
    def get(self, request, *args, **kwargs):

        # Set locale time to french
        locale.setlocale(locale.LC_TIME, 'fr_FR')

        # Template for the view
        template_src = 'reports/month_rdv_listing.html'

        period = request.session['month_rdv']['period']

        # load moth rdv in the session
        session_data = json.loads(request.session['month_rdv']['data'])
        # For each rdv object convert dupms date to datetime object
        for item in session_data:
            # item['date_rdv'] = dt.datetime.strptime(item['date_rdv'], "%Y-%m-%d").date()
            item['proch_rdv'] = dt.datetime.strptime(item['proch_rdv'].split('/')[0], '%Y-%m-%d').date()



        # define conext
        context = {
            'rdv_month_listing': session_data,
            'user': request.user,
            'service': request.user._get_account_site,
            'period': period,
            'type_rdv': request.session['month_rdv']['type'],
        }

        # response headers
        response = HttpResponse(content_type="application/pdf")
        response['Content-Disposition'] = "inline; filename=LISTING_RDV_"+ period.upper() +'.pdf'
        response['Content-Transfer-Encoding'] = "binary"

        # Create pdf file using export_to_pdf func
        result = export_to_pdf(template_src, context)

        with tempfile.NamedTemporaryFile(delete=False) as output:
            output.write(result)
            output.flush()
            output.close()
            output = open(output.name, 'rb')
            response.write(output.read())
            output.close()
            os.remove(output.name)

        return response


# GENERATE MONTH MISSED RDV LIST
class GenerateMissedRDVListingPDF(View):
    def get(self, request, *args, **kwargs):

        # Set locale time to french
        locale.setlocale(locale.LC_TIME, 'fr_FR')

        # Template for the view
        template_src = 'reports/missed_rdv_listing.html'

        # get period of rdv from session
        # period = str(request.session['rdv_missed_listing']['period']['month']) + '-' + request.session['rdv_missed_listing']['period']['year']
        period = request.session['missed_rdv']['period']
        # period_str = dt.datetime.strptime(period, '%m-%Y').strftime('%B %Y')

        # load moth rdv in the session
        session_data = json.loads(request.session['missed_rdv']['data'])

        # For each rdv object convert dupms date to datetime object
        for item in session_data:
            # item['date_rdv'] = dt.datetime.strptime(json.loads(item['date_rdv']), "%Y-%m-%d").date()
            item['proch_rdv'] = dt.datetime.strptime(item['proch_rdv'].split('/')[0], '%Y-%m-%d').date()

        # define conext
        context = {
            'rdv_missed_listing': session_data,
            'user': request.user,
            'service': request.user._get_account_site,
            'period': period,
        }

        # response headers
        response = HttpResponse(content_type="application/pdf")
        response['Content-Disposition'] = "inline; filename=LISTING_MISSED_RDV_"+ period.upper() +'.pdf'
        response['Content-Transfer-Encoding'] = "binary"

        # Create pdf file using export_to_pdf func
        result = export_to_pdf(template_src, context)

        with tempfile.NamedTemporaryFile(delete=False) as output:
            output.write(result)
            output.flush()
            output.close()
            output = open(output.name, 'rb')
            response.write(output.read())
            output.close()
            os.remove(output.name)

        return response


# GENERATE MONTH MISSED RDV LIST
class GenerateLostPatientListingPDF(View):
    def get(self, request, *args, **kwargs):

        # Set locale time to french
        locale.setlocale(locale.LC_TIME, 'fr_FR')

        # Template for the view
        template_src = 'reports/lost_patient_listing.html'

        # load moth rdv in the session
        session_data = json.loads(request.session['patient_pvd']['data'])
        type_losted = request.session['patient_pvd']['type']
        nbr_days = request.session['patient_pvd']['time']
        # For each rdv object convert dupms date to datetime object
        for item in session_data:
            # item['date_rdv'] = dt.datetime.strptime(json.loads(item['date_rdv']), "%Y-%m-%d").date()
            item['proch_rdv'] = dt.datetime.strptime(item['proch_rdv'].split('/')[0], '%Y-%m-%d').date()

        # define conext
        context = {
            'rdv_lost_listing': session_data,
            'user': request.user,
            'service': request.user._get_account_site,
            'type_losted': type_losted,
            'time': nbr_days
        }

        # response headers
        response = HttpResponse(content_type="application/pdf")
        response['Content-Disposition'] = "inline; filename=LISTING_LOST_RDV_" + dt.date.today().strftime("%d-%m-%Y").upper() +'.pdf'
        response['Content-Transfer-Encoding'] = "binary"

        # Create pdf file using export_to_pdf func
        result = export_to_pdf(template_src, context)

        with tempfile.NamedTemporaryFile(delete=False) as output:
            output.write(result)
            output.flush()
            output.close()
            output = open(output.name, 'rb')
            response.write(output.read())
            output.close()
            os.remove(output.name)

        return response