# main.py
import logging

from apps.piweatherbox import WeatherBox

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                        datefmt='%B %d, %Y %H:%M:%S')

    box = WeatherBox()
    box.mainloop()
