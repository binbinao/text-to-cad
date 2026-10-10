from __future__ import annotations
from cadgen import step
# Prompt: Socket head cap screw, M10 x 40, with a real helical ISO thread.

from lib.simple_model_library import make_socket_head_cap_screw


@step(out="../STEP/socket_head_cap_screw.step")
def socket_head_cap_screw():
    return make_socket_head_cap_screw()


if __name__ == "__main__":
    socket_head_cap_screw()
