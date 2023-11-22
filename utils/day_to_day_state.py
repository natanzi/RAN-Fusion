# day_to_day_state.py

from datetime import datetime

def adjust_traffic_pattern(ue):
    current_time = datetime.now().time()
    morning_peak = current_time >= datetime.strptime('07:00', '%H:%M').time() and current_time <= datetime.strptime('09:00', '%H:%M').time()
    noon_peak = current_time >= datetime.strptime('11:00', '%H:%M').time() and current_time <= datetime.strptime('14:00', '%H:%M').time()
    evening_peak = current_time >= datetime.strptime('17:00', '%H:%M').time() and current_time <= datetime.strptime('20:00', '%H:%M').time()
    night_peak = current_time >= datetime.strptime('22:00', '%H:%M').time() and current_time <= datetime.strptime('00:00', '%H:%M').time()

    if morning_peak or noon_peak or evening_peak or night_peak:
        # Increase the likelihood of video and data traffic during peak hours
        ue.ServiceType = 'video' if random.random() < 0.5 else 'data'
    else:
        # Otherwise, use the normal random distribution of service types
        ue.ServiceType = random.choice(["video", "game", "voice", "data", "IoT"])

    # Now generate traffic based on the updated service type
    return ue.generate_traffic()