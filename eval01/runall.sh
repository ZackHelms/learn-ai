#!/bin/bash

# PPP=r; MODEL=haiku45
# PPP=s; MODEL=sonnet5
# PPP=t; MODEL=opus5
PPP=u; MODEL=fable5
QQQ=1

NOWDTTM=$(date +"%Y%m%d_%H%M%S_%Z")
LOGFILE="runall.${NOWDTTM}.log"
{
    date +"%Y-%m-%d_%H:%M:%S_%Z"
    ./eval01/generate.sh $MODEL ${PPP}${QQQ}                # ask bare bones model+effort(5 levels) sessions to generate output html
    ./eval01/eval_ashfall.py    ${PPP}${QQQ}{1..5}          # deterministic eval for each of the 5 model+effort output html (1..5)
    ./eval01/grade.sh           ${PPP}${QQQ}{1..5}{a..e}    # does ai grading 5x (a..e) for each of the 5 model+effort output html
    ./eval01/listscore.py       ${PPP}${QQQ}{1..5}{a..e}    # list all scores and AVG (of ai grades) per model+effort group
    date +"%Y-%m-%d_%H:%M:%S_%Z"
} | tee $LOGFILE

echo
echo "INFO: Full output in $(realpath $LOGFILE)"
echo
