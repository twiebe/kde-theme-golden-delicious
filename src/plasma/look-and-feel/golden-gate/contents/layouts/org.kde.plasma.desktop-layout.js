// One floating top panel: launcher and tasks left, tray and clock right.
var panel = new Panel;
panel.location = "top";
panel.height = 44;
panel.floating = true;

panel.addWidget("org.kde.plasma.kickoff");
panel.addWidget("org.kde.plasma.icontasks");
panel.addWidget("org.kde.plasma.panelspacer");
panel.addWidget("org.kde.plasma.systemtray");
panel.addWidget("org.kde.plasma.digitalclock");
