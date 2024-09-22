import up  # don't remove this
import bot.bin.django_bin  # to enable django support
from bot.src.runners.started_convs import run_started_convs

if __name__ == "__main__":
    run_started_convs()
