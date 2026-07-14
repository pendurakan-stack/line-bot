#!/usr/bin/env python3
"""
Update requirements.txt on GitHub with new versions
Fix numpy.dtype ValueError by adding numpy version constraint
Run this on YOUR LOCAL COMPUTER NOW
"""

import requests
import base64

# Configuration
TOKEN = "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"
REPO = "pendurakan-stack/line-bot"
FILE = "requirements.txt"

# New requirements with numpy version constraint
NEW_REQUIREMENTS = """flask>=3.0.0
line-bot-sdk>=3.0.0
pandas>=2.0.0
numpy>=1.24.0,<2.0.0
openpyxl>=3.1.0
python-dotenv>=1.0.0
requests>=2.31.0
gunicorn>=21.2.0
beautifulsoup4>=4.12.0
APScheduler>=3.10.0
lxml>=4.9.0
"""

print("=" * 60)
print("🔧 UPDATING requirements.txt on GitHub")
print("=" * 60)

# Step 1: Get current file SHA
print("\n📖 Step 1: Fetching current file from GitHub...")
headers = {"Authorization": f"token {TOKEN}"}
url = f"https://api.github.com/repos/{REPO}/contents/{FILE}"

try:
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch file: {response.status_code}")
        print(f"   Check token and repository name")
        exit(1)

    sha = response.json()['sha']
    print(f"✅ Got SHA: {sha[:8]}...")

    # Step 2: Encode new content
    print("\n📝 Step 2: Preparing new requirements.txt...")
    content_b64 = base64.b64encode(NEW_REQUIREMENTS.encode()).decode()
    print(f"✅ File ready ({len(NEW_REQUIREMENTS)} bytes)")

    # Step 3: Update file
    print("\n📤 Step 3: Updating file on GitHub...")
    payload = {
        "message": "fix: add numpy version constraint to fix ValueError numpy.dtype issue",
        "content": content_b64,
        "sha": sha,
        "branch": "main"
    }

    response = requests.put(url, json=payload, headers=headers)

    if response.status_code in [200, 201]:
        print("✅ File updated successfully!")
        commit_sha = response.json()['commit']['sha'][:8]
        print(f"   Commit: {commit_sha}")

        print("\n" + "=" * 60)
        print("🚀 Railway will auto-redeploy in ~30-60 seconds")
        print("=" * 60)
        print("📊 Status will change:")
        print("   🔴 Crashed → 🟡 Building → 🟢 Active")
        print("\n⏳ Waiting...")
        print("\n📋 Changes made:")
        print("   • numpy>=1.24.0,<2.0.0  (NEW - fixes ValueError)")
        print("   • All other packages use >= (flexible versions)")
        print("\n📱 When complete, send a test message to LINE bot!")

    else:
        print(f"❌ Update failed: {response.status_code}")
        print(f"   Response: {response.json()}")
        exit(1)

except requests.exceptions.RequestException as e:
    print(f"❌ Error: {e}")
    exit(1)

print("\n✅ All done!")
