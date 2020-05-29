# PiAwareLEDd
Blink LED when PiAware packet received

---
# PiawareLEDd.py - Daemon 
#   - Connect to dump1090-fa port (127.0.0.1:30003)
#   - Blink LED when packet received
#      * RED - No data
#      * GREEN - Some data
#   - Separate thread for LDR  - modify LED brightness - DAY/NIGHT mode
