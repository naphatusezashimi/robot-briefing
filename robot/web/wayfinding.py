_KEYWORDS = [
    "อยู่ที่ไหน", "อยู่ไหน", "ตรงไหน", "ที่ไหน",
    "ไปยังไง", "ไปทางไหน", "ไปยัง", "เดินไป",
    "ทางไป", "เส้นทาง", "แผนผัง", "แผนที่",
    "อาคาร", "ตึก", "ห้อง", "สนาม",
    "โรงอาหาร", "หอประชุม", "ป้อมยาม",
    "เสาธง", "ที่จอดรถ", "บ้านพัก",
    # โหมดภาษาอังกฤษ
    "where is", "where's", "how do i get", "how to get", "map", "building",
    "room", "canteen", "cafeteria", "parking", "auditorium",
]

# คำที่บอกว่าถามถึงที่นอกวิทยาลัย (ท่องเที่ยว/ของฝากสระบุรี) — แผนผังวิทยาลัยไม่ช่วยอะไร
_OFF_CAMPUS = [
    "เที่ยว", "สระบุรี", "จังหวัด", "อำเภอ", "เสาไห้", "บ้านหมอ",
    "น้ำตก", "ตลาด", "ร้าน", "ของฝาก", "ซื้อ", "otop", "โอทอป",
    "อาหาร", "ของกิน", "อร่อย", "คาเฟ่", "พักผ่อน",
    "visit", "travel", "trip", "tourist", "saraburi", "province", "district",
    "waterfall", "temple", "market", "souvenir", "restaurant", "food", "cafe",
]


def wants_map(text: str) -> bool:
    """คืน True ถ้าข้อความถามเรื่องตำแหน่ง/ทางภายในวิทยาลัย"""
    low = text.lower()
    if "แผนผัง" in text or "campus map" in low:
        return True
    canteen = "โรงอาหาร" in text or "canteen" in low or "cafeteria" in low
    if not canteen and any(w in low for w in _OFF_CAMPUS):
        return False
    return any(kw in low for kw in _KEYWORDS)
