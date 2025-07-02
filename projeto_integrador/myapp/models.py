from datetime import datetime
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
    matricula = models.CharField(max_length=100)
    nascimento=models.CharField(max_length=100)
    endereco=models.CharField(max_length=100)
    telefone =models.CharField(max_length=100)
    cidade=models.CharField(max_length=100)
    arquivo=models.FileField(upload_to='media/')
    def save(self, *args, **kwargs):
        if not self.matricula:
            ano_atual = datetime.now().year  # Ex: 2024
            prefixo = str(ano_atual)

            # Pega últimas matrículas do mesmo ano
            ultimos = Cadastro.objects.filter(matricula__startswith=prefixo).order_by('-matricula')
            if ultimos.exists():
                ultimo_numero = int(ultimos.first().matricula[-3:])  # pega os últimos 3 dígitos
                novo_numero = ultimo_numero + 1
            else:
                novo_numero = 1

            self.matricula = f'{prefixo}{novo_numero:03d}'  # Ex: 2024001
        super().save(*args, **kwargs)
  

