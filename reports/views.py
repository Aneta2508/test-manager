from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from test_cases.models import Project, TestCase
from defects.models import Defect
import datetime
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Czcionka z polskimi znakami
pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))

# Kolory lawendowe spójne z aplikacją
LAVENDER = colors.HexColor('#7C6FAD')
LAVENDER_LIGHT = colors.HexColor('#EDE9FF')
LAVENDER_DARK = colors.HexColor('#4A3F7A')
SUCCESS_COLOR = colors.HexColor('#2D6A4F')
SUCCESS_BG = colors.HexColor('#D4F4DD')
FAIL_COLOR = colors.HexColor('#8B2020')
FAIL_BG = colors.HexColor('#FFE0E0')
WARNING_COLOR = colors.HexColor('#8B6914')
WARNING_BG = colors.HexColor('#FFF3CC')
GRAY = colors.HexColor('#9B93C4')
DARK = colors.HexColor('#4A3F7A')

def report_list(request):
    projects = Project.objects.all()
    return render(request, 'reports/report_list.html', {'projects': projects})

def generate_report(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="raport_{project.project_number}.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    story = []

    # Style
    title_style = ParagraphStyle('Title', parent=styles['Normal'],
        fontSize=28, textColor=LAVENDER_DARK, alignment=TA_CENTER, spaceAfter=10, fontName='DejaVuSans-Bold')
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'],
        fontSize=14, textColor=LAVENDER, alignment=TA_CENTER, spaceAfter=6)
    heading_style = ParagraphStyle('Heading', parent=styles['Normal'],
        fontSize=14, textColor=LAVENDER_DARK, spaceBefore=16, spaceAfter=8, fontName='DejaVuSans-Bold')
    normal_style = ParagraphStyle('Normal2', parent=styles['Normal'],
        fontSize=10, textColor=DARK, spaceAfter=4)
    small_style = ParagraphStyle('Small', parent=styles['Normal'],
        fontSize=9, textColor=GRAY, spaceAfter=4, fontName='DejaVuSans')
    center_style = ParagraphStyle('Center', parent=styles['Normal'],
        fontSize=10, textColor=DARK, alignment=TA_CENTER)

    # ============================================================
    # STRONA 1 — TYTUŁOWA
    # ============================================================
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("RAPORT Z TESTÓW", title_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=LAVENDER))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"{project.project_number}", subtitle_style))
    story.append(Paragraph(f"{project.name}", subtitle_style))
    story.append(Spacer(1, 1*cm))

    # Data wygenerowania
    story.append(Paragraph(f"Data wygenerowania: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}", center_style))
    story.append(Paragraph(f"Status projektu: {project.get_status_display()}", center_style))
    if project.deadline:
        story.append(Paragraph(f"Termin projektu: {project.deadline.strftime('%d.%m.%Y')}", center_style))
    story.append(Spacer(1, 1.5*cm))

    # Osoby zaangażowane
    contacts = project.contacts.all()
    if contacts:
        story.append(Paragraph("Osoby zaangażowane:", heading_style))
        contact_data = [['Imię i nazwisko', 'Rola', 'Email']]
        for contact in contacts:
            contact_data.append([contact.full_name, contact.get_role_display(), contact.email])

        contact_table = Table(contact_data, colWidths=[5*cm, 4*cm, 7*cm])
        contact_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), LAVENDER),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LAVENDER_LIGHT]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDD8F5')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(contact_table)

    # Nowa strona
    from reportlab.platypus import PageBreak
    story.append(PageBreak())

    # ============================================================
    # STRONA 2 — PODSUMOWANIE
    # ============================================================
    story.append(Paragraph("PODSUMOWANIE", heading_style))
    story.append(HRFlowable(width="100%", thickness=1, color=LAVENDER))
    story.append(Spacer(1, 0.5*cm))

    # Statystyki
    all_cases = TestCase.objects.filter(test_plan__project=project)
    total = all_cases.count()
    passed = all_cases.filter(status='PASS').count()
    failed = all_cases.filter(status='FAIL').count()
    ongoing = all_cases.filter(status='ONGOING').count()
    blocked = all_cases.filter(status='BLOCKED').count()
    not_started = all_cases.filter(status='NOT_STARTED').count()
    progress = round((passed / total * 100)) if total > 0 else 0

    stats_data = [
        ['Łączna liczba przypadków testowych', str(total)],
        ['PASS', str(passed)],
        ['FAIL', str(failed)],
        ['ONGOING', str(ongoing)],
        ['BLOCKED', str(blocked)],
        ['NOT STARTED', str(not_started)],
        ['Pokrycie testowe (% PASS)', f'{progress}%'],
    ]

    stats_table = Table(stats_data, colWidths=[12*cm, 4*cm])
    stats_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), DARK),
        ('TEXTCOLOR', (1, 0), (1, -1), DARK),
        ('FONTNAME', (0, 6), (-1, 6), 'DejaVuSans-Bold'),
        ('TEXTCOLOR', (1, 6), (1, 6), LAVENDER),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, LAVENDER_LIGHT]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDD8F5')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 0.5*cm))

    # Defekty według wagi
    all_defects = Defect.objects.filter(test_case__test_plan__project=project)
    critical = all_defects.filter(severity='CRITICAL').count()
    major = all_defects.filter(severity='MAJOR').count()
    medium = all_defects.filter(severity='MEDIUM').count()
    minor = all_defects.filter(severity='MINOR').count()

    story.append(Paragraph("Defekty według wagi:", heading_style))
    defect_stats_data = [
        ['Waga', 'Liczba'],
        ['CRITICAL', str(critical)],
        ['MAJOR', str(major)],
        ['MEDIUM', str(medium)],
        ['MINOR', str(minor)],
        ['ŁĄCZNIE', str(all_defects.count())],
    ]

    defect_stats_table = Table(defect_stats_data, colWidths=[12*cm, 4*cm])
    defect_stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), LAVENDER),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 5), (-1, 5), 'DejaVuSans-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LAVENDER_LIGHT]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDD8F5')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(defect_stats_table)
    story.append(PageBreak())

    # ============================================================
    # STRONA 3+ — WYNIKI TESTÓW
    # ============================================================
    story.append(Paragraph("WYNIKI TESTÓW", heading_style))
    story.append(HRFlowable(width="100%", thickness=1, color=LAVENDER))

    test_plans = project.test_plans.all()
    for plan in test_plans:
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(f"Plan testów: {plan.name}", heading_style))
        if plan.description:
            story.append(Paragraph(plan.description, small_style))

        cases = plan.test_cases.all()
        if cases:
            case_data = [['ID', 'Nazwa', 'Priorytet', 'Status', 'Środowisko', 'Data']]
            for tc in cases:
                case_data.append([
                    tc.test_id,
                    tc.name[:40] + '...' if len(tc.name) > 40 else tc.name,
                    tc.priority,
                    tc.status,
                    tc.environment[:20] if tc.environment else '—',
                    tc.executed_at.strftime('%d.%m.%Y') if tc.executed_at else '—'
                ])

            case_table = Table(case_data, colWidths=[1.5*cm, 5.5*cm, 2*cm, 2.5*cm, 3*cm, 2*cm])
            case_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), LAVENDER),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LAVENDER_LIGHT]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDD8F5')),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(case_table)
        else:
            story.append(Paragraph("Brak przypadków testowych w tym planie.", small_style))

    story.append(PageBreak())

    # ============================================================
    # OSTATNIA STRONA — DEFEKTY + WNIOSKI
    # ============================================================
    story.append(Paragraph("DEFEKTY", heading_style))
    story.append(HRFlowable(width="100%", thickness=1, color=LAVENDER))
    story.append(Spacer(1, 0.3*cm))

    if all_defects:
        defect_data = [['Nazwa', 'Waga', 'Status', 'Przypadek testowy', 'Data']]
        for defect in all_defects:
            defect_data.append([
                defect.name[:35] + '...' if len(defect.name) > 35 else defect.name,
                defect.severity,
                defect.status,
                defect.test_case.test_id,
                defect.reported_at.strftime('%d.%m.%Y')
            ])

        defect_table = Table(defect_data, colWidths=[5.5*cm, 2.5*cm, 2.5*cm, 3*cm, 2.5*cm])
        defect_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), LAVENDER),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LAVENDER_LIGHT]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDD8F5')),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(defect_table)
    else:
        story.append(Paragraph("Nie zgłoszono żadnych defektów.", small_style))

    story.append(Spacer(1, 1*cm))

    # Wnioski i rekomendacje
    story.append(Paragraph("WNIOSKI I REKOMENDACJE", heading_style))
    story.append(HRFlowable(width="100%", thickness=1, color=LAVENDER))
    story.append(Spacer(1, 0.3*cm))

    if critical > 0:
        story.append(Paragraph(
            f"⚠️ BLOKADA WDROŻENIA: Wykryto {critical} defekt(ów) o wadze CRITICAL. "
            f"Projekt nie jest gotowy do wdrożenia. Wymagane natychmiastowe działania naprawcze.",
            ParagraphStyle('Warning', parent=styles['Normal'], fontSize=10,
                textColor=FAIL_COLOR, spaceAfter=8, fontName='DejaVuSans-Bold')
        ))
    elif major > 0:
        story.append(Paragraph(
            f"⚠️ UWAGA: Wykryto {major} defekt(ów) o wadze MAJOR. "
            f"Zalecane jest naprawienie tych defektów przed wdrożeniem.",
            ParagraphStyle('Warning', parent=styles['Normal'], fontSize=10,
                textColor=WARNING_COLOR, spaceAfter=8, fontName='DejaVuSans-Bold')
        ))
    elif failed > 0:
        story.append(Paragraph(
            f"Wykryto {failed} nieudanych przypadków testowych. "
            f"Zalecana analiza i retesty przed wdrożeniem.",
            normal_style
        ))
    else:
        story.append(Paragraph(
            f"✓ Wszystkie wykonane przypadki testowe zakończone pomyślnie. "
            f"Projekt gotowy do wdrożenia.",
            ParagraphStyle('Success', parent=styles['Normal'], fontSize=10,
                textColor=SUCCESS_COLOR, spaceAfter=8, fontName='DejaVuSans-Bold')
        ))

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"Raport wygenerowany automatycznie przez Test Manager — {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}", small_style))

    doc.build(story)
    return response