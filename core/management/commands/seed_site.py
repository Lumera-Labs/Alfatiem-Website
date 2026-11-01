"""Fill an empty database with the site's current texts, projects and news.

    python manage.py seed_site            # adds anything missing, never overwrites edits
    python manage.py seed_site --reset-texts   # put every page text back to the original wording
"""
import datetime as dt
import json
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import ContentBlock, Page, SiteSettings
from news.models import Category, Post, PostImage
from projects.models import ExtraPhoto, Project, ProjectPhoto

CORE = Path(__file__).resolve().parents[2]
IMG = Path(settings.BASE_DIR) / "static" / "img"

CATS = [("approvals", "Approvals", "الاعتمادات"), ("projects", "Projects", "المشاريع"), ("company", "Company", "الشركة")]

NEWS = [
 dict(slug="al-fatiem-eifs-pro-registered-with-ewa", cat="approvals", date=dt.date(2025, 12, 2), featured=True,
      cover="wadi-3", gallery=[("ewa-1", "Certificate TIP25046, page 1", "الشهادة TIP25046، الصفحة 1"), ("ewa-2", "Certificate TIP25046, materials list", "الشهادة TIP25046، قائمة المواد")],
      title=("AL FATIEM EIFS PRO registered with EWA", "تسجيل AL FATIEM EIFS PRO لدى هيئة الكهرباء والماء"),
      summary=("Certificate TIP25046 registers our EIFS PRO system for wall insulation. It is valid until 31 December 2027.",
               "سُجّل نظام EIFS PRO لدينا لعزل الجدران بموجب الشهادة TIP25046، وهي صالحة حتى 31 ديسمبر 2027."),
      body=("The Electricity and Water Authority has registered AL FATIEM EIFS PRO under certificate TIP25046, issued to Al-Fatiem Alarabi Trading Co. W.L.L. on 2 December 2025 under Ministerial Order 149/2018. The registration is valid until 31 December 2027.\n\n"
            "The system uses insulation board made by Bahrain Polystyrene Factory W.L.L. and glass-fibre mesh from Dakota Group S.a.S. The registered board is 55 mm minimum, with a thermal conductivity of 0.0382 W/m·K.\n\n"
            "The certificate and its materials list are published on our Approvals page.",
            "سجّلت هيئة الكهرباء والماء نظام AL FATIEM EIFS PRO بموجب الشهادة TIP25046 الصادرة لشركة الفطيم العربي للتجارة ذ.م.م بتاريخ 2 ديسمبر 2025 وفق القرار الوزاري 149/2018. والتسجيل صالح حتى 31 ديسمبر 2027.\n\n"
            "يستخدم النظام ألواح عزل من إنتاج مصنع البحرين للبوليسترين وشبك ألياف زجاجية من Dakota Group S.a.S. ولا تقل سماكة اللوح المسجّل عن 55 مم، بموصلية حرارية 0.0382 واط/م·كلفن.\n\n"
            "الشهادة وقائمة المواد منشورتان في صفحة الاعتمادات.")),
 dict(slug="al-fatiem-eifs-registered-with-ewa", cat="approvals", date=dt.date(2025, 9, 18),
      cover="sitra-1", gallery=[("ewa-3", "Certificate TIP25039, page 1", "الشهادة TIP25039، الصفحة 1"), ("ewa-4", "Certificate TIP25039, materials list", "الشهادة TIP25039، قائمة المواد")],
      title=("AL FATIEM EIFS registered with EWA", "تسجيل AL FATIEM EIFS لدى هيئة الكهرباء والماء"),
      summary=("Certificate TIP25039 registers our original EIFS system for wall insulation. It is valid until 30 September 2027.",
               "سُجّل نظام EIFS الأصلي لدينا لعزل الجدران بموجب الشهادة TIP25039، وهي صالحة حتى 30 سبتمبر 2027."),
      body=("The Electricity and Water Authority has registered AL FATIEM EIFS under certificate TIP25039, issued to Al-Fatiem Alarabi Trading Co. W.L.L. on 18 September 2025. The registration is valid until 30 September 2027.\n\n"
            "The system uses insulation board made by Bahrain Polystyrene Factory W.L.L. and glass-fibre mesh from Dr. Gunther Kast GmbH & Co and Valmiera Glass Group.",
            "سجّلت هيئة الكهرباء والماء نظام AL FATIEM EIFS بموجب الشهادة TIP25039 الصادرة لشركة الفطيم العربي للتجارة ذ.م.م بتاريخ 18 سبتمبر 2025. والتسجيل صالح حتى 30 سبتمبر 2027.\n\n"
            "يستخدم النظام ألواح عزل من إنتاج مصنع البحرين للبوليسترين وشبك ألياف زجاجية من Dr. Gunther Kast GmbH & Co وValmiera Glass Group.")),
 dict(slug="eshp-phase-3-completed", cat="projects", date=dt.date(2025, 1, 1), year_only=True,
      cover="eshp-2", gallery=[("s-eshp", "Scaffolding at ESHP Phase 3", "السقالات في إسكان شرق سترة، المرحلة 3"), ("eshp-3", "", "")],
      title=("ESHP Phase 3 completed: our largest project to date", "اكتمال إسكان شرق سترة المرحلة 3: أكبر مشاريعنا حتى الآن"),
      summary=("We insulated 87,338 m² of Ministry of Housing homes in East Sitra for Al-Nasir Contracting, with a further 7,560 m² for Aradous Contracting.",
               "عزلنا 87,338 م² من منازل وزارة الإسكان في شرق سترة لصالح الناصر للمقاولات، إضافة إلى 7,560 م² لصالح أرادوس للمقاولات."),
      body=("On East Sitra Housing Phase 3 we insulated 87,338 m² of Ministry of Housing homes for the main contractor, Al-Nasir Contracting W.L.L., and supplied the scaffolding on the same package.\n\n"
            "A second package of 7,560 m² was completed for Aradous Contracting and Maintenance Co. W.L.L.",
            "في مشروع إسكان شرق سترة المرحلة 3 عزلنا 87,338 م² من منازل وزارة الإسكان لصالح المقاول الرئيسي الناصر للمقاولات، ووفّرنا السقالات للحزمة نفسها.\n\n"
            "وأنجزنا حزمة ثانية بمساحة 7,560 م² لصالح أرادوس للمقاولات والصيانة.")),
 dict(slug="insulation-and-scaffolding-on-east-hidd", cat="projects", date=dt.date(2025, 1, 1), year_only=True,
      cover="s-hidd", gallery=[("s-hidd2", "East Hidd buildings", "مباني شرق الحد")],
      title=("Insulation and scaffolding on East Hidd", "العزل والسقالات في مشروع شرق الحد"),
      summary=("For MITCO we erected the scaffolding and applied the insulation on the East Hidd buildings, about 2,650 m² of facade.",
               "لصالح ميتكو ركّبنا السقالات ونفّذنا العزل في مباني شرق الحد، بمساحة واجهات نحو 2,650 م²."),
      body=("For Modern Insulation Technology Co. (MITCO) we erected the scaffolding and applied the insulation on the East Hidd buildings, about 2,650 m² of facade.",
            "لصالح الشركة الحديثة لتقنية العزل (ميتكو) ركّبنا السقالات ونفّذنا العزل في مباني شرق الحد، بمساحة واجهات نحو 2,650 م².")),
 dict(slug="scaffolding-company-established", cat="company", date=dt.date(2023, 1, 1), year_only=True,
      cover="s-hero", gallery=[("s-tower", "Scaffold tower and working platform", "برج سقالات ومنصة عمل"), ("s-sunset", "Scaffolding on a villa", "سقالات على فيلا")],
      title=("Scaffolding company established", "تأسيس شركة السقالات"),
      summary=("Al-Fatiem Alarabi Trading Co. W.L.L. began supplying, renting and erecting scaffolding alongside our insulation division.",
               "بدأت شركة الفطيم العربي للتجارة بتوريد السقالات وتأجيرها وتركيبها إلى جانب قسم العزل."),
      body=("Al-Fatiem Alarabi Trading Co. W.L.L. (CR 139385-2) began supplying, renting and erecting scaffolding alongside our insulation division.\n\n"
            "It sells new and used material, rents scaffolding for the length of a programme, erects and dismantles with its own crews, and buys back used material.",
            "بدأت شركة الفطيم العربي للتجارة ذ.م.م (س.ت 139385-2) بتوريد السقالات وتأجيرها وتركيبها إلى جانب قسم العزل.\n\n"
            "تبيع الشركة المواد الجديدة والمستعملة، وتؤجّر السقالات طوال مدة المشروع، وتركّبها وتفكّها بفرقها الخاصة، وتشتري المواد المستعملة.")),
]


def put(field, name):
    src = IMG / f"{name}.webp"
    with src.open("rb") as fh:
        field.save(src.name, File(fh), save=False)


class Command(BaseCommand):
    help = "Load the website's starting content (texts, contact details, projects, news)."

    def add_arguments(self, p):
        p.add_argument("--reset-texts", action="store_true", help="Overwrite edited page texts with the original wording.")

    @transaction.atomic
    def handle(self, *a, reset_texts=False, **kw):
        data = json.loads((CORE / "content_defaults.json").read_text(encoding="utf-8"))
        added = 0
        for i, p in enumerate(data["pages"]):
            page, _ = Page.objects.get_or_create(slug=p["slug"], defaults={"name": p["name"], "position": i})
            if not page.meta_title and p.get("title"):
                page.meta_title, page.meta_description = p["title"], p.get("description", "")
                page.save()
            for j, b in enumerate(p["blocks"]):
                obj, made = ContentBlock.objects.get_or_create(
                    key=b["key"], defaults={"page": page, "position": j, "kind": b["kind"], "en": b["en"], "ar": b["ar"]})
                added += made
                if reset_texts and not made:
                    obj.en, obj.ar = b["en"], b["ar"]
                    obj.save()
        SiteSettings.load()
        self.stdout.write(f"page texts: {ContentBlock.objects.count()} ({added} new)")

        cats = {}
        for i, (slug, en, ar) in enumerate(CATS):
            cats[slug], _ = Category.objects.get_or_create(slug=slug, defaults={"name_en": en, "name_ar": ar, "position": i})
        if not Post.objects.exists():
            for n in NEWS:
                post = Post(slug=n["slug"], category=cats[n["cat"]], date=n["date"], year_only=n.get("year_only", False),
                            is_featured=n.get("featured", False), title_en=n["title"][0], title_ar=n["title"][1],
                            summary_en=n["summary"][0], summary_ar=n["summary"][1], body_en=n["body"][0], body_ar=n["body"][1])
                put(post.cover, n["cover"])
                post.save()
                for k, (img, cen, car) in enumerate(n["gallery"]):
                    pi = PostImage(post=post, caption_en=cen, caption_ar=car, position=k)
                    put(pi.image, img)
                    pi.save()
        self.stdout.write(f"news articles: {Post.objects.count()}")

        if not Project.objects.exists():
            for p in json.loads((CORE / "seed_projects.json").read_text(encoding="utf-8")):
                pr = Project.objects.create(
                    code=p["id"], name_en=p["en"], name_ar=p["ar"], sector=p["s"], year=p["y"], area=p["a"],
                    location_en=p["loc"]["en"], location_ar=p["loc"]["ar"],
                    client_en=(p.get("cl") or {}).get("en", ""), client_ar=(p.get("cl") or {}).get("ar", ""),
                    consultant=p.get("cons", ""),
                    contractors_en=(p.get("chain") or {}).get("en", "").replace(" · ", ". "),
                    contractors_ar=(p.get("chain") or {}).get("ar", "").replace(" · ", "، "),
                    insulation="eifs" in p["sv"], scaffolding="scaf" in p["sv"],
                    on_home=p["id"] in ("eshp-n", "wadi", "sahel"))
                for k, ph in enumerate(p.get("ph", [])):
                    pp = ProjectPhoto(project=pr, position=k)
                    put(pp.image, ph)
                    pp.save()
            for k, (img, en, ar) in enumerate([("storey3", "Three-storey residence", "مبنى سكني من ثلاثة طوابق"),
                                               ("karranah", "Villa, Karranah", "فيلا، كرانة")]):
                e = ExtraPhoto(caption_en=en, caption_ar=ar, position=k)
                put(e.image, img)
                e.save()
        self.stdout.write(f"projects: {Project.objects.count()}")
        self.stdout.write(self.style.SUCCESS("Done."))
