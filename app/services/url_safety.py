import re
import os
import logging
import joblib
from urllib.parse import urlparse

from app.config import settings

logger = logging.getLogger(__name__)

MALICIOUS_PATTERNS = [
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", 
    r"\.exe\b",
    r"\.bat\b",
    r"\.cmd\b",
    r"\.scr\b",
    r"\.msi\b",
    r"\.vbs\b",
    r"\.ps1\b",
    r"data:text/html",
    r"javascript:",
    r"phishing",
    r"login.*\.php\?",
    r"account.*verify",
    r"secure.*update.*\.html",
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in MALICIOUS_PATTERNS]

BLOCKED_DOMAINS = {
    "evil.com",
    "malware.com",
    "phishing-site.com",
    "fake-bank.com",
    "scam-site.net",
    "login-verify.com",
    "account-update.com",
    "secure-login.net",
    "free-prize.com",
    "click-here-now.com",
}

ADULT_DOMAINS = {
    "pornhub.com",
    "xvideos.com",
    "xnxx.com",
    "redtube.com",
    "youporn.com",
    "xhamster.com",
    "xhamster46.com",
    "xhamster46.desi",
    "spankbang.com",
    "tube8.com",
    "keezmovies.com",
    "sex.com",
    "adult.com",
    "xxx.com",
    "porn.com",
}

SAFE_DOMAINS = {
    "youtube.com",
    "youtu.be",
    "google.com",
    "github.com",
    "stackoverflow.com",
    "reddit.com",
    "wikipedia.org",
    "twitter.com",
    "facebook.com",
    "linkedin.com",
    "medium.com",
    "dev.to",
}


class URLSafetyService:

    def __init__(self):
        self._ml_model = None
        self._model_loaded = False

    def _load_ml_model(self):
        if self._model_loaded:
            return

        model_path = settings.ml_model_path
        if os.path.exists(model_path):
            try:
                self._ml_model = joblib.load(model_path)
                logger.info(f"ML safety model loaded from {model_path}")
            except Exception as e:
                logger.warning(f"Failed to load ML model: {e}")
        else:
            logger.info("No ML model found — using heuristic-only detection")

        self._model_loaded = True

    def check_regex_rules(self, url: str) -> tuple[bool, str]:
      
        for pattern in COMPILED_PATTERNS:
            if pattern.search(url):
                return False, f"URL matches malicious pattern: {pattern.pattern}"
        return True, "Passed regex rules"

    def check_domain_blocklist(self, url: str) -> tuple[bool, str]:
    
        try:
            parsed = urlparse(url)
            domain = parsed.hostname or ""
            # Check exact match and subdomain match
            domain_parts = domain.split(".")
            for i in range(len(domain_parts)):
                check_domain = ".".join(domain_parts[i:])
                if check_domain in BLOCKED_DOMAINS:
                    return False, f"Domain '{check_domain}' is on the blocklist"
        except Exception:
            pass
        return True, "Domain is clean"

    def _extract_features(self, url: str) -> list[float]:
   
        parsed = urlparse(url)
        domain = parsed.hostname or ""
        path = parsed.path or ""

        suspicious_tlds = {".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".pw"}

        features = [
            len(url),
            url.count("."),
            url.count("-"),
            sum(c.isdigit() for c in url),
            1.0 if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", domain) else 0.0,
            path.count("/"),
            1.0 if parsed.query else 0.0,
            sum(not c.isalnum() and c not in "/:.-_" for c in url),
            len(domain),
            1.0 if any(domain.endswith(tld) for tld in suspicious_tlds) else 0.0,
        ]
        return features

    def get_ml_score(self, url: str) -> float:
 
        self._load_ml_model()

        if self._ml_model is None:
            return 1.0  # No model available, assume safe

        try:
            features = [self._extract_features(url)]
            # Predict probability of being safe
            proba = self._ml_model.predict_proba(features)
            # Index 1 = probability of "safe" class
            return float(proba[0][1]) if proba.shape[1] > 1 else float(proba[0][0])
        except Exception as e:
            logger.warning(f"ML scoring failed: {e}")
            return 1.0

    def check_apk_malware(self, url: str) -> tuple[bool, str]:
    
        url_lower = url.lower()
        
        # Check for direct APK files
        if url_lower.endswith(".apk"):
            return False, "URL is a direct APK (Android app) download — potential malware risk"
        
        apk_hosting_patterns = [
            r"apk-.*\.com",
            r".*apk.*download",
            r".*apk.*host",
            r"modapk",
            r"apk\.co",
            r"apkpure",
            r"apkmonk",
        ]
        
        for pattern in apk_hosting_patterns:
            if re.search(pattern, url_lower):
                return False, "URL appears to be from APK/malware hosting site"
        
        return True, "No APK/malware indicators detected"

    def check_adult_content(self, url: str) -> tuple[bool, str]:
     
        try:
            parsed = urlparse(url)
            domain = parsed.hostname or ""
            url_lower = url.lower()
            
            domain_parts = domain.split(".")
            for i in range(len(domain_parts)):
                check_domain = ".".join(domain_parts[i:])
                if check_domain in ADULT_DOMAINS:
                    return False, "⚠️ ADULT CONTENT DETECTED — This URL leads to adult/NSFW website"
            
            adult_keywords = ["porn", "xxx", "sex", "nsfw", "adult", "nude", "XXX"]
            for keyword in adult_keywords:
                if keyword.lower() in url_lower:
                    if "sex.com" not in url_lower:  
                        continue
                    return False, "⚠️ ADULT CONTENT DETECTED — URL contains adult content indicators"
        except Exception:
            pass
        
        return True, "Not adult content"

    def check_suspicious_patterns(self, url: str) -> tuple[bool, str]:
       
        url_lower = url.lower()
        
        redirect_count = url.count("redirect=") + url.count("goto=") + url.count("next=")
        if redirect_count > 3:
            return False, "🚨 Suspicious: Multiple redirect parameters detected — potential phishing"
        
        shortener_domains = ["bit.ly", "tinyurl", "ow.ly", "goo.gl", "short.link"]
        for shortener in shortener_domains:
            if url_lower.count(shortener) > 1:
                return False, "🚨 Suspicious: Chained URL shorteners — potential hidden malware"
        
        special_chars = sum(not c.isalnum() and c not in "/:.-_?&=" for c in url)
        if special_chars > 10:
            return False, "🚨 Suspicious: Highly obfuscated URL detected"
        
        dangerous_ports = [":1433", ":3389", ":3306", ":27017"]
        for port in dangerous_ports:
            if port in url:
                return False, f"🚨 Suspicious: URL contains dangerous port {port}"
        
        return True, "No suspicious patterns detected"

    def check_url(self, url: str) -> tuple[float, bool, str, dict]:
        
        warnings = {}
        
        try:
            parsed = urlparse(url)
            domain = parsed.hostname or ""
            if not domain:
                domain = parsed.netloc or ""
            
            domain_lower = domain.lower()
            
            if domain_lower in SAFE_DOMAINS:
                return 1.0, True, "✓ Domain is whitelisted as safe", warnings
            
            domain_parts = domain_lower.split(".")
            for i in range(len(domain_parts)):
                check_domain = ".".join(domain_parts[i:])
                if check_domain in SAFE_DOMAINS:
                    return 1.0, True, "✓ Domain is whitelisted as safe", warnings
        except Exception as e:
            logger.warning(f"Whitelist check error: {e}")

        is_safe, reason = self.check_adult_content(url)
        if not is_safe:
            return 0.0, False, reason, {"warning_type": "ADULT_CONTENT", "message": reason}

        is_safe, reason = self.check_apk_malware(url)
        if not is_safe:
            return 0.0, False, reason, {"warning_type": "MALWARE", "message": reason}

        is_safe, reason = self.check_regex_rules(url)
        if not is_safe:
            return 0.0, False, reason, {"warning_type": "MALICIOUS_PATTERN", "message": reason}

        is_safe, reason = self.check_domain_blocklist(url)
        if not is_safe:
            return 0.1, False, reason, {"warning_type": "BLOCKED_DOMAIN", "message": reason}

        is_safe, reason = self.check_suspicious_patterns(url)
        if not is_safe:
            warnings["suspicious_patterns"] = reason
            if reason.startswith("🚨"):  # Critical warning
                return 0.2, False, reason, {"warning_type": "SUSPICIOUS", "message": reason}

        ml_score = self.get_ml_score(url)
        if ml_score < settings.safety_score_threshold:
            return ml_score, False, f"ML model flagged URL as suspicious (score: {ml_score:.2f})", \
                   {"warning_type": "ML_FLAGGED", "message": f"ML Score: {ml_score:.2f}"}

        return ml_score, True, "✓ URL passed all safety checks", warnings


url_safety_service = URLSafetyService()