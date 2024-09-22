import up  # don't remove this
import bot.bin.django_bin  # to enable django support
from bot.src.runners.recent_convs import run_recent_convs

if __name__ == "__main__":
    run_recent_convs()
