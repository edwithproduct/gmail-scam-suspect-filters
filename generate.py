#!/usr/bin/env python3
"""Build a Gmail mailFilters.xml from Taiwan scam subject phrases.

Exception domains come from govorgan.csv (almost all *.gov.tw / edu.tw),
plus gov.taipei which Taipei City uses for email and is missing from the CSV.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from urllib.parse import urlparse
from xml.sax.saxutils import quoteattr

CSV_PATH = Path(__file__).with_name("data") / "govorgan.csv"
OUT_PATH = Path(__file__).with_name("mailFilters.xml")
LABEL = "scam-suspect"

# Official sending domains for platforms Taiwan users actually hear from.
# Do NOT add personal mailbox providers (gmail.com, yahoo.com.tw, hotmail.com,
# outlook.com, icloud.com). Scam mail often comes from those, and adding them
# would punch a hole in every rule.
PLATFORM_DOMAINS = [
    # Messaging / accounts
    "line.me",
    "linecorp.com",
    "google.com",
    "apple.com",
    "microsoft.com",
    "facebookmail.com",
    "facebook.com",
    "instagram.com",
    # Shopping
    "shopee.tw",
    "shopee.com",
    "pchome.com.tw",
    "momoshop.com.tw",
    "momo.com.tw",
    "books.com.tw",
    "ruten.com.tw",
    "rakuten.com.tw",
    "foodpanda.com",
    "foodpanda.tw",
    "uber.com",
    "ubereats.com",
    "klook.com",
    "kkday.com",
    "eztravel.com.tw",
    "trip.com",
    "ctrip.com",
    "airbnb.com",
    "airbnb.com.tw",
    # Jobs
    "104.com.tw",
    "1111.com.tw",
    "yes123.com.tw",
    "518.com.tw",
    "cake.me",
    "cakeresume.com",
    # Entertainment
    "showtimes.com.tw",
    "vscinemas.com.tw",
    # Telecom
    "cht.com.tw",
    "taiwanmobile.com",
    "fetnet.net",
    # Convenience / logistics
    "family.com.tw",
    "famiport.com.tw",
    "7-11.com.tw",
    "7-eleven.com.tw",
    "presco.com.tw",
    "ibon.com.tw",
    "hilife.com.tw",
    "okmart.com.tw",
    "hct.com.tw",
    "t-cat.com.tw",
    "thsrc.com.tw",
    # Payments / retail
    "jkos.com",
    "pxmart.com.tw",
    "carrefour.com.tw",
    "costco.com.tw",
    "cpc.com.tw",
    "taipower.com.tw",
    "easycard.com.tw",
    # Banks (real「帳戶異常」mail uses these)
    "bot.com.tw",
    "landbank.com.tw",
    "firstbank.com.tw",
    "hncb.com.tw",
    "chb.com.tw",
    "mega.com.tw",
    "fubon.com",
    "fubon.com.tw",
    "cathaybk.com.tw",
    "ctbcbank.com",
    "esunbank.com.tw",
    "esunbank.com",
    "taishinbank.com.tw",
    "sinopac.com",
    "tcb-bank.com.tw",
    "linebank.com.tw",
    "rakuten-bank.com.tw",
    "nextbank.com.tw",
]

# Distinctive subject phrases from 165 / MOF / CIB / TFC / Chunghwa Post.
# Skip short words like 訂單、發票、驗證 — too many false positives.
SUBJECTS = [
    "載具歸戶異常",
    "載具信息核實",
    "載具資料有誤",
    "發票中獎通知",
    "中獎需更新載具",
    "獎金自動入帳",
    "稅務退稅通知",
    "退稅補件",
    "補繳關稅",
    "補繳運費",
    "包裹無法寄達",
    "交通違規逾期",
    "誤設分期付款",
    "重複訂購與定期扣款",
    "自動請款",
    "通報聯徵",
    "通報金融聯合徵信",
    "止付驗證",
    "中止綁定",
    "金流驗證",
    "已攔阻可疑登入",
    "帳戶最近在多台裝置上使用",
    "信用購",
]


def host_from_url(url: str) -> str | None:
    url = (url or "").strip().strip('"')
    if not url:
        return None
    if not re.match(r"^https?://", url, re.I):
        url = "http://" + url
    parsed = urlparse(url)
    host = (parsed.netloc or parsed.path).split("@")[-1].split(":")[0].split("/")[0]
    host = host.lower()
    if host.startswith("www."):
        host = host[4:]
    return host or None


def exception_query(csv_path: Path) -> str:
    """Gmail from:gov.tw matches *.gov.tw, so CSV rows collapse to a few parents."""
    extras: set[str] = set()
    if csv_path.exists():
        with csv_path.open(newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                host = host_from_url(row.get("網址") or "")
                if not host:
                    continue
                if host.endswith(".gov.tw") or host == "gov.tw":
                    continue
                extras.add(host)

    # Taipei email moved off taipei.gov.tw; CSV still lists the old website.
    extras.add("gov.taipei")
    extras.add("edu.tw")
    extras.update(PLATFORM_DOMAINS)

    parts = ["gov.tw"] + sorted(extras)
    return "from:(" + " OR ".join(parts) + ")"


def entry_xml(subject: str, negated: str) -> str:
    return f"""  <entry>
    <category term='filter'></category>
    <title>Mail Filter</title>
    <content></content>
    <apps:property name='subject' value={quoteattr(subject)}/>
    <apps:property name='doesNotHaveTheWord' value={quoteattr(negated)}/>
    <apps:property name='shouldArchive' value='true'/>
    <apps:property name='label' value={quoteattr(LABEL)}/>
    <apps:property name='sizeOperator' value='s_sl'/>
    <apps:property name='sizeUnit' value='s_smb'/>
  </entry>"""


def main() -> None:
    negated = exception_query(CSV_PATH)
    body = "\n".join(entry_xml(s, negated) for s in SUBJECTS)
    xml = f"""<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns='http://www.w3.org/2005/Atom' xmlns:apps='http://schemas.google.com/apps/2006'>
  <title>Mail Filters</title>
{body}
</feed>
"""
    OUT_PATH.write_text(xml, encoding="utf-8")
    print(f"wrote {OUT_PATH}")
    print(f"filters {len(SUBJECTS)}")
    print(f"exception_chars {len(negated)}")
    print(f"exception {negated}")


if __name__ == "__main__":
    main()
