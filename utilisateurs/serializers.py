from rest_framework import serializers
from .models import User, Docteur, Patient, Specialite



# Serializer pour l'utilisateur
class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)
    nom= serializers.CharField(max_length=100, required=True)
    prenom = serializers.CharField(max_length=100, required=True)
    role = serializers.ChoiceField(choices=[('patient', 'Patient'), ('docteur', 'Docteur'), ('admin', 'Administrateur')], default='patient')
    telephone = serializers.CharField(max_length=20, allow_blank=True, required=False)
    date_naiss = serializers.DateField(required=False, allow_null=True)
    adresse = serializers.CharField(style={'base_template': 'textarea.html'}, allow_blank=True, required=False)
    genre = serializers.ChoiceField(choices=[('M', 'Masculin'), ('F', 'Féminin'), ('O', 'Autre')], allow_blank=True, required=False)
    is_doctor_request = serializers.BooleanField(default=False)
    verification_code = serializers.CharField(max_length=6, allow_blank=True, required=False)
    code_expires_at = serializers.DateTimeField(required=False, allow_null=True)
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.nom = validated_data.get('nom', instance.nom)
        instance.prenom = validated_data.get('prenom', instance.prenom)
        instance.role = validated_data.get('role', instance.role) 
        instance.telephone = validated_data.get('telephone', instance.telephone)
        instance.date_naiss = validated_data.get('date_naiss', instance.date_naiss)
        instance.adresse = validated_data.get('adresse', instance.adresse)
        instance.genre = validated_data.get('genre', instance.genre)
        instance.is_doctor_request = validated_data.get('is_doctor_request', instance.is_doctor_request)
        instance.verification_code = validated_data.get('verification_code', instance.verification_code)
        instance.code_expires_at = validated_data.get('code_expires_at', instance.code_expires_at)
        instance.save()
        return instance
    
# Serializer pour le docteur
class DocteurSerializer(serializers.ModelSerializer):
    user= UserSerializer()
    specialite = serializers.CharField(max_length=100, required=True)
    est_approuve = serializers.BooleanField(default=False)
    numero_licence = serializers.CharField(max_length=50, required=True)
    bio= serializers.CharField(style={'base_template': 'textarea.html'}, allow_blank=True, required=False)
    experience = serializers.IntegerField(required=False, allow_null=True)
    consultation_fee = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)

    def create(self, validated_data):
        return Docteur.objects.create(
            user=User.objects.create_user(**validated_data.pop('user')),
            **validated_data
        )
    def update(self, instance, validated_data):
        instance.user= validated_data['user'].get('username', instance.user.username)
        instance.specialite = validated_data.get('specialite', instance.specialite)
        instance.est_approuve = validated_data.get('est_approuve', instance.est_approuve)
        instance.numero_licence = validated_data.get('numero_licence', instance.numero_licence)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.experience = validated_data.get('experience', instance.experience)
        instance.consultation_fee = validated_data.get('consultation_fee', instance.consultation_fee)
        instance.save()
        return instance
    

# Serializer pour le patient  

class PatientSerializer(serializers.ModelSerializer):
    user= UserSerializer()
    docteur_principal = serializers.PrimaryKeyRelatedField(
        queryset=Docteur.objects.all(),
        allow_null=True,
        required=False
    )
    groupe_sanguin = serializers.CharField(max_length=10, allow_blank=True, required=False)
    taille= serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True, required=False)
    poids = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True, required=False)
    allergies = serializers.CharField(style={'base_template': 'textarea.html'}, allow_blank=True, required=False)
    antecedents = serializers.CharField(style={'base_template': 'textarea.html'}, allow_blank=True, required=False) 

    def create(self, validated_data):
        return Patient.objects.create(
            user=User.objects.create_user(**validated_data.pop('user')),
            **validated_data
        )
    def update(self, instance, validated_data):
        instance.user = validated_data['user'].get('username', instance.user.username)
        instance.docteur_principal = validated_data.get('docteur_principal', instance.docteur_principal)
        instance.groupe_sanguin = validated_data.get('groupe_sanguin', instance.groupe_sanguin)
        instance.taille = validated_data.get('taille', instance.taille)
        instance.poids = validated_data.get('poids', instance.poids)
        instance.allergies = validated_data.get('allergies', instance.allergies)
        instance.antecedents = validated_data.get('antecedents', instance.antecedents)
        instance.save()
        return instance
    
#Serializer pour specialite

class SpecialiteSerializer(serializers.ModelSerializer):
    nom= serializers.CharField(max_length=100, required=True)
    description = serializers.CharField(style={'base_template': 'textarea.html'}, allow_blank=True, required=False)

    def create(self, validated_data):
        return Specialite.objects.create(**validated_data)
    def update(self, instance, validated_data):
        instance.nom = validated_data.get('nom', instance.nom)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance
    