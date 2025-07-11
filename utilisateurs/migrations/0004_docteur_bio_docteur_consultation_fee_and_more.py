# Generated by Django 5.2.1 on 2025-06-19 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilisateurs', '0003_user_code_expires_at_user_verification_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='docteur',
            name='bio',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='docteur',
            name='consultation_fee',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='docteur',
            name='experience',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='docteur',
            name='numero_licence',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='allergies',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='antecedents',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='groupe_sanguin',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name='patient',
            name='poids',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='taille',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
    ]
