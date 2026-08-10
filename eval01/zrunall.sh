#!/bin/bash

# PPP=r; MODEL=haiku45
# PPP=s; MODEL=sonnet5
# PPP=t; MODEL=opus5
PPP=u; MODEL=fable5
QQQ=1

THISDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THISSCRIPT="$(basename "${BASH_SOURCE[0]}")"
NOWDTTM=$(date +"%Y%m%d_%H%M%S_%Z")
LOGFILE="$THISDIR/runall.${NOWDTTM}.log"
{
    date +"%Y-%m-%d_%H:%M:%S_%Z"
    echo "INFO: THISSCRIPT($THISSCRIPT)"
    echo "INFO:    THISDIR($THISDIR)"
    echo "INFO:    LOGFILE($LOGFILE)"
    $THISDIR/generate.sh $MODEL ${PPP}${QQQ}                # ask bare bones model+effort(5 levels) sessions to generate output html
    $THISDIR/eval_ashfall.py    ${PPP}${QQQ}{1..5}          # deterministic eval for each of the 5 model+effort output html (1..5)
    $THISDIR/grade.sh           ${PPP}${QQQ}{1..5}{a..e}    # does ai grading 5x (a..e) for each of the 5 model+effort output html
    $THISDIR/listscore.py       ${PPP}${QQQ}{1..5}{a..e}    # list all scores and AVG (of ai grades) per model+effort group
    date +"%Y-%m-%d_%H:%M:%S_%Z"
} | tee $LOGFILE

echo
echo "INFO: Full output in $(realpath $LOGFILE)"
echo
