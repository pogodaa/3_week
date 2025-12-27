from app.services.statistics import load_requests_from_excel, calculate_avg_repair_time

def test_avg_repair_time():
    requests = load_requests_from_excel()
    avg = calculate_avg_repair_time(requests)
    assert avg == 68.0