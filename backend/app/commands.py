"""Flask CLI commands for seeding and maintenance."""
import click
from flask.cli import with_appcontext

from app.extensions import db
from datetime import date, datetime, timedelta

from app.models import Asset, Brand, Category, ChangeRequest, Department, DeviceModel, Incident, Location, Problem, Role, ServiceRequest, SoftwareLicense, User
from app.utils.security import hash_password


@click.command('seed')
@with_appcontext
def seed_command():
    """Seed default roles, admin user, and sample master data."""
    today = date.today()

    # Roles
    roles = {}
    for name in ('Administrator', 'Operator'):
        role = Role.query.filter_by(name=name).first()
        if not role:
            role = Role(name=name)
            db.session.add(role)
        roles[name] = role
    db.session.commit()

    # Departments
    dept_data = [
        ('Infrastructure',        'Core infrastructure team'),
        ('Network Operations',    'Network operations center'),
        ('IT Service Desk',       'Service desk team'),
        ('Security & Compliance', 'Security team'),
        ('Data Center Ops',       'Data center operations'),
        ('Software Development',  'Application development team'),
        ('Database Administration','DBA team'),
        ('Cloud Operations',      'Cloud infrastructure team'),
        ('Cybersecurity',         'Threat detection and response'),
        ('IT Procurement',        'Hardware and software procurement'),
        ('End User Computing',    'Workstation and peripherals support'),
    ]
    for name, desc in dept_data:
        if not Department.query.filter_by(name=name).first():
            db.session.add(Department(name=name, description=desc))

    # Locations
    loc_data = [
        ('HQ Jakarta — Lt. 12 IDF',  'Intermediate Distribution Frame'),
        ('HQ Jakarta — DC Room',     'Main Data Center'),
        ('Branch Surabaya',          'East Java regional branch'),
        ('Branch Bandung',           'West Java regional branch'),
        ('Branch Medan',             'North Sumatera regional branch'),
        ('Warehouse DC',             'Inventory & spare parts'),
        ('Branch Semarang',          'Central Java regional branch'),
        ('Branch Makassar',          'South Sulawesi regional branch'),
        ('Branch Bali',              'Bali regional branch'),
        ('HQ Jakarta — Lt. 8 MDF',  'Main Distribution Frame'),
        ('Data Center Colocation',   'Third-party colocation facility'),
    ]
    for name, desc in loc_data:
        if not Location.query.filter_by(name=name).first():
            db.session.add(Location(name=name, description=desc))

    # Categories
    for name in ('Router', 'Switch', 'Firewall', 'Access Point', 'Printer',
                 'Server', 'UPS', 'NAS', 'KVM Switch', 'Patch Panel', 'IP Camera'):
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))

    # Brands
    for name in ('Cisco', 'MikroTik', 'Juniper', 'Fortinet', 'Aruba', 'Ubiquiti',
                 'HP', 'Brother', 'Dell', 'Palo Alto', 'Ruckus', 'Synology',
                 'APC', 'Eaton', 'Hikvision'):
        if not Brand.query.filter_by(name=name).first():
            db.session.add(Brand(name=name))

    db.session.commit()

    # Default admin user
    admin_email = 'admin@iams.local'
    if not User.query.filter_by(email=admin_email).first():
        admin = User(
            name='Rendy Adhitama',
            email=admin_email,
            password_hash=hash_password('admin123'),
            role_id=roles['Administrator'].id,
            department_id=1,
            is_active=True,
        )
        db.session.add(admin)

    operator_email = 'operator@iams.local'
    if not User.query.filter_by(email=operator_email).first():
        operator = User(
            name='Sari Wulandari',
            email=operator_email,
            password_hash=hash_password('operator123'),
            role_id=roles['Operator'].id,
            department_id=2,
            is_active=True,
        )
        db.session.add(operator)

    db.session.commit()

    # Sample models
    model_data = [
        ('ISR 4331', 'Cisco', 'Router', '3x GE WAN, IP Base'),
        ('RB4011iGS+', 'MikroTik', 'Router', '10x GbE, 1x SFP+'),
        ('Catalyst 9300-48P', 'Cisco', 'Switch', '48x PoE+ GbE'),
        ('CRS328-24P-4S+RM', 'MikroTik', 'Switch', '24x PoE, 4x SFP+'),
        ('FortiGate 100F', 'Fortinet', 'Firewall', 'NGFW, 20 Gbps FW'),
        ('SRX345', 'Juniper', 'Firewall', 'Branch SRX 5 Gbps'),
        ('AP-515', 'Aruba', 'Access Point', 'Wi-Fi 6, 2x2:2 MU-MIMO'),
        ('U6-Pro', 'Ubiquiti', 'Access Point', 'Wi-Fi 6, Dual-band'),
        ('LaserJet M428fdw', 'HP', 'Printer', 'Mono, 40 ppm'),
        ('HL-L2375DW', 'Brother', 'Printer', 'Mono, 36 ppm'),
    ]
    models = {}
    for name, brand_name, category_name, specs in model_data:
        m = DeviceModel.query.filter_by(name=name).first()
        if not m:
            brand = Brand.query.filter_by(name=brand_name).first()
            category = Category.query.filter_by(name=category_name).first()
            m = DeviceModel(
                name=name,
                brand_id=brand.id if brand else None,
                category_id=category.id if category else None,
                specifications=specs,
            )
            db.session.add(m)
        models[name] = m
    db.session.commit()

    # Sample assets
    if Asset.query.count() == 0:
        assets = [
            ('AST-RTR-0001', 'ISR 4331',          'HQ Jakarta — Lt. 12 IDF', 'Active',    today - timedelta(days=400),  36, 'admin@iams.local'),
            ('AST-RTR-0002', 'RB4011iGS+',        'Branch Surabaya',         'Active',    today - timedelta(days=700),  24, 'operator@iams.local'),
            ('AST-RTR-0003', 'ISR 4331',           'Branch Bandung',          'Active',    today - timedelta(days=520),  36, None),
            ('AST-RTR-0004', 'RB4011iGS+',        'Branch Medan',            'Repair',    today - timedelta(days=600),  24, None),
            ('AST-SWT-0001', 'Catalyst 9300-48P', 'HQ Jakarta — DC Room',    'Active',    today - timedelta(days=380),  60, None),
            ('AST-SWT-0002', 'CRS328-24P-4S+RM',  'Branch Surabaya',         'Active',    today - timedelta(days=450),  36, None),
            ('AST-SWT-0003', 'Catalyst 9300-48P', 'Branch Bandung',          'Available', today - timedelta(days=200),  60, None),
            ('AST-FWL-0001', 'FortiGate 100F',    'HQ Jakarta — DC Room',    'Active',    today - timedelta(days=200),  36, 'admin@iams.local'),
            ('AST-FWL-0002', 'SRX345',            'Branch Bandung',          'Repair',    today - timedelta(days=1000), 36, 'operator@iams.local'),
            ('AST-FWL-0003', 'FortiGate 100F',    'Branch Surabaya',         'Active',    today - timedelta(days=120),  36, None),
            ('AST-APX-0001', 'AP-515',            'HQ Jakarta — Lt. 12 IDF', 'Active',    today - timedelta(days=300),  24, None),
            ('AST-APX-0002', 'U6-Pro',            'Branch Medan',            'Disposed',  today - timedelta(days=2000), 12, None),
            ('AST-APX-0003', 'AP-515',            'Branch Bandung',          'Active',    today - timedelta(days=150),  24, None),
            ('AST-PRT-0001', 'LaserJet M428fdw',  'HQ Jakarta — Lt. 12 IDF', 'Available', today - timedelta(days=900),  12, None),
            ('AST-PRT-0002', 'HL-L2375DW',        'Branch Surabaya',         'Active',    today - timedelta(days=500),  12, None),
        ]
        for tag, model_name, location_name, status, purchase, warranty, owner_email in assets:
            model = models.get(model_name)
            location = Location.query.filter_by(name=location_name).first()
            owner = User.query.filter_by(email=owner_email).first() if owner_email else None
            db.session.add(Asset(
                asset_tag=tag,
                serial_number=f'DEMO-SN-{tag}',
                model_id=model.id if model else None,
                location_id=location.id if location else None,
                user_id=owner.id if owner else None,
                status=status,
                purchase_date=purchase,
                warranty_months=warranty,
            ))
        db.session.commit()

    # Sample incidents
    if Incident.query.count() == 0:
        incidents = [
            ('Gangguan link utama HQ',            'Critical', 'Open',        'AST-RTR-0001', 'admin@iams.local'),
            ('Switch DC overheat',                'High',     'In Progress',  'AST-SWT-0001', 'operator@iams.local'),
            ('Printer floor 12 offline',          'Low',      'Open',         'AST-PRT-0001', None),
            ('Firewall Bandung tidak merespons',  'High',     'Open',         'AST-FWL-0002', 'admin@iams.local'),
            ('AP Medan sinyal lemah',             'Medium',   'In Progress',  'AST-APX-0002', 'operator@iams.local'),
            ('Router Surabaya packet loss tinggi','High',     'Resolved',     'AST-RTR-0002', 'admin@iams.local'),
            ('Switch Surabaya port mati',         'Medium',   'Open',         'AST-SWT-0002', None),
            ('Firewall HQ log penuh',             'Low',      'Resolved',     'AST-FWL-0001', 'operator@iams.local'),
            ('AP Bandung intermittent',           'Medium',   'Open',         'AST-APX-0003', None),
            ('Printer Surabaya jam',              'Low',      'Closed',       'AST-PRT-0002', None),
            ('Router Bandung CPU 100%',           'Critical', 'In Progress',  'AST-RTR-0003', 'admin@iams.local'),
            ('Switch HQ VLAN corrupt',            'High',     'Open',         'AST-SWT-0003', 'operator@iams.local'),
        ]
        for idx, (title, severity, status, tag, assignee_email) in enumerate(incidents, start=1):
            asset = Asset.query.filter_by(asset_tag=tag).first()
            assignee = User.query.filter_by(email=assignee_email).first() if assignee_email else None
            db.session.add(Incident(
                code=f'INC-{today.year}-{idx:04d}',
                title=title, severity=severity, status=status,
                asset_id=asset.id if asset else None,
                assignee_id=assignee.id if assignee else None,
            ))
        db.session.commit()

    # Sample problems
    if Problem.query.count() == 0:
        problems = [
            ('Link utama sering flapping',           'High',     'Investigating', 'operator@iams.local'),
            ('Printer network tidak stabil',         'Low',      'Open',          None),
            ('Firewall drop connection periodic',    'Critical', 'Known Error',   'admin@iams.local'),
            ('AP roaming handoff gagal',             'Medium',   'Investigating', 'operator@iams.local'),
            ('Switch spanning-tree instabil',        'High',     'Open',          'admin@iams.local'),
            ('Router BGP flap berkala',              'Critical', 'Known Error',   'admin@iams.local'),
            ('DNS resolution lambat di HQ',          'Medium',   'Investigating', 'operator@iams.local'),
            ('NTP sinkronisasi gagal',               'Low',      'Open',          None),
            ('VLAN isolasi tidak konsisten',         'High',     'Investigating', 'admin@iams.local'),
            ('QoS traffic shaping bermasalah',       'Medium',   'Open',          'operator@iams.local'),
            ('Backup otomatis sering timeout',       'High',     'Known Error',   'admin@iams.local'),
            ('Log syslog tidak terkirim ke server',  'Low',      'Closed',        None),
        ]
        for idx, (title, priority, status, owner_email) in enumerate(problems, start=1):
            owner = User.query.filter_by(email=owner_email).first() if owner_email else None
            db.session.add(Problem(
                code=f'PRB-{today.year}-{idx:04d}',
                title=title, priority=priority, status=status,
                owner_id=owner.id if owner else None,
            ))
        db.session.commit()

    # Sample requests
    if ServiceRequest.query.count() == 0:
        admin = User.query.filter_by(email='admin@iams.local').first()
        operator = User.query.filter_by(email='operator@iams.local').first()
        r1 = Asset.query.filter_by(asset_tag='AST-RTR-0001').first()
        sample_requests = [
            ('Permintaan laptop baru untuk tim finance',      'Asset Request',       'Medium',   'Open',            admin,    None,     None, today + timedelta(days=14)),
            ('Perbaikan router utama cabang Surabaya',        'Repair Request',      'High',     'In Progress',     admin,    operator, r1,   today + timedelta(days=2)),
            ('Akses VPN untuk karyawan baru',                 'Access Request',      'Low',      'Waiting Approval',operator, admin,   None, today + timedelta(days=7)),
            ('Pemindahan printer ke lantai 3',                'Relocation Request',  'Medium',   'Open',            operator, None,    None, today + timedelta(days=30)),
            ('Penggantian switch DC yang sudah EOL',          'Replacement Request', 'Critical', 'Approved',        admin,    operator, None, None),
            ('Konfigurasi VLAN baru untuk IoT devices',       'Network Request',     'High',     'In Progress',     admin,    operator, None, today + timedelta(days=5)),
            ('Penambahan port network ruang meeting lantai 5','Network Request',     'Low',      'Open',            operator, None,    None, today + timedelta(days=21)),
            ('Upgrade RAM server backup DC',                  'Asset Request',       'Medium',   'Waiting Approval',admin,    operator, None, today + timedelta(days=10)),
            ('Perbaikan AP Bandung intermittent',             'Repair Request',      'Medium',   'Open',            operator, admin,   None, today + timedelta(days=3)),
            ('Penggantian firewall SRX345 rusak',             'Replacement Request', 'Critical', 'Approved',        admin,    operator, None, today + timedelta(days=7)),
            ('Akses remote desktop tim developer',            'Access Request',      'Low',      'Fulfilled',       operator, admin,   None, today - timedelta(days=5)),
            ('Pemindahan server ke rack baru',                'Relocation Request',  'High',     'Closed',          admin,    operator, None, today - timedelta(days=10)),
        ]
        for idx, (title, rtype, priority, status, requester, assignee, asset, due) in enumerate(sample_requests, 1):
            db.session.add(ServiceRequest(
                request_number=f'REQ-{today.year}-{idx:04d}',
                title=title, request_type=rtype, priority=priority, status=status,
                requester_id=requester.id if requester else None,
                assigned_to_id=assignee.id if assignee else None,
                asset_id=asset.id if asset else None,
                due_date=due,
            ))
        db.session.commit()

    # Sample changes
    if ChangeRequest.query.count() == 0:
        admin = User.query.filter_by(email='admin@iams.local').first()
        operator = User.query.filter_by(email='operator@iams.local').first()
        r1 = Asset.query.filter_by(asset_tag='AST-RTR-0001').first()
        sample = [
            ('Upgrade firmware router core HQ',            'Maintenance',   'Low',      'Medium',   'Scheduled',   admin,    operator, r1,   today + timedelta(days=3),  today + timedelta(days=3)),
            ('Migrasi firewall ke FortiGate 100F',         'Replacement',   'High',     'Critical', 'Under Review',admin,    None,     None, today + timedelta(days=7),  today + timedelta(days=8)),
            ('Penambahan VLAN untuk IoT',                  'Configuration', 'Medium',   'Medium',   'Draft',       operator, None,     None, None,                       None),
            ('Patching keamanan AP seluruh cabang',        'Emergency',     'High',     'High',     'Approved',    admin,    operator, None, None,                       None),
            ('Upgrade switch HQ ke 10GbE',                'Replacement',   'Medium',   'High',     'Submitted',   admin,    operator, None, today + timedelta(days=14), today + timedelta(days=15)),
            ('Konfigurasi BGP failover link Surabaya',     'Configuration', 'High',     'Critical', 'Approved',    admin,    operator, None, today + timedelta(days=5),  today + timedelta(days=5)),
            ('Relokasi server backup ke DC room baru',     'Relocation',    'Low',      'Low',      'Completed',   operator, admin,    None, today - timedelta(days=7),  today - timedelta(days=6)),
            ('Penggantian UPS yang sudah 5 tahun',         'Replacement',   'Medium',   'Medium',   'Scheduled',   admin,    None,     None, today + timedelta(days=30), today + timedelta(days=31)),
            ('Implementasi monitoring SNMP seluruh aset',  'Standard',      'Low',      'Low',      'Draft',       operator, None,     None, None,                       None),
            ('Upgrade firmware firewall FortiGate HQ',    'Maintenance',   'Medium',   'High',     'Submitted',   admin,    operator, None, today + timedelta(days=10), today + timedelta(days=10)),
            ('Penambahan bandwidth ISP Bandung 500Mbps',   'Normal',        'High',     'High',     'Under Review',admin,    None,     None, today + timedelta(days=20), today + timedelta(days=20)),
            ('Konfigurasi RADIUS untuk WiFi perusahaan',  'Configuration', 'Medium',   'Medium',   'Draft',       operator, admin,    None, None,                       None),
        ]
        for n, (title, ctype, risk, impact, status, req, assignee, asset, ps, pe) in enumerate(sample, 1):
            db.session.add(ChangeRequest(
                change_number=f'CHG-{today.year}-{n:04d}',
                title=title, change_type=ctype, risk_level=risk, impact=impact, status=status,
                requester_id=req.id, assignee_id=assignee.id if assignee else None,
                asset_id=asset.id if asset else None,
                planned_start=datetime.combine(ps, datetime.min.time()) if ps else None,
                planned_end=datetime.combine(pe, datetime.min.time()) if pe else None,
            ))
        db.session.commit()

    # Sample software licenses
    if SoftwareLicense.query.count() == 0:
        licenses_data = [
            ('Microsoft 365 Business',          'N9J4R-2KPHF-WXB79-7CQJD-M3GYK', 50,  'it-admin@company.co.id',      today - timedelta(days=180), today + timedelta(days=185)),
            ('Windows Server 2022 Datacenter',  'WX4NM-KYWYW-QJJR4-XV3QB-6VM33', 5,   'infra@company.co.id',         today - timedelta(days=365), today + timedelta(days=730)),
            ('VMware vSphere Enterprise Plus',  'HV4WC-01087-1ZJ30-08EP0-CK212',  3,   'datacenter@company.co.id',    today - timedelta(days=90),  today + timedelta(days=275)),
            ('Kaspersky Endpoint Security',     'KESC-1234-5678-9012',             100, 'security@company.co.id',     today - timedelta(days=30),  today + timedelta(days=335)),
            ('Adobe Creative Cloud Teams',      'ADBE-CC-TEAM-2026',               10,  'design@company.co.id',       today - timedelta(days=60),  today + timedelta(days=305)),
            ('Fortinet FortiGuard Bundle',      'FG100F-LIC-BDL-2026',             2,   'noc@company.co.id',          today - timedelta(days=200), today + timedelta(days=165)),
            ('Zoom Meetings Business',          'ZOOM-BIZ-XXXX-2026',              25,  'hr@company.co.id',           today - timedelta(days=120), today + timedelta(days=245)),
            ('Slack Pro',                       'SLCK-PRO-XXXX-2026',              50,  'ops@company.co.id',          today - timedelta(days=150), today + timedelta(days=215)),
            ('JetBrains All Products Pack',     'JB-ALL-XXXX-2026',                5,   'dev@company.co.id',          today - timedelta(days=45),  today + timedelta(days=320)),
            ('Atlassian Confluence Cloud',      'ATLS-CONF-XXXX-2026',             30,  'pm@company.co.id',           today - timedelta(days=75),  today + timedelta(days=290)),
            ('Veeam Backup & Replication',      'VEEAM-BR-XXXX-2026',              3,   'backup@company.co.id',       today - timedelta(days=300), today + timedelta(days=65)),
            ('SolarWinds Network Performance',  'SW-NPM-XXXX-2026',                1,   'monitoring@company.co.id',   today - timedelta(days=180), today + timedelta(days=185)),
        ]
        for name, key, seats, email, purchase, expiry in licenses_data:
            db.session.add(SoftwareLicense(
                name=name,
                product_key=key,
                seats=seats,
                licensed_to_email=email,
                purchase_date=purchase,
                expiration_date=expiry,
            ))
        db.session.commit()

    click.echo('Seed completed.')
