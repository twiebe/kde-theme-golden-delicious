# Splits the Breeze names still to draw into batch lists tmp/batches/NN.txt and
# copies the Breeze originals to tmp/breeze22/<context>/ for reference (22 px,
# or 16 px where Breeze has no 22). Run in the harness image:
#   docker run --rm -v "$PWD:/repo" -w /repo --entrypoint python3 golden-delicious-shot:6.8 dev/icons/plan-batches.py [first-batch-number]
import os
import re
import shutil
import sys

B = "/usr/share/icons/breeze-dark"
CONTEXTS = ["actions", "places", "devices", "status", "emblems"]
SIZE = 28
first = int(sys.argv[1]) if len(sys.argv) > 1 else 1

done = {f[:-4] for f in os.listdir("dev/icons/src")}
# Colour variants of folders and -symbolic twins get aliased by the build, not drawn.
skip = re.compile(r"-(brown|magenta|green|black|yellow|cyan|orange|violet|grey|blue|red)$|-symbolic$")

todo = {}
for ctx in CONTEXTS:
    os.makedirs(f"tmp/breeze22/{ctx}", exist_ok=True)
    for size in ("16", "22"):  # 22 wins: copied last
        d = f"{B}/{ctx}/{size}"
        for f in os.listdir(d):
            if not f.endswith(".svg"):
                continue
            shutil.copy(os.path.realpath(f"{d}/{f}"), f"tmp/breeze22/{ctx}/{f}")
            n = f[:-4]
            if not os.path.islink(f"{d}/{f}") and n not in done and not skip.search(n):
                todo.setdefault(n, ctx)

names = sorted(todo)
for i in range(0, len(names), SIZE):
    num = first + i // SIZE
    with open(f"tmp/batches/{num:02}.txt", "w") as fh:
        fh.write("\n".join(names[i:i + SIZE]) + "\n")
print(f"{len(names)} names in batches {first:02}..{num:02}")
