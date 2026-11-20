from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Image
)
from test_cases.models import Project, TestCase
from defects.models import Defect
import datetime

# Czcionka z obsługą polskich znaków
pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))

# Kolory spójne z aplikacją
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
BORDER = colors.HexColor('#DDD8F5')

# Tło pola "Status" w karcie przypadku testowego
STATUS_BG = {
    'PASS': SUCCESS_BG,
    'FAIL': FAIL_BG,
    'BLOCKED': FAIL_BG,
    'ONGOING': WARNING_BG,
    'NOT_STARTED': LAVENDER_LIGHT,
}

# Kolejność sortowania defektów: najpoważniejsze na początku
SEVERITY_ORDER = {'CRITICAL': 0, 'MAJOR': 1, 'MEDIUM': 2, 'MINOR': 3}

# Tło pola "Waga" i "Status" w karcie defektu
SEVERITY_BG = {
    'CRITICAL': FAIL_BG,
    'MAJOR': FAIL_BG,
    'MEDIUM': WARNING_BG,
    'MINOR': SUCCESS_BG,
}
DEFECT_STATUS_BG = {
    'NEW': LAVENDER_LIGHT,
    'IN_PROGRESS': WARNING_BG,
    'RESOLVED': SUCCESS_BG,
    'CLOSED': LAVENDER_LIGHT,
}

# Style tekstu
styles = getSampleStyleSheet()
title_style = ParagraphStyle('ReportTitle', parent=styles['Normal'], fontName='DejaVuSans-Bold',
    fontSize=28, leading=34, textColor=LAVENDER_DARK, alignment=TA_CENTER, spaceAfter=10)
subtitle_style = ParagraphStyle('ReportSubtitle', parent=styles['Normal'], fontName='DejaVuSans',
    fontSize=14, leading=18, textColor=LAVENDER, alignment=TA_CENTER, spaceAfter=6)
heading_style = ParagraphStyle('ReportHeading', parent=styles['Normal'], fontName='DejaVuSans-Bold',
    fontSize=14, leading=18, textColor=LAVENDER_DARK, spaceBefore=16, spaceAfter=8)
normal_style = ParagraphStyle('ReportNormal', parent=styles['Normal'], fontName='DejaVuSans',
    fontSize=10, leading=14, textColor=DARK, spaceAfter=4)
small_style = ParagraphStyle('ReportSmall', parent=styles['Normal'], fontName='DejaVuSans',
    fontSize=9, leading=12, textColor=GRAY, spaceAfter=4)
center_style = ParagraphStyle('ReportCenter', parent=styles['Normal'], fontName='DejaVuSans',
    fontSize=10, leading=14, textColor=DARK, alignment=TA_CENTER)
label_style = ParagraphStyle('ReportLabel', parent=styles['Normal'], fontName='DejaVuSans-Bold',
    fontSize=8, leading=10, textColor=LAVENDER_DARK)
value_style = ParagraphStyle('ReportValue', parent=styles['Normal'], fontName='DejaVuSans',
    fontSize=9, leading=12, textColor=DARK)
card_title_style = ParagraphStyle('ReportCardTitle', parent=styles['Normal'], fontName='DejaVuSans-Bold',
    fontSize=10, leading=13, textColor=colors.white)


def text(value):
    """Zamienia tekst z bazy na bezpieczny tekst dla Paragraph:
    escapuje znaki specjalne (&, <, >) i zachowuje nowe linie."""
    if not value:
        return '—'
    return escape(str(value)).replace('\r', '').replace('\n', '<br/>')


def key_value_table(rows):
    """Tabela dwukolumnowa: etykieta po lewej, wartość po prawej."""
    table = Table(rows, colWidths=[4.5*cm, 12.5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), LAVENDER_LIGHT),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    return table


def screenshot_flowable(test_case):
    """Zrzut ekranu skalowany do rozsądnego rozmiaru; w razie błędu zwraca komunikat."""
    try:
        path = test_case.screenshot.path
        width, height = ImageReader(path).getSize()
        scale = min(10*cm / width, 7*cm / height, 1)
        return Image(path, width=width * scale, height=height * scale)
    except Exception:
        return Paragraph('Nie udało się wczytać zrzutu ekranu.', value_style)


def test_case_card(tc):
    """Karta ze wszystkimi danymi jednego przypadku testowego."""
    executed = tc.executed_at.strftime('%d.%m.%Y') if tc.executed_at else None
    rows = [
        [Paragraph(f'{escape(tc.test_id)} — {escape(tc.name)}', card_title_style), ''],
        [Paragraph('Opis', label_style), Paragraph(text(tc.description), value_style)],
        [Paragraph('Warunki wstępne', label_style), Paragraph(text(tc.preconditions), value_style)],
        [Paragraph('Kroki testowe', label_style), Paragraph(text(tc.steps), value_style)],
        [Paragraph('Oczekiwany rezultat', label_style), Paragraph(text(tc.expected_result), value_style)],
        [Paragraph('Priorytet', label_style), Paragraph(text(tc.priority), value_style)],
        [Paragraph('Status', label_style), Paragraph(text(tc.status.replace('_', ' ')), value_style)],
        [Paragraph('Komentarz', label_style), Paragraph(text(tc.comment), value_style)],
        [Paragraph('Data wykonania', label_style), Paragraph(text(executed), value_style)],
        [Paragraph('Środowisko', label_style), Paragraph(text(tc.environment), value_style)],
    ]
    if tc.screenshot:
        rows.append([Paragraph('Zrzut ekranu', label_style), screenshot_flowable(tc)])

    table = Table(rows, colWidths=[4.5*cm, 12.5*cm], repeatRows=1)
    table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('BACKGROUND', (0, 0), (1, 0), LAVENDER),
        ('BACKGROUND', (0, 1), (0, -1), LAVENDER_LIGHT),
        ('BACKGROUND', (1, 6), (1, 6), STATUS_BG.get(tc.status, colors.white)),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    return table


def defect_card(defect):
    """Karta ze wszystkimi danymi jednego defektu (jak w zakładce Defekty)."""
    project = defect.test_case.test_plan.project
    rows = [
        [Paragraph(escape(defect.name), card_title_style), ''],
        [Paragraph('Projekt', label_style),
         Paragraph(f'{escape(project.project_number)} — {escape(project.name)}', value_style)],
        [Paragraph('Przypadek testowy', label_style),
         Paragraph(f'{escape(defect.test_case.test_id)} — {escape(defect.test_case.name)}', value_style)],
        [Paragraph('Waga', label_style), Paragraph(text(defect.severity), value_style)],
        [Paragraph('Status', label_style), Paragraph(text(defect.status.replace('_', ' ')), value_style)],
        [Paragraph('Opis', label_style), Paragraph(text(defect.description), value_style)],
        [Paragraph('Data zgłoszenia', label_style),
         Paragraph(defect.reported_at.strftime('%d.%m.%Y %H:%M'), value_style)],
    ]

    table = Table(rows, colWidths=[4.5*cm, 12.5*cm], repeatRows=1)
    table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('BACKGROUND', (0, 0), (1, 0), LAVENDER),
        ('BACKGROUND', (0, 1), (0, -1), LAVENDER_LIGHT),
        ('BACKGROUND', (1, 3), (1, 3), SEVERITY_BG.get(defect.severity, colors.white)),
        ('BACKGROUND', (1, 4), (1, 4), DEFECT_STATUS_BG.get(defect.status, colors.white)),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    return table


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

    story = []
    test_plans = project.test_plans.all()
    all_cases = TestCase.objects.filter(test_plan__project=project)
    all_defects = Defect.objects.filter(test_case__test_plan__project=project)

    # ============================================================
    # STRONA 1 — TYTUŁOWA
    # ============================================================
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("TEST RAPORT", title_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=LAVENDER))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(escape(project.project_number), subtitle_style))
    story.append(Paragraph(escape(project.name), subtitle_style))
    story.append(Spacer(1, 1.5*cm))

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
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(contact_table)

    # Data, status i termin — pod tabelą z osobami
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Data wygenerowania: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}", center_style))
    story.append(Paragraph(f"Status projektu: {project.get_status_display()}", center_style))
    if project.deadline:
        story.append(Paragraph(f"Termin projektu: {project.deadline.strftime('%d.%m.%Y')}", center_style))

    story.append(PageBreak())

    # ============================================================
    # STRONA 2 — INFORMACJE O PROJEKCIE + PODSUMOWANIE
    # ============================================================
    story.append(Paragraph("INFORMACJE O PROJEKCIE", heading_style))
    story.append(HRFlowable(width="100%", thickness=1, color=LAVENDER))
    story.append(Spacer(1, 0.4*cm))

    deadline_text = project.deadline.strftime('%d.%m.%Y') if project.deadline else None
    info_rows = [
        [Paragraph('Numer projektu', label_style), Paragraph(text(project.project_number), value_style)],
        [Paragraph('Nazwa projektu', label_style), Paragraph(text(project.name), value_style)],
        [Paragraph('Opis', label_style), Paragraph(text(project.description), value_style)],
        [Paragraph('Status', label_style), Paragraph(text(project.get_status_display()), value_style)],
        [Paragraph('Termin', label_style), Paragraph(text(deadline_text), value_style)],
        [Paragraph('Data utworzenia', label_style), Paragraph(project.created_at.strftime('%d.%m.%Y %H:%M'), value_style)],
        [Paragraph('Liczba planów testów', label_style), Paragraph(str(test_plans.count()), value_style)],
        [Paragraph('Liczba przypadków testowych', label_style), Paragraph(str(all_cases.count()), value_style)],
    ]
    story.append(key_value_table(info_rows))

    story.append(Paragraph("PODSUMOWANIE", heading_style))
    story.append(HRFlowable(width="100%", thickness=1, color=LAVENDER))
    story.append(Spacer(1, 0.4*cm))

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
    stats_table = Table(stats_data, colWidths=[13*cm, 4*cm])
    stats_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTNAME', (0, 6), (-1, 6), 'DejaVuSans-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), DARK),
        ('TEXTCOLOR', (1, 6), (1, 6), LAVENDER),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, LAVENDER_LIGHT]),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(stats_table)
    story.append(PageBreak())

    # ============================================================
    # STRONA 3+ — WYNIKI PRZEPROWADZONYCH TESTÓW
    # ============================================================
    story.append(Paragraph("WYNIKI PRZEPROWADZONYCH TESTÓW", heading_style))
    story.append(HRFlowable(width="100%", thickness=1, color=LAVENDER))

    for plan in test_plans:
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(f"Plan testów: {escape(plan.name)}", heading_style))
        if plan.description:
            story.append(Paragraph(text(plan.description), small_style))

        cases = plan.test_cases.all()
        story.append(Paragraph(f"Liczba przypadków testowych w planie: {cases.count()}", small_style))
        story.append(Spacer(1, 0.2*cm))

        if cases:
            for tc in cases:
                story.append(test_case_card(tc))
                story.append(Spacer(1, 0.4*cm))
        else:
            story.append(Paragraph("Brak przypadków testowych w tym planie.", small_style))

    story.append(PageBreak())

    # ============================================================
    # OSTATNIA STRONA — DEFEKTY + WNIOSKI
    # ============================================================
    story.append(Paragraph("DEFEKTY", heading_style))
    story.append(HRFlowable(width="100%", thickness=1, color=LAVENDER))
    story.append(Spacer(1, 0.3*cm))

    critical = all_defects.filter(severity='CRITICAL').count()
    major = all_defects.filter(severity='MAJOR').count()
    medium = all_defects.filter(severity='MEDIUM').count()
    minor = all_defects.filter(severity='MINOR').count()

    story.append(Paragraph("Wykryte defekty posortowane według wagi", heading_style))
    defect_stats_data = [
        ['Waga', 'Liczba'],
        ['CRITICAL', str(critical)],
        ['MAJOR', str(major)],
        ['MEDIUM', str(medium)],
        ['MINOR', str(minor)],
        ['ŁĄCZNIE', str(all_defects.count())],
    ]
    defect_stats_table = Table(defect_stats_data, colWidths=[13*cm, 4*cm])
    defect_stats_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 5), (-1, 5), 'DejaVuSans-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), DARK),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, LAVENDER_LIGHT]),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(defect_stats_table)

    story.append(Paragraph("Szczegóły defektów", heading_style))
    # sorted() jest stabilne: w obrębie jednej wagi zostaje kolejność od najnowszego
    sorted_defects = sorted(
        all_defects.select_related('test_case__test_plan__project'),
        key=lambda d: SEVERITY_ORDER.get(d.severity, 99)
    )
    if sorted_defects:
        for defect in sorted_defects:
            story.append(defect_card(defect))
            story.append(Spacer(1, 0.4*cm))
    else:
        story.append(Paragraph("Nie zgłoszono żadnych defektów.", small_style))

    story.append(Spacer(1, 0.6*cm))
    story.append(Paragraph("WNIOSKI I REKOMENDACJE", heading_style))
    story.append(HRFlowable(width="100%", thickness=1, color=LAVENDER))
    story.append(Spacer(1, 0.3*cm))

    if critical > 0:
        story.append(Paragraph(
            f"⚠️ BLOKADA WDROŻENIA: Wykryto {critical} defekt(ów) o wadze CRITICAL. "
            f"Projekt nie jest gotowy do wdrożenia. Wymagane natychmiastowe działania naprawcze.",
            ParagraphStyle('Warning', parent=normal_style, textColor=FAIL_COLOR, fontName='DejaVuSans-Bold')
        ))
    elif major > 0:
        story.append(Paragraph(
            f"⚠️ UWAGA: Wykryto {major} defekt(ów) o wadze MAJOR. "
            f"Zalecane jest naprawienie tych defektów przed wdrożeniem.",
            ParagraphStyle('Warning', parent=normal_style, textColor=WARNING_COLOR, fontName='DejaVuSans-Bold')
        ))
    elif failed > 0:
        story.append(Paragraph(
            f"Wykryto {failed} nieudanych przypadków testowych. "
            f"Zalecana analiza i retesty przed wdrożeniem.",
            normal_style
        ))
    else:
        story.append(Paragraph(
            "✓ Wszystkie wykonane przypadki testowe zakończone pomyślnie. "
            "Projekt gotowy do wdrożenia.",
            ParagraphStyle('Success', parent=normal_style, textColor=SUCCESS_COLOR, fontName='DejaVuSans-Bold')
        ))

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        f"Raport wygenerowany automatycznie przez Test Manager — {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}",
        small_style
    ))

    doc.build(story)
    return response