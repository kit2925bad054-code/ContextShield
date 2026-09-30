import re
from urllib.parse import urlparse


# ============================================================
# CATEGORY KEYWORDS
# ============================================================

CATEGORY_WORDS = {

    "Banking": [
        "bank",
        "account",
        "transaction",
        "upi",
        "refund",
        "otp",
        "pin",
        "cvv",
        "sbi",
        "hdfc",
        "icici",
        "axis"
    ],

    "Delivery": [
        "delivery",
        "courier",
        "parcel",
        "package",
        "shipment",
        "customs",
        "tracking"
    ],

    "Shopping": [
        "order",
        "shopping",
        "purchase",
        "amazon",
        "flipkart",
        "offer",
        "discount"
    ],

    "Job": [
        "job",
        "interview",
        "salary",
        "hiring",
        "recruiter",
        "vacancy",
        "work from home"
    ],

    "Investment": [
        "investment",
        "invest",
        "profit",
        "trading",
        "crypto",
        "returns",
        "double your money"
    ],

    "Education": [
        "college",
        "university",
        "course",
        "scholarship",
        "exam",
        "admission",
        "certificate"
    ],

    "Government": [
        "government",
        "income tax",
        "tax",
        "police",
        "court",
        "aadhaar",
        "pan",
        "official notice"
    ],

    "Account": [
        "account",
        "login",
        "password",
        "verify",
        "verification",
        "suspended",
        "blocked"
    ],

    "Romance": [
        "love",
        "dating",
        "relationship",
        "romance",
        "gift"
    ]
}


# ============================================================
# SCAM SIGNAL KEYWORDS
# ============================================================

URGENCY = [
    "urgent",
    "immediately",
    "now",
    "within",
    "minutes",
    "final notice",
    "last chance",
    "final chance",
    "act fast",
    "expires",
    "expire",
    "deadline",
    "limited time",
    "12 hours",
    "24 hours",
    "30 minutes",
    "today"
]


THREATS = [
    "blocked",
    "suspended",
    "closed",
    "terminated",
    "legal action",
    "penalty",
    "fine",
    "permanently",
    "disable",
    "deactivated"
]


CREDENTIALS = [
    "otp",
    "password",
    "pin",
    "cvv",
    "verification code",
    "security code",
    "login details",
    "card details",
    "bank details"
]


PAYMENTS = [
    "pay",
    "payment",
    "fee",
    "rupees",
    "rs.",
    "₹",
    "money",
    "transfer",
    "send",
    "deposit",
    "reactivation fee",
    "processing fee",
    "registration fee",
    "service fee"
]


SUSPICIOUS = [
    "click",
    "verify",
    "claim",
    "reward",
    "prize",
    "winner",
    "free",
    "refund",
    "reactivate",
    "security check",
    "account-security",
    "offer",
    "exclusive",
    "congratulations"
]


# ============================================================
# URL SHORTENERS
# ============================================================

SHORTENERS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "is.gd",
    "cutt.ly"
}


# ============================================================
# MATCH KEYWORDS
# ============================================================

def _matches(text, words):

    text = text or ""

    t = text.lower()

    return [
        word
        for word in words
        if word.lower() in t
    ]


# ============================================================
# LANGUAGE DETECTION
# ============================================================

def detect_language(text):

    text = text or ""

    # Tamil Unicode block
    if re.search(r"[\u0B80-\u0BFF]", text):
        return "Tamil"

    # Simple Tanglish detection
    tanglish_words = [
        "enna",
        "unga",
        "ungal",
        "irukku",
        "panunga",
        "pannunga",
        "varum",
        "send",
        "bro",
        "akka",
        "anna"
    ]

    lower_text = text.lower()

    if any(word in lower_text.split() for word in tanglish_words):
        return "Tanglish"

    return "English"


# ============================================================
# URL EXTRACTION
# ============================================================

def extract_urls(text):

    text = text or ""

    return re.findall(
        r"https?://[^\s<>\"']+",
        text,
        flags=re.I
    )


# ============================================================
# CATEGORY CLASSIFICATION
# ============================================================

def classify(text):

    text = text or ""

    low = text.lower()

    scores = {}

    for category, words in CATEGORY_WORDS.items():

        scores[category] = sum(
            1
            for word in words
            if word.lower() in low
        )

    best = max(
        scores,
        key=scores.get
    )

    if scores[best] == 0:
        return "General"

    return best


# ============================================================
# URL ANALYSIS
# ============================================================

def analyze_url(url):

    try:

        parsed = urlparse(url)

        host = (
            parsed.hostname or ""
        ).lower()

        findings = []

        risk = 0

        # ----------------------------------------------------
        # HTTPS
        # ----------------------------------------------------

        if parsed.scheme != "https":

            findings.append(
                "Uses a non-HTTPS link."
            )

            risk += 12

        # ----------------------------------------------------
        # IP ADDRESS
        # ----------------------------------------------------

        if re.fullmatch(
            r"\d{1,3}(?:\.\d{1,3}){3}",
            host
        ):

            findings.append(
                "Uses an IP address instead of a normal domain."
            )

            risk += 25

        # ----------------------------------------------------
        # MULTIPLE HYPHENS
        # ----------------------------------------------------

        if host.count("-") >= 2:

            findings.append(
                "Domain contains multiple hyphens."
            )

            risk += 12

        # ----------------------------------------------------
        # LONG DOMAIN
        # ----------------------------------------------------

        if len(host) > 35:

            findings.append(
                "Domain name is unusually long."
            )

            risk += 10

        # ----------------------------------------------------
        # URL SHORTENER
        # ----------------------------------------------------

        if any(
            host == shortener
            or host.endswith("." + shortener)
            for shortener in SHORTENERS
        ):

            findings.append(
                "Uses a URL shortener."
            )

            risk += 15

        # ----------------------------------------------------
        # SUSPICIOUS DOMAIN WORDS
        # ----------------------------------------------------

        suspicious_domain_words = [
            "account-security",
            "verify-account",
            "login-secure",
            "claim-reward",
            "free-gift",
            "secure-login",
            "payment-verify",
            "account-verify"
        ]

        found_words = [
            word
            for word in suspicious_domain_words
            if word in host
        ]

        if found_words:

            findings.append(
                "Domain contains suspicious security or reward wording."
            )

            risk += min(
                25,
                len(found_words) * 10
            )

        # ----------------------------------------------------
        # DOMAIN DIGITS
        # ----------------------------------------------------

        digit_count = len(
            re.findall(r"\d", host)
        )

        if digit_count >= 4:

            findings.append(
                "Domain contains an unusual number of digits."
            )

            risk += 8

        return risk, findings

    except Exception:

        return (
            20,
            ["The URL could not be parsed safely."]
        )


# ============================================================
# MAIN ANALYSIS ENGINE
# ============================================================

def analyze(
    text,
    input_type="message"
):

    text = text or ""

    # --------------------------------------------------------
    # BASIC EXTRACTION
    # --------------------------------------------------------

    language = detect_language(text)

    urls = extract_urls(text)

    category = classify(text)

    # --------------------------------------------------------
    # DETECT SIGNALS
    # --------------------------------------------------------

    urgency = _matches(
        text,
        URGENCY
    )

    threats = _matches(
        text,
        THREATS
    )

    credentials = _matches(
        text,
        CREDENTIALS
    )

    payments = _matches(
        text,
        PAYMENTS
    )

    suspicious = _matches(
        text,
        SUSPICIOUS
    )

    # --------------------------------------------------------
    # INITIAL SCORE
    # --------------------------------------------------------

    score = 0

    reasons = []

    # --------------------------------------------------------
    # URGENCY
    # --------------------------------------------------------

    if urgency:

        score += min(
            15,
            5 + len(urgency) * 3
        )

        reasons.append(
            "Creates urgency or pressure to act quickly."
        )

    # --------------------------------------------------------
    # THREATS
    # --------------------------------------------------------

    if threats:

        score += min(
            20,
            8 + len(threats) * 4
        )

        reasons.append(
            "Uses a threat such as blocking, suspension, penalty, or legal action."
        )

    # --------------------------------------------------------
    # CREDENTIALS
    # --------------------------------------------------------

    if credentials:

        score += 25

        reasons.append(
            "Requests sensitive credentials or verification codes."
        )

    # --------------------------------------------------------
    # PAYMENT
    # --------------------------------------------------------

    if payments:

        score += 22

        reasons.append(
            "Requests money, payment, transfer, or a fee."
        )

    # --------------------------------------------------------
    # SUSPICIOUS LANGUAGE
    # --------------------------------------------------------

    if suspicious:

        score += min(
            12,
            len(suspicious) * 3
        )

        reasons.append(
            "Contains suspicious request or reward language."
        )

    # --------------------------------------------------------
    # CATEGORY SIGNAL
    # --------------------------------------------------------

    if category != "General":

        score += 4

    # --------------------------------------------------------
    # URL ANALYSIS
    # --------------------------------------------------------

    url_risk = 0

    for url in urls:

        risk, findings = analyze_url(url)

        url_risk += risk

        reasons.extend(findings)

    score += min(
        35,
        url_risk
    )

    # --------------------------------------------------------
    # COMBINATION / ESCALATION SIGNALS
    # --------------------------------------------------------

    groups = sum(
        bool(x)
        for x in [
            urgency,
            threats,
            credentials,
            payments,
            urls
        ]
    )

    # --------------------------------------------------------
    # URGENCY + PAYMENT
    # --------------------------------------------------------

    if urgency and payments:

        score += 20

        reasons.append(
            "Combines urgent pressure with a request for payment or money."
        )

    # --------------------------------------------------------
    # THREAT + URGENCY
    # --------------------------------------------------------

    if threats and urgency:

        score += 12

        reasons.append(
            "Combines a threat with strong time pressure."
        )

    # --------------------------------------------------------
    # PAYMENT + URL
    # --------------------------------------------------------

    if payments and urls:

        score += 15

        reasons.append(
            "Combines a money request with an external link."
        )

    # --------------------------------------------------------
    # CREDENTIAL + URL
    # --------------------------------------------------------

    if credentials and urls:

        score += 12

        reasons.append(
            "Combines a credential request with an external link."
        )

    # --------------------------------------------------------
    # PAYMENT + SUSPICIOUS LANGUAGE
    # --------------------------------------------------------

    if payments and suspicious:

        score += 12

        reasons.append(
            "Combines a money request with suspicious offer or reward language."
        )

    # --------------------------------------------------------
    # URGENCY + SUSPICIOUS LANGUAGE
    # --------------------------------------------------------

    if urgency and suspicious:

        score += 10

        reasons.append(
            "Uses urgency together with suspicious request or reward language."
        )

    # --------------------------------------------------------
    # THREAT + PAYMENT + CREDENTIAL
    # --------------------------------------------------------

    if threats and payments and credentials:

        score += 25

        reasons.append(
            "Combines a threat, payment request, and credential request."
        )

    # --------------------------------------------------------
    # MULTIPLE INDEPENDENT INDICATORS
    # --------------------------------------------------------

    if groups >= 3:

        score += 10

        reasons.append(
            "Several independent warning signals appear together."
        )

    if groups >= 4:

        score += 15

        reasons.append(
            "Multiple independent scam indicators appear together."
        )

    # --------------------------------------------------------
    # REWARD + PAYMENT
    # --------------------------------------------------------

    if payments and suspicious:

        score += 5

        reasons.append(
            "The message combines a financial request with an offer or reward."
        )

    # --------------------------------------------------------
    # CRITICAL-SIGNAL OVERRIDE
    # --------------------------------------------------------

    critical = sum(
        bool(x)
        for x in [
            threats,
            payments,
            credentials,
            urls
        ]
    )

    # Clear combination of several critical indicators
    if critical >= 3:

        score = max(
            score,
            75
        )

    # Payment + external link
    elif payments and urls:

        score = max(
            score,
            55
        )

    # --------------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------------

    score = min(
        100,
        max(0, score)
    )

    # --------------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------------

    if score >= 75:

        level = "HIGH"

    elif score >= 40:

        level = "MEDIUM"

    else:

        level = "LOW"

    # --------------------------------------------------------
    # FALLBACK REASON
    # --------------------------------------------------------

    if not reasons:

        reasons = [
            "No strong scam indicators were detected in this input."
        ]

    # Remove duplicate reasons
    reasons = list(
        dict.fromkeys(reasons)
    )

    # --------------------------------------------------------
    # SAFE ACTION
    # --------------------------------------------------------

    if level == "HIGH":

        action = (
            "Do not click, pay, reply, or share OTP/password/PIN. "
            "Open the official service app or website yourself."
        )

    elif level == "MEDIUM":

        action = (
            "Pause before responding. "
            "Independently verify the sender, request, "
            "and website through an official channel."
        )

    else:

        action = (
            "No strong scam indicators were detected, "
            "but verify important requests through an "
            "independently opened official channel."
        )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    return {

        "risk_score": score,

        "risk_level": level,

        "category": category,

        "language": language,

        "reasons": reasons,

        "safe_action": action,

        "official_url": None,

        "input_type": input_type,

        "engine": "rule"
    }