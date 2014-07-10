def quick_setup():
    global pump
    try:
        reload(pump_model)
    except:
        import pump_model
    pump = pump_model.Pump(3)
    #pump.accept_new('/dev/tty.usbserial-FTDWBH0Y')
    #pump.initialize_pump()

def status_debug():
    global pump
    print "TRY #1, no sleep!"
    pump.send_Command('A3000')
