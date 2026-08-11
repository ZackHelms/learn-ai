#!/bin/bash
THISDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THISSCRIPT="$(basename "${BASH_SOURCE[0]}")"

function zrunall {
    local QQQ=$1
    local PPP=$2
    local MODEL=$3
    local NOWDTTM=$(date +"%Y%m%d_%H%M%S_%Z")
    local LOGFILE="$THISDIR/runall.${NOWDTTM}.log"
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
}
export -f zrunall

# QQQ=1 # DONE 10Aug2026 eval01 set1

QQQ=2
zrunall $QQQ r haiku45
zrunall $QQQ s sonnet5
zrunall $QQQ t opus5
zrunall $QQQ u fable5  # ~1h
