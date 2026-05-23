# Payslip Generator System — Implementation Plan

## Goal

Build a professional **Payroll Document Automation System** focused on:

```
Generate → Store → Send Payslips Reliably
```

**Not** an ERP/HRMS/Attendance system. A focused MVP for payslip generation, storage, and WhatsApp delivery.

---

## User Review Required

> [!IMPORTANT]
> **PostgreSQL**: The plan assumes PostgreSQL is already installed and accessible locally. If not, should we use SQLite for initial development and switch to PostgreSQL later?

> [!IMPORTANT]
> **Redis**: Celery requires Redis as a message broker. Is Redis installed locally, or should we plan for installation? On Windows, Redis can run via WSL or Docker. Alternatively, we could start with `django-rq` or a simpler queue initially.

> [!IMPORTANT]
> **TailwindCSS**: The plan uses **TailwindCSS v4** via **`django-tailwind-cli`** (no Node.js required — uses standalone Tailwind CLI binary). This is the modern recommended approach. Please confirm this is acceptable.

> [!IMPORTANT]
> **WhatsApp API**: Meta WhatsApp Cloud API requires a **Meta Business Account**, a **WhatsApp Business App**, and an **approved message template** for sending documents. Do you already have these credentials, or should the WhatsApp module be built as a placeholder with mock sending initially?

> [!WARNING]
> **WeasyPrint on Windows (v68.1)**: WeasyPrint requires **MSYS2 + Pango** on Windows. Installation steps: (1) Install MSYS2 from msys2.org, (2) Run `pacman -S mingw-w64-x86_64-pango` in MSYS2 shell, (3) Set `WEASYPRINT_DLL_DIRECTORIES=C:\msys64\mingw64\bin`. An alternative is `xhtml2pdf` which is pure Python but produces lower quality PDFs. Which do you prefer?

---

## Open Questions

1. **Company branding**: Do you have a company logo and specific brand colors for the PDF payslip template, or should I design a professional generic template?
2. **Authentication**: Should the admin dashboard use Django's built-in auth with a login page, or is there a specific auth requirement?
3. **Multi-company support**: Is this for a single company, or should the system support multiple company profiles from the start?
4. **PDF template**: Should the payslip PDF follow a specific format (e.g., a sample you have), or should I design one?
5. **Deployment target**: Where will this be deployed? (Heroku, AWS, VPS, local server?)

---

## Tech Stack (Final)

| Layer | Technology | Version | Notes |
|-------|-----------|---------|-------|
| Backend | Django | 5.1+ | |
| API | Django REST Framework | 3.15+ | |
| Database | PostgreSQL | 15+ (or SQLite for dev) | |
| Async | Celery | 5.6.3 | `--pool=solo` on Windows dev |
| Broker | Redis | 7+ | Via WSL or Docker on Windows |
| PDF | WeasyPrint | 68.1 | Requires MSYS2 + Pango on Windows |
| Frontend | Django Templates + HTMX | HTMX 2.0.x | CDN or static file |
| Styling | TailwindCSS | v4.x | Via `django-tailwind-cli` (no Node.js) |
| Excel | openpyxl | 3.1+ | Row-by-row processing with error tracking |
| Task monitoring | django-celery-results | 2.5+ | |

---

## Project Structure

```
payslip_generator/
│
├── config/                          # Django project settings
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                  # Shared settings
│   │   ├── development.py           # Dev overrides
│   │   └── production.py            # Prod overrides
│   ├── urls.py                      # Root URL config
│   ├── celery.py                    # Celery app config
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── core/                        # Shared utilities, base models
│   │   ├── models.py                # TimeStampedModel base
│   │   ├── utils.py
│   │   └── templatetags/
│   │       └── core_tags.py         # Custom template filters
│   │
│   ├── employees/                   # Employee CRUD
│   │   ├── models.py                # Employee model
│   │   ├── views.py                 # CRUD views
│   │   ├── forms.py                 # Employee forms
│   │   ├── urls.py
│   │   ├── serializers.py           # DRF serializers
│   │   └── api_views.py             # DRF viewsets
│   │
│   ├── configs/                     # Salary rules & system config
│   │   ├── models.py                # SalaryComponent, SystemConfig
│   │   ├── views.py                 # Config management views
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── services.py              # Config lookup service
│   │
│   ├── payroll/                     # Payroll engine (core logic)
│   │   ├── models.py                # Payslip, PayslipItem, EmployeeSalaryStructure
│   │   ├── engine.py                # ★ Payroll calculation engine
│   │   ├── views.py                 # Manual generation views
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── serializers.py
│   │   ├── api_views.py
│   │   └── tasks.py                 # Celery tasks for generation
│   │
│   ├── pdf_generator/               # PDF generation service
│   │   ├── generator.py             # WeasyPrint PDF generation
│   │   └── utils.py
│   │
│   ├── bulk_upload/                 # Excel upload & processing
│   │   ├── models.py                # BulkUpload, BulkUploadRow
│   │   ├── views.py                 # Upload views
│   │   ├── parser.py                # Excel parser & validator
│   │   ├── urls.py
│   │   └── tasks.py                 # Celery tasks for bulk processing
│   │
│   └── whatsapp/                    # WhatsApp delivery
│       ├── models.py                # WhatsAppMessage log (optional)
│       ├── sender.py                # Meta Cloud API client
│       ├── views.py
│       ├── urls.py
│       └── tasks.py                 # Async sending tasks
│
├── templates/
│   ├── base.html                    # Master layout (sidebar, nav)
│   ├── components/                  # Reusable HTMX partials
│   │   ├── _sidebar.html
│   │   ├── _topbar.html
│   │   ├── _modal.html
│   │   ├── _table.html
│   │   ├── _pagination.html
│   │   └── _toast.html
│   ├── dashboard/
│   │   └── index.html
│   ├── employees/
│   │   ├── list.html
│   │   ├── create.html
│   │   ├── edit.html
│   │   └── partials/
│   │       └── _employee_row.html
│   ├── configs/
│   │   ├── salary_components.html
│   │   └── system_settings.html
│   ├── payroll/
│   │   ├── generate.html
│   │   ├── preview.html
│   │   ├── history.html
│   │   └── partials/
│   │       └── _payslip_row.html
│   ├── bulk_upload/
│   │   ├── upload.html
│   │   ├── status.html
│   │   └── partials/
│   │       └── _upload_progress.html
│   └── pdf/
│       └── payslip_template.html    # HTML template for PDF rendering
│
├── static/
│   ├── css/
│   │   └── input.css                # TailwindCSS input
│   ├── js/
│   │   └── app.js                   # HTMX config, Alpine.js utils
│   └── images/
│       └── logo.png
│
├── media/
│   ├── payslips/                    # Generated PDF storage
│   └── uploads/                     # Uploaded Excel files
│
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
│
├── manage.py
├── .env.example
├── .gitignore
└── README.md
```

---

## Proposed Changes

### Phase 1: Foundation & Setup

#### [NEW] `config/` — Django Project Configuration

- **`settings/base.py`**: Core Django settings with installed apps, middleware, database config, media/static roots, Celery config, and custom auth settings.
- **`settings/development.py`**: DEBUG=True, SQLite fallback, CORS open.
- **`settings/production.py`**: Security hardening, PostgreSQL, Redis.
- **`celery.py`**: Celery app initialization with autodiscover.
- **`urls.py`**: Root URL router including all app URLs and API endpoints.

#### [NEW] `apps/core/` — Shared Utilities

- **`models.py`**: `TimeStampedModel` abstract base with `created_at` and `updated_at` fields.
- **`utils.py`**: Shared helpers (currency formatting, date utils).
- **`templatetags/core_tags.py`**: Custom template filters for currency formatting, status badges.

#### [NEW] `templates/base.html` — Master Layout

- Responsive sidebar dashboard layout using TailwindCSS.
- Top navigation bar with breadcrumbs.
- HTMX integration (`hx-boost`, `hx-target`).
- Toast notification system.
- Dark/light mode support.

#### [NEW] `requirements/base.txt`

```
Django>=5.1
djangorestframework>=3.15
django-cors-headers
django-environ
django-tailwind-cli
celery[redis]>=5.6
django-celery-results
redis[hiredis]
WeasyPrint>=68
openpyxl>=3.1
Pillow
gunicorn
whitenoise
requests
```

> [!NOTE]
> **Celery on Windows**: Use `celery -A config worker --pool=solo -l info` for development. For production, deploy on Linux (WSL/Docker). Never use `prefork` pool on Windows.

---

### Phase 2: Employee Management

#### [NEW] `apps/employees/models.py`

```python
class Employee(TimeStampedModel):
    employee_code   = CharField(unique=True, max_length=20)
    full_name       = CharField(max_length=200)
    phone           = CharField(max_length=15)
    email           = EmailField(blank=True)
    designation     = CharField(max_length=100)
    department      = CharField(max_length=100)
    bank_name       = CharField(max_length=100, blank=True)
    account_number  = CharField(max_length=30, blank=True)
    pan_number      = CharField(max_length=10, blank=True)
    uan_number      = CharField(max_length=20, blank=True)
    esi_number      = CharField(max_length=20, blank=True)
    joining_date    = DateField()
    is_active       = BooleanField(default=True)
```

#### [NEW] `apps/employees/views.py`

Full CRUD views:
- `EmployeeListView` — paginated list with search/filter, HTMX partial support.
- `EmployeeCreateView` — form with validation.
- `EmployeeUpdateView` — edit form.
- `EmployeeDeleteView` — soft delete with confirmation modal.

#### [NEW] `apps/employees/api_views.py`

DRF ViewSet for:
- `GET /api/employees/` — list with search & pagination.
- `POST /api/employees/` — create.
- `PUT /api/employees/{id}/` — update.
- `DELETE /api/employees/{id}/` — deactivate.

---

### Phase 3: Salary Configuration

#### [NEW] `apps/configs/models.py`

```python
class SalaryComponent(TimeStampedModel):
    code               = CharField(unique=True, max_length=20)    # e.g., "BASIC", "HRA"
    name               = CharField(max_length=100)                 # e.g., "House Rent Allowance"
    component_type     = CharField(choices=EARNING/DEDUCTION)
    calculation_type   = CharField(choices=FIXED/PERCENTAGE/MANUAL)
    percentage_value   = DecimalField(null=True)                   # e.g., 40.00 for HRA
    fixed_value        = DecimalField(null=True)                   # e.g., 500 for Internet
    based_on_component = ForeignKey('self', null=True)             # e.g., HRA based on BASIC
    is_active          = BooleanField(default=True)
    display_order      = IntegerField(default=0)

class SystemConfiguration(TimeStampedModel):
    key   = CharField(unique=True, max_length=100)
    value = TextField()
    # Keys: company_name, company_logo, whatsapp_enabled, default_currency, etc.
```

#### [NEW] `apps/configs/views.py`

- Salary component list with inline editing (HTMX).
- Add/edit/delete components.
- System settings form (company name, logo upload, toggles).

#### [NEW] `apps/configs/services.py`

- `get_config(key, default=None)` — cached config lookup.
- `get_active_components()` — returns ordered active components.

---

### Phase 4: Payroll Engine (★ Core Logic)

This is the heart of the system. Business logic is **completely separated** from views.

#### [NEW] `apps/payroll/models.py`

```python
class EmployeeSalaryStructure(TimeStampedModel):
    """Per-employee salary values"""
    employee  = ForeignKey(Employee)
    component = ForeignKey(SalaryComponent)
    amount    = DecimalField()

    class Meta:
        unique_together = ('employee', 'component')

class Payslip(TimeStampedModel):
    """Frozen payroll snapshot — NEVER recalculated"""
    employee          = ForeignKey(Employee)
    month             = CharField(max_length=20)       # "April"
    year              = IntegerField()
    gross_salary      = DecimalField()
    total_deductions  = DecimalField()
    net_salary        = DecimalField()
    pdf_file          = FileField(upload_to='payslips/')
    generation_status = CharField(choices=PENDING/GENERATED/FAILED)
    whatsapp_status   = CharField(choices=PENDING/SENT/FAILED)

    class Meta:
        unique_together = ('employee', 'month', 'year')

class PayslipItem(TimeStampedModel):
    """Individual salary line items — frozen at generation time"""
    payslip        = ForeignKey(Payslip)
    component_name = CharField(max_length=100)
    component_type = CharField(choices=EARNING/DEDUCTION)
    amount         = DecimalField()
```

#### [NEW] `apps/payroll/engine.py` — ★ Payroll Calculation Engine

```python
class PayrollEngine:
    """
    Core salary calculation logic.
    Separated from views/serializers for testability.
    """

    def calculate(self, employee, month, year, overrides=None):
        """
        1. Load employee salary structure
        2. Apply component rules (fixed/percentage/manual)
        3. Apply overrides (manual entries from form or Excel)
        4. Calculate earnings total
        5. Calculate deductions total
        6. Return PayrollResult dataclass
        """

    def _calculate_component(self, component, base_values, overrides):
        """Calculate a single component based on its type."""

    def generate_payslip(self, employee, month, year, overrides=None):
        """
        1. Run calculate()
        2. Create Payslip record
        3. Create PayslipItem records
        4. Generate PDF
        5. Return Payslip instance
        """
```

Key design decisions:
- **Overrides dict**: Allows manual/Excel values to override calculated ones.
- **Dependency resolution**: Components calculated in `display_order`, so percentage-based components can reference already-calculated ones.
- **Frozen snapshots**: Once generated, payslip data is NEVER recalculated from rules.

#### [NEW] `apps/payroll/views.py`

- `GeneratePayslipView` — form with employee selector, month/year picker, manual component overrides.
- `PayslipPreviewView` — HTMX partial that shows calculated breakdown before generating.
- `PayslipHistoryView` — filterable list of all generated payslips.
- `PayslipDownloadView` — serves the PDF file.

#### [NEW] `apps/payroll/tasks.py`

```python
@shared_task
def generate_payslip_task(employee_id, month, year, overrides=None):
    """Celery task for async payslip generation."""

@shared_task
def generate_and_send_task(employee_id, month, year, overrides=None):
    """Generate payslip + send via WhatsApp."""
```

---

### Phase 5: PDF Generation

#### [NEW] `apps/pdf_generator/generator.py`

```python
class PayslipPDFGenerator:
    def generate(self, payslip):
        """
        1. Load payslip + items from DB
        2. Load company config (name, logo)
        3. Render HTML template with context
        4. Convert to PDF via WeasyPrint
        5. Save to media/payslips/
        6. Return file path
        """
```

#### [NEW] `templates/pdf/payslip_template.html`

Professional A4 payslip layout:

```
┌──────────────────────────────────────────────┐
│  [LOGO]    COMPANY NAME                      │
│            Address / Contact                 │
│──────────────────────────────────────────────│
│  PAYSLIP — April 2025                        │
│──────────────────────────────────────────────│
│  Employee: Vijay Kumar    Code: EMP001       │
│  Department: Engineering  Designation: SDE   │
│  Bank: HDFC              A/C: XXXX1234       │
│  PAN: ABCDE1234F         UAN: 1234567890     │
│──────────────────────────────────────────────│
│  EARNINGS              │  DEDUCTIONS         │
│  ──────────             │  ──────────         │
│  Basic       ₹20,000   │  PF         ₹2,400  │
│  HRA          ₹8,000   │  ESI          ₹300  │
│  CA           ₹1,600   │  PT            ₹200 │
│  Internet       ₹500   │  TDS         ₹1,500 │
│  ──────────             │  ──────────         │
│  Total       ₹30,100   │  Total       ₹4,400 │
│──────────────────────────────────────────────│
│  NET SALARY: ₹25,700                        │
│──────────────────────────────────────────────│
│  This is a system-generated payslip.         │
└──────────────────────────────────────────────┘
```

Design focus:
- Clean typography (Google Fonts: Inter or Roboto)
- Proper spacing and alignment
- Company branding
- A4 compatible (210mm × 297mm)
- Print-friendly CSS

---

### Phase 6: Bulk Upload & Async Processing

#### [NEW] `apps/bulk_upload/models.py`

```python
class BulkUpload(TimeStampedModel):
    file          = FileField(upload_to='uploads/')
    total_rows    = IntegerField(default=0)
    success_count = IntegerField(default=0)
    failed_count  = IntegerField(default=0)
    status        = CharField(choices=PENDING/PROCESSING/COMPLETED)

class BulkUploadRow(TimeStampedModel):
    bulk_upload   = ForeignKey(BulkUpload)
    row_number    = IntegerField()
    employee_code = CharField(max_length=20)
    status        = CharField(choices=PENDING/SUCCESS/FAILED)
    error_message = TextField(blank=True)
```

#### [NEW] `apps/bulk_upload/parser.py`

```python
class ExcelParser:
    REQUIRED_COLUMNS = ['employee_code', 'month', 'year', 'basic']
    OPTIONAL_COLUMNS = ['bonus', 'deductions', 'phone']

    def parse(self, file):
        """Parse and validate Excel file, return list of row dicts."""

    def validate_row(self, row_data, row_number):
        """Validate a single row, return errors list."""
```

#### [NEW] `apps/bulk_upload/tasks.py`

```python
@shared_task
def process_bulk_upload(upload_id):
    """
    1. Load upload record
    2. Parse Excel
    3. Create BulkUploadRow for each row
    4. For each valid row: queue generate_payslip_task
    5. Update upload status as processing completes
    """

@shared_task
def process_single_row(upload_id, row_id, row_data):
    """Process one row from bulk upload — generates payslip + optional WhatsApp."""
```

#### [NEW] `apps/bulk_upload/views.py`

- `BulkUploadView` — file upload form.
- `BulkUploadStatusView` — HTMX polling for progress (auto-refresh every 3s).
- `BulkUploadHistoryView` — list of past uploads with stats.
- `DownloadErrorReportView` — CSV/Excel of failed rows with error details.

---

### Phase 7: WhatsApp Integration

#### [NEW] `apps/whatsapp/sender.py`

```python
class WhatsAppSender:
    def __init__(self):
        self.api_url = settings.WHATSAPP_API_URL
        self.token = settings.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID

    def send_payslip(self, phone, payslip):
        """
        1. Upload PDF to Meta media endpoint
        2. Send document message via WhatsApp Cloud API
        3. Log result
        4. Update payslip.whatsapp_status
        """

    def upload_media(self, file_path):
        """Upload PDF to WhatsApp media API, return media_id."""

    def send_document(self, phone, media_id, caption):
        """Send document message with media_id."""
```

#### [NEW] `apps/whatsapp/tasks.py`

```python
@shared_task(bind=True, max_retries=3)
def send_whatsapp_payslip(self, payslip_id):
    """Async WhatsApp delivery with retry logic."""
```

#### [NEW] `apps/whatsapp/views.py`

- `SendPayslipView` — manual send trigger.
- `ResendPayslipView` — retry failed sends.

---

### Phase 8: Dashboard & Polish

#### [NEW] `templates/dashboard/index.html`

Dashboard widgets:
- **Total Employees** — count card with icon.
- **Payslips This Month** — generated vs pending.
- **WhatsApp Delivery** — sent/failed/pending breakdown.
- **Recent Uploads** — last 5 bulk uploads with status.
- **Recent Activity** — timeline of recent actions.

All widgets use HTMX for lazy loading.

---

## UI/UX Design Approach

| Element | Approach |
|---------|----------|
| Layout | Fixed sidebar + scrollable content area |
| Sidebar | Collapsible, icons + labels, active state highlighting |
| Tables | Striped rows, hover effects, sticky headers, pagination |
| Forms | Floating labels, inline validation, grouped sections |
| Modals | Slide-in panels for create/edit (HTMX loaded) |
| Toasts | Bottom-right notification stack for success/error feedback |
| Colors | Professional dark blue sidebar, white content, accent green |
| Status badges | Color-coded pills (green=success, yellow=pending, red=failed) |
| Loading | Skeleton loaders for HTMX content swaps |
| Responsive | Mobile-friendly with collapsed sidebar on small screens |

---

## Database Seeding Strategy

Create a management command `python manage.py seed_data` that:
1. Creates default salary components (Basic, HRA, CA, CCA, PF, ESI, PT, TDS).
2. Creates default system configs (company_name, currency, etc.).
3. Creates 5 sample employees for testing.
4. Generates sample payslips for demo.

---

## Verification Plan

### Automated Tests

```bash
# Run unit tests for payroll engine
python manage.py test apps.payroll.tests

# Run all tests
python manage.py test

# Specific test suites:
python manage.py test apps.payroll.tests.test_engine      # Calculation logic
python manage.py test apps.employees.tests                 # Employee CRUD
python manage.py test apps.bulk_upload.tests.test_parser   # Excel validation
python manage.py test apps.pdf_generator.tests             # PDF generation
```

Key test cases:
- Payroll engine calculates percentage-based components correctly.
- Payroll engine handles missing components gracefully.
- Payroll engine respects manual overrides.
- Excel parser validates required columns.
- Excel parser catches invalid data types.
- PDF generator produces valid PDF files.
- Bulk upload creates correct number of rows.

### Manual Verification

1. **Employee CRUD**: Create, edit, list, search employees through the UI.
2. **Salary Config**: Add/edit salary components, verify they appear in payslip generation.
3. **Manual Payslip**: Generate a payslip for an employee, verify PDF content matches calculations.
4. **PDF Quality**: Open generated PDF, verify A4 rendering, table alignment, font rendering.
5. **Bulk Upload**: Upload a sample Excel, verify async processing, check success/failure counts.
6. **WhatsApp**: Test with a sandbox number (or mock), verify status tracking.
7. **Dashboard**: Verify all widget counts are accurate.

---

## Execution Order (Phased)

| Phase | Description | Dependencies |
|-------|-------------|-------------|
| 1 | Project setup, settings, base templates, TailwindCSS, HTMX | None |
| 2 | Employee CRUD (models, views, templates) | Phase 1 |
| 3 | Salary Components & System Config | Phase 1 |
| 4 | Payroll Engine + Manual Generation | Phase 2, 3 |
| 5 | PDF Generation | Phase 4 |
| 6 | Bulk Upload + Celery/Redis | Phase 4, 5 |
| 7 | WhatsApp Integration | Phase 5 |
| 8 | Dashboard, Polish, Seed Data | All phases |

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| WeasyPrint Windows issues | Use `xhtml2pdf` as fallback; test GTK installation early |
| Celery on Windows | Use `--pool=solo` for dev; recommend WSL/Docker for production |
| PDF formatting bugs | Build and test PDF template early in Phase 5; iterate on spacing |
| Salary calculation bugs | Engine is isolated in `engine.py` with comprehensive unit tests |
| Bulk upload timeouts | Everything async via Celery; never synchronous processing |
| WhatsApp API limits | Retry with exponential backoff; queue management via Celery |
