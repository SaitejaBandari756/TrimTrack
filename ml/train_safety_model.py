import os
import random
import numpy as np
import pandas as pd
from urllib.parse import urlparse
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import re


def generate_synthetic_dataset(n_safe=5000, n_phishing=5000):
    safe_domains = [
        "google.com", "github.com", "stackoverflow.com", "python.org",
        "wikipedia.org", "amazon.com", "microsoft.com", "apple.com",
        "youtube.com", "twitter.com", "linkedin.com", "medium.com",
        "reddit.com", "nytimes.com", "bbc.co.uk", "cnn.com",
        "numpy.org", "fastapi.tiangolo.com", "docs.python.org",
    ]
    safe_paths = [
        "", "/", "/about", "/docs", "/api/v1", "/blog/post-123",
        "/products", "/search?q=test", "/user/profile", "/help",
    ]
    phishing_patterns = [
        "http://{ip}/login.php?id={id}",
        "http://secure-{bank}.{tld}/verify",
        "http://{random}.{sus_tld}/account/update",
        "http://{ip}/paypal-verify.html",
        "https://login.{random}.{sus_tld}/auth",
        "http://{random}.{sus_tld}/free-prize-claim",
        "http://{ip}/microsoft-support.exe",
        "http://account-verify.{sus_tld}/signin",
        "http://{ip}/update-info.bat",
    ]
    sus_tlds = ["tk", "ml", "ga", "cf", "gq", "xyz", "top", "pw", "click", "link"]
    bank_names = ["chase", "wellsfargo", "bofa", "citi", "hsbc"]

    urls, labels = [], []

    for _ in range(n_safe):
        domain = random.choice(safe_domains)
        path = random.choice(safe_paths)
        protocol = random.choice(["https://", "https://www."])
        urls.append(f"{protocol}{domain}{path}")
        labels.append(1) 

    for _ in range(n_phishing):
        pattern = random.choice(phishing_patterns)
        ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
        url = pattern.format(
            ip=ip,
            bank=random.choice(bank_names),
            tld=random.choice(sus_tlds),
            random="".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=random.randint(5, 15))),
            sus_tld=random.choice(sus_tlds),
            id=random.randint(1000, 9999),
        )
        urls.append(url)
        labels.append(0) 

    return urls, labels


def extract_features(url: str) -> list:
    try:
        parsed = urlparse(url)
    except Exception:
        parsed = urlparse("http://invalid")

    domain = parsed.hostname or ""
    path = parsed.path or ""
    sus_tlds = {".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".pw"}

    return [
        len(url),
        url.count("."),
        url.count("-"),
        sum(c.isdigit() for c in url),
        1.0 if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", domain) else 0.0,
        path.count("/"),
        1.0 if parsed.query else 0.0,
        sum(not c.isalnum() and c not in "/:.-_" for c in url),
        len(domain),
        1.0 if any(domain.endswith(tld) for tld in sus_tlds) else 0.0,
    ]


def main():
    print("=" * 60)
    print("URL Safety Classifier — Training")
    print("=" * 60)

    print("\n[1/4] Generating synthetic dataset...")
    urls, labels = generate_synthetic_dataset(5000, 5000)
    print(f"  Total samples: {len(urls)} (Safe: {sum(labels)}, Phishing: {len(labels) - sum(labels)})")

    print("[2/4] Extracting features...")
    features = np.array([extract_features(url) for url in urls])
    labels = np.array(labels)

    feature_names = [
        "url_length", "dot_count", "hyphen_count", "digit_count",
        "has_ip", "path_depth", "has_query", "special_chars",
        "domain_length", "suspicious_tld",
    ]

    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.2, random_state=42, stratify=labels
    )
    print(f"  Train: {len(X_train)}, Test: {len(X_test)}")

    print("[3/4] Training Logistic Regression model...")
    model = LogisticRegression(max_iter=1000, random_state=42, C=1.0)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n[4/4] Evaluation Results:")
    print(f"  Accuracy: {accuracy:.4f} ({accuracy*100:.1f}%)")
    print(f"\n  Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Phishing", "Safe"]))
    print(f"  Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    print(f"\n  Feature Importance (coefficients):")
    for name, coef in sorted(zip(feature_names, model.coef_[0]), key=lambda x: abs(x[1]), reverse=True):
        print(f"    {name:20s}: {coef:+.4f}")

    os.makedirs("ml", exist_ok=True)
    model_path = "ml/model.pkl"
    joblib.dump(model, model_path)
    print(f"\n  Model saved to {model_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
