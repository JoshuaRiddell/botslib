from machine import ADC

class Battery(object):
  def __init__(self, pin):
    "Setup the ADC pin for reading battery voltage."

    self.bat_adc = ADC(35)
    self.bat_adc.atten(ADC().ATTN_11DB)

  def read(self):
    "Read pin voltage and scale to battery voltage."

    voltage = self.bat_adc.read()*0.0057
    voltage = floor(voltage*10)/10 
    return voltage 
