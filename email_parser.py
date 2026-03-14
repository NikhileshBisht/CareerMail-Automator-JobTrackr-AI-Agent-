import re


def parse_email(sender, subject):

    company = sender.split("@")[-1].split(".")[0]

    job_id = None
    match = re.search(r'\d+', subject)

    if match:
        job_id = match.group()

    description = subject

    return company, job_id, description