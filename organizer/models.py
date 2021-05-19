from django.db import models
from med.models import Patient, Service


class Record(models.Model):
    name = models.CharField(verbose_name='Название', max_length=100, blank=True)
    patient = models.ForeignKey(Patient, verbose_name='Пациент', on_delete=models.CASCADE)
    service = models.ForeignKey(Service, verbose_name='Услуга', on_delete=models.CASCADE)
    date_of_creation = models.DateTimeField(verbose_name='Дата записи')
    date_start = models.DateTimeField(verbose_name='Дата начала')
    date_end = models.DateTimeField(verbose_name='Дата окончания')
    done = models.BooleanField(verbose_name='Статус завершения', default=False)
    description = models.TextField(verbose_name='Описание', max_length=500, blank=True)

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ['done', '-date_start']

    def __str__(self):
        return 'Запись ' + str(self.id)
