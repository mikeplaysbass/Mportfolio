import re
import os

def test_compliance():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    with open('css/style.css', 'r', encoding='utf-8') as f:
        css = f.read()

    with open('js/main.js', 'r', encoding='utf-8') as f:
        js = f.read()

    errors = []

    # 1. Viewport & Scaling
    if 'name="viewport"' not in html:
        errors.append("Missing viewport meta tag")
    if 'maximum-scale' in html or 'user-scalable=no' in html:
        errors.append("Disallowed viewport scaling restriction detected")

    # 2. Touch targets in CSS
    if 'min-height: 48px' not in css or 'min-width: 48px' not in css:
        errors.append("Touch targets missing explicit 48px minimum in CSS")

    # 3. LCP & Image Optimization
    if 'fetchpriority="high"' not in html:
        errors.append("LCP hero image missing fetchpriority='high'")
    
    # Check all img tags for width & height
    img_tags = re.findall(r'<img[^>]+>', html)
    for tag in img_tags:
        if 'width=' not in tag or 'height=' not in tag:
            errors.append(f"Image missing width or height: {tag}")
        if 'fetchpriority="high"' in tag and 'loading="lazy"' in tag:
            errors.append(f"Above-the-fold image should not have loading='lazy': {tag}")

    # 4. Form Labels
    input_ids = re.findall(r'<input[^>]+id="([^"]+)"', html)
    for i_id in input_ids:
        if f'for="{i_id}"' not in html:
            errors.append(f"Input id '{i_id}' missing matching <label for='{i_id}'>")

    # 5. Accessibility checks
    if ':focus-visible' not in css:
        errors.append("Missing :focus-visible in CSS")
    if 'prefers-reduced-motion' not in css:
        errors.append("Missing prefers-reduced-motion in CSS")
    if 'skip-to-content' not in html:
        errors.append("Missing accessible skip-to-content link")

    # 6. Asset existence
    srcs = re.findall(r'src="([^"]+)"', html) + re.findall(r'href="(css/[^"]+)"', html)
    for src in srcs:
        if src.startswith('http'):
            continue
        if not os.path.exists(src):
            errors.append(f"Referenced asset not found on disk: {src}")

    # 7. Mobile Nav Dialog
    if '<dialog id="mobile-nav-dialog"' not in html:
        errors.append("Missing mobile navigation <dialog>")

    # 8. Tour Section Blueprint
    if 'id="tour"' not in html:
        errors.append("Missing #tour section")
    if 'tour-card' not in html:
        errors.append("Missing tour-card component")

    print(f"Total verification checks completed.")
    if errors:
        print("ERRORS FOUND:")
        for err in errors:
            print(" -", err)
        return False
    else:
        print("ALL AUDIT & ACCESSIBILITY CRITERIA PASSED! 100% compliant with AGENTS.md.")
        return True

if __name__ == '__main__':
    success = test_compliance()
    exit(0 if success else 1)
