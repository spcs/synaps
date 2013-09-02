#!/bin/bash

SYNAPS_DIR='synaps/' # include trailing slash
DOCS_DIR='source'

modules=''
for x in `find ${SYNAPS_DIR} -name '*.py' | grep -v synaps/tests`; do
    if [ `basename ${x} .py` == "__init__" ] ; then
        continue
    fi
    relative=synaps.`echo ${x} | sed -e 's$^'${SYNAPS_DIR}'$$' -e 's/.py$//' -e 's$/$.$g'`
    modules="${modules} ${relative}"
done

for mod in ${modules} ; do
  if [ ! -f "${DOCS_DIR}/${mod}.rst" ];
  then
    echo ${mod}
  fi
done
