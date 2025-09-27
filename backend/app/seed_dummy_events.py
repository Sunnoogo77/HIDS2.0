# # backend/app/scripts/seed_dummy_events.py
# from sqlalchemy.orm import Session
# from app.db.session import SessionLocal
# from app.db.models import Alert, ActivityEvent
# from datetime import datetime, timedelta
# import random

# def run():
#     db: Session = SessionLocal()
#     try:
#         # quelques alerts
#         severities = ["low","medium","high","critical"]
#         entities = ["file","folder","ip"]
#         for i in range(120):
#             sev = random.choice(severities)
#             et = random.choice(entities)
#             lbl = "/var/log/auth.log" if et!="ip" else "192.168.1.%d" % random.randint(2,254)
#             a = Alert(
#                 ts = datetime.utcnow() - timedelta(minutes=i),
#                 severity = sev,
#                 rule = "demo_rule_"+sev,
#                 entity_type = et,
#                 entity_id = i,
#                 entity_label = lbl,
#                 message = f"Dummy alert {i} ({sev}) on {et} {lbl}",
#                 meta = {"demo": True, "i": i}
#             )
#             db.add(a)

#         # quelques activity events
#         kinds = ["scan_started","scan_done","file_added","file_removed","ip_scanned"]
#         for i in range(150):
#             et = random.choice(entities)
#             lbl = "/etc/passwd" if et!="ip" else "10.0.0.%d" % random.randint(2,254)
#             ev = ActivityEvent(
#                 ts = datetime.utcnow() - timedelta(minutes=i),
#                 kind = random.choice(kinds),
#                 entity_type = et,
#                 entity_id = i,
#                 entity_label = lbl,
#                 message = f"Dummy event {i} on {et} {lbl}",
#                 meta = {"demo": True, "i": i}
#             )
#             db.add(ev)

#         db.commit()
#         print("Seed done.")
#     finally:
#         db.close()

# if __name__ == "__main__":
#     run()

