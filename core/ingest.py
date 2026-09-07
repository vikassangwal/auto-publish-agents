"""
Multi-Format Product Ingestion & Intelligence Engine.
Automatically detects, classifies, analyzes, and bundles 10+ digital product formats:
1. Spreadsheets (.xlsx, .xls, .xlsm, .csv, .ods)
2. eBooks & Publications (.pdf, .epub, .mobi)
3. Design Assets & UI Kits (.fig, .psd, .ai, .sketch, .xd, .canva, .procreate)
4. Code, Scripts, SaaS Boilerplates & Bots (.py, .js, .ts, .zip, .json, .sql)
5. Presentations & Pitch Decks (.pptx, .key, .ppt)
6. Documents, Resumes & Business Plans (.docx, .doc, .rtf)
7. Audio & Sample Packs (.mp3, .wav, .flac, .midi)
8. Video Courses & Masterclasses (.mp4, .mov, .mkv)
9. 3D Models & VR Assets (.blend, .obj, .fbx, .stl)
10. Notion & Digital Planners (.notion, .md, .zip)
"""
import os
import zipfile
import shutil
from pathlib import Path
from typing import Optional, List, Dict
from .models import ProductMetadata

class ProductIngestionEngine:
    def __init__(self, product_path: str):
        self.path = Path(product_path)
        if not self.path.exists():
            raise FileNotFoundError(f"Product file not found: {product_path}")

    def analyze(self) -> ProductMetadata:
        ext = self.path.suffix.lower()
        file_name = self.path.name
        stem_name = self.path.stem.replace("_", " ").replace("-", " ").title()

        # Format dispatch table
        if ext in [".xlsx", ".xls", ".xlsm", ".csv", ".ods"]:
            return self._analyze_spreadsheet(stem_name, ext)
        elif ext in [".epub", ".mobi", ".azw3"] or (ext == ".pdf" and ("book" in file_name.lower() or "guide" in file_name.lower())):
            return self._analyze_ebook(stem_name, ext)
        elif ext == ".pdf":
            return self._analyze_pdf_document(stem_name)
        elif ext in [".fig", ".psd", ".ai", ".sketch", ".xd", ".procreate"]:
            return self._analyze_design_asset(stem_name, ext)
        elif ext in [".pptx", ".ppt", ".key"]:
            return self._analyze_presentation(stem_name, ext)
        elif ext in [".docx", ".doc", ".rtf", ".pages"]:
            return self._analyze_document(stem_name, ext)
        elif ext in [".py", ".js", ".ts", ".jsx", ".tsx", ".sql", ".sh"]:
            return self._analyze_code_script(stem_name, ext)
        elif ext in [".mp3", ".wav", ".flac", ".midi", ".aac"]:
            return self._analyze_audio(stem_name, ext)
        elif ext in [".mp4", ".mov", ".mkv", ".webm"]:
            return self._analyze_video_course(stem_name, ext)
        elif ext in [".blend", ".obj", ".fbx", ".stl"]:
            return self._analyze_3d_asset(stem_name, ext)
        elif ext == ".zip":
            return self._analyze_zip_bundle(stem_name)
        else:
            return self._analyze_generic(stem_name, ext)

    # 1. Spreadsheets
    def _analyze_spreadsheet(self, title: str, ext: str) -> ProductMetadata:
        bundle_path = self._ensure_bundle()
        is_portfolio = "portfolio" in title.lower() or "investment" in title.lower()

        if is_portfolio:
            display_title = "Ultimate Investment Portfolio Tracker Pro (v2.0)"
            tagline = "Institutional-Grade Multi-Asset Wealth Intelligence & Dividend Dashboard for Excel"
            description = (
                "Take full institutional control of your investments with zero recurring subscriptions. "
                "The Ultimate Investment Portfolio Tracker Pro consolidates Stocks, ETFs, Mutual Funds, "
                "Bonds, REITs, Gold, Crypto, and Cash into one automated dashboard. "
                "Features Time-Weighted Returns (TWR), Money-Weighted Returns (XIRR), automated portfolio "
                "rebalancing drift bands, 30-year FIRE compounding scenarios, and monthly dividend cashflow "
                "projections-100% macro-free, private, and local on your machine."
            )
            features = [
                "100% Macro-Free & Secure: Zero VBA security warnings; 100% local privacy.",
                "Multi-Asset Coverage: Stocks, ETFs, Mutual Funds, Bonds, REITs, Gold, Crypto, Cash.",
                "Executive Wealth Intelligence: Net worth, invested capital, open gains, S&P 500 alpha.",
                "True Performance Metrics: Time-Weighted Return (TWR) & Money-Weighted Return (XIRR).",
                "Automated Rebalancing Engine: Real-time drift alerts with tax-efficient Buy/Sell guidance.",
                "Dividend & Cashflow Projector: Yield-on-Cost (YoC) and monthly dividend trajectory.",
                "FIRE Freedom Simulator: 30-year wealth compounding and Safe Withdrawal Rate (SWR) modeling.",
                "Multi-Currency Toggle: Supports USD ($), INR (Rs), EUR (EUR), GBP (GBP), CAD, AUD, JPY."
            ]
            tags = ["investment tracker", "portfolio tracker", "excel spreadsheet", "dividend tracker",
                    "stock tracker", "net worth dashboard", "fire calculator", "wealth management", "personal finance"]
            price_usd, price_inr = 29.00, 1999.00
        else:
            display_title = f"{title} - Professional Spreadsheet Template"
            tagline = f"Automated Dynamic Formula-Driven {title} for Excel & Google Sheets"
            description = f"High-performance, automated spreadsheet template designed to streamline {title.lower()} workflows."
            features = ["Instant calculation engine", "Visual interactive dashboard", "Google Sheets & Excel compatible"]
            tags = ["excel template", "spreadsheet", "dashboard", "productivity"]
            price_usd, price_inr = 24.00, 1499.00

        return ProductMetadata(
            file_path=str(self.path),
            file_name=self.path.name,
            product_type="Spreadsheet & Financial Template",
            format_category="Spreadsheets (.xlsx / .csv)",
            title=display_title,
            tagline=tagline,
            description=description,
            key_features=features,
            price_usd=price_usd,
            price_inr=price_inr,
            currency="USD",
            tags=tags,
            suggested_categories=["Personal Finance", "Spreadsheets & Templates", "Productivity"],
            recommended_channels=["Gumroad", "Lemon Squeezy", "Etsy", "Whop", "Payhip", "Cosmofeed"],
            bundle_zip_path=bundle_path
        )

    # 2. eBooks & Publications
    def _analyze_ebook(self, title: str, ext: str) -> ProductMetadata:
        bundle_path = self._ensure_bundle()
        return ProductMetadata(
            file_path=str(self.path),
            file_name=self.path.name,
            product_type="Digital eBook & Publication",
            format_category=f"eBook ({ext.upper()})",
            title=f"{title}: The Definitive Master Guide",
            tagline="Actionable Step-by-Step Playbook for Modern Practitioners",
            description=f"A comprehensive digital book breaking down proven strategies, checklists, and workflows in {title.lower()}.",
            key_features=["Readable on Kindle, iPad, Android & Desktop", "Print-ready typography", "Actionable checklists included"],
            price_usd=19.99,
            price_inr=999.00,
            currency="USD",
            tags=["ebook", "digital book", "guide", "kindle", "education", "self improvement"],
            suggested_categories=["Books & Literature", "Education & Guides", "Career & Business"],
            recommended_channels=["Gumroad", "Payhip", "Amazon KDP", "Lemon Squeezy", "Cosmofeed"],
            bundle_zip_path=bundle_path
        )

    # 3. PDF Documents & Workbooks
    def _analyze_pdf_document(self, title: str) -> ProductMetadata:
        bundle_path = self._ensure_bundle()
        return ProductMetadata(
            file_path=str(self.path),
            file_name=self.path.name,
            product_type="PDF Printable & Digital Workbook",
            format_category="PDF Printable Document",
            title=f"{title} - Printable Framework & Checklist",
            tagline="Ready-to-Print Digital Framework and Step-by-Step Blueprint",
            description=f"Clean, minimalist printable workbook and reference guide for {title.lower()}.",
            key_features=["A4 & US Letter print sizes", "Fillable digital PDF fields", "Lifetime instant access"],
            price_usd=14.99,
            price_inr=799.00,
            currency="USD",
            tags=["printable", "pdf planner", "workbook", "checklist", "productivity"],
            suggested_categories=["Printables", "Templates", "Personal Growth"],
            recommended_channels=["Etsy", "Gumroad", "Payhip", "Creative Market"],
            bundle_zip_path=bundle_path
        )

    # 4. Design Assets & UI Kits
    def _analyze_design_asset(self, title: str, ext: str) -> ProductMetadata:
        bundle_path = self._ensure_bundle()
        software_map = {
            ".fig": "Figma UI Kit & Design System",
            ".psd": "Photoshop PSD Mockup Bundle",
            ".ai": "Adobe Illustrator Vector Asset Pack",
            ".sketch": "Sketch UI Template",
            ".xd": "Adobe XD Prototype Kit",
            ".procreate": "Procreate Brush & Texture Pack"
        }
        prod_type = software_map.get(ext, "Design Asset")

        return ProductMetadata(
            file_path=str(self.path),
            file_name=self.path.name,
            product_type=prod_type,
            format_category=f"Design Asset ({ext.upper()})",
            title=f"{title} - {prod_type}",
            tagline="Pixel-Perfect, Fully Layered & Componentized Modern Creative Asset",
            description=f"Professional-grade {prod_type.lower()} with organized auto-layout components, responsive variants, and modern typography.",
            key_features=["100% Vector & Scalable", "Auto-layout & component variants", "Commercial use license included"],
            price_usd=39.00,
            price_inr=2499.00,
            currency="USD",
            tags=["ui kit", "figma", "design system", "graphic design", "creative market", "web design"],
            suggested_categories=["Design & UI/UX", "Graphics & Templates", "Web Development"],
            recommended_channels=["Creative Market", "Etsy", "Gumroad", "Lemon Squeezy", "Whop"],
            bundle_zip_path=bundle_path
        )

    # 5. Code, Scripts, SaaS Boilerplates & Bots
    def _analyze_code_script(self, title: str, ext: str) -> ProductMetadata:
        bundle_path = self._ensure_bundle()
        return ProductMetadata(
            file_path=str(self.path),
            file_name=self.path.name,
            product_type="Developer Software & Automation Script",
            format_category=f"Source Code ({ext.upper()})",
            title=f"{title} - Production Ready Automation Engine",
            tagline="Turnkey Codebase, Bot & Developer Script with Clean Modular Architecture",
            description=f"Complete production script and boilerplate for {title.lower()}. Fully documented, tested, and ready to deploy in minutes.",
            key_features=["Well-commented & typed code", "Zero config plug-and-play", "Includes Dockerfile & setup guide"],
            price_usd=49.00,
            price_inr=3499.00,
            currency="USD",
            tags=["code script", "python bot", "automation", "developer tools", "saas boilerplate", "github"],
            suggested_categories=["Software & Development", "Developer Tools", "Automation"],
            recommended_channels=["Gumroad", "Whop", "Product Hunt", "Lemon Squeezy", "CodeCanyon"],
            bundle_zip_path=bundle_path
        )

    # 6. Presentations & Pitch Decks
    def _analyze_presentation(self, title: str, ext: str) -> ProductMetadata:
        bundle_path = self._ensure_bundle()
        return ProductMetadata(
            file_path=str(self.path),
            file_name=self.path.name,
            product_type="Presentation & Pitch Deck Template",
            format_category="Slides (.pptx / .key)",
            title=f"{title} - Investor Pitch Deck & Presentation Suite",
            tagline="Clean 16:9 Modern Presentation Slides Designed for High-Stakes Storytelling",
            description=f"Institutional-grade presentation deck containing 50+ animated slides, financial charts, and problem-solution frameworks.",
            key_features=["16:9 Full HD widescreen", "Free fonts included", "Drag-and-drop image placeholders"],
            price_usd=29.00,
            price_inr=1999.00,
            currency="USD",
            tags=["pitch deck", "powerpoint template", "presentation", "keynote", "investor deck", "business slides"],
            suggested_categories=["Business & Startups", "Presentations", "Corporate Templates"],
            recommended_channels=["Etsy", "Creative Market", "Gumroad", "Payhip"],
            bundle_zip_path=bundle_path
        )

    # 7. Word & Document Templates
    def _analyze_document(self, title: str, ext: str) -> ProductMetadata:
        bundle_path = self._ensure_bundle()
        return ProductMetadata(
            file_path=str(self.path),
            file_name=self.path.name,
            product_type="Professional Document & Resume Suite",
            format_category="Word Document (.docx)",
            title=f"{title} - Professional Document & Resume Template",
            tagline="ATS-Friendly, Executive Typography and Modern Layout for Word & Docs",
            description=f"Clean, professional template designed to pass Applicant Tracking Systems (ATS) and impress clients.",
            key_features=["ATS-tested format", "Matching cover letter & portfolio pages", "Easy single-click customization"],
            price_usd=18.00,
            price_inr=999.00,
            currency="USD",
            tags=["resume template", "cv template", "word template", "job application", "career"],
            suggested_categories=["Career & Resumes", "Office Templates", "Business Documents"],
            recommended_channels=["Etsy", "Creative Market", "Gumroad", "Payhip"],
            bundle_zip_path=bundle_path
        )

    # 8. Audio & Music Samples
    def _analyze_audio(self, title: str, ext: str) -> ProductMetadata:
        bundle_path = self._ensure_bundle()
        return ProductMetadata(
            file_path=str(self.path),
            file_name=self.path.name,
            product_type="Audio Sample Pack & Sound Kit",
            format_category=f"Audio Sample ({ext.upper()})",
            title=f"{title} - Royalty-Free Audio & Sound Kit",
            tagline="24-bit 48kHz Studio Quality Sample Pack for Producers and Creators",
            description=f"Pristine studio audio pack including loops, one-shots, and MIDI files for music producers and video creators.",
            key_features=["100% Royalty-Free", "Key and BPM labeled", "Mastered for streaming & broadcast"],
            price_usd=25.00,
            price_inr=1499.00,
            currency="USD",
            tags=["sample pack", "music production", "audio loops", "sound effects", "beatmakers", "whop"],
            suggested_categories=["Music & Audio", "Sound Kits", "Creator Tools"],
            recommended_channels=["Whop", "Gumroad", "Sellfy", "Lemon Squeezy"],
            bundle_zip_path=bundle_path
        )

    # 9. Video Courses & Masterclasses
    def _analyze_video_course(self, title: str, ext: str) -> ProductMetadata:
        bundle_path = self._ensure_bundle()
        return ProductMetadata(
            file_path=str(self.path),
            file_name=self.path.name,
            product_type="Video Masterclass & Course Module",
            format_category="Video Course (.mp4)",
            title=f"{title} - Full HD Masterclass",
            tagline="In-Depth Video Training Module with Actionable Frameworks",
            description=f"Comprehensive step-by-step 1080p/4K video tutorial providing hands-on execution strategies.",
            key_features=["1080p HD video", "Audio transcript included", "Downloadable resource exercises"],
            price_usd=49.00,
            price_inr=2999.00,
            currency="USD",
            tags=["video course", "masterclass", "tutorial", "online learning", "skill building"],
            suggested_categories=["Education & Courses", "Video Tutorials", "Skill Training"],
            recommended_channels=["Gumroad", "Whop", "Lemon Squeezy", "Graphy", "TagMango", "Podia"],
            bundle_zip_path=bundle_path
        )

    # 10. 3D Models & VR Assets
    def _analyze_3d_asset(self, title: str, ext: str) -> ProductMetadata:
        bundle_path = self._ensure_bundle()
        return ProductMetadata(
            file_path=str(self.path),
            file_name=self.path.name,
            product_type="3D Asset & Game-Ready Model",
            format_category=f"3D Model ({ext.upper()})",
            title=f"{title} - Low-Poly Game-Ready 3D Asset",
            tagline="PBR Textured, Rigged & Optimized 3D Model for Unity, Unreal & Blender",
            description=f"High-fidelity 3D asset ready for game engines, VR/AR experiences, and architectural visualization.",
            key_features=["PBR 4K textures", "Clean topology & unwrapped UVs", "Multiple LODs included"],
            price_usd=35.00,
            price_inr=2499.00,
            currency="USD",
            tags=["3d model", "blender", "game asset", "unity", "unreal engine", "pbr textures"],
            suggested_categories=["3D & Game Assets", "Digital Art", "AR/VR"],
            recommended_channels=["Gumroad", "Creative Market", "Sellfy", "Whop"],
            bundle_zip_path=bundle_path
        )

    # 11. ZIP Archive
    def _analyze_zip_bundle(self, title: str) -> ProductMetadata:
        internal_exts = []
        try:
            with zipfile.ZipFile(self.path, "r") as zf:
                for info in zf.infolist():
                    sub_ext = Path(info.filename).suffix.lower()
                    if sub_ext:
                        internal_exts.append(sub_ext)
        except Exception:
            pass

        if any(e in internal_exts for e in [".xlsx", ".xls", ".xlsm"]):
            return self._analyze_spreadsheet(title, ".xlsx")
        elif any(e in internal_exts for e in [".fig", ".psd", ".ai"]):
            return self._analyze_design_asset(title, ".fig")
        elif any(e in internal_exts for e in [".py", ".js", ".ts"]):
            return self._analyze_code_script(title, ".py")
        elif any(e in internal_exts for e in [".wav", ".mp3"]):
            return self._analyze_audio(title, ".wav")

        return ProductMetadata(
            file_path=str(self.path),
            file_name=self.path.name,
            product_type="Multi-Resource Digital Bundle (ZIP)",
            format_category="ZIP Archive Bundle",
            title=f"{title} - Complete Resource Toolkit",
            tagline="All-in-One Digital Bundle with Production Files, Guides & Bonus Assets",
            description=f"Comprehensive master bundle containing ready-to-use digital templates, source files, and documentation.",
            key_features=["Instant ZIP download", "Everything in one place", "Complete commercial license"],
            price_usd=34.00,
            price_inr=2499.00,
            currency="USD",
            tags=["digital bundle", "toolkit", "starter kit", "productivity", "all in one"],
            suggested_categories=["Digital Bundles", "Templates & Kits", "Productivity"],
            recommended_channels=["Gumroad", "Lemon Squeezy", "Whop", "Payhip", "Etsy"],
            bundle_zip_path=str(self.path)
        )

    def _analyze_generic(self, title: str, ext: str) -> ProductMetadata:
        bundle_path = self._ensure_bundle()
        return ProductMetadata(
            file_path=str(self.path),
            file_name=self.path.name,
            product_type="Digital Download Asset",
            format_category="Generic Digital Asset",
            title=f"{title} - Premium Digital Asset",
            tagline="High-Value Digital Download with Full Commercial Rights",
            description=f"Premium digital asset for {title.lower()}.",
            key_features=["Instant download delivery", "Lifetime ownership"],
            price_usd=25.00,
            price_inr=1499.00,
            currency="USD",
            tags=["digital asset", "download", "premium template"],
            suggested_categories=["Digital Goods", "Templates"],
            recommended_channels=["Gumroad", "Payhip", "Sellfy", "Lemon Squeezy"],
            bundle_zip_path=bundle_path
        )

    def _ensure_bundle(self) -> str:
        bundle_zip = self.path.parent / f"{self.path.stem}_Bundle.zip"
        if not bundle_zip.exists():
            with zipfile.ZipFile(bundle_zip, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.write(self.path, self.path.name)
        return str(bundle_zip)
