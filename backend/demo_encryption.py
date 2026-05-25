"""
Demo AES-256 Encryption untuk presentasi ke pembimbing.
Jalankan: docker exec -it iams_backend python demo_encryption.py

Script ini SELF-CONTAINED — buat semua data yang dibutuhkan sendiri.
"""
from app import create_app
from app.extensions import db
from app.models.asset_credential import AssetCredential
from app.models.asset import Asset
from app.models.model_device import DeviceModel
from app.models.location import Location
from app.models.brand import Brand
from app.models.category import Category
from app.utils.crypto import encrypt_text, decrypt_text

app = create_app('development')

with app.app_context():
    print("=" * 60)
    print("  DEMO AES-256 ENCRYPTION — IAMS")
    print("=" * 60)
    print()

    # === DEMO 1: Enkripsi/Dekripsi langsung ===
    print("[1] DEMO ENCRYPT / DECRYPT")
    print("-" * 40)

    password_asli = "SuperSecretRouter@123"
    encrypted_1 = encrypt_text(password_asli)
    encrypted_2 = encrypt_text(password_asli)
    decrypted = decrypt_text(encrypted_1)

    print(f"  Password asli  : {password_asli}")
    print(f"  Encrypted (1)  : {encrypted_1[:60]}...")
    print(f"  Encrypted (2)  : {encrypted_2[:60]}...")
    print(f"  Decrypt (1)    : {decrypted}")
    print(f"  Cocok?         : {decrypted == password_asli}")
    print(f"  Enc1 == Enc2?  : {encrypted_1 == encrypted_2}  (IV acak = selalu beda!)")
    print()

    # === DEMO 2: Buat data + simpan credential terenkripsi ===
    print("[2] DEMO SIMPAN KE DATABASE")
    print("-" * 40)

    # Pastikan ada Brand
    brand = Brand.query.filter_by(name="Cisco").first()
    if not brand:
        brand = Brand(name="Cisco")
        db.session.add(brand)
        db.session.flush()

    # Pastikan ada Category
    cat = Category.query.filter_by(name="Router").first()
    if not cat:
        cat = Category(name="Router")
        db.session.add(cat)
        db.session.flush()

    # Pastikan ada Model
    model = DeviceModel.query.filter_by(name="ISR 4321").first()
    if not model:
        model = DeviceModel(name="ISR 4321", brand_id=brand.id, category_id=cat.id)
        db.session.add(model)
        db.session.flush()

    # Pastikan ada Location
    loc = Location.query.filter_by(name="Server Room A").first()
    if not loc:
        loc = Location(name="Server Room A")
        db.session.add(loc)
        db.session.flush()

    # Pastikan ada Asset
    asset = Asset.query.filter_by(asset_tag="RTR-DEMO-001").first()
    if not asset:
        asset = Asset(
            asset_tag="RTR-DEMO-001",
            serial_number="DEMO-SN-001",
            model_id=model.id,
            location_id=loc.id,
            status="Active",
        )
        db.session.add(asset)
        db.session.flush()

    # Buat credential terenkripsi
    cred = AssetCredential.query.filter_by(
        asset_id=asset.id, credential_type="SSH Demo"
    ).first()

    if not cred:
        cred = AssetCredential(
            asset_id=asset.id,
            credential_type="SSH Demo",
            username="admin_router",
        )
        cred.set_password("MyRouter@Pass!2026")
        db.session.add(cred)

    # Buat credential kedua untuk variasi
    cred2 = AssetCredential.query.filter_by(
        asset_id=asset.id, credential_type="Web Console"
    ).first()

    if not cred2:
        cred2 = AssetCredential(
            asset_id=asset.id,
            credential_type="Web Console",
            username="webadmin",
        )
        cred2.set_password("W3bC0ns0le#Secure")
        db.session.add(cred2)

    db.session.commit()

    print(f"  Asset          : {asset.asset_tag} (ID: {asset.id})")
    print(f"  Brand/Model    : {brand.name} / {model.name}")
    print(f"  Location       : {loc.name}")
    print()
    print(f"  --- Credential 1 ---")
    print(f"  Type           : {cred.credential_type}")
    print(f"  Username       : {cred.username}")
    print(f"  Di DB (cipher) : {cred.password_encrypted[:50]}...")
    print(f"  Decrypt        : {cred.get_password()}")
    print()
    print(f"  --- Credential 2 ---")
    print(f"  Type           : {cred2.credential_type}")
    print(f"  Username       : {cred2.username}")
    print(f"  Di DB (cipher) : {cred2.password_encrypted[:50]}...")
    print(f"  Decrypt        : {cred2.get_password()}")
    print()

    # === DEMO 3: Query langsung dari DB ===
    print("[3] BUKTI DI DATABASE (raw SQL query)")
    print("-" * 40)

    results = db.session.execute(
        db.text("SELECT id, credential_type, username, password_encrypted FROM asset_credentials")
    ).fetchall()

    for row in results:
        print(f"  ID: {row[0]} | Type: {row[1]} | User: {row[2]}")
        print(f"    password_encrypted: {row[3][:60]}...")
        print(f"    ^ INI CIPHERTEXT, BUKAN PLAINTEXT")
        print()

    print("=" * 60)
    print("  KESIMPULAN:")
    print("  - Password TIDAK PERNAH disimpan sebagai plaintext")
    print("  - Setiap enkripsi menghasilkan ciphertext BERBEDA (IV acak)")
    print("  - Hanya bisa didekripsi dengan AES_ENCRYPTION_KEY di .env")
    print("  - Tanpa key, ciphertext tidak bisa dibaca")
    print("  - Algoritma: Fernet (AES-128-CBC + HMAC-SHA256)")
    print("=" * 60)
