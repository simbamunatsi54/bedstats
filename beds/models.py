from django.db import models


class Ward(models.Model):
    name = models.CharField(max_length=100)
    ward_type = models.CharField(max_length=100, blank=True)
    total_beds = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Bed(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Occupied', 'Occupied'),
        ('Reserved', 'Reserved'),
        ('Cleaning', 'Cleaning'),
        ('Out of Service', 'Out of Service'),
    ]

    ward = models.ForeignKey(Ward, on_delete=models.CASCADE)
    bed_number = models.CharField(max_length=20)
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Available'
    )

    def __str__(self):
        return f"{self.ward.name} - Bed {self.bed_number}"

class Patient(models.Model):
    SEX_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    patient_number = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES)
    age = models.PositiveIntegerField()
    diagnosis = models.CharField(max_length=255, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_number} - {self.first_name} {self.last_name}"
class Admission(models.Model):
        patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
        bed = models.ForeignKey(Bed, on_delete=models.CASCADE)
        admission_date = models.DateTimeField(auto_now_add=True)
        expected_discharge_date = models.DateField(null=True, blank=True)
        diagnosis = models.CharField(max_length=255, blank=True)
        attending_department = models.CharField(max_length=100, blank=True)

        STATUS_CHOICES = [
            ('Admitted', 'Admitted'),
            ('Discharged', 'Discharged'),
            ('Transferred', 'Transferred'),
        ]

        status = models.CharField(
            max_length=20,
            choices=STATUS_CHOICES,
            default='Admitted'
        )

        def save(self, *args, **kwargs):
            self.bed.status = 'Occupied'
            self.bed.save()
            super().save(*args, **kwargs)

        def __str__(self):
            return f"{self.patient.patient_number} - {self.bed}"

class Discharge(models.Model):
            admission = models.OneToOneField(
                Admission,
                on_delete=models.CASCADE
            )
            discharge_date = models.DateTimeField(auto_now_add=True)
            discharge_reason = models.CharField(
                max_length=255,
                blank=True
            )
            remarks = models.TextField(blank=True)

            def save(self, *args, **kwargs):
                self.admission.status = 'Discharged'
                self.admission.save()

                self.admission.bed.status = 'Available'
                self.admission.bed.save()

                super().save(*args, **kwargs)

            def __str__(self):
                return (
                    f"{self.admission.patient.patient_number} - "
                    f"Discharged"
                )
class Transfer(models.Model):
    admission = models.ForeignKey(
        Admission,
        on_delete=models.CASCADE
    )

    from_bed = models.ForeignKey(
        Bed,
        on_delete=models.CASCADE,
        related_name='transfers_from'
    )

    to_bed = models.ForeignKey(
        Bed,
        on_delete=models.CASCADE,
        related_name='transfers_to'
    )

    transfer_date = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(
        max_length=255,
        blank=True
    )
    remarks = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.from_bed.status = 'Available'
        self.from_bed.save()

        self.to_bed.status = 'Occupied'
        self.to_bed.save()

        self.admission.bed = self.to_bed
        self.admission.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.admission.patient.patient_number} - "
            f"{self.from_bed} to {self.to_bed}"
        )
class Death(models.Model):
    admission = models.OneToOneField(
        Admission,
        on_delete=models.CASCADE
    )

    death_date = models.DateTimeField(auto_now_add=True)

    cause_of_death = models.CharField(
        max_length=255,
        blank=True
    )

    remarks = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.admission.status = 'Discharged'
        self.admission.save()

        self.admission.bed.status = 'Available'
        self.admission.bed.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.admission.patient.patient_number} - Death"