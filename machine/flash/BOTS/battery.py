from machine import ADC
from math import floor

class Battery(ADC):
  "Define the battery class as an extension of the ADC."

  def __init__(self, pin):
    "Setup the ADC pin for reading battery voltage."
    super().__init__(pin)
    self.atten(self.ATTN_11DB)

  def read(self):
    "Read pin voltage and scale to battery voltage."

    voltage = super().read()*0.0057
    voltage = floor(voltage*10)/10 
    return voltage 
