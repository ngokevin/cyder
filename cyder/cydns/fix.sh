for file in `ls -l | grep -E ^d | awk '{print $9}'`;
do
    cd $file
    pwd
    ls *
    for afile in `ls *`
    do
        cat $afile
        cat $afile | sed 's/cyder\.c/cyder.cy/' > $afile
    done
    cd ..
done
