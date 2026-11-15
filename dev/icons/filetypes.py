"""File type icons like a macOS document: a white page with a folded corner, a
grey symbol for the kind of file and the extension on a coloured label below.
One per Breeze mimetype name; the symbol comes from our line drawings
(dev/icons/src), the label from the name. Used by dev/gen-icons.py.
"""
import re
from pathlib import Path

import folders

BREEZE = Path("/usr/share/icons/breeze/mimetypes")
PAGE = "M30 10 H82 L104 32 V112 a6 6 0 0 1 -6 6 H30 a6 6 0 0 1 -6 -6 V16 a6 6 0 0 1 6 -6 Z"
FOLD = "M82 10 V26 a6 6 0 0 0 6 6 H104 Z"
GLYPH = "#8a8a90"

# Kinds of file, first match wins: (name pattern, symbol drawing, label colour).
KINDS = [
    (r"pdf", "acrobat", "#e5413a"),
    (r"^font|-font|fonts-", "format-text-bold", "#5e5ce6"),
    (r"x-iso|efi.iso|squashfs|x-cue$|x-cda$|cd-image|disk-image|diskimage|raw-disk|vmdk|qcow|virtualbox-v", "media-optical", "#0a84ff"),
    (r"rpm|deb$|-deb|flatpak|appimage|snap|android-package|x-msi|package|x-apk", "archive-insert", "#a05ad6"),
    (r"zip|-tar|x-tar|-rar|\.rar|7z|compress|gzip|bzip|-xz|zstd|lzma|lzip|lz4|cpio|archive|x-cab|lha|arj|x-ace|x-ar$|x-jar|java-archive", "folder-tar", "#a2845e"),
    (r"pgp|gpg|x509|pkcs|pkix|keygroup|vpn-settings|-pem|keyring|encrypted|-key$|certificate|x-java-keystore", "folder-locked", "#6e6e73"),
    (r"spreadsheet|excel|calc|wps-office.xl|applix-spreadsheet|csv|gnumeric|x-office-spreadsheet|-ods$|tab-separated", "folder-table", "#1f9d55"),
    (r"presentation|powerpoint|wps-office.p|impress|x-office-presentation|slide", "folder-presentation", "#e8590c"),
    (r"drawing|draw|illustrator|scribus|opendocument.chart|opendocument.image|x-office-drawing|graphics|inkscape|vnd.visio|x-kontour|karbon", "folder-drawing", "#14a3a3"),
    (r"database|sqlite|ms-access|kexi|x-office-database|libreoffice-base|x-sql$", "folder-database", "#2fa4d8"),
    (r"formula|mathml|x-tex$|latex", "folder-calculate", "#2b7cd3"),
    (r"epub|mobi|fictionbook|djvu|comicbook|x-cb[rz7t]|ebook|audiobook", "bookmarks", "#c9772f"),
    (r"message|mbox|msoutlook|stardivision.mail|rfc822|x-mail|ms-outlook|vnd.ms-tnef", "mail-message", "#3a8ee6"),
    (r"calendar|icalendar|x-vcalendar", "view-calendar", "#e5413a"),
    (r"vcard|x-vcard|address-book|contact", "address-book-new", "#8e8e93"),
    (r"msword|ms-word|wps-office.do|applix-word|sxw|msonenote|postscript|dvi$|x-chm|wordprocessing|opendocument.text|oasis-text|libreoffice-text|x-office-document|rtf|abiword|kword|vnd.wordperfect|master-document", "folder-documents", "#2b7cd3"),
    (r"^image-|x-office-photo", "folder-pictures", "#28b14c"),
    (r"^audio-|application-ogg|audacity|x-office-sound|playlist|mpegurl", "folder-music", "#ff375f"),
    (r"^video-|x-office-video|x-flash-video|x-matroska|realmedia", "folder-videos", "#ff8a00"),
    (r"executable|sharedlib|x-object|ms-dos|msdownload|x-desktop|shellscript|x-sh$|x-csh|x-bat|x-perl|x-ruby|x-python-bytecode|x-elf|x-mach|x-core|x-pe", "system-run", "#3a3a3c"),
    (r"text-x-generic|readme|x-log$|copying|authors|changelog|text-x-install|x-nfo|text-plain", "folder-documents", "#8e8e93"),
    (r"^text-x-|^text-html|css|javascript|json|xml|x-php|x-yaml|toml|x-qml|-x-python|x-shellscript|x-diff|x-patch|makefile|cmake|x-source|x-java$|x-kotlin|x-rust|x-go|x-typescript|webassembly|x-awk|gdscript|relaxng|application-sql", "format-text-code", "#5e5ce6"),
    (r"^text-|x-office-|markdown|x-log|readme|plain", "folder-documents", "#8e8e93"),
]
GENERIC = ("folder-documents", "#8e8e93")

# Labels that the name does not spell out plainly.
LABELS = {
    "image-jpeg": "JPG", "image-svg+xml": "SVG", "image-svg+xml-compressed": "SVGZ", "image-x-xcf": "XCF",
    "image-vnd.adobe.photoshop": "PSD", "image-x-icon": "ICO", "image-vnd.microsoft.icon": "ICO",
    "image-x-portable-bitmap": "PBM", "image-x-portable-pixmap": "PPM", "image-x-portable-graymap": "PGM",
    "audio-mpeg": "MP3", "audio-x-vorbis+ogg": "OGG", "audio-x-flac+ogg": "OGG", "audio-x-speex+ogg": "OGG",
    "audio-x-ms-wma": "WMA", "audio-x-wav": "WAV", "audio-x-mpegurl": "M3U", "audio-x-scpls": "PLS",
    "audio-x-aiff": "AIFF", "audio-mp4": "M4A", "audio-x-m4b": "M4B", "audio-midi": "MIDI",
    "video-x-matroska": "MKV", "video-quicktime": "MOV", "video-x-msvideo": "AVI", "video-x-ms-wmv": "WMV",
    "video-mpeg": "MPG", "video-x-flv": "FLV", "video-x-ogm+ogg": "OGM", "video-ogg": "OGV",
    "video-x-theora+ogg": "OGV", "video-3gpp": "3GP", "video-mp2t": "TS",
    "text-x-c++src": "C++", "text-x-csrc": "C", "text-x-chdr": "H", "text-x-c++hdr": "HPP", "text-x-c": "C",
    "text-x-python": "PY", "text-x-python3": "PY", "text-x-javascript": "JS", "application-javascript": "JS",
    "text-x-typescript": "TS", "text-x-makefile": "MAKE", "text-x-cmake": "CMAKE", "text-x-csharp": "CS",
    "text-x-ruby": "RB", "text-x-rust": "RS", "text-x-perl": "PL", "text-x-script": "SH",
    "application-x-shellscript": "SH", "text-x-markdown": "MD", "text-markdown": "MD", "text-plain": "TXT",
    "text-x-generic": "TXT", "text-x-log": "LOG", "text-html": "HTML", "text-css": "CSS", "text-csv": "CSV",
    "text-x-patch": "DIFF", "text-x-diff": "DIFF", "text-x-tex": "TEX", "text-x-qml": "QML",
    "text-x-kotlin": "KT", "text-x-objcsrc": "M", "text-x-sql": "SQL", "application-sql": "SQL",
    "text-calendar": "ICS", "text-vcard": "VCF", "text-x-vcard": "VCF", "text-rtf": "RTF",
    "text-x-readme": "TXT", "text-x-copying": "TXT", "text-x-authors": "TXT", "text-x-changelog": "TXT",
    "text-x-install": "TXT", "text-xml": "XML", "application-xml": "XML", "application-json": "JSON",
    "text-x-yaml": "YAML", "application-x-yaml": "YAML", "application-toml": "TOML",
    "application-msword": "DOC", "application-vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCX",
    "application-vnd.ms-excel": "XLS", "application-vnd.openxmlformats-officedocument.spreadsheetml.sheet": "XLSX",
    "application-vnd.ms-powerpoint": "PPT",
    "application-vnd.openxmlformats-officedocument.presentationml.presentation": "PPTX",
    "application-vnd.oasis.opendocument.text": "ODT", "application-vnd.oasis.opendocument.spreadsheet": "ODS",
    "application-vnd.oasis.opendocument.presentation": "ODP", "application-vnd.oasis.opendocument.graphics": "ODG",
    "application-vnd.oasis.opendocument.formula": "ODF", "application-vnd.oasis.opendocument.database": "ODB",
    "application-x-7z-compressed": "7Z", "application-x-compressed-tar": "TGZ", "application-gzip": "GZ",
    "application-x-gzip": "GZ", "application-x-bzip-compressed-tar": "TBZ", "application-x-bzip": "BZ2",
    "application-x-xz-compressed-tar": "TXZ", "application-x-xz": "XZ", "application-x-zstd-compressed-tar": "TZST",
    "application-zstd": "ZST", "application-x-rar": "RAR", "application-vnd.rar": "RAR", "application-x-tar": "TAR",
    "application-zip": "ZIP", "application-x-zip": "ZIP", "application-x-java-archive": "JAR",
    "application-x-cd-image": "ISO", "application-vnd.efi.iso": "ISO", "application-vnd.efi.img": "IMG", "application-x-iso9660-image": "ISO", "application-x-rpm": "RPM",
    "application-x-deb": "DEB", "application-vnd.debian.binary-package": "DEB", "application-vnd.flatpak": "FLATPAK",
    "application-vnd.flatpak.ref": "FLATPAK", "application-vnd.flatpak.repo": "FLATPAK",
    "application-x-appimage": "APPIMAGE", "application-vnd.appimage": "APPIMAGE", "application-x-snap": "SNAP",
    "application-vnd.android.package-archive": "APK", "android-package-archive": "APK",
    "application-x-executable": "EXE", "application-x-ms-dos-executable": "EXE", "application-x-msdownload": "EXE",
    "application-x-sharedlib": "SO", "application-x-object": "O", "application-x-desktop": "DESKTOP",
    "application-x-bittorrent": "TORRENT", "application-pgp-encrypted": "PGP", "application-pgp-keys": "PGP",
    "application-pgp-signature": "SIG", "application-epub+zip": "EPUB", "application-x-mobipocket-ebook": "MOBI",
    "application-x-fictionbook+xml": "FB2", "message-rfc822": "EML", "application-mbox": "MBOX",
    "font-ttf": "TTF", "font-otf": "OTF", "application-x-font-ttf": "TTF", "application-x-font-otf": "OTF",
    "font-woff": "WOFF", "font-woff2": "WOFF", "application-x-sqlite3": "DB", "application-vnd.sqlite3": "DB",
    "application-x-php": "PHP", "application-x-perl": "PL", "application-x-ruby": "RB",
}
SKIP = re.compile(r"^inode-|^unknown$")


def names():
    """Every Breeze mimetype name at any size."""
    found = {f.stem for f in BREEZE.glob("*/*.svg")}
    return sorted(n for n in found if not SKIP.match(n))


def kind(name):
    for pattern, glyph, colour in KINDS:
        if re.search(pattern, name):
            return glyph, colour
    return GENERIC


def label(name):
    if name in LABELS:
        return LABELS[name]
    word = re.sub(r"^(application|text|image|audio|video|font|message|x-office)-", "", name)
    word = re.sub(r"^(x-|vnd\.)+", "", word)
    word = re.split(r"[-+.]", word)[0]
    return word.upper() if 0 < len(word) <= 4 else ""


def page(glyph, colour, text):
    pill = ""
    if text:
        size = 14 if len(text) <= 4 else 11
        w = 12 + size * 0.68 * len(text)
        pill = (f'  <rect x="{64 - w / 2:.1f}" y="88" width="{w:.1f}" height="22" rx="6" fill="{colour}"/>\n'
                f'  <text x="64" y="{104 if size == 14 else 103}" text-anchor="middle" font-family="Inter, sans-serif" '
                f'font-weight="700" font-size="{size}" fill="#ffffff">{text}</text>\n')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">\n'
            f'  <path d="{PAGE}" fill="#fbfbfd" stroke="#000" stroke-opacity="0.18" stroke-width="1.2"/>\n'
            f'  <path d="{FOLD}" fill="#e2e2e8" stroke="#000" stroke-opacity="0.12" stroke-width="1"/>\n'
            f'{glyph}{pill}</svg>\n')


def build(out, ours):
    """Write the file type icons into out; ours(name) gives our drawing of a name."""
    out.mkdir(parents=True, exist_ok=True)
    glyphs = {}
    for name in names():
        drawing, colour = kind(name)
        if drawing not in glyphs:
            text = ours(drawing)
            glyphs[drawing] = folders.emboss(folders.strip_folder(text), GLYPH, (64, 56), 38, 1) if text else ""
        text = label(name)
        if len(text) > 7:
            text = ""
        (out / f"{name}.svg").write_text(page(glyphs[drawing], colour, text))
    return names()
