import pandas as pd 
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ankiapp.settings')
django.setup()

from webapp.models import *

data = pd.read_csv('uw_course.csv')

Course.objects.bulk_create([
    Course(subject=row['Subject'],catalog_number=row['Catalog Number'],title=row['Title'],topic=row['Topic'],campus=row['Campus'])
    for _, row in data.iterrows()
])