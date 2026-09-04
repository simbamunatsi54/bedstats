from io import BytesIO
from xml.sax.saxutils import escape
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from openpyxl.styles import Font
from django.db.models import Q
from django.utils.dateparse import parse_date
from datetime import timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from openpyxl import Workbook

from .models import (
    Ward,
    Bed,
    Patient,
    Admission,
    Discharge,
    Transfer,
    Death,
)

def user_in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


def require_group(user, *groups):
    if user.is_superuser:
        return

    if not any(
        user_in_group(user, group)
        for group in groups
    ):
        raise PermissionDenied
# =========================
# DASHBOARD
# =========================

@login_required
def dashboard(request):

    require_group(
        request.user,
        "Administrator",
        "Health Information Officer",
        "Matron/Nurse",
        "Records Officer",
        "Doctor",
        "Management",
    )
    is_admin = (
            request.user.is_superuser
            or request.user.groups.filter(
        name="Administrator"
    ).exists()
    )

    is_hio = request.user.groups.filter(
        name="Health Information Officer"
    ).exists()

    is_nurse = request.user.groups.filter(
        name="Matron/Nurse"
    ).exists()

    is_records = request.user.groups.filter(
        name="Records Officer"
    ).exists()

    is_doctor = request.user.groups.filter(
        name="Doctor"
    ).exists()

    is_management = request.user.groups.filter(
        name="Management"
    ).exists()

    total_beds = Bed.objects.count()

    occupied_beds = Bed.objects.filter(
        status="Occupied"
    ).count()

    available_beds = Bed.objects.filter(
        status="Available"
    ).count()

    today = timezone.localdate()

    admissions_today = Admission.objects.filter(
        admission_date__date=today
    ).count()

    discharges_today = Discharge.objects.filter(
        discharge_date__date=today
    ).count()

    transfers_today = Transfer.objects.filter(
        transfer_date__date=today
    ).count()

    deaths_today = Death.objects.filter(
        death_date__date=today
    ).count()

    if total_beds > 0:
        occupancy_rate = round(
            (occupied_beds / total_beds) * 100,
            1
        )
    else:
        occupancy_rate = 0

    ward_data = []

    for ward in Ward.objects.all().order_by("name"):

        total = Bed.objects.filter(
            ward=ward
        ).count()

        occupied = Bed.objects.filter(
            ward=ward,
            status="Occupied"
        ).count()

        available = Bed.objects.filter(
            ward=ward,
            status="Available"
        ).count()

        if total > 0:
            rate = round(
                (occupied / total) * 100,
                1
            )
        else:
            rate = 0

        ward_data.append({
            "name": ward.name,
            "total": total,
            "occupied": occupied,
            "available": available,
            "rate": rate,
        })

    context = {
        "total_beds": total_beds,
        "occupied_beds": occupied_beds,
        "available_beds": available_beds,
        "occupancy_rate": occupancy_rate,
        "admissions_today": admissions_today,
        "discharges_today": discharges_today,
        "transfers_today": transfers_today,
        "deaths_today": deaths_today,
        "ward_data": ward_data,

        "is_admin": is_admin,
        "is_hio": is_hio,
        "is_nurse": is_nurse,
        "is_records": is_records,
        "is_doctor": is_doctor,
        "is_management": is_management,
    }

    return render(
        request,
        "beds/dashboard.html",
        context
    )


# =========================
# PATIENT LIST
# =========================

@login_required
def patient_list(request):
    require_group(
        request.user,
        "Administrator",
        "Health Information Officer",
        "Records Officer",
        "Doctor",
        "Management",
    )

    patients = Patient.objects.all().order_by(
        "-registration_date"
    )

    return render(
        request,
        "beds/patient_list.html",
        {"patients": patients}
    )


# =========================
# REGISTER PATIENT
# =========================

@login_required
def register_patient(request):
    require_group(
        request.user,
        "Administrator",
        "Health Information Officer",
        "Records Officer",
    )

    if request.method == "POST":

        patient_number = request.POST.get(
            "patient_number"
        )

        first_name = request.POST.get(
            "first_name"
        )

        last_name = request.POST.get(
            "last_name"
        )

        sex = request.POST.get(
            "sex"
        )

        age = request.POST.get(
            "age"
        )

        diagnosis = request.POST.get(
            "diagnosis"
        )

        registration_date = request.POST.get(
            "registration_date"
        )

        if Patient.objects.filter(
            patient_number=patient_number
        ).exists():

            return render(
                request,
                "beds/patient_register.html",
                {
                    "error":
                    "Patient number already exists."
                }
            )

        Patient.objects.create(
            patient_number=patient_number,
            first_name=first_name,
            last_name=last_name,
            sex=sex,
            age=age,
            diagnosis=diagnosis,
            registration_date=registration_date,
        )

        return redirect("patient_list")

    return render(
        request,
        "beds/patient_register.html"
    )


# =========================
# BED LIST
# =========================

@login_required
def bed_list(request):
    require_group(
        request.user,
        "Administrator",
        "Health Information Officer",
        "Matron/Nurse",
        "Records Officer",
        "Doctor",
        "Management",
    )

    beds = Bed.objects.select_related(
        "ward"
    ).order_by(
        "ward__name",
        "bed_number"
    )

    return render(
        request,
        "beds/bed_list.html",
        {"beds": beds}
    )


# =========================
# CHANGE BED STATUS
# =========================

@login_required
def change_bed_status(request, bed_id):
    require_group(
        request.user,
        "Administrator",
        "Health Information Officer",
        "Matron/Nurse",
    )

    bed = Bed.objects.get(
        id=bed_id
    )

    if request.method == "POST":

        status = request.POST.get(
            "status"
        )

        bed.status = status
        bed.save()

    return redirect("bed_list")


# =========================
# ADMISSION
# =========================

@login_required
def admission_create(request):
    require_group(
        request.user,
        "Administrator",
        "Health Information Officer",
        "Matron/Nurse",
        "Records Officer",
        "Doctor",
    )

    patients = Patient.objects.all().order_by(
        "patient_number"
    )

    beds = Bed.objects.filter(
        status="Available"
    ).select_related(
        "ward"
    ).order_by(
        "ward__name",
        "bed_number"
    )

    if request.method == "POST":

        patient_id = request.POST.get(
            "patient"
        )

        bed_id = request.POST.get(
            "bed"
        )

        admission_date = request.POST.get(
            "admission_date"
        )

        expected_discharge_date = request.POST.get(
            "expected_discharge_date"
        )

        diagnosis = request.POST.get(
            "diagnosis"
        )

        attending_department = request.POST.get(
            "attending_department"
        )

        try:

            patient = Patient.objects.get(
                id=patient_id
            )

            bed = Bed.objects.get(
                id=bed_id
            )

            if bed.status != "Available":

                return render(
                    request,
                    "beds/admission_create.html",
                    {
                        "patients": patients,
                        "beds": beds,
                        "error":
                        "The selected bed is no longer available."
                    }
                )

            Admission.objects.create(
                patient=patient,
                bed=bed,
                admission_date=admission_date,
                expected_discharge_date=
                    expected_discharge_date,
                diagnosis=diagnosis,
                attending_department=
                    attending_department,
                status="Admitted",
            )

            bed.status = "Occupied"
            bed.save()

            return redirect("dashboard")

        except Exception as e:

            return render(
                request,
                "beds/admission_create.html",
                {
                    "patients": patients,
                    "beds": beds,
                    "error": str(e),
                }
            )

    return render(
        request,
        "beds/admission_create.html",
        {
            "patients": patients,
            "beds": beds,
        }
    )


# =========================
# DISCHARGE
# =========================

@login_required
def discharge_create(request):
    require_group(
        request.user,
        "Administrator",
        "Health Information Officer",
        "Matron/Nurse",
        "Records Officer",
    )

    admissions = Admission.objects.filter(
        status="Admitted"
    ).select_related(
        "patient",
        "bed"
    )

    if request.method == "POST":

        admission_id = request.POST.get(
            "admission"
        )

        discharge_date = request.POST.get(
            "discharge_date"
        )

        reason = request.POST.get(
            "reason"
        )

        remarks = request.POST.get(
            "remarks"
        )

        try:

            admission = Admission.objects.get(
                id=admission_id
            )

            Discharge.objects.create(
                admission=admission,
                discharge_date=discharge_date,
                reason=reason,
                remarks=remarks,
            )

            admission.status = "Discharged"
            admission.save()

            bed = admission.bed
            bed.status = "Available"
            bed.save()

            return redirect("dashboard")

        except Exception as e:

            return render(
                request,
                "beds/discharge_create.html",
                {
                    "admissions": admissions,
                    "error": str(e),
                }
            )

    return render(
        request,
        "beds/discharge_create.html",
        {
            "admissions": admissions,
        }
    )


# =========================
# TRANSFER
# =========================

@login_required
def transfer_create(request):
    require_group(
        request.user,
        "Administrator",
        "Health Information Officer",
        "Matron/Nurse",
        "Records Officer",
    )

    admissions = Admission.objects.filter(
        status="Admitted"
    ).select_related(
        "patient",
        "bed"
    )

    beds = Bed.objects.filter(
        status="Available"
    ).select_related(
        "ward"
    ).order_by(
        "ward__name",
        "bed_number"
    )

    if request.method == "POST":

        admission_id = request.POST.get(
            "admission"
        )

        to_bed_id = request.POST.get(
            "to_bed"
        )

        transfer_date = request.POST.get(
            "transfer_date"
        )

        reason = request.POST.get(
            "reason"
        )

        remarks = request.POST.get(
            "remarks"
        )

        try:

            admission = Admission.objects.get(
                id=admission_id
            )

            to_bed = Bed.objects.get(
                id=to_bed_id
            )

            if to_bed.status != "Available":

                return render(
                    request,
                    "beds/transfer_create.html",
                    {
                        "admissions": admissions,
                        "beds": beds,
                        "error":
                        "The selected bed is not available."
                    }
                )

            from_bed = admission.bed

            Transfer.objects.create(
                admission=admission,
                from_bed=from_bed,
                to_bed=to_bed,
                transfer_date=transfer_date,
                reason=reason,
                remarks=remarks,
            )

            from_bed.status = "Available"
            from_bed.save()

            to_bed.status = "Occupied"
            to_bed.save()

            admission.bed = to_bed
            admission.save()

            return redirect("dashboard")

        except Exception as e:

            return render(
                request,
                "beds/transfer_create.html",
                {
                    "admissions": admissions,
                    "beds": beds,
                    "error": str(e),
                }
            )

    return render(
        request,
        "beds/transfer_create.html",
        {
            "admissions": admissions,
            "beds": beds,
        }
    )


# =========================
# DEATH
# =========================

@login_required
def death_create(request):
    require_group(
        request.user,
        "Administrator",
        "Health Information Officer",
        "Records Officer",
    )

    admissions = Admission.objects.filter(
        status="Admitted"
    ).select_related(
        "patient",
        "bed"
    )

    if request.method == "POST":

        admission_id = request.POST.get(
            "admission"
        )

        death_date = request.POST.get(
            "death_date"
        )

        cause_of_death = request.POST.get(
            "cause_of_death"
        )

        remarks = request.POST.get(
            "remarks"
        )

        try:

            admission = Admission.objects.get(
                id=admission_id
            )

            Death.objects.create(
                admission=admission,
                death_date=death_date,
                cause_of_death=cause_of_death,
                remarks=remarks,
            )

            admission.status = "Discharged"
            admission.save()

            bed = admission.bed
            bed.status = "Available"
            bed.save()

            return redirect("dashboard")

        except Exception as e:

            return render(
                request,
                "beds/death_create.html",
                {
                    "admissions": admissions,
                    "error": str(e),
                }
            )

    return render(
        request,
        "beds/death_create.html",
        {
            "admissions": admissions,
        }
    )


# =========================
# REPORTS
# =========================
@login_required
def reports(request):
    require_group(
        request.user,
        "Administrator",
        "Health Information Officer",
        "Matron/Nurse",
        "Records Officer",
        "Doctor",
        "Management",
    )

    today = timezone.localdate()

    # Get selected dates
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    # Default to today
    if not from_date:
        from_date = today.strftime("%Y-%m-%d")

    if not to_date:
        to_date = today.strftime("%Y-%m-%d")

    # Convert dates
    start_date = parse_date(from_date)
    end_date = parse_date(to_date)

    if not start_date:
        start_date = today

    if not end_date:
        end_date = today

    # -------------------------------------------------
    # PATIENT MOVEMENT FOR SELECTED PERIOD
    # -------------------------------------------------

    admissions_count = Admission.objects.filter(
        admission_date__date__range=[
            start_date,
            end_date
        ]
    ).count()

    discharges_count = Discharge.objects.filter(
        discharge_date__date__range=[
            start_date,
            end_date
        ]
    ).count()

    transfers_count = Transfer.objects.filter(
        transfer_date__date__range=[
            start_date,
            end_date
        ]
    ).count()

    deaths_count = Death.objects.filter(
        death_date__date__range=[
            start_date,
            end_date
        ]
    ).count()

    # -------------------------------------------------
    # OVERALL BED STATISTICS
    # -------------------------------------------------

    total_beds = Bed.objects.count()

    occupied_beds = Bed.objects.filter(
        status="Occupied"
    ).count()

    available_beds = Bed.objects.filter(
        status="Available"
    ).count()

    reserved_beds = Bed.objects.filter(
        status="Reserved"
    ).count()

    cleaning_beds = Bed.objects.filter(
        status="Cleaning"
    ).count()

    out_of_service_beds = Bed.objects.filter(
        status="Out of Service"
    ).count()

    # Occupancy rate
    if total_beds:
        occupancy_rate = round(
            (occupied_beds / total_beds) * 100,
            1
        )
    else:
        occupancy_rate = 0

    # -------------------------------------------------
    # WARD STATISTICS
    # -------------------------------------------------

    ward_statistics = []

    for ward in Ward.objects.all().order_by("name"):

        total = Bed.objects.filter(
            ward=ward
        ).count()

        occupied = Bed.objects.filter(
            ward=ward,
            status="Occupied"
        ).count()

        available = Bed.objects.filter(
            ward=ward,
            status="Available"
        ).count()

        reserved = Bed.objects.filter(
            ward=ward,
            status="Reserved"
        ).count()

        cleaning = Bed.objects.filter(
            ward=ward,
            status="Cleaning"
        ).count()

        out_of_service = Bed.objects.filter(
            ward=ward,
            status="Out of Service"
        ).count()

        if total:
            rate = round(
                (occupied / total) * 100,
                1
            )
        else:
            rate = 0

        ward_statistics.append({
            "name": ward.name,
            "total": total,
            "occupied": occupied,
            "available": available,
            "reserved": reserved,
            "cleaning": cleaning,
            "out_of_service": out_of_service,
            "rate": rate,
        })

    # -------------------------------------------------
    # DAILY STATISTICS
    # -------------------------------------------------

    daily_statistics = []

    current_date = start_date

    while current_date <= end_date:

        daily_statistics.append({
            "date": current_date,

            "admissions": Admission.objects.filter(
                admission_date__date=current_date
            ).count(),

            "discharges": Discharge.objects.filter(
                discharge_date__date=current_date
            ).count(),

            "transfers": Transfer.objects.filter(
                transfer_date__date=current_date
            ).count(),

            "deaths": Death.objects.filter(
                death_date__date=current_date
            ).count(),
        })

        current_date += timedelta(days=1)

    # -------------------------------------------------
    # MANAGEMENT SUMMARY
    # -------------------------------------------------

    net_patient_movement = (
        admissions_count
        - discharges_count
    )

    bed_utilization = occupancy_rate

    management_summary = {
        "net_patient_movement": net_patient_movement,

        "bed_utilization": bed_utilization,

        "available_beds": available_beds,

        "occupied_beds": occupied_beds,

        "admissions": admissions_count,

        "discharges": discharges_count,

        "transfers": transfers_count,

        "deaths": deaths_count,
    }

    # -------------------------------------------------
    # CONTEXT
    # -------------------------------------------------

    context = {

        "from_date": from_date,

        "to_date": to_date,

        # Patient movement
        "admissions_count": admissions_count,

        "discharges_count": discharges_count,

        "transfers_count": transfers_count,

        "deaths_count": deaths_count,

        # Bed statistics
        "total_beds": total_beds,

        "occupied_beds": occupied_beds,

        "available_beds": available_beds,

        "reserved_beds": reserved_beds,

        "cleaning_beds": cleaning_beds,

        "out_of_service_beds": out_of_service_beds,

        "occupancy_rate": occupancy_rate,

        # Ward statistics
        "ward_statistics": ward_statistics,

        # Daily statistics
        "daily_statistics": daily_statistics,

        # Management summary
        "management_summary": management_summary,
    }

    return render(
        request,
        "beds/reports.html",
        context
    )
# =========================
# EXCEL REPORT
# =========================

@login_required
def export_excel(request):

    require_group(
        request.user,
        "Administrator",
        "Health Information Officer",
        "Management",
    )

    workbook = Workbook()

    sheet = workbook.active
    sheet.title = "Bed Statistics"

    today = timezone.localdate()

    # Title
    sheet.append(["BEDSTATS HOSPITAL BED STATISTICS"])
    sheet.append([f"Report Date: {today.strftime('%d/%m/%Y')}"])
    sheet.append([])

    # Summary
    sheet.append(["SUMMARY"])
    sheet.append(["Total Beds", Bed.objects.count()])
    sheet.append([
        "Occupied Beds",
        Bed.objects.filter(status="Occupied").count()
    ])
    sheet.append([
        "Available Beds",
        Bed.objects.filter(status="Available").count()
    ])
    sheet.append([
        "Reserved Beds",
        Bed.objects.filter(status="Reserved").count()
    ])
    sheet.append([
        "Cleaning Beds",
        Bed.objects.filter(status="Cleaning").count()
    ])
    sheet.append([
        "Out of Service Beds",
        Bed.objects.filter(
            status="Out of Service"
        ).count()
    ])

    total_beds = Bed.objects.count()
    occupied_beds = Bed.objects.filter(
        status="Occupied"
    ).count()

    if total_beds:
        occupancy_rate = round(
            (occupied_beds / total_beds) * 100,
            1
        )
    else:
        occupancy_rate = 0

    sheet.append([
        "Occupancy Rate",
        f"{occupancy_rate}%"
    ])

    sheet.append([])

    # Ward statistics
    sheet.append(["WARD OCCUPANCY"])
    sheet.append([
        "Ward",
        "Total Beds",
        "Occupied",
        "Available",
        "Reserved",
        "Cleaning",
        "Out of Service",
        "Occupancy Rate",
    ])

    for ward in Ward.objects.all().order_by("name"):

        total = Bed.objects.filter(
            ward=ward
        ).count()

        occupied = Bed.objects.filter(
            ward=ward,
            status="Occupied"
        ).count()

        available = Bed.objects.filter(
            ward=ward,
            status="Available"
        ).count()

        reserved = Bed.objects.filter(
            ward=ward,
            status="Reserved"
        ).count()

        cleaning = Bed.objects.filter(
            ward=ward,
            status="Cleaning"
        ).count()

        out_of_service = Bed.objects.filter(
            ward=ward,
            status="Out of Service"
        ).count()

        if total:
            rate = round(
                (occupied / total) * 100,
                1
            )
        else:
            rate = 0

        sheet.append([
            ward.name,
            total,
            occupied,
            available,
            reserved,
            cleaning,
            out_of_service,
            f"{rate}%",
        ])

    # Adjust column widths
    widths = {
        "A": 30,
        "B": 15,
        "C": 15,
        "D": 15,
        "E": 15,
        "F": 15,
        "G": 20,
        "H": 20,
    }

    for column, width in widths.items():
        sheet.column_dimensions[column].width = width

    # Bold important rows
    for cell in sheet[1]:
        cell.font = Font(bold=True, size=16)

    for cell in sheet[4]:
        cell.font = Font(bold=True)

    # Header row for ward statistics
    for cell in sheet[13]:
        cell.font = Font(bold=True)

    output = BytesIO()

    workbook.save(output)

    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    response["Content-Disposition"] = (
        'attachment; filename="BedStats_Report.xlsx"'
    )

    return response
# =========================
# PDF REPORT
# =========================
@login_required
def export_pdf(request):

    require_group(
        request.user,
        "Administrator",
        "Health Information Officer",
        "Management",
    )

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25,
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    normal_style = styles["Normal"]

    story = []

    today = timezone.localdate()

    # =========================
    # TITLE
    # =========================

    story.append(
        Paragraph(
            "BEDSTATS HOSPITAL",
            title_style
        )
    )

    story.append(
        Paragraph(
            "BED STATISTICS REPORT",
            heading_style
        )
    )

    story.append(
        Paragraph(
            f"Report Date: {today.strftime('%d/%m/%Y')}",
            normal_style
        )
    )

    story.append(Spacer(1, 15))

    # =========================
    # BED SUMMARY
    # =========================

    total_beds = Bed.objects.count()

    occupied_beds = Bed.objects.filter(
        status="Occupied"
    ).count()

    available_beds = Bed.objects.filter(
        status="Available"
    ).count()

    reserved_beds = Bed.objects.filter(
        status="Reserved"
    ).count()

    cleaning_beds = Bed.objects.filter(
        status="Cleaning"
    ).count()

    out_of_service_beds = Bed.objects.filter(
        status="Out of Service"
    ).count()

    if total_beds:
        occupancy_rate = round(
            (occupied_beds / total_beds) * 100,
            1
        )
    else:
        occupancy_rate = 0

    story.append(
        Paragraph(
            "BED STATUS SUMMARY",
            heading_style
        )
    )

    summary_data = [
        ["Indicator", "Number"],
        ["Total Beds", total_beds],
        ["Occupied Beds", occupied_beds],
        ["Available Beds", available_beds],
        ["Reserved Beds", reserved_beds],
        ["Cleaning Beds", cleaning_beds],
        ["Out of Service Beds", out_of_service_beds],
        ["Occupancy Rate", f"{occupancy_rate}%"],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[250, 100]
    )

    summary_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.grey
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black
            ),
            (
                "ALIGN",
                (1, 1),
                (-1, -1),
                "CENTER"
            ),
        ])
    )

    story.append(summary_table)

    story.append(Spacer(1, 20))

    # =========================
    # PATIENT MOVEMENT SUMMARY
    # =========================

    admissions_count = Admission.objects.filter(
        admission_date__date=today
    ).count()

    discharges_count = Discharge.objects.filter(
        discharge_date__date=today
    ).count()

    transfers_count = Transfer.objects.filter(
        transfer_date__date=today
    ).count()

    deaths_count = Death.objects.filter(
        death_date__date=today
    ).count()

    story.append(
        Paragraph(
            "PATIENT MOVEMENT TODAY",
            heading_style
        )
    )

    movement_data = [
        ["Movement", "Number"],
        ["Admissions", admissions_count],
        ["Discharges", discharges_count],
        ["Transfers", transfers_count],
        ["Deaths", deaths_count],
    ]

    movement_table = Table(
        movement_data,
        colWidths=[250, 100]
    )

    movement_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.grey
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black
            ),
            (
                "ALIGN",
                (1, 1),
                (-1, -1),
                "CENTER"
            ),
        ])
    )

    story.append(movement_table)

    story.append(Spacer(1, 20))

    # =========================
    # WARD OCCUPANCY
    # =========================

    story.append(
        Paragraph(
            "WARD OCCUPANCY",
            heading_style
        )
    )

    ward_data = [
        [
            "Ward",
            "Total",
            "Occupied",
            "Available",
            "Reserved",
            "Cleaning",
            "O/S",
            "Rate",
        ]
    ]

    for ward in Ward.objects.all().order_by("name"):

        total = Bed.objects.filter(
            ward=ward
        ).count()

        occupied = Bed.objects.filter(
            ward=ward,
            status="Occupied"
        ).count()

        available = Bed.objects.filter(
            ward=ward,
            status="Available"
        ).count()

        reserved = Bed.objects.filter(
            ward=ward,
            status="Reserved"
        ).count()

        cleaning = Bed.objects.filter(
            ward=ward,
            status="Cleaning"
        ).count()

        out_of_service = Bed.objects.filter(
            ward=ward,
            status="Out of Service"
        ).count()

        if total:
            rate = round(
                (occupied / total) * 100,
                1
            )
        else:
            rate = 0

        ward_data.append([
            escape(str(ward.name)),
            total,
            occupied,
            available,
            reserved,
            cleaning,
            out_of_service,
            f"{rate}%",
        ])

    ward_table = Table(
        ward_data,
        colWidths=[
            110,
            45,
            50,
            50,
            45,
            45,
            45,
            45,
        ],
        repeatRows=1,
    )

    ward_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.grey
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black
            ),
            (
                "ALIGN",
                (1, 1),
                (-1, -1),
                "CENTER"
            ),
        ])
    )

    story.append(ward_table)

    story.append(Spacer(1, 25))

    # =========================
    # FOOTER
    # =========================

    story.append(
        Paragraph(
            "Generated by BedStats Hospital Bed Management System.",
            normal_style
        )
    )

    document.build(story)

    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'attachment; filename="BedStats_Report.pdf"'
    )

    return response
@login_required
def patient_movement(request):

    require_group(
        request.user,
        "Administrator",
        "Health Information Officer",
        "Matron/Nurse",
        "Records Officer",
        "Doctor",
        "Management",
    )

    search = request.GET.get("search", "").strip()
    from_date = request.GET.get("from_date", "")
    to_date = request.GET.get("to_date", "")

    admissions = Admission.objects.select_related(
        "patient",
        "bed",
        "bed__ward"
    ).order_by("-admission_date")

    transfers = Transfer.objects.select_related(
        "admission",
        "admission__patient",
        "from_bed",
        "from_bed__ward",
        "to_bed",
        "to_bed__ward",
    ).order_by("-transfer_date")

    discharges = Discharge.objects.select_related(
        "admission",
        "admission__patient",
        "admission__bed",
        "admission__bed__ward",
    ).order_by("-discharge_date")

    deaths = Death.objects.select_related(
        "admission",
        "admission__patient",
        "admission__bed",
        "admission__bed__ward",
    ).order_by("-death_date")


    # SEARCH
    if search:

        search_filter = (
            Q(patient__patient_number__icontains=search)
            | Q(patient__first_name__icontains=search)
            | Q(patient__last_name__icontains=search)
        )

        admissions = admissions.filter(search_filter)

        transfers = transfers.filter(
            Q(admission__patient__patient_number__icontains=search)
            | Q(admission__patient__first_name__icontains=search)
            | Q(admission__patient__last_name__icontains=search)
        )

        discharges = discharges.filter(
            Q(admission__patient__patient_number__icontains=search)
            | Q(admission__patient__first_name__icontains=search)
            | Q(admission__patient__last_name__icontains=search)
        )

        deaths = deaths.filter(
            Q(admission__patient__patient_number__icontains=search)
            | Q(admission__patient__first_name__icontains=search)
            | Q(admission__patient__last_name__icontains=search)
        )


    # DATE FILTER
    if from_date:

        admissions = admissions.filter(
            admission_date__date__gte=from_date
        )

        transfers = transfers.filter(
            transfer_date__date__gte=from_date
        )

        discharges = discharges.filter(
            discharge_date__date__gte=from_date
        )

        deaths = deaths.filter(
            death_date__date__gte=from_date
        )


    if to_date:

        admissions = admissions.filter(
            admission_date__date__lte=to_date
        )

        transfers = transfers.filter(
            transfer_date__date__lte=to_date
        )

        discharges = discharges.filter(
            discharge_date__date__lte=to_date
        )

        deaths = deaths.filter(
            death_date__date__lte=to_date
        )


    # COMBINE ALL MOVEMENTS
    movements = []


    # ADMISSIONS
    for admission in admissions:

        movements.append({

            "date": admission.admission_date,

            "patient_id": admission.patient.id,

            "patient_number":
                admission.patient.patient_number,

            "patient_name":
                f"{admission.patient.first_name} "
                f"{admission.patient.last_name}",

            "movement": "ADMISSION",

            "from_ward": "-",

            "from_bed": "-",

            "to_ward":
                admission.bed.ward.name,

            "to_bed":
                admission.bed.bed_number,

            "details":
                admission.diagnosis,

        })


    # TRANSFERS
    for transfer in transfers:

        movements.append({

            "date": transfer.transfer_date,

            "patient_id":
                transfer.admission.patient.id,

            "patient_number":
                transfer.admission.patient.patient_number,

            "patient_name":
                f"{transfer.admission.patient.first_name} "
                f"{transfer.admission.patient.last_name}",

            "movement": "TRANSFER",

            "from_ward":
                transfer.from_bed.ward.name,

            "from_bed":
                transfer.from_bed.bed_number,

            "to_ward":
                transfer.to_bed.ward.name,

            "to_bed":
                transfer.to_bed.bed_number,

            "details":
                transfer.reason,

        })


    # DISCHARGES
    for discharge in discharges:

        movements.append({

            "date": discharge.discharge_date,

            "patient_id":
                discharge.admission.patient.id,

            "patient_number":
                discharge.admission.patient.patient_number,

            "patient_name":
                f"{discharge.admission.patient.first_name} "
                f"{discharge.admission.patient.last_name}",

            "movement": "DISCHARGE",

            "from_ward":
                discharge.admission.bed.ward.name,

            "from_bed":
                discharge.admission.bed.bed_number,

            "to_ward": "-",

            "to_bed": "-",

            "details":
                discharge.discharge_reason,

        })


    # DEATHS
    for death in deaths:

        movements.append({

            "date": death.death_date,

            "patient_id":
                death.admission.patient.id,

            "patient_number":
                death.admission.patient.patient_number,

            "patient_name":
                f"{death.admission.patient.first_name} "
                f"{death.admission.patient.last_name}",

            "movement": "DEATH",

            "from_ward":
                death.admission.bed.ward.name,

            "from_bed":
                death.admission.bed.bed_number,

            "to_ward": "-",

            "to_bed": "-",

            "details":
                death.cause_of_death,

        })


    # SORT BY DATE
    movements.sort(
        key=lambda item: item["date"],
        reverse=True
    )


    context = {

        "movements": movements,

        "search": search,

        "from_date": from_date,

        "to_date": to_date,

    }


    return render(
        request,
        "beds/patient_movement.html",
        context
    )
def custom_permission_denied(request, exception):
    _ = exception

    return render(
        request,
        "403.html",
        status=403
    )