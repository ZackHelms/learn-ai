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
        echo
        echo "INFO: `date +"%Y-%m-%d_%H:%M:%S_%Z"` QQQ($QQQ) PPP($PPP) MODEL($MODEL) LOGFILE($LOGFILE) - BEGIN"
        echo "INFO: THISSCRIPT($THISSCRIPT)"
        echo "INFO:    THISDIR($THISDIR)"
        echo "INFO:    LOGFILE($LOGFILE)"
        echo
        # ask bare bones model+effort(5 levels) sessions to generate output html
        echo "INFO: $THISDIR/generate.sh $MODEL ${PPP}${QQQ}"
                    $THISDIR/generate.sh $MODEL ${PPP}${QQQ}
        echo
        # deterministic eval for each of the 5 model+effort output html (1..5)
        echo "INFO: $THISDIR/eval_ashfall.py    ${PPP}${QQQ}{1..5}"
                    $THISDIR/eval_ashfall.py    ${PPP}${QQQ}{1..5}
        echo
        # ai grade 5x (a..e) for each of the 5 model+effort output html
        echo "INFO: $THISDIR/grade.sh           ${PPP}${QQQ}{1..5}{a..e}"
                    $THISDIR/grade.sh           ${PPP}${QQQ}{1..5}{a..e}
        echo
        # list all scores and AVG (of ai grades) per model+effort group
        echo "INFO: $THISDIR/listscore.py       ${PPP}${QQQ}{1..5}{a..e}"
                    $THISDIR/listscore.py       ${PPP}${QQQ}{1..5}{a..e}
        echo
        echo "INFO: `date +"%Y-%m-%d_%H:%M:%S_%Z"` QQQ($QQQ) PPP($PPP) MODEL($MODEL) LOGFILE($LOGFILE) - END"
    } |& tee $LOGFILE

    echo
    echo "INFO: Full output in $(realpath $LOGFILE)"
    echo
}
export -f zrunall

# QQQ=1 # DONE 22:00 10Aug2026 eval01 set1
# QQQ=2 # DONE 10:16 11Aug2026 eval01 set2

QQQ=3
zrunall $QQQ r haiku45    # 20m
zrunall $QQQ s sonnet5    # 47m
zrunall $QQQ t opus5      # 47m
zrunall $QQQ u fable5     # 60m
