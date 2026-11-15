# Icon batch brief

The prompt for each drawing subagent: "Read dev/icons/BRIEF.md and follow it. Your batch:
tmp/batches/NN.txt". The batch lists and tmp/breeze22 come from dev/icons/plan-batches.py.

Draw monochrome symbolic icons for a KDE icon theme. Repo: /workspaces/kde-theme-molden-mate.
Do not commit. Write only the SVGs of your own batch (plus scratch PNGs in your scratch dir).

Read first:
- dev/icons/STYLE.md: the style rules. Follow them exactly (skeleton, stroke 1.6, round caps/joins,
  24 grid, live area 3..21, paths only).
- dev/icons/src/*.svg: the existing icons (several hundred; read the ones related to your batch,
  not all of them). Yours must look like they belong to this set. When the base icon of a family
  already exists (document-new for document-*, drive-harddisk for drive-*), reuse its shape. Good
  references: folder, user-home, edit-find, configure, view-refresh, document-open, help-about.
- tmp/breeze22/<context>/<name>.svg (context = actions, places, devices, status or emblems): the
  Breeze original for each name. Keep its metaphor, draw it fresh, don't trace. Breeze details that
  don't survive 16 px go.

Consistency inside families matters more than detail:
- folder-* places: start from dev/icons/src/folder.svg exactly and put a small symbol inside it, like
  folder-documents, folder-music and folder-download do.
- document-* / edit-* variants of one base (e.g. document-edit-encrypt): reuse the base shape and
  add one small badge; don't redraw the base differently each time.
- Names that only differ by a suffix (-ltr/-rtl, -symbolic) must mirror or match each other.

Output: dev/icons/src/<name>.svg, one per name in your batch file. Overwrite if it exists.

Check: build one contact sheet of your batch instead of one render per file, e.g.
  docker run --rm -v "$PWD:/repo" -w /repo --entrypoint bash golden-delicious-shot:6.8 -c '
    for n in $(cat tmp/batches/NN.txt); do
      rsvg-convert -w 48 -h 48 dev/icons/src/$n.svg -o /tmp/$n-48.png
      rsvg-convert -w 16 -h 16 dev/icons/src/$n.svg -o /tmp/$n-16.png; done
    montage /tmp/*-48.png -background "#2B2B2D" -geometry +6+6 -tile 10x tmp/batches/NN-48.png
    montage /tmp/*-16.png -background "#2B2B2D" -geometry +4+4 -tile 10x tmp/batches/NN-16.png'
Look at both PNGs with the Read tool (the 16 px one is small, which is the point), fix what doesn't
read well, then delete those two PNGs.

Report back in under 8 lines: icons you're unsure about and why. No list of what you did.
