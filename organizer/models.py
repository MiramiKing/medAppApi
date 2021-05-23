from django.db import models
from med.models import Patient, Service, MedPersona


class Record(models.Model):
    name = models.CharField(verbose_name='Название', max_length=100, blank=True)
    patient = models.ForeignKey(Patient, verbose_name='Пациент', on_delete=models.CASCADE)
    # service = models.ForeignKey(Service, verbose_name='Услуга', on_delete=models.CASCADE)
    date_of_creation = models.DateTimeField(verbose_name='Дата записи')
    date_start = models.DateTimeField(verbose_name='Дата начала')
    date_end = models.DateTimeField(verbose_name='Дата окончания')
    done = models.BooleanField(verbose_name='Завершен', default=False)
    editable = models.BooleanField(verbose_name='Редактируемый', default=False)
    description = models.TextField(verbose_name='Описание', max_length=500, blank=True)

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ['done', '-date_start']

    def __str__(self):
        return 'Запись ' + str(self.id)


class RecordService(models.Model):
    record = models.OneToOneField(
        Record,
        verbose_name='Запись',
        related_name='record_service',
        on_delete=models.CASCADE
    )
    service = models.ForeignKey(
        Service,
        verbose_name='Услуга',
        related_name='service_record',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Запись-Услуга'
        verbose_name_plural = 'Записи-Услуги'

    def __str__(self):
        return 'Запись-Услуга ' + str(self.id)


class RecordServiceMedPersona(models.Model):
    record_service = models.OneToOneField(
        RecordService,
        verbose_name='Запись-Услуга',
        related_name='record_service_medpersona',
        on_delete=models.CASCADE,
    )
    # внешний ключ поскольку один мед сотрудник может стоять за несколькими 
    # услугами, соответственно может быть несколько записей на совершенно разные
    # услуги одного мед работника
    medpersona = models.ForeignKey(
        MedPersona,
        verbose_name='Мед персона',
        related_name='medpersona_record_service',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Запись-Услуга-Медперсона'
        verbose_name_plural = 'Записи-Услуги-Медперсоны'

    def __str__(self):
        return 'Запись-Услуга-Медперсона ' + str(self.id)