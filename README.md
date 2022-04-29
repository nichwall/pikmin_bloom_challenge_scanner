# Pikmin Bloom Challenge Scanner
Scans screenshots of Pikmin Bloom Challenge screen to create a table of what were used

Currently, hearts seem to be detected correctly, individual pikmin are partitioned out from the main image, and color is detected. Color detection happens based on the name, so if a pikmin has been renamed, it will prompt the user for the color (Red, Yellow, Blue, White, Winged, Rock, Purple) and store the name so the user does not need to specify the color on a future run.

Todo:
- Detect decor
- Compare two screenshots from the same challenge and remove duplicate pikmin
- Add party attack calculation
- Store results to file
