from django.urls import path
from . import views

app_name = 'patientlisting'

urlpatterns = [
    path('', views.index, name ='pl_index'),
    #extract data from files
    path('all-patients/', views.upload_patient_file, name ="pl_upload_patient_file"),
    path('upload-patient-file/save-content', views.save_file_content, name ="pl_save_file_content"),
    path('download-patient-model-file/', views.download_patient_model_file, name="pl_patient_model_file"),
    path('download-patient-uploaded-file/', views.download_patient_uploaded_file, name="pl_upload_loaded_patient_file"),
    
    #extract data from database
    path('month-rdv-listing/', views.waited_patient, name="month_rdv"),
    path('lost-patient/', views.patient_PVD, name="pl_lost_rdv"),
    path('missed-rdv/', views.missed_rdv_patient, name="pl_missed_rdv"),
    
    #export data into pdf files
    path('export-month-listing/', views.GenerateMonthRDVListingPDF.as_view(), name="pl_export_month_listing"),
    path('export-missed-listing/', views.GenerateMissedRDVListingPDF.as_view(), name="pl_export_missed_listing"),
    path('export-lost-listing/', views.GenerateLostPatientListingPDF.as_view(), name="pl_export_lost_listing"),
]