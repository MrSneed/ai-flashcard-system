from datetime import date, timedelta

def sm2(quality:int, easiness:float, interval:int, repetitions: int):
    
    if quality<3:
        repetitions =0
        interval = 1
    
    else:
        if repetitions==0:
            interval = 1
        elif repetitions ==1:
            interval =6
        else:
            interval = round(interval*easiness) 
        repetitions+=1
    
    easiness = easiness + 0.1-(5-quality)*(0.08+(5-quality)*0.02)
    easiness = max(1.3, round(easiness, 2))

    next_due = date.today() + timedelta(days=interval)
    return easiness, interval, repetitions, next_due.isoformat()

