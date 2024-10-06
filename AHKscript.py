from ahk import AHK
import time

def ahk_script(num_accounts, extended_hours, start_from, stop_event, market_limit, buy_sell, delay_speed, update_status):

    ahk.click() 
    if extended_hours == True:
        if buy_sell == 'Buy':
            first_tab = 16
            second_tab = 14
        elif buy_sell == 'Sell':
            first_tab = 18
            second_tab = 16
        if market_limit == 'Market':
            first_tab -= 2
            second_tab -= 2
    elif extended_hours == False:
        if buy_sell == 'Buy':
            first_tab = 17
            second_tab = 15
        elif buy_sell == 'Sell':
            first_tab = 19
            second_tab = 17
        if market_limit == 'Market':
            first_tab -= 2
            second_tab -= 2
        
    if start_from == 0:
        update_status(1)
        ahk.click()
        for _ in range(first_tab):
            ahk.send('{Tab}') 
            time.sleep(0.1)
        ahk.send('{Enter}')
        time.sleep(2) 
        ahk.send('{Enter}')  
        time.sleep(1)
    print(num_accounts)

    for account_num in range(start_from+1, num_accounts +1):

        if stop_event.is_set():
            break

        update_status(account_num+1)
        
        time.sleep(1) 
        ahk.click()  
        time.sleep(1)  
        for _ in range(2):
            ahk.send('{Tab}') 
        ahk.send('{Enter}') 

        time.sleep(1) 
        for _ in range(account_num):
            ahk.send('{Down}')
        time.sleep(1)
        ahk.send('{Enter}') 

        time.sleep(1.5) 

        for _ in range(second_tab):
            ahk.send('{Tab}')
            time.sleep(0.1)
        time.sleep(1) 
        ahk.send('{Enter}') 
        time.sleep(2) 
        ahk.send('{Enter}')  
        time.sleep(1)  
        ahk.click() 


def stop_script():
    global stop_event
    ahk.stop_hotkeys()
    stop_event.set()

ahk = AHK()