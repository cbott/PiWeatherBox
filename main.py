# main.py
import logging

from apps.piweatherbox import WeatherBox

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s',
                        datefmt='%B %d, %Y %H:%M:%S')

    box = WeatherBox()
    box.mainloop()
