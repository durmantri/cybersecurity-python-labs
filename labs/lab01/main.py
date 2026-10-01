import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from labs.lab01.task1 import main as main1
from labs.lab01.task2 import main as main2
from labs.lab01.task3 import main as main3

if __name__ == "__main__":
    main1()
    main2()
    main3()