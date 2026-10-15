from agent import LoanSupportAgent
def test_healthy():
    r=LoanSupportAgent("healthy").run()
    assert r["status"]=="SUCCESS" and len(r["events"])==4
def test_timeout():
    r=LoanSupportAgent("api_timeout").run()
    assert r["status"]=="FAILED" and any(e["http_status"]==504 for e in r["events"])
def test_quality_regression():
    r=LoanSupportAgent("quality_regression").run()
    assert r["status"]=="DEGRADED" and r["quality_flags"]
