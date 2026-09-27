#!/usr/bin/env bash
# Wrapper for the overnight fleet hygiene cron.
#
# WHY THIS EXISTS: Hermes' cron `script:` field is a BARE PATH, not a command line.
# cron/scheduler_script.py::_resolve_script_path() validates the whole string as a filename
# inside HERMES_HOME/scripts/ and never splits arguments — so a script field reading
# "fleet-hygiene-audit.py --quiet" resolves to a non-existent filename and the job can
# never fire. (The same bug killed the fleet drift check's first cron.) This wrapper keeps
# the intended flags without changing the detector itself.
#
# EXIT CONTRACT — the job is `no_agent: true`, so this script IS the job.
# Hermes treats ANY non-zero exit as a FAILURE, whatever the script printed. So:
#   0 = ran fine, output delivered (findings OR "clean"; empty stdout sends nothing)
#   2 = a detector ERRORED — the scan could not measure everything (real failure)
#
# It is deliberately NOT 1-on-findings. Findings are a successful run of a detector, and
# exiting non-zero for them made the job raise a failure alert every night it found
# something — which is most nights. An alarm that always fires is as useless as one that
# never fires. Use `fleet-hygiene-audit.py --strict-exit` by hand for the human
# clean/findings distinction.
#
# Silent-when-clean is deliberate: an overnight report that always fires is noise, and
# noise gets ignored. It speaks when there is something to say.

set -euo pipefail
DIR="$(dirname "$(readlink -f "$0")")"
python3 "$DIR/fleet-hygiene-audit.py" --quiet
