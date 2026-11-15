// One floating top panel like the Mac menu bar: launcher and tasks left, tray
// and clock right. No pager, no "show desktop".
var panel = new Panel;
panel.location = "top";
panel.height = 44;
panel.floating = true;
panel.opacity = "translucent";
panel.hiding = "none";

// The theme's apple, also where the distribution set its own logo.
var kickoff = panel.addWidget("org.kde.plasma.kickoff");
kickoff.currentConfigGroup = ["General"];
kickoff.writeConfig("icon", "start-here-kde-symbolic");

panel.addWidget("org.kde.plasma.icontasks");
panel.addWidget("org.kde.plasma.marginsseparator");
panel.addWidget("org.kde.plasma.systemtray");

// A compact semibold clock with seconds, like the menu bar's.
var clock = panel.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("autoFontAndSize", false);
clock.writeConfig("fontFamily", "Inter");
clock.writeConfig("fontStyleName", "SemiBold");
clock.writeConfig("fontWeight", 600);
clock.writeConfig("boldText", true);
clock.writeConfig("fontSize", 8);
clock.writeConfig("showSeconds", "Always");
