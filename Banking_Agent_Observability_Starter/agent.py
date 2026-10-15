import argparse, json, time, uuid
from datetime import datetime, timezone
from pathlib import Path

CUSTOMERS={"CUST-1001":{"customer_ref":"CUST-1001","name":"Alex Morgan","kyc_status":"VERIFIED"},
"CUST-1002":{"customer_ref":"CUST-1002","name":"Jamie Taylor","kyc_status":"PENDING"}}
LOANS={"LOAN-2001":{"loan_ref":"LOAN-2001","loan_type":"Home Loan","status":"UNDER_REVIEW"},
"LOAN-2002":{"loan_ref":"LOAN-2002","loan_type":"Personal Loan","status":"APPROVED"}}
def now(): return datetime.now(timezone.utc).isoformat()

class MockBankingAPIs:
    def __init__(self, scenario): self.scenario=scenario
    def call(self, name, request):
        start=time.perf_counter(); status=200; error=None
        if self.scenario=="api_timeout" and name=="KYC Verification API":
            time.sleep(.08); status=504; error="Simulated KYC API timeout"; response={"error":"timeout"}
        elif self.scenario=="api_500" and name=="Loan Status API":
            status=500; error="Simulated upstream service error"; response={"error":"upstream_error"}
        elif self.scenario=="invalid_response" and name=="Customer Profile API":
            response={"customer_ref":request.get("customer_ref"),"profile":None}
        elif name=="Customer Profile API": response=CUSTOMERS.get(request.get("customer_ref"),{"error":"customer_not_found"})
        elif name=="Loan Status API": response=LOANS.get(request.get("loan_ref"),{"error":"loan_not_found"})
        elif name=="KYC Verification API": response={"customer_ref":request.get("customer_ref"),"kyc_status":CUSTOMERS.get(request.get("customer_ref"),{}).get("kyc_status","UNKNOWN")}
        else: response={"loan_ref":request.get("loan_ref"),"risk_band":"LOW","assessment":"MOCK"}
        return {"api_name":name,"request":request,"response":response,"status_code":status,
                "duration_ms":round((time.perf_counter()-start)*1000,2),"success":status<400,"error":error}

class LoanSupportAgent:
    def __init__(self, scenario="healthy"): self.scenario=scenario; self.apis=MockBankingAPIs(scenario)
    def run(self, customer_ref="CUST-1001", loan_ref="LOAN-2001"):
        sid="sess-"+uuid.uuid4().hex[:10]; tid=uuid.uuid4().hex; started=now(); events=[]; errors=[]
        calls=[("Customer Profile API",{"customer_ref":customer_ref}),("Loan Status API",{"loan_ref":loan_ref}),
               ("KYC Verification API",{"customer_ref":customer_ref}),("Risk Assessment API",{"loan_ref":loan_ref})]
        results={}
        for name,req in calls:
            c=self.apis.call(name,req); status="OK" if c["success"] else "ERROR"; err=c["error"]
            if name=="Customer Profile API" and not c["response"].get("name"):
                status="ERROR"; err="ValidationError: customer profile missing"
            e={"session_id":sid,"trace_id":tid,"span_id":uuid.uuid4().hex[:16],"operation":name,
               "timestamp":now(),"duration_ms":c["duration_ms"],"status":status,"http_status":c["status_code"],
               "error":err,"request":c["request"],"response":c["response"]}
            events.append(e); results[name]=c["response"]
            if status=="ERROR": errors.append({"operation":name,"error":err or "Invalid response"})
        if self.scenario=="quality_regression":
            answer="Your request is complete."; quality=["Answer omits loan status and KYC status"]
        elif errors:
            answer="I could not fully verify your loan details. Please try again later or contact support."; quality=[]
        else:
            loan=results["Loan Status API"]; kyc=results["KYC Verification API"]
            answer=f"Your {loan.get('loan_type','loan')} status is {loan.get('status','UNKNOWN')}. Your KYC status is {kyc.get('kyc_status','UNKNOWN')}."
            quality=[]
        return {"session_id":sid,"trace_id":tid,"started_at":started,"ended_at":now(),"scenario":self.scenario,
                "question":"Check my loan status and KYC verification.","answer":answer,
                "status":"FAILED" if errors else ("DEGRADED" if quality else "SUCCESS"),
                "errors":errors,"quality_flags":quality,"events":events}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--scenario",choices=["healthy","api_timeout","api_500","invalid_response","quality_regression"],default="healthy")
    p.add_argument("--customer",default="CUST-1001"); p.add_argument("--loan",default="LOAN-2001"); p.add_argument("--output",default="data/latest_session.json")
    a=p.parse_args(); run=LoanSupportAgent(a.scenario).run(a.customer,a.loan)
    Path(a.output).parent.mkdir(parents=True,exist_ok=True); Path(a.output).write_text(json.dumps(run,indent=2),encoding="utf-8")
    print(json.dumps({k:run[k] for k in ["session_id","trace_id","scenario","status","answer","errors","quality_flags"]},indent=2))
    print("Saved synthetic session to:",a.output)
if __name__=="__main__": main()
