import up  # don't remove this
import core.bin.django_bin  # to enable django support
from core.scripts.runners.recent_convs import run_recent_convs

if __name__ == "__main__":
    run_recent_convs()
