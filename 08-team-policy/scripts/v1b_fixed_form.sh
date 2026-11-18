#!/bin/bash
# V1b: (1) serverName with the underscore plugin form; (2) FIXED-PATH plugin design: plugin starts /opt/kiran/bin/noor-bookings
# Run INSIDE WSL / Linux as root:  bash v1b_fixed_form.sh [lab-user]   (default: $LAB_USER). Removes the managed file at the end.
set -u
U="${1:-${LAB_USER:?set LAB_USER to the normal (non-root) lab user, or pass it as the first argument}}"; F=/etc/claude-code/managed-settings.json; EP8="$(cd "$(dirname "$0")/.." && pwd)"
asuser() { setpriv --reuid="$U" --regid="$U" --init-groups env -i HOME="/home/$U" USER="$U" PATH="/home/$U/.local/bin:/usr/bin:/bin" TERM=dumb "$@"; }
run() { printf '{ "allowManagedMcpServersOnly": true, "allowedMcpServers": %s }\n' "$2" > "$F"; echo "=== $1"; echo "policy: $2"; asuser claude mcp list 2>&1 | grep -v '^Checking' | sed '/^$/d;s/^/  /'; echo; }
mkdir -p /etc/claude-code
run "G serverName plugin_kiran-noor_noor-bookings" '[{"serverName":"plugin_kiran-noor_noor-bookings"}]'
echo "--- switching kiran-noor to the FIXED-PATH form (v1.0.1): command /opt/kiran/bin/noor-bookings"
rm -f "$F"
NOOR_FORM=fixed bash "$EP8/scripts/setup-root.sh" | tail -1
asuser claude plugin marketplace update kiran-marketplace 2>&1 | tail -1
asuser claude plugin update kiran-noor@kiran-marketplace 2>&1 | tail -1
run "H fixed form, entry = [\"/opt/kiran/bin/noor-bookings\"]" '[{"serverCommand":["/opt/kiran/bin/noor-bookings"]}]'
run "I fixed form, control entry /bin/false" '[{"serverCommand":["/bin/false"]}]'
echo "--- user tries to re-point the same NAME at another command in ~/.claude.json (spoof)"
asuser claude mcp add --scope user noor-bookings -- /usr/bin/python3 -c 'print(1)' 2>&1 | sed 's/^/  /'
rm -f "$F"
