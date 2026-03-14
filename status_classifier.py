def classify_status(subject):

    text = subject.lower()

    if "unfortunately" in text or "not selected" in text:
        return "Rejected"

    if "congratulations" in text or "next round" in text:
        return "Accepted"

    return "Applied"