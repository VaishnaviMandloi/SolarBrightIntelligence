import model
from datetime import datetime, timedelta


def battery_calculation(initial_battery, latitude, longitude, date, power_consumption_rate, mode):
    date = datetime.strptime(date, "%Y-%m-%d")
    final_output = []
    for i in range(5):
        day_levels = {}
        current_date = date + timedelta(days=i)

        current_date_str = current_date.strftime("%Y-%m-%d")

        output_from_model = model.xgb_model(latitude, longitude, current_date_str, initial_battery)

        day_levels[output_from_model['sunrise_hour']] = initial_battery
        final_battery_percentage = min(100,output_from_model['total_increase'])
        day_duration = output_from_model['sunset_hour']-output_from_model['sunrise_hour'] + 1
        night_duration = 24 - day_duration
        output_for_consumption = consumption(final_battery_percentage,power_consumption_rate,mode,night_duration)

        battery_discharge = output_for_consumption[1]
        output_from_model['discharge'] = battery_discharge
        output_from_model['max_glow_time'] = output_for_consumption[0]
        final_output.append(output_from_model)
        initial_battery = battery_discharge

    return final_output


def consumption(initial_battery, power_consumption_rate, mode, night_duration, max_capacity=460):
    battery_capacity = initial_battery*(max_capacity/100)
    power_consumption_rate = power_consumption_rate * mode_finder(mode)
    max_glow_time = battery_capacity/power_consumption_rate

    if max_glow_time < night_duration:
        return (max_glow_time, 0)


    energy_consumed = power_consumption_rate*night_duration
    battery_final_capacity = battery_capacity - energy_consumed
    return (night_duration,battery_final_capacity/4.60)


def mode_finder(mode):
    mode_dic = {
        0: 0.30,
        1: 0.50,
        2: 0.70,
        3: 1
    }
    return mode_dic[int(mode)]


# out = battery_calculation(10, 25, 55, '2024-03-23', 20, 3)
# print(out)