# Icon correction brief

A correction pass over icons already drawn from BRIEF.md. Repo: /workspaces/kde-theme-molden-mate.
Do not commit. Read dev/icons/STYLE.md and dev/icons/BRIEF.md first; their rules still hold.

You get a list of batches. For each batch NN:
- tmp/batches/NN.txt lists its icon names (in dev/icons/src/<name>.svg),
- tmp/batches/reports/NN.md is what the drawing agent was unsure about.

Work:
1. Build one contact sheet per batch at 48 and 16 px (command as in BRIEF.md) and look at it.
2. Fix the icons the report flags and any other icon in the batch that clearly fails: does not read
   at 16 px, breaks the style, or looks like a different icon of the set. Prefer a simpler, bolder
   metaphor over shrinking details. A badge (lock, plus, gear, clock...) should take about a third
   of the icon, bottom right, with the base shape cut back around it.
3. Leave icons that are fine alone. Don't restyle what works.
4. Only edit names from your batch files. Skip battery-* names: another agent owns that family.
5. Delete your contact sheets when done.

Report back in under 6 lines: what you changed (names only) and anything still weak.
