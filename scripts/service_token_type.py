import os

BASE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.abspath(os.path.join(BASE, ".."))

_token = os.environ.get("DOPPLER_TOKEN")

if _token:
    if not _token.startswith("dp"):
        print("[ERROR] - DOPPLER_TOKEN is not a valid Doppler token.")
        exit(1)

    if _token.startswith("dp"):
        tokenized = _token.split(".")
        if not len(tokenized) >= 3:
            print("[ERROR] - DOPPLER_TOKEN is not a valid Doppler token.")
            exit(1)
        
        if tokenized[1] == "pt":
            print("personal_token")
        elif tokenized[1] == "st":
            print("service_token")
        elif tokenized[1] == "sa":
            print("serivce_account")

else:
    print("[ERROR] - DOPPLER_TOKEN is not set.")
    exit(0)
