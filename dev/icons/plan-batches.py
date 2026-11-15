# Splits the Breeze names still to draw into batch lists in tmp/batches and copies
# the Breeze 22px originals to tmp/breeze22 for reference. Run in the harness image:
#   docker run --rm -v "$PWD:/repo" -w /repo --entrypoint python3 golden-gate-shot:6.8 dev/icons/plan-batches.py
import os, re, shutil
B = "/usr/share/icons/breeze-dark"
done = {f[:-4] for f in os.listdir("dev/icons/src")}
redo = "go-previous go-next go-up view-list-icons view-list-details view-split-left-right edit-copy edit-cut edit-paste edit-delete edit-rename edit-undo edit-redo document-new folder-new tab-new tab-close".split()
colors = r"-(brown|magenta|green|black|yellow|cyan|orange|violet|grey|blue|red)$"
def names(ctx):
    d = f"{B}/{ctx}/22"
    return sorted(f[:-4] for f in os.listdir(d) if f.endswith(".svg") and not os.path.islink(f"{d}/{f}"))
# copy refs (resolved) for every context
for ctx in ["actions", "places", "devices", "status", "emblems"]:
    os.makedirs(f"tmp/breeze22/{ctx}", exist_ok=True)
    d = f"{B}/{ctx}/22"
    for f in os.listdir(d):
        if f.endswith(".svg"):
            shutil.copy(os.path.realpath(f"{d}/{f}"), f"tmp/breeze22/{ctx}/{f}")
skip = lambda n: n in done or n.endswith("-symbolic") or re.search(colors, n)
places = [n for n in names("places") if not skip(n)]
devices = [n for n in names("devices") if not skip(n)]
act = [n for n in names("actions") if not skip(n) and n not in redo
       and re.match(r"(go|edit|document|list|zoom|window|media|view)-", n)]
def chunks(l, k): 
    s = -(-len(l) // k); return [l[i:i+s] for i in range(0, len(l), s)]
batches = [redo] + chunks(places, 2) + chunks(devices, 2) + chunks(act[:140], 5)
for i, b in enumerate(batches, 1):
    open(f"tmp/batches/{i:02}.txt", "w").write("\n".join(b) + "\n")
    print(i, len(b), " ".join(b[:6]), "...")
print("places", len(places), "devices", len(devices), "actions core", len(act))
open("tmp/batches/actions-rest.txt", "w").write("\n".join(act[140:]) + "\n")
