#!/bin/sh
# No mutation, temporary checkout, or arbitrary failure is accepted as inversion.
printf '%s\n' 'INCONCLUSIVE: automatic inversion is unsupported. Run named behavioral tests against isolated before/after revisions with the same locked dependencies; distinguish assertion failures from setup failures.'
exit 2
