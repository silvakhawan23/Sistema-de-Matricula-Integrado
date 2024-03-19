from django.db import models
class Aprovado(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=100)
    cpf=models.CharField(max_length=100)
    curso=models.CharField(max_length=100)

class Cadastro (models.Model):
    id=models.AutoField(primary_key=True)
    escola=models.CharField(max_length=100)
    email=models.EmailField(max_length=254)
    aprovados = models.ForeignKey(Aprovado,on_delete=models.CASCADE,blank=False)
    nascimento=models.CharField(max_length=100)
    endereco=models.CharField(max_length=100)
    cidade=models.CharField(max_length=100)
    arquivo=models.FileField(upload_to='media/')
  

