// One floating top panel: launcher and tasks left, tray and clock right.
var panel = new Panel;
panel.location = "top";
panel.height = 44;
panel.floating = true;

// The theme's apple, also where the distribution set its own logo.
var kickoff = panel.addWidget("org.kde.plasma.kickoff");
kickoff.currentConfigGroup = ["General"];
kickoff.writeConfig("icon", "start-here-kde-symbolic");
panel.addWidget("org.kde.plasma.icontasks");
panel.addWidget("org.kde.plasma.panelspacer");
panel.addWidget("org.kde.plasma.systemtray");
panel.addWidget("org.kde.plasma.digitalclock");
